"""
Player Roster Ingestion Worker

Fetches player rosters from ESPN game summaries and maintains a database
of player-team associations for enriching props from sources that don't
provide team information.
"""

import asyncio
import httpx
from typing import Dict, Any, Optional, Iterable, Set
from datetime import datetime, timedelta
import json

import structlog
from redis.asyncio import Redis

from config import get_settings
from db.player_roster_db import PlayerRosterDB
from utils.team_names import canonicalize_team

logger = structlog.get_logger(__name__)


class RosterIngestionWorker:
    """Worker that ingests player rosters from theScore API."""
    
    # theScore API endpoint - returns all games for a date range
    THESCORE_API_URL = "https://api.thescore.com/multisport/events"
    
    # theScore headers
    THESCORE_HEADERS = {
        "accept": "application/json",
        "x-country-code": "US",
        "accept-language": "en-US;q=1",
        "x-api-version": "1.8.2",
        "cache-control": "max-age=0",
        "user-agent": "theScore/25.19.0 iOS/26.2 (iPhone; Retina, 1284x2778)",
        "x-app-version": "25.19.0",
        "x-region-code": "FL",
    }

    LEAGUE_PATH_LOOKUP = {
        "basketball_nba": "nba",
        "basketball_wnba": "wnba",
        "americanfootball_nfl": "nfl",
        "americanfootball_ncaaf": "ncaaf",
        "icehockey_nhl": "nhl",
        "baseball_mlb": "mlb",
        "basketball_ncaab": "ncaab",
    }
    
    def __init__(self):
        self.settings = get_settings()
        self.db = PlayerRosterDB()
        self.redis: Optional[Redis] = None
        self.session: Optional[httpx.AsyncClient] = None
        self.is_running = False
        self._fetched_team_rosters: Set[str] = set()
        self._fetched_league_rosters: Set[str] = set()
        
    async def start(self) -> None:
        """Start the roster ingestion worker."""
        if self.is_running:
            logger.warning("Roster ingestion worker already running")
            return
        
        self.is_running = True
        
        # Connect to database
        await self.db.connect()
        
        # Connect to Redis for caching
        self.redis = Redis.from_url(
            self.settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Create HTTP session with theScore headers
        self.session = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers=self.THESCORE_HEADERS
        )
        
        logger.info("Roster ingestion worker started")
        
        # Run initial ingestion
        await self.run_ingestion_cycle()
        
    async def stop(self) -> None:
        """Stop the roster ingestion worker."""
        self.is_running = False
        
        if self.session:
            await self.session.aclose()
            self.session = None
        
        if self.redis:
            await self.redis.close()
            self.redis = None
        
        await self.db.disconnect()
        
        logger.info("Roster ingestion worker stopped")
    
    async def run_ingestion_cycle(
        self,
        start_date: Optional[datetime] = None,
        days: int = 7,
        sports: Optional[Iterable[str]] = None,
    ) -> None:
        """Run a single ingestion cycle for a range of days."""

        if start_date is None:
            start_date = datetime.now()

        if sports is None:
            # Default to all major pro + college sports we support
            sports = [
                "basketball_nba",
                "basketball_ncaab",
                "americanfootball_nfl",
                "americanfootball_ncaaf",
                "icehockey_nhl",
            ]

        total_matchups = 0

        for offset in range(days):
            day = start_date - timedelta(days=offset)
            try:
                matchups = await self._ingest_day_matchups(day, sports)
                total_matchups += matchups
                logger.info(
                    "Stored matchups for day",
                    date=day.strftime("%Y-%m-%d"),
                    matchup_count=matchups,
                )
            except Exception as exc:
                logger.error(
                    "Error ingesting matchups",
                    date=day.strftime("%Y-%m-%d"),
                    error=str(exc),
                    exc_info=True,
                )

        logger.info("Matchup ingestion complete", total_matchups=total_matchups, days=days)

    async def _fetch_event_roster(self, event: Dict[str, Any], sport: str, league_key: str) -> None:
        """Fetch and store player rosters for both teams in a theScore event."""
        if not isinstance(event, dict):
            return

        home_team = event.get("home_team") or {}
        away_team = event.get("away_team") or {}

        await asyncio.gather(
            self._fetch_team_roster(home_team, sport, league_key, event),
            self._fetch_team_roster(away_team, sport, league_key, event),
        )

    async def _fetch_league_rosters(self, sport: str, league_key: str) -> None:
        """Fetch rosters for every team in a league even if no events are scheduled."""
        league_path = self.LEAGUE_PATH_LOOKUP.get(sport) or league_key
        if not league_path:
            return

        if league_path in self._fetched_league_rosters:
            return

        if not self.session:
            return

        url = f"https://api.thescore.com/{league_path}/teams"
        params = {"rpp": "-1"}

        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            teams_payload = response.json()
        except Exception as exc:
            logger.warning(
                "Failed to fetch league teams",
                league=league_path,
                sport=sport,
                error=str(exc),
                exc_info=True,
            )
            return

        if isinstance(teams_payload, dict):
            teams = teams_payload.get("teams") or teams_payload.get("data") or []
        elif isinstance(teams_payload, list):
            teams = teams_payload
        else:
            teams = []

        if not isinstance(teams, list):
            return

        placeholder_event = {"id": None, "start_time": None, "game_date": None}

        for team in teams:
            if isinstance(team, dict):
                await self._fetch_team_roster(team, sport, league_key, placeholder_event)

        self._fetched_league_rosters.add(league_path)

    async def _fetch_team_roster(
        self, team: Dict[str, Any], sport: str, league_key: str, event: Dict[str, Any]
    ) -> None:
        """Fetch and upsert roster entries for a specific team."""
        if not isinstance(team, dict):
            return

        team_id = team.get("id")
        if team_id is None:
            return

        league_path = self.LEAGUE_PATH_LOOKUP.get(sport) or league_key
        if not league_path:
            return

        cache_key = f"roster:{league_path}:{team_id}"
        if cache_key in self._fetched_team_rosters:
            return

        if not self.session:
            return

        url = f"https://api.thescore.com/{league_path}/teams/{team_id}/players"
        params = {"sideload": "team", "rpp": "-1"}

        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            roster_payload = response.json()
        except Exception as exc:
            logger.warning(
                "Failed to fetch team roster",
                league=league_path,
                team_id=team_id,
                sport=sport,
                error=str(exc),
                exc_info=True,
            )
            return

        if isinstance(roster_payload, dict):
            players = roster_payload.get("players") or []
            team_payload = roster_payload.get("team") or team
        elif isinstance(roster_payload, list):
            players = roster_payload
            team_payload = team
        else:
            players = []
            team_payload = team

        if not isinstance(players, list):
            return

        CHUNK_SIZE = 100
        for chunk_start in range(0, len(players), CHUNK_SIZE):
            chunk = players[chunk_start : chunk_start + CHUNK_SIZE]
            await asyncio.gather(
                *[
                    self._process_roster_entry(
                        {"player": player, "team": team_payload},
                        sport,
                        event,
                    )
                    for player in chunk
                    if isinstance(player, dict)
                ]
            )

        self._fetched_team_rosters.add(cache_key)

    async def _process_roster_entry(
        self, roster_entry: Dict[str, Any], sport: str, event: Dict[str, Any]
    ) -> None:
        """Persist a single roster entry into the roster DB with retry backoff."""
        player = roster_entry.get("player") or {}
        team = roster_entry.get("team") or {}

        player_name = player.get("full_name") or player.get("display_name")
        team_name = team.get("full_name") or team.get("medium_name")

        if not player_name or not team_name:
            return

        # Some entries provide additional metadata we want to preserve for debugging/matching.
        metadata = {
            "player_id": player.get("id"),
            "team_id": team.get("id"),
            "event_id": event.get("id"),
            "event_start": event.get("start_time") or event.get("game_date"),
        }

        backoff = 0.1
        for attempt in range(3):
            try:
                await self.db.upsert_player(
                    player_name=player_name,
                    team_name=team_name,
                    sport=sport,
                    position=player.get("position"),
                    jersey_number=player.get("jersey_number"),
                    player_id=str(player.get("id")) if player.get("id") else None,
                    source="thescore",
                    metadata=metadata,
                )
                break
            except Exception as exc:
                logger.warning(
                    "Failed to upsert player to roster DB",
                    player=player_name,
                    team=team_name,
                    sport=sport,
                    attempt=attempt + 1,
                    error=str(exc),
                )
                await asyncio.sleep(backoff)
                backoff *= 2

    async def _ingest_day_matchups(self, date: datetime, sports: Iterable[str]) -> int:
        """Ingest team matchups for all requested sports on a specific day."""

        date_key = date.strftime("%Y-%m-%d")
        cache_key = f"matchup:thescore:{date_key}"

        if await self.redis.get(cache_key):
            logger.debug("Skipping day; matchup cache hit", date=date_key)
            return 0

        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date.replace(hour=23, minute=59, second=59, microsecond=0)

        date_start_str = date_start.strftime("%Y-%m-%dT%H:%M:%S-0500")
        date_end_str = date_end.strftime("%Y-%m-%dT%H:%M:%S-0500")

        params = {
            "game_date.in": f"{date_start_str},{date_end_str}",
            "betmode": "true",
        }

        response = await self.session.get(self.THESCORE_API_URL, params=params)
        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, dict):
            logger.warning("Unexpected theScore payload format", date=date_key)
            return 0

        sport_lookup = {
            "nba": "basketball_nba",
            "nfl": "americanfootball_nfl",
            "nhl": "icehockey_nhl",
            "mlb": "baseball_mlb",
            "wnba": "basketball_wnba",
            "ncaab": "basketball_ncaab",
            "ncaaf": "americanfootball_ncaaf",
        }

        target_sports = set(sports)
        stored = 0
        processed_sports: Set[str] = set()

        for league_key, league_data in payload.items():
            sport = sport_lookup.get(league_key)
            if not sport or sport not in target_sports:
                continue

            processed_sports.add(sport)

            events = league_data.get("events", []) if isinstance(league_data, dict) else []
            logger.debug(
                "Processing theScore events",
                league=league_key,
                sport=sport,
                event_count=len(events),
            )

            for event in events:
                if not isinstance(event, dict):
                    continue

                event_id = event.get("id")
                home_team = event.get("home_team", {})
                away_team = event.get("away_team", {})

                home_name = home_team.get("full_name") or home_team.get("medium_name")
                away_name = away_team.get("full_name") or away_team.get("medium_name")

                if not event_id or not home_name or not away_name:
                    continue

                home_canonical = canonicalize_team(home_name, sport) or home_name
                away_canonical = canonicalize_team(away_name, sport) or away_name

                await self.db.upsert_matchup(
                    sport=sport,
                    event_id=str(event_id),
                    home_team=home_canonical,
                    away_team=away_canonical,
                    date=date_key,
                    metadata={
                        "league": league_key,
                        "home_abbr": home_team.get("abbreviation"),
                        "away_abbr": away_team.get("abbreviation"),
                    },
                )

                # Capture rosters for this event so v5 enrichment has player-team links.
                try:
                    await self._fetch_event_roster(event, sport, league_key)
                except Exception as exc:
                    logger.warning(
                        "Failed to fetch roster for event",
                        sport=sport,
                        event_id=event_id,
                        error=str(exc),
                        exc_info=True,
                    )

                stored += 1

            # Even if no events were returned (offseason), ensure league rosters are fetched once.
            await self._fetch_league_rosters(sport, league_key)

        # Fetch rosters for sports that didn't appear in the payload (e.g., offseason leagues).
        missing_sports = target_sports - processed_sports
        for sport in missing_sports:
            league_key = next((k for k, v in sport_lookup.items() if v == sport), sport.split("_")[-1])
            await self._fetch_league_rosters(sport, league_key)

        await self.redis.setex(cache_key, 86400, "1")
        return stored
    
    async def run_continuous(self, interval_minutes: int = 30) -> None:
        """Run continuous ingestion cycles."""
        while self.is_running:
            try:
                await self.run_ingestion_cycle()
            except Exception as e:
                logger.error("Error in ingestion cycle", error=str(e), exc_info=True)
            
            # Wait before next cycle
            await asyncio.sleep(interval_minutes * 60)


# Singleton instance
_worker: Optional[RosterIngestionWorker] = None


async def get_roster_worker() -> RosterIngestionWorker:
    """Get or create the global roster ingestion worker."""
    global _worker
    if _worker is None:
        _worker = RosterIngestionWorker()
        await _worker.start()
    return _worker
