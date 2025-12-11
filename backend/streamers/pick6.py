"""DraftKings Pick6 raw data streamer."""

import json
import os
import subprocess
from typing import Any, Dict, List, Optional
import httpx
import structlog

from streamers.base import BaseStreamer

logger = structlog.get_logger()


class Pick6Streamer(BaseStreamer):
    """Streamer that fetches DraftKings Pick6 player props data."""

    BASE_URL = "https://api.draftkings.com/pick6/v1/pickgroups/{pick_group_id}/pickables"

    SPORT_CONFIG = {
        "baseball_mlb": {"pick_group_id": "134830"},
        "basketball_nba": {"pick_group_id": "134952"},
        "americanfootball_nfl": {"pick_group_id": "134575"},
        "basketball_wnba": {"pick_group_id": "134959"},
        "esports_counterstrike": {"pick_group_id": "134999"},
        "esports_lol": {"pick_group_id": "134998"},
    }

    DEFAULT_HEADERS = {
        "User-Agent": "psxios/3010001 (iOS; iPhone13,4; iOS26.0.0)",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "x-client-name": "psxios",
        "x-client-version": "3010001",
        "x-dk-device-appname": "psxios",
        "x-dk-device-version": "3010001",
        "x-dk-device-isadtrackingenabled": "false",
        "priority": "u=3",
    }

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.is_connected = False

        self.sport = config.get("sport")
        self.pick_group_id = config.get("pick_group_id")
        self.headers_override = config.get("headers") or {}
        self.curl_file = config.get("curl_file")
        self.execute_curl = bool(config.get("execute_curl", True))

        # Validate sport and get pick_group_id
        if not self.curl_file:
            if not self.sport or self.sport not in self.SPORT_CONFIG:
                raise ValueError(f"Unsupported Pick6 sport: {self.sport!r}. Use one of: {list(self.SPORT_CONFIG.keys())}")
            self.pick_group_id = self.pick_group_id or self.SPORT_CONFIG[self.sport]["pick_group_id"]

        self.client: Optional[httpx.AsyncClient] = None

        logger.info(
            "Initialized Pick6 streamer",
            sport=self.sport,
            pick_group_id=self.pick_group_id,
        )

    async def connect(self) -> bool:
        try:
            headers = {**self.DEFAULT_HEADERS, **self._auth_headers(), **self.headers_override}

            # If a local curl capture is available, use its headers
            if self.curl_file and os.path.exists(self.curl_file):
                curl_headers = self._parse_curl_headers(self.curl_file)
                headers.update(curl_headers)

            self.client = httpx.AsyncClient(timeout=30.0, headers=headers, follow_redirects=True)

            # Test connection
            url = self.BASE_URL.format(pick_group_id=self.pick_group_id)
            params = {"appname": "psxios", "version": "3010001"}
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            response.json()

            logger.info("Connected to Pick6 API", sport=self.sport, pick_group_id=self.pick_group_id)
            self.is_connected = True
            return True
        except Exception as exc:
            logger.error("Failed to connect to Pick6 API", error=str(exc))
            if self.client:
                await self.client.aclose()
            self.client = None
            self.is_connected = False
            return False

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
            logger.info("Disconnected from Pick6 API")
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
                # Force compressed and silent for consistency
                if " --compressed" not in cmd:
                    cmd += " --compressed"
                
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                stdout = proc.stdout
                if proc.returncode != 0:
                    raise RuntimeError(f"curl failed: {proc.stderr[:200]}")
                
                data = json.loads(stdout)
                pickables = data.get("pickables", [])
                
                return {
                    "sport": self.sport,
                    "fetch_type": "curl_direct",
                    "pick_group_id": self.pick_group_id,
                    "raw_response": data,
                    "pickables": pickables,
                    "fetched_at": self._utc_now_iso(),
                }
            except Exception as exc:
                logger.error("Failed executing curl capture", error=str(exc))
                # Fallback to HTTPX path below

        if not self.client:
            raise RuntimeError("Not connected to Pick6 API")

        url = self.BASE_URL.format(pick_group_id=self.pick_group_id)
        params = {"appname": "psxios", "version": "3010001"}
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        pickables = data.get("pickables", [])
        
        return {
            "sport": self.sport,
            "fetch_type": "http_client",
            "pick_group_id": self.pick_group_id,
            "raw_response": data,
            "pickables": pickables,
            "fetched_at": self._utc_now_iso(),
        }

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        # Process pickables into standardized format
        processed_pickables = []
        for pickable in raw_data.get("pickables", []):
            processed = self._process_pickable(pickable)
            if processed:
                processed_pickables.append(processed)

        return {
            "book": "draftkings_pick6",
            "sport": raw_data.get("sport"),
            "fetch_type": raw_data.get("fetch_type"),
            "pick_group_id": raw_data.get("pick_group_id"),
            "raw_response": raw_data.get("raw_response"),
            "pickables": processed_pickables,
            "fetched_at": raw_data.get("fetched_at"),
            "metadata": {
                "has_multipliers": True,
                "market_types": ["player_props"],
                "book_type": "pick6",
                "total_pickables": len(processed_pickables),
            },
        }

    def _process_pickable(self, pickable: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single pickable into standardized format."""
        try:
            pickable_id = pickable.get("pickableId")
            market_category_id = pickable.get("marketCategoryId")
            
            # Extract player information
            entities = pickable.get("pickableEntities", [])
            if not entities:
                return None
                
            entity = entities[0]  # Take first entity
            player_name = entity.get("displayName")
            player_short_name = entity.get("shortName")
            dk_id = entity.get("dkId")
            
            # Extract game information
            competitions = entity.get("pickableCompetitions", [])
            if not competitions:
                return None
                
            competition = competitions[0]
            comp_summary = competition.get("competitionSummary", {})
            
            # Extract team information
            team_info = competition.get("team", {})
            team_name = team_info.get("name")
            team_city = team_info.get("city")
            team_abbreviation = team_info.get("abbreviation")
            
            # Extract game details
            home_team = comp_summary.get("homeTeam", {})
            away_team = comp_summary.get("awayTeam", {})
            game_name = comp_summary.get("name")
            start_time = comp_summary.get("startTime")
            
            # Determine market type from market category ID
            market_type = self._get_market_type_from_category_id(market_category_id)
            
            return {
                "pickable_id": pickable_id,
                "market_category_id": market_category_id,
                "market_type": market_type,
                "player_name": player_name,
                "player_short_name": player_short_name,
                "dk_id": dk_id,
                "team_name": team_name,
                "team_city": team_city,
                "team_abbreviation": team_abbreviation,
                "game_name": game_name,
                "home_team": home_team.get("name"),
                "away_team": away_team.get("name"),
                "start_time": start_time,
                "is_unpickable": pickable.get("isUnpickable", False),
                "is_swappable": pickable.get("isSwappable", False),
                "pick_type": pickable.get("pickType"),
                "is_correlatable": pickable.get("isCorrelatable", False),
            }
        except Exception as exc:
            logger.error("Failed to process pickable", error=str(exc), pickable=pickable)
            return None

    def _get_market_type_from_category_id(self, category_id: int) -> str:
        """Map market category ID to standardized market type."""
        # Based on the curl response, these are the main category IDs for MLB
        market_mapping = {
            1: "hits",
            2: "runs", 
            3: "rbis",
            4: "strikeouts",
            5: "walks",
            6: "stolen_bases",
            7: "doubles",
            8: "triples", 
            9: "home_runs",
            10: "total_bases",
            11: "fantasy_points",
            12: "at_bats",
            13: "plate_appearances",
            14: "singles",
            15: "extra_base_hits",
            16: "earned_runs_allowed",
            17: "hits_against",
            18: "walks_allowed",
            19: "strikeouts_thrown",
            20: "outs",
            21: "innings_pitched",
            2834: "walks",  # 1+ Walks
        }
        
        return market_mapping.get(category_id, f"unknown_{category_id}")

    @classmethod
    def get_supported_sports(cls) -> List[str]:
        return list(cls.SPORT_CONFIG.keys())

    @classmethod
    def get_default_config(cls, sport: str) -> Dict[str, Any]:
        # Auto-wire local curl captures if present
        curl_map = {
            "baseball_mlb": "/Users/drax/Downloads/KashRock™️/pick6-mlb",
            "basketball_nba": "/Users/drax/Downloads/KashRock™️/pick6-nba",
            "americanfootball_nfl": "/Users/drax/Downloads/KashRock™️/pick6-nfl",
            "basketball_wnba": "/Users/drax/Downloads/KashRock™️/pick6-wnba",
            "esports_counterstrike": "/Users/drax/Downloads/KashRock™️/pick6-cs",
            "esports_lol": "/Users/drax/Downloads/KashRock™️/pick6-lol",
        }
        cfg = {"sport": sport}
        
        # Add pick_group_id from SPORT_CONFIG
        if sport in cls.SPORT_CONFIG:
            cfg["pick_group_id"] = cls.SPORT_CONFIG[sport]["pick_group_id"]
        
        if sport in curl_map and os.path.exists(curl_map[sport]):
            cfg["curl_file"] = curl_map[sport]
        return cfg

    def _auth_headers(self) -> Dict[str, str]:
        headers = {}
        mapping = {
            "cookie": "PICK6_COOKIE",
            "x-dk-device-idfa": "PICK6_X_DK_DEVICE_IDFA",
            "x-dk-device-idfv": "PICK6_X_DK_DEVICE_IDFV",
            "tracestate": "PICK6_TRACESTATE",
            "newrelic": "PICK6_NEWRELIC",
            "traceparent": "PICK6_TRACEPARENT",
            "user-agent": "PICK6_USER_AGENT",
        }
        for header, env_var in mapping.items():
            value = os.getenv(env_var)
            if value:
                headers[header] = value
        return headers

    def _parse_curl_headers(self, file_path: str) -> Dict[str, str]:
        """Parse headers from curl file."""
        try:
            text = open(file_path, "r").read()
        except Exception:
            return {}

        headers: Dict[str, str] = {}
        import re
        
        # Extract all -H headers
        for m in re.finditer(r"-H\s+'([^:]+):\s*([^']+)'", text):
            key = m.group(1).strip()
            val = m.group(2).strip()
            headers[key.lower()] = val

        return headers

    @staticmethod
    def _utc_now_iso() -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
