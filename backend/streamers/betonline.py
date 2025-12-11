"""BetOnline raw data streamer."""

import os
from typing import Any, Dict, List, Optional

import httpx
import structlog

from .base import BaseStreamer

logger = structlog.get_logger()


class BetOnlineStreamer(BaseStreamer):
    """Streamer that fetches raw BetOnline game markets."""

    BASE_URL = "https://api-offering.betonline.ag/api/offering/Sports/offering-by-league"

    SPORT_LEAGUE_MAP: Dict[str, Dict[str, str]] = {
        "basketball_wnba": {"Sport": "basketball", "League": "wnba"},
        "basketball_nba": {"Sport": "basketball", "League": "nba"},
        "football_nfl": {"Sport": "football", "League": "nfl"},
        "football_cfb": {"Sport": "football", "League": "ncaa"},
        "baseball_mlb": {"Sport": "baseball", "League": "mlb", "Period": 1},
        "hockey_nhl": {"Sport": "hockey", "League": "nhl"},
        "tennis_atp": {"Sport": "tennis", "League": "atp", "ScheduleText": "atp-shanghai", "endpoint": "offering-by-scheduletext"},
        "soccer_epl": {"Sport": "soccer", "League": "epl", "ScheduleText": "english-premier-league", "endpoint": "offering-by-scheduletext"},
        "mma_ufc": {"Sport": "martial-arts", "League": "mma", "ScheduleText": "ufc-320", "endpoint": "offering-by-scheduletext"},
    }

    DEFAULT_HEADERS = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "gsetting": "bolsassite",
        "origin": "https://www.betonline.ag",
        "referer": "https://www.betonline.ag/",
        "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "utc-offset": "240",
        "x-requested-with": "XMLHttpRequest",
    }

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)

        self.sport = config.get("sport", "basketball_wnba")
        self.limit = config.get("limit", None)
        self.custom_payload = config.get("payload")
        self.cookie_header = config.get("cookie") or os.getenv("BETONLINE_COOKIES", "").strip()
        self.client: Optional[httpx.AsyncClient] = None

        logger.info("Initialized BetOnline streamer", sport=self.sport)

    async def connect(self) -> bool:
        try:
            headers = dict(self.DEFAULT_HEADERS)
            if self.cookie_header:
                headers["cookie"] = self.cookie_header

            self.client = httpx.AsyncClient(timeout=30.0, headers=headers)

            payload = self._build_payload(self.sport)
            if payload is None:
                logger.error("Unsupported BetOnline sport", sport=self.sport)
                return False

            # Determine the correct endpoint based on sport mapping
            mapping = self.SPORT_LEAGUE_MAP.get(self.sport, {})
            endpoint = mapping.get("endpoint", "offering-by-league")
            url = f"https://api-offering.betonline.ag/api/offering/Sports/{endpoint}"

            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            response.json()

            logger.info("Connected to BetOnline API", sport=self.sport)
            return True
        except Exception as exc:
            logger.error("Failed to connect to BetOnline API", error=str(exc))
            if self.client:
                await self.client.aclose()
            self.client = None
            return False

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
            logger.info("Disconnected from BetOnline API")
            self.client = None

    async def fetch_data(self) -> Dict[str, Any]:
        payload = self.custom_payload or self._build_payload(self.sport)
        if payload is None:
            raise RuntimeError(f"Unsupported sport: {self.sport}")

        logger.debug("Requesting BetOnline data", payload=payload)

        if not self.client:
            raise RuntimeError("Not connected to BetOnline API")

        # Determine the correct endpoint based on sport mapping
        mapping = self.SPORT_LEAGUE_MAP.get(self.sport, {})
        endpoint = mapping.get("endpoint", "offering-by-league")
        url = f"https://api-offering.betonline.ag/api/offering/Sports/{endpoint}"

        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        raw_json = response.json()

        return {
            "sport": self.sport,
            "payload": payload,
            "fetched_at": self._utc_now_iso(),
            "raw_response": raw_json,
        }

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "book": "betonline",
            "sport": raw_data.get("sport"),
            "payload": raw_data.get("payload"),
            "raw_response": raw_data.get("raw_response"),
            "fetched_at": raw_data.get("fetched_at"),
            "metadata": {
                "has_odds": True,
                "has_lines": True,
                "market_types": ["sportsbook"],
                "book_type": "sportsbook",
            },
        }

    @classmethod
    def get_supported_sports(cls) -> List[str]:
        return list(cls.SPORT_LEAGUE_MAP.keys())

    @classmethod
    def get_default_config(cls, sport: str) -> Dict[str, Any]:
        return {"sport": sport}

    def _build_payload(self, sport: str) -> Optional[Dict[str, Any]]:
        mapping = self.SPORT_LEAGUE_MAP.get(sport)
        if not mapping:
            return None
        payload = {
            "Sport": mapping["Sport"],
            "League": mapping["League"],
            "ScheduleText": mapping.get("ScheduleText"),
            "filterTime": 0,
        }
        # Add Period if specified (for MLB)
        if "Period" in mapping:
            payload["Period"] = mapping["Period"]
        # Allow caller to override filterTime via config
        if self.limit is not None:
            payload["eventsLimit"] = self.limit
        return payload

    @staticmethod
    def _utc_now_iso() -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()


