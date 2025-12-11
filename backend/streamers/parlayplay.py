"""ParlayPlay raw data streamer."""

import os
import subprocess
from typing import Any, Dict, List, Optional

import httpx
import structlog
from curl_cffi import requests

from .base import BaseStreamer

logger = structlog.get_logger()


class ParlayPlayStreamer(BaseStreamer):
    """Streamer for ParlayPlay cross-game DFS data (raw only)."""

    BASE_URL = "https://parlayplay.io/api/v1/crossgame/search"

    SPORT_CONFIG: Dict[str, Dict[str, str]] = {
        "football_cfb": {"sport": "Football", "league": "CFB"},
        "football_nfl": {"sport": "Football", "league": "NFL"},
        "basketball_wnba": {"sport": "Basketball", "league": "WNBA"},
        "basketball_nba": {"sport": "Basketball", "league": "NBA"},
        "baseball_mlb": {"sport": "Baseball", "league": "MLB"},
        "esports_cs2": {"sport": "eSports", "league": "CS2"},
        "esports_lol": {"sport": "eSports", "league": "LoL"},
        "esports_csgo": {"sport": "eSports", "league": "CSGO"},
    }

    DEFAULT_HEADERS = {
        "User-Agent": "ParlayPlay/2 CFNetwork/3860.100.1 Darwin/25.0.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "X-Parlay-Request": "1",
        "Priority": "u=3",
        "X-ParlayPlay-Native-Platform": "ios",
        "X-Radar-Device-ID": "B71BDB92-370C-4248-B551-C461872C5DEF",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYwNzM1NDkwLCJpYXQiOjE3NTk1MjU4OTAsImp0aSI6IjQwZjUxMjAyZTIxYjRjM2JiMjY2MjlhNDZmZGNkYzk5IiwidXNlcl9pZCI6Ijc4MDc0In0.iFl8S4wxLJeRFYSUV1RgcVAgT5PZ-IphVaXwnu7Fljg",
        "Cookie": "sessionid=ri2k1np6eli1ag5wnjkatvr1zml5tdws"
    }

    PERIOD_MAP = {
        "full_game": "FG",
        "first_half": "FH",
        "second_half": "SH",
        "first_quarter": "FQ",
        "second_quarter": "SQ",
        "third_quarter": "TQ",
        "fourth_quarter": "LQ",
    }

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)

        self.sport = config.get("sport", "football_nfl")
        self.period = config.get("period", "full_game")
        self.include_alt = config.get("include_alt", True)
        self.include_boost = config.get("include_boost", True)
        self.custom_params = config.get("params")
        self.curl_file = config.get("curl_file")
        self.execute_curl = bool(config.get("execute_curl", True))

        self.token = config.get("token") or os.getenv("PARLAYPLAY_BEARER")
        self.session_cookie = config.get("cookie") or os.getenv("PARLAYPLAY_SESSION")

        self.client: Optional[httpx.AsyncClient] = None
        self.cffi_session: Optional[requests.Session] = None

        logger.info(
            "Initialized ParlayPlay streamer",
            sport=self.sport,
            period=self.period,
            include_alt=self.include_alt,
            include_boost=self.include_boost,
        )

    async def connect(self) -> bool:
        try:
            # Try curl_cffi first to bypass Cloudflare
            headers = dict(self.DEFAULT_HEADERS)
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            if self.session_cookie:
                headers["Cookie"] = self.session_cookie

            self.cffi_session = requests.Session()
            self.cffi_session.headers.update(headers)

            params = self._build_params(self.sport, self.period)
            if params is None:
                logger.error("Unsupported ParlayPlay sport", sport=self.sport)
                return False

            response = self.cffi_session.get(self.BASE_URL, params=params, impersonate="safari15_5")
            response.raise_for_status()
            response.json()

            logger.info("Connected to ParlayPlay API with curl_cffi", sport=self.sport)
            return True
        except Exception as exc:
            logger.error("Failed to connect to ParlayPlay API with curl_cffi", error=str(exc))
            # Fallback to httpx
            try:
                headers = dict(self.DEFAULT_HEADERS)
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"
                if self.session_cookie:
                    headers["Cookie"] = self.session_cookie

                self.client = httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True)

                params = self._build_params(self.sport, self.period)
                if params is None:
                    logger.error("Unsupported ParlayPlay sport", sport=self.sport)
                    return False

                response = await self.client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                response.json()

                logger.info("Connected to ParlayPlay API with httpx", sport=self.sport)
                return True
            except Exception as exc2:
                logger.error("Failed to connect to ParlayPlay API with httpx", error=str(exc2))
                if self.client:
                    await self.client.aclose()
                self.client = None
                return False

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
            logger.info("Disconnected from ParlayPlay API")
            self.client = None
        if self.cffi_session:
            self.cffi_session.close()
            logger.info("Disconnected from ParlayPlay API (curl_cffi)")
            self.cffi_session = None

    async def fetch_data(self) -> Dict[str, Any]:
        if not self.client and not self.cffi_session:
            raise RuntimeError("Not connected to ParlayPlay API")

        params = self.custom_params or self._build_params(self.sport, self.period)
        if params is None:
            raise RuntimeError(f"Unsupported sport: {self.sport}")

        # Try executing local curl capture first if available
        if self.curl_file and os.path.exists(self.curl_file) and self.execute_curl:
            try:
                cmd = open(self.curl_file, "r").read().strip()
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                if proc.returncode != 0:
                    raise RuntimeError(f"curl failed: {proc.stderr[:200]}")
                raw_json = self._safe_json_load(proc.stdout)
                if raw_json.get("results"):
                    return {
                        "sport": self.sport,
                        "period": self.period,
                        "params": params,
                        "fetched_at": self._utc_now_iso(),
                        "raw_response": raw_json,
                    }
            except Exception as exc:
                logger.error("Failed executing ParlayPlay curl capture", error=str(exc))

        logger.debug("Requesting ParlayPlay data", params=params)

        # Try curl_cffi first, then fallback to httpx
        if self.cffi_session:
            try:
                response = self.cffi_session.get(self.BASE_URL, params=params, impersonate="safari15_5")
                response.raise_for_status()
                raw_json = response.json()
                
                return {
                    "sport": self.sport,
                    "period": self.period,
                    "params": params,
                    "fetched_at": self._utc_now_iso(),
                    "raw_response": raw_json,
                }
            except Exception as exc:
                logger.error("Failed to fetch ParlayPlay data with curl_cffi", error=str(exc))

        # Fallback to httpx
        if self.client:
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            raw_json = response.json()

            return {
                "sport": self.sport,
                "period": self.period,
                "params": params,
                "fetched_at": self._utc_now_iso(),
                "raw_response": raw_json,
            }
        
        raise RuntimeError("No active session available for ParlayPlay API")

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "book": "parlayplay",
            "sport": raw_data.get("sport"),
            "period": raw_data.get("period"),
            "params": raw_data.get("params"),
            "raw_response": raw_data.get("raw_response"),
            "fetched_at": raw_data.get("fetched_at"),
            "metadata": {
                "has_odds": True,
                "has_multipliers": True,
                "market_types": ["dfs"],
                "book_type": "dfs",
            },
        }

    @classmethod
    def get_supported_sports(cls) -> List[str]:
        return list(cls.SPORT_CONFIG.keys())

    @classmethod
    def get_default_config(cls, sport: str) -> Dict[str, Any]:
        return {"sport": sport, "period": "full_game"}

    def _build_params(self, sport: str, period: str) -> Optional[Dict[str, Any]]:
        mapping = self.SPORT_CONFIG.get(sport)
        if not mapping:
            return None

        period_code = self.PERIOD_MAP.get(period, self.PERIOD_MAP["full_game"])

        params: Dict[str, Any] = {
            "period": period_code,
            "includeSports": "true",
            "version": "2",
            "includeAlt": str(self.include_alt).lower(),
            "includeBoost": str(self.include_boost).lower(),
            "league": mapping["league"],
            "sport": mapping["sport"],
        }
        return params

    @staticmethod
    def _safe_json_load(data: str) -> Dict[str, Any]:
        try:
            import json

            return json.loads(data)
        except Exception:
            return {}

    @staticmethod
    def _utc_now_iso() -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()


