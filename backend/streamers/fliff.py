"""Fliff raw data streamer."""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import structlog

from streamers.base import BaseStreamer

logger = structlog.get_logger()


class FliffStreamer(BaseStreamer):
    """Streamer that returns raw Fliff feed JSON without normalization."""

    BASE_URL = "https://herald-2.app.getfliff.com/fc_mobile_api_public"

    SPORT_SUBFEED_MAP: Dict[str, List[int]] = {
        "wnba": [3123499, 3123209, 3123609, 3123208, 3123608, 3123308, 3123606, 3123306, 3123206, 3123202, 3123602, 3123303, 3123399, 3123203],
        "nba": [3123499, 3123209, 3123609, 3123208, 3123608, 3123308, 3123606, 3123306, 3123206, 3123202, 3123602, 3123303, 3123399, 3123203],
        "nfl": [3123499, 3123209, 3123609, 3123208, 3123608, 3123308, 3123606, 3123306, 3123206, 3123202, 3123602, 3123303, 3123399, 3123203],
        "mlb": [3123499, 3123209, 3123609, 3123208, 3123608, 3123308, 3123606, 3123306, 3123206, 3123202, 3123602, 3123303, 3123399, 3123203],
        "ncaaf": [3123499, 3123209, 3123609, 3123208, 3123608, 3123308, 3123606, 3123306, 3123206, 3123202, 3123602, 3123303, 3123399, 3123203],
        "ncaab": [3123499, 3123209, 3123609, 3123208, 3123608, 3123308, 3123606, 3123306, 3123206, 3123202, 3123602, 3123303, 3123399, 3123203],
    }

    # Sport-specific connection parameters
    SPORT_CONN_PARAMS = {
        "basketball_nba": {"conn_id": "17", "xtag": "meta_17"},
        "basketball_wnba": {"conn_id": "12", "xtag": "meta_12"},
        "americanfootball_nfl": {"conn_id": "24", "xtag": "meta_24"},
        "baseball_mlb": {"conn_id": "32", "xtag": "meta_32"},
        "football_cfb": {"conn_id": "27", "xtag": "meta_27"},
        "icehockey_nhl": {"conn_id": "29", "xtag": "meta_29"},
        "tennis": {"conn_id": "37", "xtag": "meta_37"},
        "mma": {"conn_id": "34", "xtag": "meta_34"},
    }

    DEFAULT_PARAMS = {
        "device_x_id": os.getenv("FLIFF_DEVICE_X_ID", "ios.A0C89328-2F3C-453A-8D31-551DAC179B6B"),
        "app_x_version": os.getenv("FLIFF_APP_X_VERSION", "5.8.4.258"),  # Use working version
        "app_install_token": os.getenv("FLIFF_APP_INSTALL_TOKEN", "pr9qlSazL8"),
        "auth_token": os.getenv("FLIFF_AUTH_TOKEN", "fobj__sb_user_profile__541050"),
        "conn_id": os.getenv("FLIFF_CONN_ID", "18"),  # Default fallback
        "platform": os.getenv("FLIFF_PLATFORM", "prod"),
        "usa_state_code": os.getenv("FLIFF_USA_STATE_CODE", "FL"),
        "usa_state_code_source": os.getenv(
            "FLIFF_USA_STATE_CODE_SOURCE",
            "ipOrigin=radar|regionCode=FL|meta=successGetRegionCode|geocodeOrigin=radar|regionCode=FL|meta=successGetRegionCode",
        ),
        "xtag": os.getenv("FLIFF_XTAG", "meta_18"),  # Default fallback
        "country_code": os.getenv("FLIFF_COUNTRY_CODE", "US"),
    }

    DEFAULT_HEADERS = {
        "content-type": "application/json",
        "accept": "application/json, text/plain, */*",
        "baggage": "sentry-environment=production,sentry-public_key=44cf74b044a14251a75b1194fb12c336,sentry-release=5.8.4,sentry-trace_id=496e2d98150c4ddb8d79f5036e8069ab",
        "priority": "u=3, i",
        "sentry-trace": "496e2d98150c4ddb8d79f5036e8069ab-c1d9c7fc452f40ee-0",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Fliff/1 CFNetwork/3860.100.1 Darwin/25.0.0",
        "cookie": "afUserId=8d91d74e-488c-4e20-85bc-26358ba07089-p",
    }

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)

        self.sport = config.get("sport")  # Optional sport key
        self.fetch_all = config.get("fetch_all", False)
        self.curl_files = config.get("curl_files")
        self.request_body = config.get("body")
        self.params_override = config.get("params") or {}
        self.headers_override = config.get("headers") or {}
        self.cookie = config.get("cookie") or os.getenv("FLIFF_COOKIE")

        # Use sport-specific connection parameters if available
        if self.sport and self.sport in self.SPORT_CONN_PARAMS:
            sport_params = self.SPORT_CONN_PARAMS[self.sport]
            self.params_override.update({
                "conn_id": sport_params["conn_id"],
                "xtag": sport_params["xtag"]
            })

        self.client: Optional[httpx.AsyncClient] = None

        logger.info(
            "Initialized Fliff streamer",
            sport=self.sport,
            fetch_all=self.fetch_all,
            curl_files=self.curl_files,
        )

    async def connect(self) -> bool:
        try:
            headers = {**self.DEFAULT_HEADERS, **self.headers_override}
            if self.cookie:
                headers["cookie"] = self.cookie

            self.client = httpx.AsyncClient(timeout=60.0, headers=headers)

            # Minimal connection test: issue a discovery or simple fetch
            if self.curl_files:
                await self._fetch_first_curl(self.curl_files[0])
            elif self.fetch_all:
                await self._fetch_all_markets()
            else:
                await self._fetch_default()

            logger.info("Connected to Fliff API")
            return True
        except Exception as exc:
            logger.error("Failed to connect to Fliff API", error=str(exc))
            if self.client:
                await self.client.aclose()
            self.client = None
            return False

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
            logger.info("Disconnected from Fliff API")
            self.client = None

    async def fetch_data(self) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("Not connected to Fliff API")

        # Try to use curl files if they exist (local development)
        if self.curl_files and self.curl_files[0]:
            try:
                raw = await self._fetch_from_curl_files(self.curl_files)
                fetch_type = f"curl_file_{self.sport}"
                return {
                    "sport": self.sport,
                    "fetch_type": fetch_type,
                    "params": {**self.DEFAULT_PARAMS, **self.params_override},
                    "request_body": f"curl_file_{self.sport}",
                    "raw_response": raw,
                    "fetched_at": self._utc_now_iso(),
                }
            except Exception as e:
                logger.warning(f"Failed to fetch from curl files, falling back to default: {e}")
                # Don't fall back to default if curl files fail
                return {
                    "sport": self.sport,
                    "fetch_type": "curl_file_error",
                    "params": {**self.DEFAULT_PARAMS, **self.params_override},
                    "request_body": "curl_file_error",
                    "raw_response": {
                        "error": f"Failed to fetch from curl files: {str(e)}",
                        "status": "error"
                    },
                    "fetched_at": self._utc_now_iso(),
                }

        # Fallback to default fetching method
        try:
            if self.fetch_all:
                raw = await self._fetch_all_markets()
            else:
                raw = await self._fetch_default()
            
            fetch_type = f"default_{self.sport}"
            return {
                "sport": self.sport,
                "fetch_type": fetch_type,
                "params": {**self.DEFAULT_PARAMS, **self.params_override},
                "request_body": "default_request",
                "raw_response": raw,
                "fetched_at": self._utc_now_iso(),
            }
        except Exception as e:
            logger.error(f"Failed to fetch data from Fliff API: {e}")
            # Return a mock response to prevent complete failure
            return {
                "sport": self.sport,
                "fetch_type": "error_fallback",
                "params": {**self.DEFAULT_PARAMS, **self.params_override},
                "request_body": "error_fallback",
                "raw_response": {
                    "error": f"Failed to fetch data: {str(e)}",
                    "status": "error"
                },
                "fetched_at": self._utc_now_iso(),
            }

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "book": "fliff",
            "sport": raw_data.get("sport"),
            "fetch_type": raw_data.get("fetch_type"),
            "params": raw_data.get("params"),
            "request_body": raw_data.get("request_body"),
            "raw_response": raw_data.get("raw_response"),
            "fetched_at": raw_data.get("fetched_at"),
            "metadata": {
                "has_odds": True,
                "market_types": ["dfs"],
                "book_type": "dfs",
            },
        }

    @classmethod
    def get_supported_sports(cls) -> List[str]:
        return list(cls.SPORT_SUBFEED_MAP.keys())

    @classmethod
    def get_default_config(cls, sport: Optional[str] = None) -> Dict[str, Any]:
        # Check for curl files in the data directory (relative to project root)
        data_dir = Path(__file__).parent.parent.parent / "data" / "curl_requests" / "fliff" / "requests"
        
        # Sport-specific curl file mapping
        sport_curl_map = {
            'basketball_nba': 'fliff-nba-props.curl',
            'basketball_wnba': 'fliff-wnba-props.curl',
            'football_nfl': 'fliff-nfl-player.curl',
            'americanfootball_nfl': 'fliff-nfl-props.curl',
            'baseball_mlb': 'fliff-mlb-.curl',
            'football_cfb': 'fliff-ncaaf.curl',
            'icehockey_nhl': 'fliff-nhl.curl',
            'tennis': 'fliff-ttennis.curl',
            'mma': 'fliff-ufc.curl',
        }
        
        config: Dict[str, Any] = {"sport": sport}
        
        # Try to find sport-specific curl file
        if sport and sport in sport_curl_map:
            curl_file = data_dir / sport_curl_map[sport]
            if curl_file.exists():
                config["curl_files"] = [str(curl_file)]
            else:
                # Fallback to default fetching
                config["fetch_all"] = False
        else:
            # No curl file for this sport, use default fetching
            config["fetch_all"] = False
            
        return config

    async def _submit_request(self, params: Dict[str, Any], body: Dict[str, Any]) -> Dict[str, Any]:
        assert self.client is not None
        response = await self.client.post(self.BASE_URL, params=params, json=body)
        response.raise_for_status()
        return response.json()

    async def _fetch_default(self) -> Dict[str, Any]:
        params = {**self.DEFAULT_PARAMS, **self.params_override}
        body = self.request_body or self._build_body(self.sport)
        return await self._submit_request(params, body)

    async def _fetch_all_markets(self) -> Dict[str, Any]:
        subfeeds = await self._discover_subfeeds()
        params = {**self.DEFAULT_PARAMS, **self.params_override}
        body = self._build_body_with_subfeeds(subfeeds)
        return await self._submit_request(params, body)

    async def _fetch_first_curl(self, curl_path: str) -> Dict[str, Any]:
        params, headers, body = self._parse_curl(Path(curl_path))
        if headers:
            self.client.headers.update(headers)
        return await self._submit_request(params or self.DEFAULT_PARAMS, body or self._build_body(self.sport))

    async def _fetch_from_curl_files(self, paths: List[str]) -> Dict[str, Any]:
        results = []
        for path in paths:
            if not path:
                continue
            
            # Check if file contains JSON response (starts with HTTP/2.0 or contains JSON)
            try:
                with open(path, 'r') as f:
                    first_line = f.readline().strip()
                    f.seek(0)
                    content = f.read()
                
                # If it's a JSON response file, parse it directly
                if first_line.startswith('HTTP/') or ('{' in content and 'x_slots' in content):
                    # Extract JSON from the response file
                    lines = content.split('\n')
                    json_start = False
                    json_content = []
                    
                    for line in lines:
                        if line.strip().startswith('{'):
                            json_start = True
                        if json_start:
                            json_content.append(line)
                    
                    if json_content:
                        import json
                        json_str = '\n'.join(json_content)
                        result = json.loads(json_str)
                        results.append(result)
                        continue
            except Exception as e:
                logger.warning(f"Failed to parse JSON response file {path}: {e}")
            
            # Fallback to curl parsing
            params, headers, body = self._parse_curl(Path(path))
            merged_params = {**self.DEFAULT_PARAMS, **self.params_override, **(params or {})}
            merged_headers = {**self.client.headers, **(headers or {})} if self.client else (headers or {})
            if self.client:
                self.client.headers.update(merged_headers)
            result = await self._submit_request(merged_params, body or self._build_body(self.sport))
            results.append(result)
        return self._merge_responses(results)

    async def _discover_subfeeds(self) -> List[Dict[str, Any]]:
        params = {**self.DEFAULT_PARAMS, **self.params_override}
        body = self._build_body_with_subfeeds([])
        data = await self._submit_request(params, body)

        subfeeds: List[Dict[str, Any]] = []
        x_slots = data.get("x_slots", {})
        for update_type in ["prematch_subfeeds_updates", "inplay_subfeeds_updates"]:
            for update in x_slots.get(update_type, []) or []:
                subfeed = {
                    "subfeed_code": update.get("subfeed_code"),
                    "revision_code": update.get("revision_code", "default"),
                    "revision_id": update.get("revision_id", -1),
                    "conflict_fkeys": update.get("conflict_fkeys", []),
                }
                if subfeed["subfeed_code"] and subfeed not in subfeeds:
                    subfeeds.append(subfeed)

        logger.info("Discovered %d Fliff subfeeds", len(subfeeds))
        return subfeeds

    def _build_body(self, sport: Optional[str]) -> Dict[str, Any]:
        """Build request body using the exact format from working curl."""
        # Use the exact format from the working WNBA curl file
        return {
            "header": {
                "device_x_id": self.DEFAULT_PARAMS.get("device_x_id"),
                "app_x_version": self.DEFAULT_PARAMS.get("app_x_version"),
                "app_install_token": self.DEFAULT_PARAMS.get("app_install_token"),
                "auth_token": self.DEFAULT_PARAMS.get("auth_token"),
                "conn_id": int(self.DEFAULT_PARAMS.get("conn_id") or 10),
                "platform": self.DEFAULT_PARAMS.get("platform"),
                "usa_state_code": self.DEFAULT_PARAMS.get("usa_state_code"),
                "usa_state_code_source": self.DEFAULT_PARAMS.get("usa_state_code_source"),
                "xtag": self.DEFAULT_PARAMS.get("xtag"),
                "country_code": self.DEFAULT_PARAMS.get("country_code"),
            },
            "invocation": {
                "request": {
                    "__object_class_name": "FCM__Public_Feed_Sync__Request",
                    "subfeed_meta": {
                        "packed_subfeed_revisions": [
                            {
                                "subfeed_code": 3123202,
                                "revision_code": "default",
                                "revision_id": -1,
                                "conflict_fkeys": []
                            }
                        ]
                    },
                    "focused_channel_id": 467,
                    "focused_conflict_fkey": "",
                    "focused_player_fkey": "",
                    "focused_ticket_conflict_fkeys": [],
                    "focused_ticket_proposal_fkeys": [],
                    "focused_ticket_data": []
                },
                "code": 3061
            },
            "x_sb_meta": {
                "sb_config_version": 7189,
                "sb_user_profile_version": 5726,
                "sb_user_profile_meta": {
                    "id_51202": 0,
                    "id_51203": 0,
                    "id_51204": 0,
                    "id_51207": 452506969,
                    "id_51206": 62212296,
                    "id_51221": 1639584918,
                    "id_51231": 0,
                    "id_51232": 0,
                    "id_51241": 0,
                    "id_51250": 0,
                    "id_51251": 1600501240,
                    "id_51252": 0,
                    "id_51253": 0,
                    "id_51254": 0,
                    "id_51255": 0,
                    "id_51256": 0
                }
            }
        }
    
    def _get_default_body(self) -> Dict[str, Any]:
        """Fallback to default NFL body if curl file fails."""
        return {
            "header": {
                "device_x_id": self.DEFAULT_PARAMS["device_x_id"],
                "app_x_version": self.DEFAULT_PARAMS["app_x_version"],
                "app_install_token": self.DEFAULT_PARAMS["app_install_token"],
                "auth_token": self.DEFAULT_PARAMS["auth_token"],
                "conn_id": int(self.DEFAULT_PARAMS["conn_id"]),
                "platform": self.DEFAULT_PARAMS["platform"],
                "usa_state_code": self.DEFAULT_PARAMS["usa_state_code"],
                "usa_state_code_source": self.DEFAULT_PARAMS["usa_state_code_source"],
                "xtag": self.DEFAULT_PARAMS["xtag"],
                "country_code": self.DEFAULT_PARAMS["country_code"]
            },
            "invocation": {
                "request": {
                    "__object_class_name": "FCM__Public_Feed_Sync__Request",
                    "subfeed_meta": {
                        "packed_subfeed_revisions": [
                            {"subfeed_code": 3123202, "revision_code": "default", "revision_id": -1, "conflict_fkeys": []},
                            {"subfeed_code": 3123209, "revision_code": "default", "revision_id": -1, "conflict_fkeys": []},
                            {"subfeed_code": 3123609, "revision_code": "default", "revision_id": -1, "conflict_fkeys": []},
                            {"subfeed_code": 3123208, "revision_code": "default", "revision_id": -1, "conflict_fkeys": []},
                            {"subfeed_code": 3123608, "revision_code": "default", "revision_id": -1, "conflict_fkeys": []},
                            {"subfeed_code": 3123308, "revision_code": "default", "revision_id": -1, "conflict_fkeys": []},
                            {"subfeed_code": 3123606, "revision_code": "default", "revision_id": -1, "conflict_fkeys": []},
                            {"subfeed_code": 3123306, "revision_code": "default", "revision_id": -1, "conflict_fkeys": []},
                            {"subfeed_code": 3123206, "revision_code": "default", "revision_id": -1, "conflict_fkeys": []},
                            {"subfeed_code": 3123602, "revision_code": "default", "revision_id": -1, "conflict_fkeys": []},
                            {"subfeed_code": 3123303, "revision_code": "default", "revision_id": -1, "conflict_fkeys": []},
                            {"subfeed_code": 3123399, "revision_code": "default", "revision_id": -1, "conflict_fkeys": []},
                            {"subfeed_code": 3123203, "revision_code": "default", "revision_id": -1, "conflict_fkeys": []}
                        ],
                        "focused_channel_id": 451,
                        "focused_conflict_fkey": "",
                        "focused_player_fkey": "",
                        "focused_ticket_conflict_fkeys": [],
                        "focused_ticket_proposal_fkeys": [],
                        "focused_ticket_data": []
                    },
                    "code": 3061
                }
            },
            "x_invocations": None,
            "x_sb_meta": {
                "sb_config_version": 7189,
                "sb_user_profile_version": 5726,
                "sb_user_profile_meta": {
                    "id_51202": 0,
                    "id_51203": 0,
                    "id_51204": 0,
                    "id_51207": 452506969,
                    "id_51206": 62212296,
                    "id_51221": 1639584918,
                    "id_51231": 0,
                    "id_51232": 0,
                    "id_51241": 0,
                    "id_51250": 0,
                    "id_51251": 1600501240,
                    "id_51252": 0,
                    "id_51253": 0,
                    "id_51254": 0,
                    "id_51255": 0,
                    "id_51256": 0
                }
            }
        }

    def _build_body_with_subfeeds(self, subfeeds: List[Dict[str, Any]]) -> Dict[str, Any]:
        body = self._build_body(self.sport)
        # Only override subfeeds if we have actual subfeeds to use
        if subfeeds:
            body["invocation"]["request"]["subfeed_meta"]["packed_subfeed_revisions"] = subfeeds
        return body

    def _parse_curl(self, path: Path) -> tuple[Dict[str, Any], Dict[str, str], Dict[str, Any]]:
        params: Dict[str, Any] = {}
        headers: Dict[str, str] = {}
        body: Dict[str, Any] = {}

        try:
            text = path.read_text()
        except Exception as exc:
            logger.warning("Failed to read curl file", file=str(path), error=str(exc))
            return params, headers, body

        for match in re.finditer(r"-H\s+(['\"])\s*([^:]+?):\s*([^'\"]+)\1", text):
            headers[match.group(2).strip().lower()] = match.group(3).strip()

        url_match = re.search(r"(['\"])https://herald-2\.app\.getfliff\.com/fc_mobile_api_public\?([^'\"]+)\1", text)
        if url_match:
            query = url_match.group(2)
            for part in query.split("&"):
                if "=" in part:
                    k, v = part.split("=", 1)
                    params[k] = v

        body_match = re.search(r"-d\s+(['\"])([\s\S]+?)\1", text)
        if body_match:
            try:
                body = json.loads(body_match.group(2))
            except Exception as exc:
                logger.warning("Failed to parse JSON body from curl file", file=str(path), error=str(exc))

        return params, headers, body

    def _merge_responses(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        merged: Dict[str, Any] = {"x_slots": {}}
        prematch: List[Dict[str, Any]] = []
        inplay: List[Dict[str, Any]] = []

        for response in responses:
            x_slots = response.get("x_slots") or {}
            prematch.extend(x_slots.get("prematch_subfeeds_updates", []))
            inplay.extend(x_slots.get("inplay_subfeeds_updates", []))
            for key, value in response.items():
                if key == "x_slots":
                    continue
                if value:
                    merged[key] = value

        merged["x_slots"] = {
            "prematch_subfeeds_updates": prematch,
            "inplay_subfeeds_updates": inplay,
        }
        return merged

    @staticmethod
    def _utc_now_iso() -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()


