"""Base class for streamers that use PropsCash as the backend scraper."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx
import structlog

from .base import BaseStreamer

logger = structlog.get_logger()


class PropsCashBackedStreamer(BaseStreamer):
    """Base streamer that uses PropsCash API to scrape a specific bookmaker."""

    BASE_URL = "https://api.props.cash"
    
    # Child classes must set this
    BOOKMAKER_NAME: str = None

    # Sport mapping for PropsCash API - based on PropsCash supported sports
    # Official PropsCash sports: NFL, NCAAF, NBA, WNBA, MLB, NHL
    SPORT_MAP: Dict[str, str] = {
        "americanfootball_nfl": "nfl",
        "football_nfl": "nfl",
        "americanfootball_ncaaf": "ncaaf",
        "baseball_mlb": "mlb",
        "basketball_wnba": "wnba",
        "basketball_nba": "nba",
        "icehockey_nhl": "nhl",
    }

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        if not self.BOOKMAKER_NAME:
            raise ValueError(f"{self.__class__.__name__} must set BOOKMAKER_NAME")

        self.sport = config.get("sport", "americanfootball_nfl")
        if self.sport not in self.SPORT_MAP:
            raise ValueError(f"Unsupported sport for PropsCash: {self.sport}")

        self.token = config.get("token") or self._load_token()
        if not self.token:
            logger.warning(
                f"PROPSCASH_TOKEN not set - {self.BOOKMAKER_NAME} will return empty data"
            )

        self.timeout = config.get("timeout", 30.0)
        self.client: Optional[httpx.AsyncClient] = None

        logger.info(
            f"Initialized {self.BOOKMAKER_NAME} streamer (PropsCash backend)",
            sport=self.sport
        )

    def _load_token(self) -> Optional[str]:
        """Load PropsCash token from environment variable."""
        token = os.getenv("PROPSCASH_TOKEN", "").strip()
        if token.startswith("'") and token.endswith("'"):
            token = token[1:-1]
        if token.startswith('"') and token.endswith('"'):
            token = token[1:-1]
        return token or None

    async def connect(self) -> bool:
        if not self.token:
            logger.warning(f"Cannot connect to PropsCash for {self.BOOKMAKER_NAME} without token")
            return False

        try:
            self.client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=self._default_headers(),
            )

            # Test connectivity
            sport_path = self.SPORT_MAP[self.sport]
            url = f"{self.BASE_URL}/{sport_path}/lines"
            resp = await self.client.get(url, headers=self._auth_headers())
            resp.raise_for_status()

            logger.info(f"Connected to PropsCash for {self.BOOKMAKER_NAME}", sport=self.sport)
            return True
        except Exception as exc:
            logger.error(
                f"Failed to connect to PropsCash for {self.BOOKMAKER_NAME}",
                sport=self.sport,
                error=str(exc)
            )
            if self.client:
                await self.client.aclose()
            self.client = None
            return False

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
            logger.info(f"Disconnected PropsCash for {self.BOOKMAKER_NAME}")
            self.client = None

    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch and filter PropsCash data for specific bookmaker."""
        if not self.client:
            raise RuntimeError(f"PropsCash client not connected for {self.BOOKMAKER_NAME}")

        sport_path = self.SPORT_MAP[self.sport]
        url = f"{self.BASE_URL}/{sport_path}/lines"
        
        try:
            resp = await self.client.get(url, headers=self._auth_headers())
            resp.raise_for_status()
            data = resp.json()
            
            if not isinstance(data, list):
                logger.error(f"Unexpected PropsCash response format for {self.BOOKMAKER_NAME}")
                return []
            
            # Filter data to only include our bookmaker
            filtered_data = self._filter_for_bookmaker(data)
            
            logger.info(
                f"Fetched {len(filtered_data)} props for {self.BOOKMAKER_NAME}",
                sport=self.sport,
                total_players=len(data)
            )
            
            return filtered_data
            
        except Exception as exc:
            logger.error(
                f"Error fetching data for {self.BOOKMAKER_NAME}",
                error=str(exc)
            )
            return []

    def _filter_for_bookmaker(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter PropsCash data to only include props for our bookmaker."""
        filtered = []
        
        for player in data:
            player_name = player.get("name")
            game_id = player.get("gameId")
            home_team = player.get("homeTeam")
            away_team = player.get("awayTeam")
            team = player.get("team")
            position = player.get("position")
            projection = player.get("projection", {})
            
            # Extract props for our bookmaker
            player_props = {}
            
            for stat_type, stat_data in projection.items():
                books = stat_data.get("books", [])
                
                # Find our bookmaker in the books list
                for book_entry in books:
                    if book_entry.get("book") == self.BOOKMAKER_NAME:
                        player_props[stat_type] = {
                            "line": book_entry.get("value"),
                            "over_price": book_entry.get("overPrice"),
                            "under_price": book_entry.get("underPrice"),
                        }
                        break
            
            # Only include player if they have props for our bookmaker
            if player_props:
                filtered.append({
                    "player_name": player_name,
                    "game_id": game_id,
                    "home_team": home_team,
                    "away_team": away_team,
                    "team": team,
                    "position": position,
                    "props": player_props,
                })
        
        return filtered

    async def process_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process filtered data into standard format."""
        return {
            "book": self.BOOKMAKER_NAME.lower().replace(" ", ""),
            "sport": self.sport,
            "raw_data": raw_data,
            "metadata": {
                "has_odds": True,
                "has_multipliers": False,
                "market_types": ["player_props"],
                "book_type": "sportsbook",
                "source": "propscash_scraper",
            },
        }

    @classmethod
    def get_supported_sports(cls) -> List[str]:
        """Get list of supported sports - based on PropsCash API.
        
        Official PropsCash sports:
        - American Football: NFL, NCAAF
        - Basketball: NBA, WNBA
        - Baseball: MLB
        - Ice Hockey: NHL
        """
        return list(cls.SPORT_MAP.keys())

    @classmethod
    def get_default_config(cls, sport: str) -> Dict[str, Any]:
        if sport not in cls.SPORT_MAP:
            raise ValueError(f"Unsupported sport: {sport}")
        return {
            "sport": sport,
            "token": os.getenv("PROPSCASH_TOKEN"),
        }

    def _auth_headers(self) -> Dict[str, str]:
        headers = self._default_headers().copy()
        headers["Authorization"] = f"Bearer {self.token}"
        return headers

    @staticmethod
    def _default_headers() -> Dict[str, str]:
        return {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Origin": "https://www.props.cash",
            "Referer": "https://www.props.cash/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Sec-GPC": "1",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/141.0.0.0 Safari/537.36"
            ),
        }


