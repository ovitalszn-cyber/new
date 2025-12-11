"""Lunosoft streamer that collects player props from the Live Scores & Odds API."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
import structlog

from streamers.base import BaseStreamer

logger = structlog.get_logger()


class LunosoftClient:
    """Async client for the Lunosoft Live Odds service."""

    BASE_URL = "https://www.lunosoftware.com/sportsData/SportsDataService.svc"

    SPORT_MAP: Dict[str, Dict[str, Any]] = {
        "americanfootball_nfl": {"sport_id": 2, "name": "NFL"},
        "americanfootball_ncaaf": {"sport_id": 3, "name": "College Football"},
        "basketball_nba": {"sport_id": 4, "name": "NBA"},
        "basketball_ncaab": {"sport_id": 5, "name": "College Basketball"},
        "icehockey_nhl": {"sport_id": 6, "name": "NHL"},
        "baseball_mlb": {"sport_id": 1, "name": "MLB"},
        "basketball_wnba": {"sport_id": 8, "name": "WNBA"},
        "soccer_mls": {"sport_id": 14, "name": "MLS"},
    }

    DEFAULT_HEADERS = {
        "accept": "*/*",
        "user-agent": "Live Scores & Odds/204 CFNetwork/3860.300.21 Darwin/25.2.0",
        "priority": "u=3",
        "accept-language": "en-US,en;q=0.9",
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.max_concurrency = max(1, int(self.config.get("max_concurrency", 8)))
        self.session: Optional[httpx.AsyncClient] = None
        self._semaphore: Optional[asyncio.Semaphore] = None
        self.is_connected = False

    async def connect(self) -> bool:
        """Create an HTTP session for Lunosoft API calls."""
        try:
            if self.session is None:
                self.session = httpx.AsyncClient(
                    headers=self.DEFAULT_HEADERS,
                    timeout=httpx.Timeout(30.0, connect=10.0),
                    follow_redirects=True,
                )
            if self._semaphore is None:
                self._semaphore = asyncio.Semaphore(self.max_concurrency)
            self.is_connected = True
            logger.info("Connected to Lunosoft API")
            return True
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to connect to Lunosoft API", error=str(exc))
            self.is_connected = False
            return False

    async def disconnect(self) -> None:
        """Close the HTTP session."""
        if self.session:
            await self.session.aclose()
            self.session = None
        self.is_connected = False
        logger.info("Disconnected from Lunosoft API")

    async def fetch_sports(
        self, sport: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch props for the requested sport (or all supported sports)."""
        if not self.is_connected:
            await self.connect()

        if not self.is_connected or self.session is None:
            logger.error("Lunosoft client is not connected")
            return {"sports": []}

        sports_to_fetch = self._resolve_sports_to_fetch(sport)
        results: List[Dict[str, Any]] = []

        for sport_key, sport_info in sports_to_fetch:
            try:
                logger.info(
                    "Fetching Lunosoft data",
                    sport=sport_key,
                    sport_id=sport_info["sport_id"],
                )
                sport_payload = await self._fetch_sport_payload(
                    sport_key, sport_info["sport_id"], sport_info.get("name")
                )
                if sport_payload:
                    results.append(sport_payload)
            except Exception as exc:  # pragma: no cover - defensive
                logger.error(
                    "Failed to fetch Lunosoft sport payload",
                    sport=sport_key,
                    error=str(exc),
                )

        return {
            "sports": results,
            "requested_sport": sport,
            "processed_sports": [item["sport"] for item in results],
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    async def fetch_book_props(
        self, book_id: int, sport: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch props filtered to a single sportsbook."""
        raw = await self.fetch_sports(sport)
        per_sport: List[Dict[str, Any]] = []

        for sport_section in raw.get("sports", []):
            filtered = [
                prop
                for prop in sport_section.get("props", [])
                if prop.get("sportsbook_id") == book_id
            ]
            if filtered:
                new_section = dict(sport_section)
                new_section["props"] = filtered
                per_sport.append(new_section)

        return {
            "sports": per_sport,
            "requested_sport": raw.get("requested_sport"),
            "processed_sports": [item.get("sport") for item in per_sport],
            "fetched_at": raw.get("fetched_at"),
        }

    def get_supported_sports(self) -> List[str]:
        return list(self.SPORT_MAP.keys())

    def get_sport_name(self, sport: str) -> str:
        info = self.SPORT_MAP.get(sport)
        return info["name"] if info else sport

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_sports_to_fetch(
        self, sport: Optional[str]
    ) -> List[Tuple[str, Dict[str, Any]]]:
        if sport:
            if sport in self.SPORT_MAP:
                return [(sport, self.SPORT_MAP[sport])]
            logger.warning("Unsupported Lunosoft sport requested", sport=sport)
            return []
        configured_sport = self.config.get("sport")
        if configured_sport:
            if isinstance(configured_sport, str):
                if configured_sport == "all":
                    return list(self.SPORT_MAP.items())
                if configured_sport in self.SPORT_MAP:
                    return [(configured_sport, self.SPORT_MAP[configured_sport])]
                logger.warning(
                    "Configured Lunosoft sport is unsupported",
                    sport=configured_sport,
                )
                return []
            if isinstance(configured_sport, list):
                return [
                    (item, self.SPORT_MAP[item])
                    for item in configured_sport
                    if item in self.SPORT_MAP
                ]

        return list(self.SPORT_MAP.items())

    async def _fetch_sport_payload(
        self, sport_key: str, sport_id: int, sport_name: Optional[str]
    ) -> Dict[str, Any]:
        # Fetch player props
        games = await self._get_json(
            f"{self.BASE_URL}/upcomingGamesWithPlayerStatOdds/{sport_id}"
        )
        stat_types = await self._get_json(
            f"{self.BASE_URL}/playerStatOddsStatTypesForUpcomingGames/{sport_id}"
        )

        games = games or []
        stat_types = stat_types or []

        stat_type_lookup = {
            int(item["StatTypeID"]): item.get("StatTypeName", "")
            for item in stat_types
            if isinstance(item, dict) and "StatTypeID" in item
        }

        props: List[Dict[str, Any]] = []
        tasks: List[asyncio.Task] = []

        for game in games:
            for stat_type_id, stat_type_name in stat_type_lookup.items():
                tasks.append(
                    asyncio.create_task(
                        self._fetch_game_stat_props(
                            sport_key,
                            sport_id,
                            sport_name,
                            game,
                            stat_type_id,
                            stat_type_name,
                        )
                    )
                )

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):  # pragma: no cover - defensive
                    logger.error(
                        "Error fetching Lunosoft game props",
                        error=str(result),
                    )
                    continue
                if result:
                    props.extend(result)

        # Fetch traditional markets (spreads, totals, moneylines)
        traditional_markets = await self._fetch_traditional_markets(sport_id)

        return {
            "sport": sport_key,
            "sport_id": sport_id,
            "sport_name": sport_name or sport_key,
            "games": games,
            "stat_types": stat_types,
            "props": props,
            "traditional_markets": traditional_markets,
        }

    async def _fetch_game_stat_props(
        self,
        sport_key: str,
        sport_id: int,
        sport_name: Optional[str],
        game: Dict[str, Any],
        stat_type_id: int,
        stat_type_name: str,
    ) -> List[Dict[str, Any]]:
        if not self.session:
            return []

        url = (
            f"{self.BASE_URL}/playerStatOddsForGame/{game.get('GameID')}"
            f"?statTypeID={stat_type_id}"
        )

        async with (self._semaphore or asyncio.Semaphore(self.max_concurrency)):
            payload = await self._get_json(url)

        if not payload:
            return []

        game_start_str = game.get("StartTimeStr")
        game_start_iso = self._parse_start_time(game_start_str)

        props: List[Dict[str, Any]] = []
        for player_prop in payload:
            if not isinstance(player_prop, dict):
                continue

            player_section = player_prop.get("Player", {})
            first_name = player_section.get("FirstName", "")
            last_name = player_section.get("LastName", "")
            player_name = " ".join(part for part in [first_name, last_name] if part).strip()
            if not player_name:
                continue

            player_team = (
                player_section.get("Team", {}) or {}
            ).get("TeamID")

            odds_list = player_prop.get("OddsList", [])
            if not isinstance(odds_list, list):
                continue

            for odds_entry in odds_list:
                if not isinstance(odds_entry, dict):
                    continue

                stat_value = odds_entry.get("StatValue")
                sportsbook_id = odds_entry.get("SportsbookID")
                sportsbook_name = odds_entry.get("SportsbookName")

                if stat_value is None or sportsbook_name is None:
                    continue

                over_line = odds_entry.get("OverLine")
                under_line = odds_entry.get("UnderLine")

                base_payload = {
                    "sport": sport_key,
                    "sport_id": sport_id,
                    "sport_name": sport_name or sport_key,
                    "stat_type_id": stat_type_id,
                    "stat_type_name": stat_type_name,
                    "game_id": game.get("GameID"),
                    "game_start": game_start_iso,
                    "game_start_raw": game_start_str,
                    "home_team_abbrev": game.get("HomeTeamAbbrev"),
                    "away_team_abbrev": game.get("AwayTeamAbbrev"),
                    "player_id": player_section.get("PlayerID"),
                    "player_team_id": player_team,
                    "player_first_name": first_name,
                    "player_last_name": last_name,
                    "player_name": player_name,
                    "books_entry": odds_entry,
                    "stat_value": stat_value,
                    "sportsbook_id": sportsbook_id,
                    "sportsbook_name": sportsbook_name,
                }

                if over_line is not None:
                    props.append(
                        {
                            **base_payload,
                            "direction": "over",
                            "odds": over_line,
                        }
                    )

                if under_line is not None:
                    props.append(
                        {
                            **base_payload,
                            "direction": "under",
                            "odds": under_line,
                        }
                    )

        return props

    async def _get_json(self, url: str) -> Any:
        if not self.session:
            return None

        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                logger.debug("Lunosoft endpoint returned 404", url=url)
            else:
                logger.error(
                    "HTTP error fetching Lunosoft data",
                    url=url,
                    status=exc.response.status_code,
                    body=exc.response.text[:200],
                )
            return None
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Unexpected error fetching Lunosoft data", url=url, error=str(exc))
            return None

    async def _fetch_traditional_markets(self, sport_id: int) -> List[Dict[str, Any]]:
        """Fetch traditional betting markets (spreads, totals, moneylines) for a sport."""
        if not self.session:
            return []

        # Get current date for the API
        from datetime import datetime as dt
        today = dt.now().strftime("%m/%d/%Y")
        
        # Build sportsbook ID list from newodds-morebooks curl
        sportsbook_ids = "1,2,5,7,8,13,21,28,83,87,89,94,90,91,92,93,98,101,99,3,103,37,145,88,141,139,135,97,22,20,132,130,86,125,147,25,122,36,119,146,118,95,17,113,100,16,110,85,109,108,107,106,6,144,105,104,102"
        
        # Build URL based on sport type
        if sport_id in [3]:  # NCAAF
            url = f"{self.BASE_URL}/gamesOddsForDateWeek/{sport_id}?conferenceID=-1&sportsbookIDList={sportsbook_ids}"
        elif sport_id in [5]:  # NCAAB
            url = f"{self.BASE_URL}/gamesOddsForDateWeek/{sport_id}?date={today}&conferenceID=-1&sportsbookIDList={sportsbook_ids}"
        elif sport_id in [2]:  # NFL
            url = f"{self.BASE_URL}/gamesOddsForDateWeek/{sport_id}?week=13&sportsbookIDList={sportsbook_ids}"
        else:  # NBA, NHL, MLB, etc.
            url = f"{self.BASE_URL}/gamesOddsForDateWeek/{sport_id}?date={today}&sportsbookIDList={sportsbook_ids}"

        payload = await self._get_json(url)
        return payload or []

    @staticmethod
    def _parse_start_time(start_time: Optional[str]) -> Optional[str]:
        if not start_time:
            return None
        try:
            dt = datetime.strptime(start_time, "%m/%d/%Y %H:%M")
            return dt.isoformat()
        except ValueError:
            return None


class LunosoftStreamer(BaseStreamer):
    """Streamer that fetches player props using the Lunosoft client."""

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        super().__init__(name, config)
        self._client = LunosoftClient(config)

    async def connect(self) -> bool:
        return await self._client.connect()

    async def disconnect(self) -> None:
        await self._client.disconnect()

    async def fetch_data(self, sport: Optional[str] = None) -> Dict[str, Any]:
        return await self._client.fetch_sports(sport)

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        player_props: List[Dict[str, Any]] = []

        if not raw_data:
            return {
                "player_props": player_props,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }

        for sport_section in raw_data.get("sports", []):
            props = sport_section.get("props", [])
            for prop in props:
                enriched = dict(prop)
                enriched["source"] = self.name
                player_props.append(enriched)

        return {
            "player_props": player_props,
            "sports": raw_data.get("processed_sports", []),
            "requested_sport": raw_data.get("requested_sport"),
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_supported_sports(self) -> List[str]:
        return self._client.get_supported_sports()

    def get_sport_name(self, sport: str) -> str:
        return self._client.get_sport_name(sport)

    async def health_check(self) -> bool:
        try:
            data = await self._client.fetch_sports("americanfootball_nfl")
            props = data.get("sports", [{}])[0].get("props", []) if data.get("sports") else []
            return len(props) > 0
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Lunosoft health check failed", error=str(exc))
            return False
