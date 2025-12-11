"""BettingPros streamer that fetches props with projections and bet ratings."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
import structlog

from streamers.base import BaseStreamer

logger = structlog.get_logger()


class BettingProsStreamer(BaseStreamer):
    """Streamer that fetches props with projections from BettingPros API."""

    BASE_URL = "https://api.bettingpros.com/v3/props"
    
    # Sport mapping
    SPORT_CONFIG = {
        "americanfootball_nfl": {"sport_key": "NFL", "name": "NFL"},
        "basketball_nba": {"sport_key": "NBA", "name": "NBA"},
        "baseball_mlb": {"sport_key": "MLB", "name": "MLB"},
        "icehockey_nhl": {"sport_key": "NHL", "name": "NHL"},
        "americanfootball_ncaaf": {"sport_key": "NCAAF", "name": "College Football"},
        "basketball_ncaab": {"sport_key": "NCAAB", "name": "College Basketball"},
    }

    DEFAULT_HEADERS = {
        "accept": "*/*",
        "x-level": "",
        "x-api-key": "3hRNO9y34O5QulijHJwqL8sct7h4kD7r4D2u63pX",
        "user-agent": "Betting Pros/972 CFNetwork/3860.300.21 Darwin/25.2.0",
        "priority": "u=3",
        "accept-language": "en-US,en;q=0.9",
    }

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        super().__init__(name, config)
        self.is_connected = False
        self.session: Optional[httpx.AsyncClient] = None
        self.location = config.get("location", "FL")
        self.sort = config.get("sort", "trending")

    async def connect(self) -> bool:
        """Connect to BettingPros API."""
        try:
            if self.session is None:
                self.session = httpx.AsyncClient(
                    headers=self.DEFAULT_HEADERS,
                    timeout=30.0,
                    follow_redirects=True,
                )
            self.is_connected = True
            logger.info("Connected to BettingPros API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to BettingPros API: {e}")
            self.is_connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from BettingPros API."""
        if self.session:
            await self.session.aclose()
            self.session = None
        self.is_connected = False
        logger.info("Disconnected from BettingPros API")

    async def fetch_data(self, sport: str = None, markets: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Fetch data from BettingPros API."""
        if not self.is_connected:
            await self.connect()

        if not self.is_connected:
            logger.error("Not connected to BettingPros API")
            return None

        # Use sport from config if not provided
        if sport is None:
            sport = self.config.get("sport", "americanfootball_nfl")

        sport_config = self.SPORT_CONFIG.get(sport)
        if not sport_config:
            logger.warning(f"Unsupported sport: {sport}, defaulting to NFL")
            sport_key = "NFL"
        else:
            sport_key = sport_config["sport_key"]

        try:
            logger.info(f"Fetching BettingPros props for sport: {sport} ({sport_key})")
            
            params = {
                "sport": sport_key,
                "include_markets": "true",
                "location": self.location,
                "sort": self.sort,
            }
            
            response = await self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Add sport context
            data["sport"] = sport
            data["sport_key"] = sport_key
            
            props_count = len(data.get("props", []))
            logger.info(f"Fetched BettingPros data: {props_count} props for {sport_key}")
            
            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching BettingPros data: {e.response.status_code} - {e.response.text[:200]}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error fetching BettingPros data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching BettingPros data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw BettingPros data into standardized format."""
        try:
            if not raw_data:
                return {"error": "No data found in BettingPros response"}
            
            props = raw_data.get("props", [])
            markets_data = raw_data.get("markets", {})
            
            # Build market lookup
            markets_by_id = {}
            if isinstance(markets_data, dict):
                for market_id, market_info in markets_data.items():
                    markets_by_id[int(market_id)] = market_info
            
            # Process props into player_props format
            player_props = []
            for prop in props:
                if not isinstance(prop, dict):
                    continue
                
                participant = prop.get("participant", {})
                player_info = participant.get("player", {})
                player_name = participant.get("name", "")
                if not player_name:
                    continue
                
                # Get market info
                market_id = prop.get("market_id")
                market_info = markets_by_id.get(market_id, {})
                stat_type = market_info.get("name", "")
                
                # Get projection info
                projection = prop.get("projection", {})
                recommended_side = projection.get("recommended_side", "")
                
                # Get over/under info
                over_data = prop.get("over", {})
                under_data = prop.get("under", {})
                
                # Create entries for both over and under
                for direction, side_data in [("over", over_data), ("under", under_data)]:
                    if not side_data:
                        continue
                    
                    line = side_data.get("line")
                    odds = side_data.get("odds")
                    book_id = side_data.get("book")
                    
                    if line is None or odds is None:
                        continue
                    
                    player_props.append({
                        "player_name": player_name,
                        "player_id": participant.get("id"),
                        "team": player_info.get("team"),
                        "position": player_info.get("position"),
                        "stat_type": stat_type,
                        "market_id": market_id,
                        "line": line,
                        "direction": direction,
                        "odds": odds,  # American odds
                        "book_id": book_id,
                        "consensus_line": side_data.get("consensus_line"),
                        "consensus_odds": side_data.get("consensus_odds"),
                        "probability": side_data.get("probability"),
                        "expected_value": side_data.get("expected_value"),
                        "bet_rating": side_data.get("bet_rating"),
                        "projection_value": projection.get("value"),
                        "projection_probability": projection.get("probability"),
                        "projection_ev": projection.get("expected_value"),
                        "projection_bet_rating": projection.get("bet_rating"),
                        "projection_diff": projection.get("diff"),
                        "recommended_side": recommended_side,
                        "is_recommended": (direction == recommended_side),
                        "event_id": prop.get("event_id"),
                        "sport": prop.get("sport", ""),
                        "opposition_rank": prop.get("extra", {}).get("opposition_rank", {}).get("rank"),
                        "opposition_value": prop.get("extra", {}).get("opposition_rank", {}).get("value"),
                    })
            
            processed_data = {
                "player_props": player_props,
                "total_props": len(player_props),
                "total_unique_props": len(props),
                "markets": markets_by_id,
                "sport": raw_data.get("sport", ""),
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Processed BettingPros data: {len(player_props)} prop entries from {len(props)} unique props")
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process BettingPros data: {e}")
            return {"error": str(e)}

    def get_supported_sports(self) -> List[str]:
        """Get list of supported sports."""
        return list(self.SPORT_CONFIG.keys())

    def get_sport_name(self, sport: str) -> str:
        """Get display name for a sport."""
        sport_config = self.SPORT_CONFIG.get(sport)
        return sport_config["name"] if sport_config else sport

    async def health_check(self) -> bool:
        """Check if BettingPros API is healthy."""
        try:
            if not self.is_connected:
                await self.connect()
            
            if not self.is_connected:
                return False

            # Test with NFL data
            data = await self.fetch_data("americanfootball_nfl")
            return data is not None and len(data.get("props", [])) > 0

        except Exception as e:
            logger.error(f"BettingPros health check failed: {e}")
            return False

    def __str__(self) -> str:
        return f"BettingProsStreamer(name={self.name}, connected={self.is_connected})"

    def __repr__(self) -> str:
        return self.__str__()
