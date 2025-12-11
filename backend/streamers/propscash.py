"""PropsCash raw data streamer."""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
import structlog

from .base import BaseStreamer

logger = structlog.get_logger()


class PropsCashStreamer(BaseStreamer):
    """Streamer that fetches raw data from the PropsCash API."""

    BASE_URL = "https://api.props.cash"

    SPORT_MAP: Dict[str, Tuple[str, str]] = {
        "americanfootball_nfl": ("NFL", "NFL"),
        "football_nfl": ("NFL", "NFL"),
        "baseball_mlb": ("MLB", "MLB"),
        "americanfootball_ncaaf": ("NCAAF", "NCAAF"),
        "football_cfb": ("NCAAF", "NCAAF"),
        "esports_csgo": ("CSGO", "CSGO"),
        "esports_cs2": ("CSGO", "CSGO"),
        "basketball_wnba": ("WNBA", "WNBA"),
        "basketball_nba": ("NBA", "NBA"),
    }

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)

        self.sport = config.get("sport", "football_nfl")
        if self.sport not in self.SPORT_MAP:
            raise ValueError(f"Unsupported PropsCash sport: {self.sport}")

        self.token = config.get("token") or self._load_token()
        if not self.token:
            logger.warning("PROPSCASH_TOKEN environment variable not set - PropsCash will return empty data")

        self.timeout = config.get("timeout", 30.0)
        self.client: Optional[httpx.AsyncClient] = None

        logger.info("Initialized PropsCash streamer", sport=self.sport)
    
    def _load_token(self) -> Optional[str]:
        """Load PropsCash token from environment variable."""
        return os.getenv("PROPSCASH_TOKEN")

    async def connect(self) -> bool:
        # Return False immediately if no token is available
        if not self.token:
            logger.warning("Cannot connect to PropsCash API without token")
            return False
            
        try:
            self.client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=self._default_headers(),
            )

            # minimal connectivity test
            lower_path, _ = self.SPORT_MAP[self.sport]
            url = f"{self.BASE_URL}/{lower_path}/lines"
            resp = await self.client.get(url, headers=self._auth_headers())
            resp.raise_for_status()

            logger.info("Connected to PropsCash API", sport=self.sport)
            return True
        except Exception as exc:
            logger.error("Failed to connect to PropsCash API", sport=self.sport, error=str(exc))
            if self.client:
                await self.client.aclose()
            self.client = None
            return False

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
            logger.info("Disconnected from PropsCash API")
            self.client = None

    async def fetch_data(self) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("PropsCash client is not connected")

        lower_path, upper_league = self.SPORT_MAP[self.sport]
        headers = self._auth_headers()

        async def _fetch(path: str) -> Optional[Dict[str, Any]]:
            url = f"{self.BASE_URL}/{path}"
            try:
                resp = await self.client.get(url, headers=headers)
                if resp.status_code == 404:
                    logger.warning("PropsCash endpoint returned 404", url=url)
                    return {"error": "not_found", "url": url}
                resp.raise_for_status()
                data = resp.json()
                return data if isinstance(data, dict) else {"data": data}
            except Exception as exc:
                logger.error("Error fetching PropsCash endpoint", url=url, error=str(exc))
                return {"error": str(exc), "url": url}

        lines_path = f"{lower_path}/lines"
        projections_path = f"{upper_league}/projections"
        trends_path = f"{upper_league}/prop-trends"

        lines, projections, trends = await asyncio.gather(
            _fetch(lines_path),
            _fetch(projections_path),
            _fetch(trends_path),
        )

        return {
            "sport": self.sport,
            "paths": {
                "lines": lines_path,
                "projections": projections_path,
                "prop_trends": trends_path,
            },
            "raw_lines": lines,
            "raw_projections": projections,
            "raw_prop_trends": trends,
            "fetched_at": self._utc_now_iso(),
        }

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "book": "propscash",
            "sport": raw_data.get("sport"),
            "paths": raw_data.get("paths"),
            "fetched_at": raw_data.get("fetched_at"),
            "raw_lines": raw_data.get("raw_lines"),
            "raw_projections": raw_data.get("raw_projections"),
            "raw_prop_trends": raw_data.get("raw_prop_trends"),
            "metadata": {
                "has_odds": False,
                "has_multipliers": False,
                "market_types": ["player_props"],
                "book_type": "analytics",
            },
        }

    @classmethod
    def get_supported_sports(cls) -> List[str]:
        return list(cls.SPORT_MAP.keys())

    @classmethod
    def get_default_config(cls, sport: str) -> Dict[str, Any]:
        if sport not in cls.SPORT_MAP:
            raise ValueError(f"Unsupported PropsCash sport: {sport}")
        return {"sport": sport}

    @staticmethod
    def _load_token() -> Optional[str]:
        token = os.getenv("PROPSCASH_TOKEN", "").strip()
        if token.startswith("'") and token.endswith("'"):
            token = token[1:-1]
        if token.startswith('"') and token.endswith('"'):
            token = token[1:-1]
        return token or None

    def _auth_headers(self) -> Dict[str, str]:
        headers = self._default_headers().copy()
        headers["Authorization"] = f"Bearer {self.token}"
        return headers

    @staticmethod
    def _default_headers() -> Dict[str, str]:
        return {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Origin": "https://props.cash",
            "Referer": "https://props.cash/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Sec-GPC": "1",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/139.0.0.0 Safari/537.36"
            ),
        }

    @staticmethod
    def _utc_now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
    
    @classmethod
    def get_default_config(cls, sport: str) -> Dict[str, Any]:
        """Get default configuration for PropsCash streamer."""
        return {
            "sport": sport,
            "token": os.getenv("PROPSCASH_TOKEN")
        }

