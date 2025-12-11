"""Walter streamer that fetches props with EV edge calculations across 16 sportsbooks."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx
import structlog

from streamers.base import BaseStreamer

logger = structlog.get_logger()


class WalterStreamer(BaseStreamer):
    """KashRock EV streamer that fetches props with EV edge calculations across sportsbooks."""

    BASE_URL = "https://ymn9v0kx.apicdn.sanity.io/v1/data/query/production"
    
    # Sport mapping
    SPORT_CONFIG = {
        "americanfootball_nfl": {"sport_key": "nfl", "name": "NFL"},
        "basketball_nba": {"sport_key": "nba", "name": "NBA"},
        "baseball_mlb": {"sport_key": "mlb", "name": "MLB"},
        "icehockey_nhl": {"sport_key": "nhl", "name": "NHL"},
        "americanfootball_ncaaf": {"sport_key": "ncaaf", "name": "College Football"},
        "basketball_ncaab": {"sport_key": "ncaab", "name": "College Basketball"},
    }

    # Sanity query to get all props with EV edge
    QUERY_TEMPLATE = """*[_type == "bettingPropV2" 
    && sport == $sport
] {      
      'player': player->{
            '_ref': _id,
            "photo_url": photo.asset->url,
            ...
          },
        'sportsbookLines': sportsbookLines[defined(evEdgeValue)  ] | order(evEdgeValue desc),
        'sportsbookLinesByEvEdgeValue': sportsbookLines[defined(evEdgeValue)  ] | order(evEdgeValue desc),
        ...,
        } [count(sportsbookLines) > 0] {
          "bestLine": sportsbookLines[0].evEdgeValue,
          "bestLineByEvEdgeValue": sportsbookLinesByEvEdgeValue[0].evEdgeValue,
          ...
        } | order(bestLine desc)"""

    DEFAULT_HEADERS = {
        "accept": "application/json",
        "user-agent": "picksapp/2434 CFNetwork/3860.300.21 Darwin/25.2.0",
        "priority": "u=3, i",
        "accept-language": "en-US,en;q=0.9",
    }

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        super().__init__(name, config)
        self.is_connected = False
        self.session: Optional[httpx.AsyncClient] = None

    async def connect(self) -> bool:
        """Connect to Walter API."""
        try:
            if self.session is None:
                self.session = httpx.AsyncClient(
                    headers=self.DEFAULT_HEADERS,
                    timeout=30.0,
                    follow_redirects=True,
                )
            self.is_connected = True
            logger.info("Connected to Walter API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Walter API: {e}")
            self.is_connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from Walter API."""
        if self.session:
            await self.session.aclose()
            self.session = None
        self.is_connected = False
        logger.info("Disconnected from Walter API")

    async def fetch_data(self, sport: str = None, markets: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Fetch data from Walter API."""
        if not self.is_connected:
            await self.connect()

        if not self.is_connected:
            logger.error("Not connected to Walter API")
            return None

        # Use sport from config if not provided
        if sport is None:
            sport = self.config.get("sport", "americanfootball_nfl")

        sport_config = self.SPORT_CONFIG.get(sport)
        if not sport_config:
            logger.warning(f"Unsupported sport: {sport}, defaulting to NFL")
            sport_key = "nfl"
        else:
            sport_key = sport_config["sport_key"]

        try:
            logger.info(f"Fetching Walter props for sport: {sport} ({sport_key})")
            
            # Build query params
            params = {
                "query": self.QUERY_TEMPLATE,
                "$sport": f'"{sport_key}"',
            }
            
            response = await self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Add sport context
            data["sport"] = sport
            data["sport_key"] = sport_key
            
            props_count = len(data.get("result", []))
            logger.info(f"Fetched Walter data: {props_count} props for {sport_key}")
            
            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching Walter data: {e.response.status_code} - {e.response.text[:200]}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error fetching Walter data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching Walter data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw Walter data into standardized format."""
        try:
            if not raw_data:
                return {"error": "No data found in Walter response"}
            
            result = raw_data.get("result", [])
            
            # Process props into player_props format
            player_props = []
            total_lines = 0
            
            for prop in result:
                if not isinstance(prop, dict):
                    continue
                
                player = prop.get("player", {})
                player_name = player.get("name", "")
                if not player_name:
                    continue
                
                # Get prop details
                bet_type = prop.get("betType", "")
                best_ev = prop.get("bestLine")
                
                # Get team info
                team = player.get("team", {})
                team_abbr = team.get("abbreviation", "")
                
                # Get opponent
                opponent = prop.get("opponentName", "")
                
                # Get game info
                game_string = prop.get("gameString", "")
                
                # Process each sportsbook line
                sportsbook_lines = prop.get("sportsbookLines", [])
                total_lines += len(sportsbook_lines)
                
                for line_data in sportsbook_lines:
                    if not isinstance(line_data, dict):
                        continue
                    
                    line = line_data.get("line")
                    outcome_type = line_data.get("outcomeType", "")  # over/under
                    american_odds = line_data.get("americanOdds")
                    sportsbook = line_data.get("sportsbook", "")
                    
                    # EV metrics
                    ev_edge_value = line_data.get("evEdgeValue")  # Expected value edge
                    expected_value = line_data.get("expectedValue")
                    
                    # Walter's calculations
                    walter_value = line_data.get("walterValue")
                    walter_probability = line_data.get("walterProbability")
                    
                    # No-vig calculations
                    no_vig_odds = line_data.get("noVigAmericanOdds")
                    no_vig_probability = line_data.get("noVigImpliedProbability")
                    
                    player_props.append({
                        "player_name": player_name,
                        "player_id": player.get("_ref"),
                        "team": team_abbr,
                        "opponent": opponent,
                        "stat_type": bet_type,
                        "line": line,
                        "direction": outcome_type,
                        "odds": american_odds,  # American odds
                        "book": sportsbook,
                        # Walter calculations
                        "walter_value": walter_value,
                        "walter_probability": walter_probability,
                        # EV calculations
                        "ev_edge_value": ev_edge_value,
                        "expected_value": expected_value,
                        "best_ev": best_ev,
                        # No-vig calculations
                        "no_vig_odds": no_vig_odds,
                        "no_vig_probability": no_vig_probability,
                        # Metadata
                        "game_string": game_string,
                        "prop_id": prop.get("_id"),
                        "sport": prop.get("sport", raw_data.get("sport", "")),
                        "link_to_sportsbook": line_data.get("linkToSportsbook"),
                    })
            
            processed_data = {
                "player_props": player_props,
                "total_props": len(player_props),
                "total_unique_props": len(result),
                "total_sportsbook_lines": total_lines,
                "sport": raw_data.get("sport", ""),
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Processed Walter data: {len(player_props)} prop entries from {len(result)} unique props with {total_lines} sportsbook lines")
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process Walter data: {e}")
            return {"error": str(e)}

    def get_supported_sports(self) -> List[str]:
        """Get list of supported sports."""
        return list(self.SPORT_CONFIG.keys())

    def get_sport_name(self, sport: str) -> str:
        """Get display name for a sport."""
        sport_config = self.SPORT_CONFIG.get(sport)
        return sport_config["name"] if sport_config else sport

    async def health_check(self) -> bool:
        """Check if Walter API is healthy."""
        try:
            if not self.is_connected:
                await self.connect()
            
            if not self.is_connected:
                return False

            # Test with NFL data
            data = await self.fetch_data("americanfootball_nfl")
            return data is not None and len(data.get("result", [])) > 0

        except Exception as e:
            logger.error(f"Walter health check failed: {e}")
            return False

    def __str__(self) -> str:
        return f"WalterStreamer(name={self.name}, connected={self.is_connected})"

    def __repr__(self) -> str:
        return self.__str__()
