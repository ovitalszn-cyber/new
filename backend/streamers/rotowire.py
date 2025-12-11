"""Rotowire streamer that fetches player props with multi-book odds and projections."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
import structlog

from streamers.base import BaseStreamer

logger = structlog.get_logger()


class RotowireStreamer(BaseStreamer):
    """Streamer that fetches player props from Rotowire API with multi-book odds."""

    BASE_URL = "https://www.rotowire.com/apps/api/picks/lines.php"
    
    # Sport mapping
    SPORT_CONFIG = {
        "americanfootball_nfl": {"sport_key": "NFL", "name": "NFL"},
        "basketball_nba": {"sport_key": "NBA", "name": "NBA"},
        "icehockey_nhl": {"sport_key": "NHL", "name": "NHL"},
        "baseball_mlb": {"sport_key": "MLB", "name": "MLB"},
        "americanfootball_ncaaf": {"sport_key": "CFB", "name": "College Football"},
        "basketball_ncaab": {"sport_key": "CBB", "name": "College Basketball"},
        "mma_ufc": {"sport_key": "MMA", "name": "MMA"},
        "soccer": {"sport_key": "Soccer", "name": "Soccer"},
    }

    DEFAULT_HEADERS = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "RotoWirePicks/4 CFNetwork/3860.300.21 Darwin/25.2.0",
        "priority": "u=3, i",
        "cookie": "PHPSESSID=1ef9f67a68976db6ad941dcfe4c4896a",
        "sentry-trace": "f3982253419e47d3bc935023c0b9c325-1cda3ff4280349e5-0",
        "baggage": "sentry-environment=production,sentry-public_key=d8a7a6d0445656bafaeea490249d4a38,sentry-release=com.rotowire.picks%401.11.0%2B4,sentry-trace_id=f3982253419e47d3bc935023c0b9c325",
    }

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        super().__init__(name, config)
        self.is_connected = False
        self.session: Optional[httpx.AsyncClient] = None

    async def connect(self) -> bool:
        """Connect to Rotowire API."""
        try:
            if self.session is None:
                self.session = httpx.AsyncClient(
                    headers=self.DEFAULT_HEADERS,
                    timeout=30.0,
                    follow_redirects=True,
                )
            self.is_connected = True
            logger.info("Connected to Rotowire API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Rotowire API: {e}")
            self.is_connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from Rotowire API."""
        if self.session:
            await self.session.aclose()
            self.session = None
        self.is_connected = False
        logger.info("Disconnected from Rotowire API")

    async def fetch_data(self, sport: str = None, markets: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Fetch data from Rotowire API."""
        if not self.is_connected:
            await self.connect()

        if not self.is_connected:
            logger.error("Not connected to Rotowire API")
            return None

        # Use sport from config if not provided
        if sport is None:
            sport = self.config.get("sport", "americanfootball_nfl")

        sport_config = self.SPORT_CONFIG.get(sport)
        if not sport_config:
            logger.warning(f"Unsupported sport: {sport}, fetching all sports")
            sport_key = None
        else:
            sport_key = sport_config["sport_key"]

        # Retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching Rotowire data for sport: {sport} ({sport_key}) - attempt {attempt + 1}/{max_retries}")
                
                response = await self.session.get(self.BASE_URL)
                response.raise_for_status()
                
                raw_data = response.json()
                
                # Filter by sport if specified
                if sport_key:
                    # Filter markets, entities, events, and props by sport
                    markets_list = raw_data.get("markets", [])
                    filtered_markets = [m for m in markets_list if m.get("sport") == sport_key]
                    
                    entities_list = raw_data.get("entities", [])
                    filtered_entities = [e for e in entities_list if e.get("sport") == sport_key]
                    
                    events_list = raw_data.get("events", [])
                    # Events don't have sport field, so we'll keep all for now
                    
                    props_list = raw_data.get("props", [])
                    # Filter props by checking if their marketID is in filtered markets
                    market_ids = {m["marketID"] for m in filtered_markets}
                    filtered_props = [p for p in props_list if p.get("marketID") in market_ids]
                    
                    filtered_data = {
                        "logos": raw_data.get("logos", {}),
                        "markets": filtered_markets,
                        "entities": filtered_entities,
                        "events": events_list,  # Keep all events for now
                        "props": filtered_props,
                        "sport": sport,
                        "sport_key": sport_key,
                    }
                    
                    logger.info(f"Filtered Rotowire data: {len(filtered_props)} props, {len(filtered_markets)} markets, {len(filtered_entities)} entities")
                    return filtered_data
                else:
                    # Return all data
                    raw_data["sport"] = sport
                    logger.info(f"Fetched all Rotowire data: {len(raw_data.get('props', []))} props")
                    return raw_data

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching Rotowire data (attempt {attempt + 1}): {e.response.status_code} - {e.response.text[:200]}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    continue
                return None
            except httpx.RequestError as e:
                logger.error(f"Request error fetching Rotowire data (attempt {attempt + 1}): {str(e)} - {type(e).__name__}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return None
            except Exception as e:
                logger.error(f"Unexpected error fetching Rotowire data (attempt {attempt + 1}): {str(e)} - {type(e).__name__}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return None
        
        return None

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw Rotowire data into standardized format."""
        try:
            if not raw_data:
                return {"error": "No data found in Rotowire response"}
            
            # Build entity lookup
            entities_by_id = {}
            for entity in raw_data.get("entities", []):
                entities_by_id[entity.get("entityID")] = entity
            
            # Build market lookup
            markets_by_id = {}
            for market in raw_data.get("markets", []):
                markets_by_id[market.get("marketID")] = market
            
            # Build event lookup
            events_by_id = {}
            for event in raw_data.get("events", []):
                events_by_id[event.get("eventID")] = event
            
            # Process props into player_props format
            player_props = []
            for prop in raw_data.get("props", []):
                market_id = prop.get("marketID")
                market = markets_by_id.get(market_id, {})
                
                # Get player info
                entity_ids = prop.get("entities", [])
                if not entity_ids:
                    continue
                
                entity = entities_by_id.get(entity_ids[0], {})
                player_name = entity.get("name", "")
                if not player_name:
                    continue
                
                event_id = entity.get("eventID")
                event = events_by_id.get(event_id, {})
                
                # Get lines from all books
                lines = prop.get("lines", [])
                
                # Create a prop entry for each book's line
                for line_data in lines:
                    book = line_data.get("book", "")
                    line_value = line_data.get("line")
                    over_odds = line_data.get("over")
                    under_odds = line_data.get("under")
                    
                    if line_value is None:
                        continue
                    
                    # Create entries for over and under
                    for direction, odds in [("over", over_odds), ("under", under_odds)]:
                        if odds is None:
                            continue
                        
                        player_props.append({
                            "prop_id": prop.get("propID"),
                            "player_name": player_name,
                            "player_link": entity.get("link"),
                            "stat_type": market.get("marketName", ""),
                            "market_category": market.get("category", ""),
                            "line": line_value,
                            "direction": direction,
                            "odds": odds,  # American odds
                            "book": book,
                            "projection": prop.get("projection"),
                            "event_id": event_id,
                            "event_name": event.get("eventName", ""),
                            "event_time": event.get("eventTime"),
                            "opponent": event.get("opponent", ""),
                            "sport": market.get("sport", ""),
                            "line_time": line_data.get("lineTime"),
                            "open_line": line_data.get("open"),
                            "prev_line": line_data.get("prev"),
                        })
            
            processed_data = {
                "player_props": player_props,
                "total_props": len(player_props),
                "total_unique_props": len(raw_data.get("props", [])),
                "total_markets": len(raw_data.get("markets", [])),
                "total_entities": len(raw_data.get("entities", [])),
                "total_events": len(raw_data.get("events", [])),
                "sport": raw_data.get("sport", ""),
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Processed Rotowire data: {len(player_props)} player prop entries from {len(raw_data.get('props', []))} unique props")
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process Rotowire data: {e}")
            return {"error": str(e)}

    def get_supported_sports(self) -> List[str]:
        """Get list of supported sports."""
        return list(self.SPORT_CONFIG.keys())

    def get_sport_name(self, sport: str) -> str:
        """Get display name for a sport."""
        sport_config = self.SPORT_CONFIG.get(sport)
        return sport_config["name"] if sport_config else sport

    async def health_check(self) -> bool:
        """Check if Rotowire API is healthy."""
        try:
            if not self.is_connected:
                await self.connect()
            
            if not self.is_connected:
                return False

            # Test with a simple fetch
            data = await self.fetch_data()
            return data is not None and len(data.get("props", [])) > 0

        except Exception as e:
            logger.error(f"Rotowire health check failed: {e}")
            return False

    def __str__(self) -> str:
        return f"RotowireStreamer(name={self.name}, connected={self.is_connected})"

    def __repr__(self) -> str:
        return self.__str__()
