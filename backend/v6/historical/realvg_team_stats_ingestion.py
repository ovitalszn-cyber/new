#!/usr/bin/env python3
"""
Real.vg Team Stat Leaders Ingestion

Pulls team stat leader boards from the Real.vg mobile API and stores them
into kashrock_historical.db for downstream modeling.

Supported sports (teamstatleaders endpoint):
    - nba, nfl, nhl, mlb, wnba

The API exposes season metadata (season numbers, season types, stat options),
plus stat leader boards for every stat category. We iterate every season and
stat option for the requested sports and persist each team/value/rank entry.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import structlog
from sqlalchemy import text

# Ensure project root is on sys.path so `v6` imports resolve when running directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from v6.historical.database import get_historical_db

logger = structlog.get_logger(__name__)


class RealVGTeamStatsIngestor:
    """Collect and store Real.vg team stat leaders."""

    BASE_URL = "https://api.real.vg/teamstatleaders"
    DEFAULT_HEADERS: Dict[str, str] = {
        # Headers observed from the user's iOS capture.
        "content-type": "application/json",
        "real-device-uuid": "51FE0A17-0A54-4556-AEAE-BE84545E21DA",
        "accept": "application/json",
        "baggage": (
            "sentry-environment=production,"
            "sentry-public_key=00e61a8109694360a8db52afe3f9a4fa,"
            "sentry-release=vg.real-10.78,"
            "sentry-trace_id=465ad49a04e642bab5ce01b1185f2332"
        ),
        "priority": "u=3, i",
        "real-device-name": "iPhone13,4",
        "real-request-token": "rQ5mLynZ1JAY6kl4",
        "real-version": "24",
        "accept-language": "en-US,en;q=0.9",
        "real-device-type": "ios",
        "sentry-trace": "465ad49a04e642bab5ce01b1185f2332-41d54507748b4214-0",
        "user-agent": "real/1 CFNetwork/3860.300.21 Darwin/25.2.0",
    }

    SUPPORTED_SPORTS = {"nba", "nfl", "nhl", "mlb", "wnba"}

    def __init__(
        self,
        sports: List[str],
        rate_limit_delay: float = 0.25,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.sports = [sport.lower() for sport in sports if sport.lower() in self.SUPPORTED_SPORTS]
        self.rate_limit_delay = rate_limit_delay
        self.headers = headers or self.DEFAULT_HEADERS
        self.database = None

    async def initialize_database(self) -> bool:
        """Create database connection and ensure tables exist."""
        self.database = await get_historical_db()
        is_sqlite = "sqlite" in self.database.database_url.lower()

        stats_table_sql = (
            """
            CREATE TABLE IF NOT EXISTS realvg_team_stat_leaders (
                id INTEGER PRIMARY KEY,
                sport TEXT NOT NULL,
                season_year INTEGER NOT NULL,
                season_label TEXT,
                season_type TEXT NOT NULL,
                stat_id INTEGER NOT NULL,
                stat_label TEXT NOT NULL,
                team_id TEXT NOT NULL,
                team_name TEXT,
                team_key TEXT,
                team_rank INTEGER,
                team_value REAL,
                team_value_raw TEXT,
                team_primary_color TEXT,
                team_avatar TEXT,
                raw_team_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(sport, season_year, season_type, stat_id, team_id)
            )
            """
            if is_sqlite
            else """
            CREATE TABLE IF NOT EXISTS realvg_team_stat_leaders (
                id SERIAL PRIMARY KEY,
                sport TEXT NOT NULL,
                season_year INTEGER NOT NULL,
                season_label TEXT,
                season_type TEXT NOT NULL,
                stat_id INTEGER NOT NULL,
                stat_label TEXT NOT NULL,
                team_id TEXT NOT NULL,
                team_name TEXT,
                team_key TEXT,
                team_rank INTEGER,
                team_value REAL,
                team_value_raw TEXT,
                team_primary_color TEXT,
                team_avatar TEXT,
                raw_team_json TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(sport, season_year, season_type, stat_id, team_id)
            )
            """
        )

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_realvg_stats_sport ON realvg_team_stat_leaders(sport)",
            "CREATE INDEX IF NOT EXISTS idx_realvg_stats_season ON realvg_team_stat_leaders(season_year)",
            (
                "CREATE INDEX IF NOT EXISTS "
                "idx_realvg_stats_season_stat ON realvg_team_stat_leaders(season_year, stat_id)"
            ),
        ]

        try:
            async with self.database.engine.begin() as conn:
                await conn.execute(text(stats_table_sql))
                for index_sql in indexes:
                    await conn.execute(text(index_sql))
            logger.info("Real.vg stats table ready")
            return True
        except Exception as exc:
            logger.error("Failed to initialize Real.vg stats table", error=str(exc))
            return False

    async def fetch_sport_metadata(
        self,
        session: aiohttp.ClientSession,
        sport: str,
    ) -> Optional[Dict[str, Any]]:
        """Fetch seasons + stat options for a sport."""
        url = f"{self.BASE_URL}/{sport}/seasons"
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.warning("Failed to fetch sport metadata", sport=sport, status=response.status)
                    return None
                data = await response.json()
                logger.debug("Fetched sport metadata", sport=sport, seasons=len(data.get("seasons", [])))
                return data
        except Exception as exc:
            logger.error("Metadata fetch error", sport=sport, error=str(exc))
            return None

    async def fetch_stat_leaders(
        self,
        session: aiohttp.ClientSession,
        sport: str,
        season_year: int,
        season_type: str,
        stat_id: int,
    ) -> List[Dict[str, Any]]:
        """Fetch leaderboard for a sport/season/stat."""
        url = (
            f"{self.BASE_URL}/{sport}/seasons/{season_year}/"
            f"seasontypes/{season_type}/stats/{stat_id}"
        )
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.warning(
                        "Failed to fetch stat leaders",
                        sport=sport,
                        season=season_year,
                        season_type=season_type,
                        stat_id=stat_id,
                        status=response.status,
                    )
                    return []
                payload = await response.json()
                teams = payload.get("teams") or []
                logger.debug(
                    "Fetched stat leaders",
                    sport=sport,
                    season=season_year,
                    season_type=season_type,
                    stat_id=stat_id,
                    team_count=len(teams),
                )
                return teams
        except Exception as exc:
            logger.error(
                "Stat fetch error",
                sport=sport,
                season=season_year,
                season_type=season_type,
                stat_id=stat_id,
                error=str(exc),
            )
            return []

    async def store_stat_leaders(self, records: List[Dict[str, Any]]) -> bool:
        """Persist leaderboard entries."""
        if not records:
            return True

        is_sqlite = "sqlite" in self.database.database_url.lower()
        if is_sqlite:
            insert_sql = """
                INSERT OR REPLACE INTO realvg_team_stat_leaders (
                    sport, season_year, season_label, season_type,
                    stat_id, stat_label, team_id, team_name, team_key,
                    team_rank, team_value, team_value_raw, team_primary_color,
                    team_avatar, raw_team_json
                ) VALUES (
                    :sport, :season_year, :season_label, :season_type,
                    :stat_id, :stat_label, :team_id, :team_name, :team_key,
                    :team_rank, :team_value, :team_value_raw, :team_primary_color,
                    :team_avatar, :raw_team_json
                )
            """
        else:
            insert_sql = """
                INSERT INTO realvg_team_stat_leaders (
                    sport, season_year, season_label, season_type,
                    stat_id, stat_label, team_id, team_name, team_key,
                    team_rank, team_value, team_value_raw, team_primary_color,
                    team_avatar, raw_team_json
                ) VALUES (
                    :sport, :season_year, :season_label, :season_type,
                    :stat_id, :stat_label, :team_id, :team_name, :team_key,
                    :team_rank, :team_value, :team_value_raw, :team_primary_color,
                    :team_avatar, :raw_team_json
                )
                ON CONFLICT (sport, season_year, season_type, stat_id, team_id)
                DO UPDATE SET
                    stat_label = EXCLUDED.stat_label,
                    team_name = EXCLUDED.team_name,
                    team_key = EXCLUDED.team_key,
                    team_rank = EXCLUDED.team_rank,
                    team_value = EXCLUDED.team_value,
                    team_value_raw = EXCLUDED.team_value_raw,
                    team_primary_color = EXCLUDED.team_primary_color,
                    team_avatar = EXCLUDED.team_avatar,
                    raw_team_json = EXCLUDED.raw_team_json
            """

        try:
            async with self.database.session_maker() as session:
                await session.execute(text(insert_sql), records)
                await session.commit()
            logger.info("Stored stat leaders", count=len(records))
            return True
        except Exception as exc:
            logger.error("Failed to store stat leaders", error=str(exc), count=len(records))
            return False

    def _parse_numeric_value(self, value: Any) -> Optional[float]:
        """Convert API value field into float if possible."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.strip().replace(",", "")
            if cleaned.endswith("%"):
                cleaned = cleaned[:-1]
            if cleaned.startswith("."):
                cleaned = f"0{cleaned}"
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    async def collect(self) -> Dict[str, Any]:
        """Run ingestion for all configured sports."""
        if not self.sports:
            raise ValueError(
                "No supported sports provided. "
                f"Supported sports: {sorted(self.SUPPORTED_SPORTS)}"
            )

        if not await self.initialize_database():
            raise RuntimeError("Database initialization failed")

        results = {
            "sports_processed": 0,
            "records_stored": 0,
            "errors": [],
            "sport_breakdown": {},
        }

        timeout = aiohttp.ClientTimeout(total=120)
        async with aiohttp.ClientSession(headers=self.headers, timeout=timeout) as session:
            for sport in self.sports:
                metadata = await self.fetch_sport_metadata(session, sport)
                if not metadata:
                    results["errors"].append(f"{sport}: metadata fetch failed")
                    continue

                seasons = metadata.get("seasons") or []
                stat_options = metadata.get("statOptions") or []
                sport_count = 0

                for season_entry in seasons:
                    season_year = season_entry.get("season")
                    season_type = season_entry.get("seasonType")
                    season_label = season_entry.get("label")

                    if not season_year or not season_type:
                        continue

                    for stat in stat_options:
                        stat_id = stat.get("id")
                        stat_label = stat.get("label", f"stat_{stat_id}")
                        if not stat_id:
                            continue

                        teams = await self.fetch_stat_leaders(
                            session, sport, season_year, season_type, stat_id
                        )

                        records = []
                        for team in teams:
                            team_id = team.get("id")
                            if team_id is None:
                                continue

                            record = {
                                "sport": sport,
                                "season_year": season_year,
                                "season_label": season_label,
                                "season_type": season_type,
                                "stat_id": stat_id,
                                "stat_label": stat_label,
                                "team_id": str(team_id),
                                "team_name": team.get("name"),
                                "team_key": team.get("key"),
                                "team_rank": team.get("rank"),
                                "team_value": self._parse_numeric_value(team.get("value")),
                                "team_value_raw": str(team.get("value")) if team.get("value") is not None else None,
                                "team_primary_color": team.get("primaryColor"),
                                "team_avatar": team.get("avatar"),
                                "raw_team_json": json.dumps(team),
                            }
                            records.append(record)

                        if records:
                            stored = await self.store_stat_leaders(records)
                            if stored:
                                count = len(records)
                                sport_count += count
                                results["records_stored"] += count

                        await asyncio.sleep(self.rate_limit_delay)

                results["sports_processed"] += 1
                results["sport_breakdown"][sport] = sport_count
                logger.info("Finished sport ingestion", sport=sport, records=sport_count)

        return results


async def _async_main(args: argparse.Namespace):
    sports = [sport.strip() for sport in args.sports.split(",") if sport.strip()]
    ingestor = RealVGTeamStatsIngestor(sports=sports)
    results = await ingestor.collect()

    print("\n📊 REAL.VG TEAM STAT INGESTION SUMMARY")
    print("=" * 60)
    print(f"Sports processed: {results['sports_processed']}")
    print(f"Total records stored: {results['records_stored']:,}")
    for sport, count in results["sport_breakdown"].items():
        print(f"  • {sport.upper()}: {count:,} records")

    if results["errors"]:
        print("\n⚠️ Errors:")
        for error in results["errors"]:
            print(f"  • {error}")
    else:
        print("\n✅ All sports ingested successfully!")


def main():
    parser = argparse.ArgumentParser(description="Ingest Real.vg team stat leaders.")
    parser.add_argument(
        "--sports",
        type=str,
        default="nba",
        help="Comma separated list of sports (nba,nfl,nhl,mlb,wnba).",
    )
    args = parser.parse_args()
    asyncio.run(_async_main(args))


if __name__ == "__main__":
    main()
