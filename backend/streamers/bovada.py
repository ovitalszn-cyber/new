"""Bovada raw data streamer."""

import asyncio
from typing import Any, Dict, List, Optional

import httpx
import structlog

from .base import BaseStreamer

logger = structlog.get_logger()


class BovadaStreamer(BaseStreamer):
    """Streamer for Bovada sportsbook data (raw only)."""

    BASE_URL = "https://www.bovada.lv/services/sports/event/coupon/events/A/description"

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.bovada.lv/",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "X-Channel": "mobile",
        "X-Sport-Context": "FOOT",
        "Priority": "u=3, i",
        "Cookie": "TS01890ddd=014b5d5d07ee8fa07fc06df7f93ea847e8efc75fcbf1b6c70bc42bd5113af4669d0ebdbc0810a2d538f61c2997122b8b26470c21aac4e3687d4aa82383c4010eca5358c39ee05970c23cbeaff61945658a38b6ac7a26a7d64612d06d9628c6d4aba69f3fe32d2a93f42411052021805c40c75f62f5; JSESSIONID=59290CD56CDDC14323EAE3E977747667; variant=v:1|lgn:0|dt:m|os:ns|cntry:US|cur:USD|jn:1|rt:o|pb:0; ln_grp=2; odds_format=AMERICAN; st=US:Florida; LANG=en; AB=variant; Device-Type=Mobile|false; JOINED=true; VISITED=true",
    }

    SPORT_ENDPOINTS = {
        "football_nfl": [
            "/football/nfl?marketFilterId=def&preMatchOnly=true&eventsLimit=5000&lang=en",
            "/football/nfl?marketFilterId=all&preMatchOnly=true&eventsLimit=5000&lang=en",
            "/football/nfl?marketFilterId=props&preMatchOnly=true&eventsLimit=5000&lang=en",
            "/football/nfl?marketFilterId=player&preMatchOnly=true&eventsLimit=5000&lang=en",
            "/football/nfl?marketFilterId=player-props&preMatchOnly=true&eventsLimit=5000&lang=en",
            "/football/nfl-preseason?marketFilterId=def&preMatchOnly=true&eventsLimit=5000&lang=en",
        ],
        "football_cfb": [
            "/football/college-football?marketFilterId=def&preMatchOnly=true&eventsLimit=5000&lang=en",
        ],
        "basketball_wnba": [
            "/basketball/wnba?marketFilterId=def&preMatchOnly=true&eventsLimit=5000&lang=en",
        ],
        "basketball_nba": [
            "/basketball/nba?marketFilterId=def&preMatchOnly=true&eventsLimit=5000&lang=en",
        ],
        "baseball_mlb": [
            "/baseball/mlb?marketFilterId=def&preMatchOnly=true&eventsLimit=5000&lang=en",
        ],
        "tennis_atp": [
            "/tennis/atp?marketFilterId=def&preMatchOnly=true&eventsLimit=50&lang=en",
        ],
        "soccer_epl": [
            "/soccer/europe/england/premier-league?marketFilterId=def&preMatchOnly=true&eventsLimit=5000&lang=en",
        ],
    }

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)

        self.sport = config.get("sport", "football_nfl")
        self.limit = config.get("limit", 5000)
        self.custom_endpoints = config.get("endpoints")
        self.client: Optional[httpx.AsyncClient] = None

        logger.info("Initialized Bovada streamer", sport=self.sport, limit=self.limit)

    async def connect(self) -> bool:
        try:
            self.client = httpx.AsyncClient(
                headers=self.DEFAULT_HEADERS,
                timeout=30.0,
                follow_redirects=True,
            )

            test_urls = self._build_urls(self.sport)
            if not test_urls:
                logger.error("Unsupported Bovada sport", sport=self.sport)
                return False

            response = await self.client.get(test_urls[0], params={"eventsLimit": 1})
            response.raise_for_status()
            response.json()

            logger.info("Connected to Bovada API", sport=self.sport)
            return True
        except Exception as exc:
            logger.error("Failed to connect to Bovada API", error=str(exc))
            if self.client:
                await self.client.aclose()
            self.client = None
            return False

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
            logger.info("Disconnected from Bovada API")
            self.client = None

    async def fetch_data(self) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("Not connected to Bovada API")

        urls = self._build_urls(self.sport)
        if not urls:
            raise RuntimeError(f"Unsupported sport: {self.sport}")

        raw_payloads: List[Any] = []

        for url in urls:
            try:
                payload = await self._fetch_url(url)
                if payload:
                    raw_payloads.append({"url": url, "payload": payload})
            except Exception as exc:
                logger.warning("Error fetching Bovada endpoint", url=url, error=str(exc))
                continue

        logger.info("Fetched Bovada payloads", sport=self.sport, count=len(raw_payloads))

        return {
            "sport": self.sport,
            "fetched_at": self._utc_now_iso(),
            "responses": raw_payloads,
        }

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "book": "bovada",
            "sport": raw_data.get("sport"),
            "raw_responses": raw_data.get("responses", []),
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
        return list(cls.SPORT_ENDPOINTS.keys())

    @classmethod
    def get_default_config(cls, sport: str) -> Dict[str, Any]:
        return {"sport": sport, "limit": 5000}

    def _build_urls(self, sport: str) -> List[str]:
        if self.custom_endpoints:
            return [f"{self.BASE_URL}{path}" for path in self.custom_endpoints]

        paths = self.SPORT_ENDPOINTS.get(sport, [])
        return [f"{self.BASE_URL}{path}" for path in paths]

    async def _fetch_url(self, url: str) -> Any:
        assert self.client is not None

        last_error: Optional[Exception] = None
        for attempt in range(3):
            try:
                response = await self.client.get(url)
                if 500 <= response.status_code < 600:
                    raise httpx.HTTPStatusError("Server error", request=response.request, response=response)

                response.raise_for_status()
                return response.json()
            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError) as exc:
                last_error = exc
                backoff = min(2 ** attempt * 0.5, 5.0)
                logger.warning(
                    "Retrying Bovada request",
                    url=url,
                    attempt=attempt + 1,
                    backoff=backoff,
                    error=str(exc),
                )
                await asyncio.sleep(backoff)

        if last_error:
            raise last_error

    @staticmethod
    def _utc_now_iso() -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()


