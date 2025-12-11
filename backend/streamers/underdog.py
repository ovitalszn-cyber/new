"""Enhanced Underdog streamer that fetches live data from multiple endpoints."""

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


class UnderdogStreamer(BaseStreamer):
    """Enhanced streamer that fetches live data from Underdog API endpoints."""

    # Sport mapping to Underdog sport IDs
    SPORT_CONFIG = {
        "americanfootball_nfl": {"sport_id": "NFL", "name": "NFL"},
        "americanfootball_ncaaf": {"sport_id": "CFB", "name": "College Football"},
        "basketball_nba": {"sport_id": "NBA", "name": "NBA"},
        "basketball_wnba": {"sport_id": "WNBA", "name": "WNBA"},
        "baseball_mlb": {"sport_id": "MLB", "name": "MLB"},
        "tennis": {"sport_id": "TENNIS", "name": "Tennis"},
        "mma": {"sport_id": "MMA", "name": "UFC/MMA"},
        "esports_counterstrike": {"sport_id": "CS", "name": "Counter-Strike 2"},
        "esports_dota2": {"sport_id": "ESPORTS", "name": "Dota 2"},
        "esports_valorant": {"sport_id": "VAL", "name": "Valorant"},
        "esports_fifa": {"sport_id": "FIFA", "name": "FIFA"},
    }

    # Default headers for Underdog API
    DEFAULT_HEADERS = {
        "client-version": "1716",
        "user-agent": "Underdog/25.37.3 (com.underdogsports.fantasy; build:1716; iOS 26.0.0) Alamofire/5.8.0",
        "client-type": "ios",
        "accept": "*/*",
        "accept-language": "en-US;q=1.0",
        "priority": "u=3, i",
        "x-datadog-origin": "rum",
    }

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        super().__init__(name, config)
        self.is_connected = False
        self.sport = config.get("sport", "football_nfl")
        self.limit = config.get("limit", 5000)
        self.include_prediction_markets = config.get("include_prediction_markets", False)
        self.product = config.get("product", "fantasy")
        self.product_experience_id = config.get("product_experience_id", "018e1234-5678-9abc-def0-123456789002")
        self.state_config_id = config.get("state_config_id", "8176bf5b-d026-4be0-b6b8-02f1f101a8c6")
        
        # Authentication headers with valid tokens from curl files
        self.auth_headers = {
            "authorization": config.get("authorization", "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNnRTM4R1FUTW1lcVA5djFYVllEUCJ9.eyJ1ZF9lbWFpbCI6ImFpdm9udGF5Y3JheHlAaWNsb3VkLmNvbSIsInVkX3VzZXJuYW1lIjoicnJzdGVlenoiLCJ1ZF9zdWIiOiJlZjZiMGIzZC03ZWQyLTQ4MjAtYjQzNC01ZTc4ZjZlMmI4MjYiLCJpc3MiOiJodHRwczovL2xvZ2luLnVuZGVyZG9nc3BvcnRzLmNvbS8iLCJzdWIiOiJhdXRoMHxlZjZiMGIzZC03ZWQyLTQ4MjAtYjQzNC01ZTc4ZjZlMmI4MjYiLCJhdWQiOlsiaHR0cHM6Ly9hcGkudW5kZXJkb2dmYW50YXN5LmNvbSIsImh0dHBzOi8vdW5kZXJkb2cudW5kZXJkb2cuYXV0aDBhcHAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTc1OTI2MTMyMSwiZXhwIjoxNzU5MjYxOTIxLCJzY29wZSI6ImVtYWlsIG9wZW5pZCBvZmZsaW5lX2FjY2VzcyIsImd0eSI6InBhc3N3b3JkIiwiYXpwIjoiemZGMldIaHdzRkhEZzJUdnV1cmYzVHVPUVhOOGk1TXgifQ.XWoR8Hguojpkp-8bKrIo4CC-sC8YLn8ZuWD8GzSHf5kKrDxe6Iv4rzS8F0LCjZFyXOQL4mn00w2Op4smt5wORgYfcBR9-3qo7h64XVjz-rEGAXAqOcFScw7uFp5wWqRtLJ-R46LZnlKgfnFbzjEJXj_nDRfqsGEZlBu8-rPWcsoMCVfj6KHVg_1UQVlDQSbuse8xRzVLCbnRts0R4Fxwb_J0RGEGTSIbEiTo4-uWJ-_n8ceJF-J0pYIN6ahtki_iU9Q_pWidp_U0uUWirRISDvLxPfhj-kydUZwfbr4Z537OY5hxjCFRrYaR8tWoRzn3rNOlvyx8xwA0xPEHUruEGg"),
            "ud-user-id": config.get("ud_user_id", "ef6b0b3d-7ed2-4820-b434-5e78f6e2b826"),
            "client-device-id": config.get("client_device_id", "F7D1B021-271B-4E9C-AF15-B3FB5D302F86"),
        }
        
        self.client: Optional[httpx.AsyncClient] = None

    async def connect(self) -> bool:
        try:
            self.client = httpx.AsyncClient(timeout=30.0)
            self.is_connected = True
            logger.info("Connected to Underdog API", sport=self.sport)
            return True
        except Exception as exc:
            logger.error("Failed to connect to Underdog API", error=str(exc))
            self.is_connected = False
            return False

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
            logger.info("Disconnected from Underdog API")
            self.client = None
        self.is_connected = False

    async def fetch_data(self) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("Underdog client not connected")

        if self.sport not in self.SPORT_CONFIG:
            raise ValueError(f"Unsupported sport: {self.sport}")

        sport_config = self.SPORT_CONFIG[self.sport]
        responses = []

        # Fetch lines data (main betting lines)
        lines_data = await self._fetch_lines(sport_config)
        if lines_data:
            responses.append({
                "endpoint": "lines",
                "data": lines_data,
                "fetched_at": self._utc_now_iso()
            })

        # Fetch player grouped lines (new endpoint)
        player_grouped_lines_data = await self._fetch_player_grouped_lines(sport_config)
        if player_grouped_lines_data:
            responses.append({
                "endpoint": "player_grouped_lines",
                "data": player_grouped_lines_data,
                "fetched_at": self._utc_now_iso()
            })

        # Fetch market filters (new endpoint)
        market_filters_data = await self._fetch_market_filters(sport_config)
        if market_filters_data:
            responses.append({
                "endpoint": "market_filters",
                "data": market_filters_data,
                "fetched_at": self._utc_now_iso()
            })

        # Fetch search results (market data)
        search_data = await self._fetch_search_results(sport_config)
        if search_data:
            responses.append({
                "endpoint": "search_results",
                "data": search_data,
                "fetched_at": self._utc_now_iso()
            })

        # Fetch search suggestions (Algolia)
        suggestions_data = await self._fetch_suggestions(sport_config)
        if suggestions_data:
            responses.append({
                "endpoint": "suggestions",
                "data": suggestions_data,
                "fetched_at": self._utc_now_iso()
            })

        return {
            "book": "underdog",
            "sport": self.sport,
            "sport_name": sport_config["name"],
            "fetched_at": self._utc_now_iso(),
            "responses": responses,
        }

    async def _fetch_lines(self, sport_config: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Fetch betting lines from Underdog API."""
        url = "https://api.underdogfantasy.com/v1/lobbies/content/lines"
        params = {
            "include_live": "true",
            "product": self.product,
            "show_mass_option_markets": "false",
            "sport_id": sport_config["sport_id"],
            "state_config_id": self.state_config_id,
        }

        headers = {**self.DEFAULT_HEADERS, **self.auth_headers}

        try:
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

        except Exception as exc:
            logger.error("Failed to fetch lines", sport=self.sport, error=str(exc))
            return None

    async def _fetch_player_grouped_lines(self, sport_config: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Fetch player grouped lines from Underdog API."""
        url = "https://api.underdogfantasy.com/v1/lobbies/content/player_grouped_lines"
        params = {
            "include_live": "true",
            "product": self.product,
            "sport_id": sport_config["sport_id"],
            "state_config_id": self.state_config_id,
        }

        headers = {**self.DEFAULT_HEADERS, **self.auth_headers}

        try:
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

        except Exception as exc:
            logger.error("Failed to fetch player grouped lines", sport=self.sport, error=str(exc))
            return None

    async def _fetch_market_filters(self, sport_config: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Fetch market filters from Underdog API."""
        url = "https://api.underdogfantasy.com/v1/lobbies/content/market_filters"
        params = {
            "product": self.product,
            "sport_id": sport_config["sport_id"],
            "state_config_id": self.state_config_id,
        }

        headers = {**self.DEFAULT_HEADERS, **self.auth_headers}

        try:
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

        except Exception as exc:
            logger.error("Failed to fetch market filters", sport=self.sport, error=str(exc))
            return None

    async def _fetch_suggestions(self, sport_config: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Fetch search suggestions from Algolia API."""
        url = "https://ut0fz1ry92-dsn.algolia.net/1/indexes/*/queries"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
            "X-Algolia-Api-Key": "7588e37063ba6ef99195fb14811529fd",
            "Accept": "*/*",
            "User-Agent": "iOS (26.0); Algolia for Swift (8.21.0); InstantSearch iOS (7.26.4); ISTelemetry(H4sIAAAAAAAAE3ukLXRAlfEECDGdUGW7oMpwQ5XhkTbnAVVWJLYgmM0IZotA2ADv8z3tOQAAAA==); Algolia insights for iOS (8.21.0)",
            "X-Algolia-Application-Id": "UT0FZ1RY92",
            "Accept-Language": "en-US,en;q=0.9",
        }

        data = {
            "requests": [{
                "indexName": "SearchSuggestions",
                "params": f'filters=(%20%22sport_id%22:%22{sport_config["sport_id"]}%22%20)%20AND%20(%20%22supported_products%22:%22fantasy%22%20)&page=0&userToken=no_user&analyticsTags=25.37.3,iOS&clickAnalytics=true'
            }],
            "strategy": "none"
        }

        try:
            response = await self.client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()

        except Exception as exc:
            logger.error("Failed to fetch suggestions", sport=self.sport, error=str(exc))
            return None

    async def _fetch_search_results(self, sport_config: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Fetch search results from Underdog API."""
        url = "https://api.underdogfantasy.com/v3/pickem_search/search_results"
        params = {
            "include_prediction_markets": self.include_prediction_markets,
            "product": self.product,
            "product_experience_id": self.product_experience_id,
            "sport_id": sport_config["sport_id"],
            "state_config_id": self.state_config_id,
        }

        headers = {**self.DEFAULT_HEADERS, **self.auth_headers}

        try:
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract appearance IDs for over/under lines
            appearance_ids = []
            if "over_under_lines" in data:
                for line in data["over_under_lines"]:
                    if "over_under" in line and "appearance_stat" in line["over_under"]:
                        appearance_stat = line["over_under"]["appearance_stat"]
                        if isinstance(appearance_stat, dict) and "appearance_id" in appearance_stat:
                            appearance_id = appearance_stat["appearance_id"]
                            if appearance_id and appearance_id not in appearance_ids:
                                appearance_ids.append(str(appearance_id))
            
            data["appearance_ids"] = appearance_ids[:10]  # Limit to first 10 for over/under lines
            return data

        except Exception as exc:
            logger.error("Failed to fetch search results", sport=self.sport, error=str(exc))
            return None

    async def _fetch_over_under_lines(self, appearance_ids: List[str]) -> Optional[Dict[str, Any]]:
        """Fetch over/under lines for specific appearance IDs."""
        if not appearance_ids:
            return None

        # Ensure all appearance IDs are strings
        appearance_ids = [str(aid) for aid in appearance_ids if aid]

        url = "https://api.underdogfantasy.com/v1/over_under_lines"
        params = {
            "appearance_ids": ",".join(appearance_ids),
            "product": self.product,
            "product_experience_id": self.product_experience_id,
            "state_config_id": self.state_config_id,
        }

        headers = {**self.DEFAULT_HEADERS, **self.auth_headers}

        try:
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

        except Exception as exc:
            logger.error("Failed to fetch over/under lines", error=str(exc))
            return None

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw Underdog data into standardized format."""
        processed_responses = []
        
        for response in raw_data.get("responses", []):
            endpoint = response.get("endpoint")
            data = response.get("data", {})
            
            if endpoint == "lines":
                processed = self._process_lines(data)
            elif endpoint == "search_results":
                processed = self._process_search_results(data)
            elif endpoint == "suggestions":
                processed = self._process_suggestions(data)
            else:
                processed = data
            
            processed_responses.append({
                "endpoint": endpoint,
                "data": processed,
                "fetched_at": response.get("fetched_at")
            })

        return {
            "book": "underdog",
            "sport": raw_data.get("sport"),
            "sport_name": raw_data.get("sport_name"),
            "fetched_at": raw_data.get("fetched_at"),
            "responses": processed_responses,
            "metadata": {
                "response_count": len(processed_responses),
                "has_odds": True,
                "has_multipliers": True,
                "market_types": ["over_under", "player_props"],
                "book_type": "dfs",
            },
        }

    def _process_lines(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process lines data."""
        processed = {
            "lines": data.get("lines", []),
            "lobbies": data.get("lobbies", []),
            "total_lines": len(data.get("lines", [])),
            "total_lobbies": len(data.get("lobbies", [])),
        }
        
        # Count active lines
        active_lines = [line for line in processed["lines"] if line.get("status") == "active"]
        processed["active_lines_count"] = len(active_lines)
        
        return processed

    def _process_suggestions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process suggestions data."""
        processed = {
            "results": data.get("results", []),
            "total_suggestions": 0,
        }
        
        if processed["results"]:
            processed["total_suggestions"] = len(processed["results"][0].get("hits", []))
        
        return processed

    def _process_search_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process search results data."""
        processed = {
            "over_under_lines": data.get("over_under_lines", []),
            "players": data.get("players", []),
            "solo_games": data.get("solo_games", []),
            "trending_players": data.get("trending_players", []),
            "appearance_ids": data.get("appearance_ids", []),
        }
        
        # Count active lines
        active_lines = [line for line in processed["over_under_lines"] if line.get("status") == "active"]
        processed["active_lines_count"] = len(active_lines)
        processed["total_lines_count"] = len(processed["over_under_lines"])
        
        return processed

    def _process_over_under_lines(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process over/under lines data."""
        return data

    @classmethod
    def get_supported_sports(cls) -> List[str]:
        """Get list of supported sports."""
        return list(cls.SPORT_CONFIG.keys())

    @classmethod
    def get_default_config(cls, sport: str) -> Dict[str, Any]:
        """Get default configuration for a sport."""
        if sport not in cls.SPORT_CONFIG:
            raise ValueError(f"Unsupported sport: {sport}")
        
        return {
            "sport": sport,
            "limit": 5000,
            "include_prediction_markets": False,
            "product": "fantasy",
            "product_experience_id": "018e1234-5678-9abc-def0-123456789002",
            "state_config_id": "8176bf5b-d026-4be0-b6b8-02f1f101a8c6",
        }

    @staticmethod
    def _utc_now_iso() -> str:
        """Get current UTC time as ISO string."""
        return datetime.now(timezone.utc).isoformat()
