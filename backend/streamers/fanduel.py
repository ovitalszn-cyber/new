"""FanDuel streamer that fetches live data from FanDuel Sportsbook API."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
import structlog

from streamers.base import BaseStreamer

logger = structlog.get_logger()


class FanDuelStreamer(BaseStreamer):
    """Streamer that fetches live data from FanDuel Sportsbook API."""

    # Sport mapping to FanDuel sport keys
    SPORT_CONFIG = {
        "americanfootball_nfl": {"sport_key": "nfl", "name": "NFL"},
        "americanfootball_ncaaf": {"sport_key": "ncaaf", "name": "College Football"},
        "basketball_nba": {"sport_key": "nba", "name": "NBA"},
        "basketball_wnba": {"sport_key": "wnba", "name": "WNBA"},
        "baseball_mlb": {"sport_key": "mlb", "name": "MLB"},
        "tennis": {"sport_key": "tennis", "name": "Tennis"},
        "mma": {"sport_key": "ufc", "name": "UFC/MMA"},
        "soccer_epl": {"sport_key": "epl", "name": "Premier League"},
        "soccer_uefa_champs_league": {"sport_key": "champions-league", "name": "Champions League"},
        "soccer_bundesliga": {"sport_key": "bundesliga", "name": "Bundesliga"},
        "soccer_serie_a": {"sport_key": "serie-a", "name": "Serie A"},
        "soccer_la_liga": {"sport_key": "la-liga", "name": "La Liga"},
        "soccer_mls": {"sport_key": "mls", "name": "MLS"},
    }

    # Default headers for FanDuel API
    DEFAULT_HEADERS = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "FanDuel-Sportsbook-iOS/2.128.1",
        "x-sportsbook-region": "AZ",
        "x-px-mobile-sdk-version": "3.2.6",
        "x-px-os": "iOS",
        "priority": "u=3, i",
        "baggage": "sentry-environment=production,sentry-public_key=0fc780cc19bb4cbcb513799a05770a00,sentry-release=2.128.1,sentry-trace_id=6b93a8c8f56d499da66849bc56ddca15",
        "sentry-trace": "6b93a8c8f56d499da66849bc56ddca15-9c81afb580284998-0",
        "cookie": "_gcl_au=1.1.2000388436.1755290453; amp_device_id=ca91b871-b819-4789-958e-c5a76fe191e3; __ssid=e2099952c9cb29e08ac0a5025721502; __pxvid=f13f1274-7a17-11f0-8bbc-a6dd854b44ac; _pxvid=f0ebf760-7a17-11f0-9658-b3fdd6e896eb; ab.storage.deviceId.de97bfbd-f043-4228-8cf1-4e42e6947527=%7B%22g%22%3A%222a071534-51c7-1015-f2b8-19f6d990bf90%22%2C%22c%22%3A1755290367625%2C%22l%22%3A1755290367625%7D; ab.storage.sessionId.de97bfbd-f043-4228-8cf1-4e42e6947527=%7B%22g%22%3A%225a16abf7-d6da-f044-069a-07a85dbe1efa%22%2C%22e%22%3A1755292167622%2C%22c%22%3A1755290367622%2C%22l%22%3A1755290367622%7D",
        "x-px-vid": "7c16ecda-590e-11f0-917c-a4d7d5430527",
        "x-px-uuid": "97c3f90e-a221-11f0-a8b5-f7e498bf3e43",
        "x-px-authorization": "3:a5004c183ecbe7f51a1e245615b2d6cd2afc3625245bb1c4290a795b941e5327:h2Cza2sl6m/nIbtisLEOjijyTqytG1PQNmfMdzKmLk0MdPyhlq/z1dny51idQXqnO0xD5JSJzf/Ashd2I0jDBg==:1000:wnU4uLYhdpXRMt+lEVNTZl9MXzwlY4VzbxsipZ1Y+Q7miO2aoNwKsPaY+dC2Wg0fwiTvaQyQBk74fJ2JH5H9voTaaKFJBHo2EBNSydRplTZvdeJzWIDKNZuffqhvdTrprDIk71Ashc12bGZxkJm/6ICJBIIybyAZdX1QlEYYvW8W9WInWnDIv4YWhdkIY93/E8SWKiAREqYMf3gzuRIeIY03GBw7+OIUPaFbqtm4VrA=",
    }

    BASE_URL = "https://api.sportsbook.fanduel.com/sbapi/content-managed-page"

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        super().__init__(name, config)
        self.is_connected = False
        self.session: Optional[httpx.AsyncClient] = None

    async def connect(self) -> bool:
        """Connect to FanDuel API."""
        try:
            if self.session is None:
                self.session = httpx.AsyncClient(
                    headers=self.DEFAULT_HEADERS,
                    timeout=30.0,
                    follow_redirects=True,
                )
            self.is_connected = True
            logger.info("Connected to FanDuel API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to FanDuel API: {e}")
            self.is_connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from FanDuel API."""
        if self.session:
            await self.session.aclose()
            self.session = None
        self.is_connected = False
        logger.info("Disconnected from FanDuel API")

    async def fetch_data(self, sport: str = None, markets: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Fetch data from FanDuel API for a specific sport."""
        if not self.is_connected:
            await self.connect()

        if not self.is_connected:
            logger.error("Not connected to FanDuel API")
            return None

        # Use sport from config if not provided
        if sport is None:
            sport = self.config.get("sport", "americanfootball_nfl")

        sport_config = self.SPORT_CONFIG.get(sport)
        if not sport_config:
            logger.warning(f"Unsupported sport: {sport}")
            return None

        try:
            params = {
                "page": "CUSTOM",
                "customPageId": sport_config["sport_key"],
                "pbHorizontal": "true",
                "_ak": "oN2groXWNuItc4hZ",
                "timezone": "America/Phoenix"
            }

            logger.info(f"Fetching FanDuel data for sport: {sport} ({sport_config['sport_key']})")
            
            response = await self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched FanDuel data for {sport}")
            
            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching FanDuel data for {sport}: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error fetching FanDuel data for {sport}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching FanDuel data for {sport}: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw FanDuel data into standardized format."""
        try:
            if not raw_data or "attachments" not in raw_data:
                return {"error": "No attachments found in FanDuel data"}
            
            attachments = raw_data["attachments"]
            markets_data = attachments.get("markets", {})
            events_data = attachments.get("events", {})
            
            processed_data = {
                "markets": markets_data,
                "events": events_data,
                "total_markets": len(markets_data),
                "total_events": len(events_data),
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Processed FanDuel data: {len(markets_data)} markets, {len(events_data)} events")
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process FanDuel data: {e}")
            return {"error": str(e)}

    def get_supported_sports(self) -> List[str]:
        """Get list of supported sports."""
        return list(self.SPORT_CONFIG.keys())

    def get_sport_name(self, sport: str) -> str:
        """Get display name for a sport."""
        sport_config = self.SPORT_CONFIG.get(sport)
        return sport_config["name"] if sport_config else sport

    async def health_check(self) -> bool:
        """Check if FanDuel API is healthy."""
        try:
            if not self.is_connected:
                await self.connect()
            
            if not self.is_connected:
                return False

            # Test with NFL data
            data = await self.fetch_data("americanfootball_nfl")
            return data is not None and "attachments" in data

        except Exception as e:
            logger.error(f"FanDuel health check failed: {e}")
            return False

    def __str__(self) -> str:
        return f"FanDuelStreamer(name={self.name}, connected={self.is_connected})"

    def __repr__(self) -> str:
        return self.__str__()