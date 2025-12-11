"""Proply streamer that fetches model-driven picks with edge calculations."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
import structlog

from streamers.base import BaseStreamer

logger = structlog.get_logger()


class ProplyStreamer(BaseStreamer):
    """Streamer that fetches model-driven picks from Proply API."""

    BASE_URL = "https://propverse-api.onrender.com/api/picks"
    
    # Sport mapping
    SPORT_CONFIG = {
        "americanfootball_nfl": {"sport_key": "nfl", "name": "NFL"},
        "americanfootball_ncaaf": {"sport_key": "ncaaf", "name": "College Football"},
        "basketball_nba": {"sport_key": "nba", "name": "NBA"},
        "basketball_ncaab": {"sport_key": "ncaab", "name": "College Basketball"},
        "baseball_mlb": {"sport_key": "mlb", "name": "MLB"},
        "icehockey_nhl": {"sport_key": "nhl", "name": "NHL"},
    }

    DEFAULT_HEADERS = {
        "accept": "*/*",
        "content-type": "application/json",
        "user-agent": "Proply/89 CFNetwork/3860.300.21 Darwin/25.2.0",
        "priority": "u=3, i",
        "accept-language": "en-US,en;q=0.9",
    }

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        super().__init__(name, config)
        self.is_connected = False
        self.session: Optional[httpx.AsyncClient] = None
        self.limit = config.get("limit", 100000)  # NO LIMITS

    async def connect(self) -> bool:
        """Connect to Proply API."""
        try:
            if self.session is None:
                self.session = httpx.AsyncClient(
                    headers=self.DEFAULT_HEADERS,
                    timeout=30.0,
                    follow_redirects=True,
                )
            self.is_connected = True
            logger.info("Connected to Proply API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Proply API: {e}")
            self.is_connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from Proply API."""
        if self.session:
            await self.session.aclose()
            self.session = None
        self.is_connected = False
        logger.info("Disconnected from Proply API")

    async def fetch_data(self, sport: str = None, markets: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Fetch data from Proply API."""
        if not self.is_connected:
            await self.connect()

        if not self.is_connected:
            logger.error("Not connected to Proply API")
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
            logger.info(f"Fetching Proply picks for sport: {sport} ({sport_key})")
            
            params = {
                "includeBooks": "true",
                "limit": "100000",  # NO LIMITS
                "sport": sport_key,
            }
            
            response = await self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Add sport context
            data["sport"] = sport
            data["sport_key"] = sport_key
            
            picks_count = len(data.get("picks", []))
            logger.info(f"Fetched Proply data: {picks_count} picks for {sport_key}")
            
            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching Proply data: {e.response.status_code} - {e.response.text[:200]}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error fetching Proply data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching Proply data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw Proply data into standardized format."""
        try:
            if not raw_data:
                return {"error": "No data found in Proply response"}
            
            picks = raw_data.get("picks", [])
            
            # Process picks into player_props format
            player_props = []
            for pick in picks:
                if not isinstance(pick, dict):
                    continue
                
                player_info = pick.get("player", {})
                player_name = player_info.get("displayFirstLast", "")
                if not player_name:
                    continue
                
                game_info = pick.get("game", {})
                
                # Extract stat type from market
                market = pick.get("market", "")
                stat_type = market.replace("player_", "").replace("_", " ").title()
                
                player_props.append({
                    "pick_id": pick.get("pickId"),
                    "player_name": player_name,
                    "player_id": player_info.get("playerId"),
                    "team_id": player_info.get("teamId"),
                    "stat_type": stat_type,
                    "market": market,
                    "line": pick.get("line"),
                    "direction": pick.get("side"),  # "over" or "under"
                    "odds": pick.get("price"),  # American odds
                    "book": pick.get("book"),
                    "model_edge": pick.get("modelEdge"),
                    "confidence": pick.get("confidence"),
                    "rationale": pick.get("rationale"),
                    "game_id": pick.get("gameId"),
                    "game_date": game_info.get("gameDateUtc"),
                    "home_team_id": game_info.get("homeTeamId"),
                    "away_team_id": game_info.get("awayTeamId"),
                    "created_at": pick.get("createdAt"),
                    "sport": raw_data.get("sport", ""),
                })
            
            processed_data = {
                "player_props": player_props,
                "total_picks": len(player_props),
                "metadata": raw_data.get("metadata", {}),
                "sport": raw_data.get("sport", ""),
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Processed Proply data: {len(player_props)} picks")
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process Proply data: {e}")
            return {"error": str(e)}

    def get_supported_sports(self) -> List[str]:
        """Get list of supported sports."""
        return list(self.SPORT_CONFIG.keys())

    def get_sport_name(self, sport: str) -> str:
        """Get display name for a sport."""
        sport_config = self.SPORT_CONFIG.get(sport)
        return sport_config["name"] if sport_config else sport

    async def health_check(self) -> bool:
        """Check if Proply API is healthy."""
        try:
            if not self.is_connected:
                await self.connect()
            
            if not self.is_connected:
                return False

            # Test with NFL data
            data = await self.fetch_data("americanfootball_nfl")
            return data is not None and len(data.get("picks", [])) > 0

        except Exception as e:
            logger.error(f"Proply health check failed: {e}")
            return False

    def __str__(self) -> str:
        return f"ProplyStreamer(name={self.name}, connected={self.is_connected})"

    def __repr__(self) -> str:
        return self.__str__()
