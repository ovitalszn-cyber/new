"""PrizePicks raw data streamer."""

import json
import os
from typing import Any, Dict, List, Optional
import subprocess
import shlex

import httpx
import structlog

from streamers.base import BaseStreamer

logger = structlog.get_logger()


class PrizePicksStreamer(BaseStreamer):
    """Streamer that fetches PrizePicks projections and returns raw JSON."""

    BASE_URL = "https://api.prizepicks.com/projections"

    SPORT_CONFIG = {
        # Traditional Sports
        "basketball_wnba": {"league_id": 3, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "basketball_nba": {"league_id": 7, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "basketball_ncaa": {"league_id": 20, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "football_nfl": {"league_id": 9, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "football_cfb": {"league_id": 15, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "baseball_mlb": {"league_id": 2, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "icehockey_nhl": {"league_id": 8, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "soccer_epl": {"league_id": 82, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "soccer_mls": {"league_id": 82, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "tennis": {"league_id": 5, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "mma": {"league_id": 12, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "mma_powerslap": {"league_id": 260, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "boxing": {"league_id": 42, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "golf_pga": {"league_id": 1, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "golf_lpga": {"league_id": 256, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "nascar": {"league_id": 4, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "f1": {"league_id": 125, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "cricket": {"league_id": 162, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "afl": {"league_id": 165, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "lacrosse": {"league_id": 230, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "handball": {"league_id": 284, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "beachvolleyball": {"league_id": 283, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "darts": {"league_id": 269, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "pwhl": {"league_id": 273, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        # Esports
        "esports_cs2": {"league_id": 265, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "esports_lol": {"league_id": 121, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "esports_valorant": {"league_id": 159, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "esports_r6": {"league_id": 274, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "esports_dota2": {"league_id": 174, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "esports_cod": {"league_id": 145, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "esports_halo": {"league_id": 267, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "esports_rocketleague": {"league_id": 161, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
        "esports_apex": {"league_id": 268, "game_mode": "prizepools", "state_code": "FL", "per_page": 250},
    }

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Origin": "https://www.prizepicks.com",
        "Referer": "https://www.prizepicks.com/",
    }

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.is_connected = False  # Track connection state

        self.sport = config.get("sport")
        self.params_override = config.get("params") or {}
        self.headers_override = config.get("headers") or {}
        self.limit = config.get("per_page")
        self.game_mode = config.get("game_mode")
        self.state_code = config.get("state_code")
        self.paged = config.get("paged", False)
        self.curl_file = config.get("curl_file")
        self.execute_curl = bool(config.get("execute_curl", True))

        # Validate sport to avoid silent fallback to unrelated leagues
        if not self.curl_file:
            if not self.sport or self.sport not in self.SPORT_CONFIG:
                raise ValueError(f"Unsupported PrizePicks sport: {self.sport!r}. Use one of: {list(self.SPORT_CONFIG.keys())}")

        self.client: Optional[httpx.AsyncClient] = None

        logger.info(
            "Initialized PrizePicks streamer",
            sport=self.sport,
            paged=self.paged,
            per_page=self.limit,
            game_mode=self.game_mode,
        )

    async def connect(self) -> bool:
        try:
            headers = {**self.DEFAULT_HEADERS, **self._auth_headers(), **self.headers_override}

            # If a local curl capture is available for this sport, use its headers
            cf = self._default_curl_for_sport(self.sport)
            if not self.curl_file and cf:
                self.curl_file = cf
            if self.curl_file and os.path.exists(self.curl_file):
                curl_headers, curl_params = self._parse_curl(self.curl_file)
                headers.update(curl_headers)
                # Use curl params to override if provided
                self.params_override.update(curl_params)

            self.client = httpx.AsyncClient(timeout=30.0, headers=headers, follow_redirects=True)

            params = self._build_params(self.sport, page=1)
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            response.json()

            logger.info("Connected to PrizePicks API", sport=self.sport)
            self.is_connected = True
            return True
        except Exception as exc:
            logger.error("Failed to connect to PrizePicks API", error=str(exc))
            if self.client:
                await self.client.aclose()
            self.client = None
            self.is_connected = False
            return False

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
            logger.info("Disconnected from PrizePicks API")
            self.client = None
        self.is_connected = False

    async def fetch_data(self) -> Dict[str, Any]:
        # If a local curl capture is available and execution is enabled, run it directly
        if self.curl_file and os.path.exists(self.curl_file) and self.execute_curl:
            try:
                cmd = open(self.curl_file, "r").read().strip()
                # Ensure curl outputs only body
                if " -i " in cmd or " --include" in cmd:
                    cmd = cmd.replace(" -i ", " ").replace(" --include", "")
                # Force compressed and silent for consistency; rely on file contents otherwise
                if " --compressed" not in cmd:
                    cmd += " --compressed"
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                stdout = proc.stdout
                if proc.returncode != 0:
                    raise RuntimeError(f"curl failed: {proc.stderr[:200]}")
                data = json.loads(stdout)
                combined = data.get("data") or []
                included = data.get("included") or []
                players_by_id = self._build_players_map(included)
                # Inject player names into combined projections
                self._inject_player_names(combined, players_by_id)
                # If curl returns no data, fall back to HTTP client path
                if combined:
                    return {
                        "sport": self.sport,
                        "fetch_type": "curl_direct",
                        "params": self.params_override or self._build_params(self.sport, page=1),
                        "raw_response": {"variants": [], "combined": combined, "meta_last": data.get("meta"), "included": included},
                        "players_by_id": players_by_id,
                        "fetched_at": self._utc_now_iso(),
                    }
            except Exception as exc:
                logger.error("Failed executing curl capture", error=str(exc))
                # Fallback to HTTPX path below

        if not self.client:
            raise RuntimeError("Not connected to PrizePicks API")

        # Try multiple parameter variants to avoid zero-results edge cases
        variants: List[Dict[str, Any]] = []
        combined_data: List[Dict[str, Any]] = []
        metas: List[Dict[str, Any]] = []
        included_accum: List[Dict[str, Any]] = []

        base = self._build_params(self.sport, page=1)
        alt_standard = {**base, "game_mode": "standard"}
        alt_no_state = {k: v for k, v in base.items() if k != "state_code"}
        alt_live = {**base, "in_game": "true"}
        tries = [base, alt_standard, alt_no_state, alt_live]

        async def fetch_once(p: Dict[str, Any]) -> Dict[str, Any]:
            r = await self.client.get(self.BASE_URL, params=p)
            r.raise_for_status()
            return r.json()

        for p in tries:
            try:
                data = await fetch_once(p)
            except Exception:
                continue
            variants.append({"params": p, "meta": data.get("meta"), "count": len(data.get("data") or [])})
            dlist = data.get("data") or []
            if dlist:
                combined_data.extend(dlist)
            if data.get("meta"):
                metas.append(data.get("meta"))
            inc = data.get("included") or []
            if inc:
                included_accum.extend(inc)

        players_by_id = self._build_players_map(included_accum)
        # Inject player names into combined projections
        self._inject_player_names(combined_data, players_by_id)

        if self.paged and not combined_data:
            paged = await self._fetch_all_pages()
            variants.append({"params": {**base, "paged": True}, "meta": paged.get("meta"), "count": len(paged.get("data") or [])})
            combined_data.extend(paged.get("data") or [])
            if paged.get("meta"):
                metas.append(paged.get("meta"))
            if paged.get("included"):
                included_accum.extend(paged.get("included") or [])
            players_by_id = self._build_players_map(included_accum)

        raw = {
            "variants": variants,
            "combined": combined_data,
            "meta_last": metas[-1] if metas else None,
            "included": included_accum,
        }
        fetch_type = "multi_variant"

        return {
            "sport": self.sport,
            "fetch_type": fetch_type,
            "params": base,
            "raw_response": raw,
            "players_by_id": players_by_id,
            "fetched_at": self._utc_now_iso(),
        }

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "book": "prizepicks",
            "sport": raw_data.get("sport"),
            "fetch_type": raw_data.get("fetch_type"),
            "params": raw_data.get("params"),
            "raw_response": raw_data.get("raw_response"),
            "players_by_id": raw_data.get("players_by_id"),
            "fetched_at": raw_data.get("fetched_at"),
            "metadata": {
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
        # Auto-wire local curl captures if present
        curl_map = {
            "basketball_wnba": "/Users/drax/Downloads/KashRock™️/prizepicks-wnba",
            "football_nfl": "/Users/drax/Downloads/KashRock™️/prizepicks-nfl",
            "basketball_nba": "/Users/drax/Downloads/KashRock™️/prizepicks-nba",
            "baseball_mlb": "/Users/drax/Downloads/KashRock™️/prizepicks-mlb",
            "esports_lol": "/Users/drax/Downloads/KashRock™️/prizepicks-lol",
            "esports_valorant": "/Users/drax/Downloads/KashRock™️/prrizepicks-val",
            "esports_r6": "/Users/drax/Downloads/KashRock™️/prizepicks-r6",
            "esports_dota2": "/Users/drax/Downloads/KashRock™️/prizepicks-dota2",
            "esports_cs2": "/Users/drax/Downloads/KashRock™️/prizepicks-cs2",
            "tennis": "/Users/drax/Downloads/KashRock™️/prizepicks-tennis",
            "mma": "/Users/drax/Downloads/KashRock™️/prizepicks-mma",
        }
        cfg = {"sport": sport, "paged": True}
        if sport in curl_map and os.path.exists(curl_map[sport]):
            cfg["curl_file"] = curl_map[sport]
        return cfg

    @classmethod
    def get_default_market_groups(cls, sport: str) -> List[str]:
        """Get default market groups for a sport. PrizePicks doesn't use market groups, so return empty list."""
        return []

    def _auth_headers(self) -> Dict[str, str]:
        headers = {}
        mapping = {
            "x-px-authorization": "PRIZEPICKS_X_PX_AUTHORIZATION",
            "x-px-device-fp": "PRIZEPICKS_X_PX_DEVICE_FP",
            "x-device-info": "PRIZEPICKS_X_DEVICE_INFO",
            "x-px-mobile-sdk-version": "PRIZEPICKS_X_PX_MOBILE_SDK_VERSION",
            "x-px-os-version": "PRIZEPICKS_X_PX_OS_VERSION",
            "x-px-os": "PRIZEPICKS_X_PX_OS",
            "x-px-hello": "PRIZEPICKS_X_PX_HELLO",
            "x-px-vid": "PRIZEPICKS_X_PX_VID",
            "x-px-uuid": "PRIZEPICKS_X_PX_UUID",
            "x-px-device-model": "PRIZEPICKS_X_PX_DEVICE_MODEL",
            "baggage": "PRIZEPICKS_BAGGAGE",
            "cookie": "PRIZEPICKS_COOKIE",
            "authorization": "PRIZEPICKS_AUTHORIZATION",
            "user-agent": "PRIZEPICKS_USER_AGENT",
            "origin": "PRIZEPICKS_ORIGIN",
            "referer": "PRIZEPICKS_REFERER",
        }
        for header, env_var in mapping.items():
            value = os.getenv(env_var)
            if value:
                headers[header] = value
        return headers

    def _build_params(self, sport: str, page: int) -> Dict[str, Any]:
        config = self.SPORT_CONFIG.get(sport, {})
        params: Dict[str, Any] = {
            "exclude_ended": "true",
            "game_mode": self.game_mode or config.get("game_mode", "prizepools"),
            "in_game": "true",
            "league_id": config.get("league_id"),
            "per_page": str(self.limit or config.get("per_page", 250)),
            "state_code": self.state_code or config.get("state_code", "FL"),
            "page": str(page),
        }
        params.update(self.params_override)
        return params

    async def _fetch_all_pages(self, max_pages: int = 20) -> Dict[str, Any]:
        assert self.client is not None
        combined: List[Dict[str, Any]] = []
        meta: Optional[Dict[str, Any]] = None
        included_accum: List[Dict[str, Any]] = []

        for page in range(1, max_pages + 1):
            params = self._build_params(self.sport, page)
            response = await self.client.get(self.BASE_URL, params=params)
            if response.status_code == 404:
                break
            response.raise_for_status()
            data = response.json()
            projections = data.get("data", [])
            if not projections:
                break
            combined.extend(projections)
            meta = data.get("meta")
            inc = data.get("included") or []
            if inc:
                included_accum.extend(inc)

        return {"data": combined, "meta": meta, "included": included_accum}

    def _default_curl_for_sport(self, sport: str) -> Optional[str]:
        paths = {
            "basketball_wnba": "/Users/drax/Downloads/KashRock™️/prizepicks-wnba",
            "football_nfl": "/Users/drax/Downloads/KashRock™️/prizepicks-nfl",
            "basketball_nba": "/Users/drax/Downloads/KashRock™️/prizepicks-nba",
            "baseball_mlb": "/Users/drax/Downloads/KashRock™️/prizepicks-mlb",
            "esports_lol": "/Users/drax/Downloads/KashRock™️/prizepicks-lol",
            "esports_valorant": "/Users/drax/Downloads/KashRock™️/prrizepicks-val",
            "esports_r6": "/Users/drax/Downloads/KashRock™️/prizepicks-r6",
            "esports_dota2": "/Users/drax/Downloads/KashRock™️/prizepicks-dota2",
            "esports_cs2": "/Users/drax/Downloads/KashRock™️/prizepicks-cs2",
            "tennis": "/Users/drax/Downloads/KashRock™️/prizepicks-tennis",
            "mma": "/Users/drax/Downloads/KashRock™️/prizepicks-mma",
        }
        p = paths.get(sport)
        return p if p and os.path.exists(p) else None

    def _parse_curl(self, file_path: str) -> tuple[Dict[str, str], Dict[str, Any]]:
        try:
            text = open(file_path, "r").read()
        except Exception:
            return {}, {}

        headers: Dict[str, str] = {}
        params: Dict[str, Any] = {}

        import re, json as _json
        for m in re.finditer(r"-H\s+'([^:]+):\s*([^']+)'", text):
            key = m.group(1).strip()
            val = m.group(2).strip()
            headers[key.lower()] = val

        urlm = re.search(r"'https://api\.prizepicks\.com/projections\?([^']+)'", text)
        if urlm:
            query = urlm.group(1)
            for part in query.split("&"):
                if "=" in part:
                    k, v = part.split("=", 1)
                    params[k] = v

        return headers, params

    @staticmethod
    def _utc_now_iso() -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _build_players_map(included: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        players: Dict[str, Dict[str, Any]] = {}
        for item in included or []:
            if not isinstance(item, dict):
                continue
            if item.get("type") != "new_player":
                continue
            pid = str(item.get("id"))
            attrs = item.get("attributes") or {}
            name = attrs.get("display_name") or attrs.get("name") or attrs.get("full_name")
            players[pid] = {
                "name": name,
                "attributes": attrs,
            }
        return players

    @staticmethod
    def _inject_player_names(
        projections: List[Dict[str, Any]], players_by_id: Dict[str, Dict[str, Any]]
    ) -> None:
        """Mutate PrizePicks projection objects to include player_id and player_name.

        Works for all sports including esports by resolving the player id from
        relationships.new_player or common attribute fields, then mapping to
        the provided players_by_id.
        """
        if not projections or not players_by_id:
            return

        def extract_player_id(proj: Dict[str, Any]) -> Optional[str]:
            rel = proj.get("relationships") or {}
            if isinstance(rel, dict):
                node = rel.get("new_player") or rel.get("player") or {}
                if isinstance(node, dict):
                    data = node.get("data") or {}
                    if isinstance(data, dict) and data.get("id"):
                        return str(data.get("id"))
            attrs = proj.get("attributes") or {}
            for key in ("new_player_id", "player_id", "athlete_id"):
                if attrs.get(key):
                    return str(attrs.get(key))
            if proj.get("new_player_id"):
                return str(proj.get("new_player_id"))
            if proj.get("player_id"):
                return str(proj.get("player_id"))
            return None

        for proj in projections:
            if not isinstance(proj, dict):
                continue
            pid = extract_player_id(proj)
            if not pid:
                continue
            pinfo = players_by_id.get(pid)
            if not pinfo:
                continue
            name = pinfo.get("name") or (pinfo.get("attributes") or {}).get("display_name")
            if not name:
                continue
            proj.setdefault("player_id", pid)
            proj.setdefault("player_name", name)
            # Also expose resolved name inside attributes for easy downstream access
            attrs = proj.get("attributes")
            if isinstance(attrs, dict) and "display_name_resolved" not in attrs:
                attrs["display_name_resolved"] = name


