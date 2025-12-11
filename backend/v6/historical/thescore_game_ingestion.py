#!/usr/bin/env python3
"""
TheScore Game & Box Score Ingestion

Backfills schedule + event data for major sports (NFL, NBA, MLB, NHL, WNBA)
from theScore API. Stores game metadata, scores, odds, and raw JSON for future
box-score/ player-stat parsing.
"""

import argparse
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import structlog
from sqlalchemy import text

# Ensure project root on path for DB helper
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from v6.historical.database import get_historical_db

logger = structlog.get_logger(__name__)


class TheScoreGameIngestor:
    BASE_URL = "https://api.thescore.com"
    DEFAULT_HEADERS = {
        "accept": "application/json",
        "x-country-code": "US",
        "priority": "u=3, i",
        "accept-language": "en-US;q=1",
        "x-api-version": "1.8.2",
        "cache-control": "max-age=0",
        "user-agent": "theScore/25.19.0 iOS/26.2 (iPhone; Retina, 1284x2778)",
        "x-app-version": "25.19.0",
        "x-region-code": "FL",
    }

    SUPPORTED_SPORTS = {"nfl", "nba", "mlb", "nhl", "wnba"}

    def __init__(
        self,
        sports: List[str],
        start_date: datetime,
        end_date: datetime,
        utc_offset: int = -18000,
        max_event_concurrency: int = 5,
    ):
        self.sports = [sport.lower() for sport in sports if sport.lower() in self.SUPPORTED_SPORTS]
        self.start_date = start_date
        self.end_date = end_date
        if self.start_date < self.end_date:
            raise ValueError("start_date must be >= end_date (going backwards in time)")
        self.utc_offset = utc_offset
        self.max_event_concurrency = max_event_concurrency

        self.database = None

    async def initialize_database(self) -> bool:
        self.database = await get_historical_db()
        is_sqlite = "sqlite" in self.database.database_url.lower()

        games_sql = (
            """
            CREATE TABLE IF NOT EXISTS thescore_games (
                id INTEGER PRIMARY KEY,
                sport TEXT NOT NULL,
                event_id INTEGER NOT NULL UNIQUE,
                season_guid TEXT,
                season_label TEXT,
                season_type TEXT,
                group_guid TEXT,
                group_label TEXT,
                group_start TEXT,
                group_end TEXT,
                week INTEGER,
                game_date TIMESTAMP,
                status TEXT,
                event_status TEXT,
                location TEXT,
                stadium TEXT,
                station TEXT,
                attendance TEXT,
                home_team_id INTEGER,
                home_team_name TEXT,
                away_team_id INTEGER,
                away_team_name TEXT,
                home_score INTEGER,
                away_score INTEGER,
                odds_line TEXT,
                odds_over_under TEXT,
                odds_closing TEXT,
                raw_event_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            if is_sqlite
            else """
            CREATE TABLE IF NOT EXISTS thescore_games (
                id SERIAL PRIMARY KEY,
                sport TEXT NOT NULL,
                event_id INTEGER NOT NULL UNIQUE,
                season_guid TEXT,
                season_label TEXT,
                season_type TEXT,
                group_guid TEXT,
                group_label TEXT,
                group_start TEXT,
                group_end TEXT,
                week INTEGER,
                game_date TIMESTAMPTZ,
                status TEXT,
                event_status TEXT,
                location TEXT,
                stadium TEXT,
                station TEXT,
                attendance TEXT,
                home_team_id INTEGER,
                home_team_name TEXT,
                away_team_id INTEGER,
                away_team_name TEXT,
                home_score INTEGER,
                away_score INTEGER,
                odds_line TEXT,
                odds_over_under TEXT,
                odds_closing TEXT,
                raw_event_json TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )

        progress_sql = (
            """
            CREATE TABLE IF NOT EXISTS thescore_ingestion_progress (
                id INTEGER PRIMARY KEY,
                sport TEXT NOT NULL,
                target_date TEXT NOT NULL,
                status TEXT NOT NULL,
                event_count INTEGER DEFAULT 0,
                error TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(sport, target_date)
            )
            """
            if is_sqlite
            else """
            CREATE TABLE IF NOT EXISTS thescore_ingestion_progress (
                id SERIAL PRIMARY KEY,
                sport TEXT NOT NULL,
                target_date TEXT NOT NULL,
                status TEXT NOT NULL,
                event_count INTEGER DEFAULT 0,
                error TEXT,
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(sport, target_date)
            )
            """
        )

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_thescore_games_event ON thescore_games(event_id)",
            "CREATE INDEX IF NOT EXISTS idx_thescore_games_sport_date ON thescore_games(sport, game_date)",
            "CREATE INDEX IF NOT EXISTS idx_thescore_progress_status ON thescore_ingestion_progress(status)",
        ]

        try:
            async with self.database.engine.begin() as conn:
                await conn.execute(text(games_sql))
                await conn.execute(text(progress_sql))
                for sql in indexes:
                    await conn.execute(text(sql))
            logger.info("theScore ingestion tables ready")
            return True
        except Exception as exc:
            logger.error("Failed to init DB tables", error=str(exc))
            return False

    async def ingest(self) -> Dict[str, Any]:
        if not self.sports:
            raise ValueError("No supported sports provided")

        if not await self.initialize_database():
            raise RuntimeError("Database init failed")

        timeout = aiohttp.ClientTimeout(total=60)
        conn = aiohttp.TCPConnector(limit=20, ssl=False)

        stats = {"sports": {}, "errors": []}

        async with aiohttp.ClientSession(
            timeout=timeout, connector=conn, headers=self.DEFAULT_HEADERS
        ) as session:
            for sport in self.sports:
                logger.info(
                    "Starting theScore ingestion",
                    sport=sport,
                    start_date=self.start_date.date().isoformat(),
                    end_date=self.end_date.date().isoformat(),
                )
                sport_stats = await self._ingest_sport(session, sport)
                stats["sports"][sport] = sport_stats

        return stats

    async def _ingest_sport(self, session: aiohttp.ClientSession, sport: str) -> Dict[str, Any]:
        total_events = 0
        dates_processed = 0
        date = self.start_date

        while date >= self.end_date:
            date_str = date.strftime("%Y-%m-%d")
            try:
                already_done = await self._progress_status(sport, date_str)
                if already_done:
                    date -= timedelta(days=1)
                    continue

                schedule_payload = await self._fetch_schedule(session, sport, date_str)
                if not schedule_payload:
                    await self._record_progress(sport, date_str, "skipped", 0, "no_schedule")
                    date -= timedelta(days=1)
                    continue

                event_meta = self._extract_event_metadata(schedule_payload)
                event_ids = list(event_meta.keys())

                if not event_ids:
                    await self._record_progress(sport, date_str, "skipped", 0, "no_events")
                    date -= timedelta(days=1)
                    continue

                stored = await self._fetch_and_store_events(session, sport, event_ids, event_meta)
                total_events += stored
                dates_processed += 1
                await self._record_progress(sport, date_str, "completed", stored)

                logger.info(
                    "Ingested date",
                    sport=sport,
                    date=date_str,
                    events_found=len(event_ids),
                    events_stored=stored,
                )

            except Exception as exc:
                stats_error = str(exc)
                logger.error("Failed ingesting date", sport=sport, date=date_str, error=stats_error)
                await self._record_progress(sport, date_str, "failed", 0, stats_error)

            date -= timedelta(days=1)

        return {"events_stored": total_events, "dates_processed": dates_processed}

    async def _fetch_schedule(
        self, session: aiohttp.ClientSession, sport: str, date_str: str
    ) -> Optional[Dict[str, Any]]:
        params = {"date": date_str, "utc_offset": str(self.utc_offset)}
        url = f"{self.BASE_URL}/{sport}/schedule"
        try:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    logger.warning("Schedule fetch failed", sport=sport, date=date_str, status=resp.status)
                    return None
                return await resp.json()
        except Exception as exc:
            logger.error("Schedule request error", sport=sport, date=date_str, error=str(exc))
            return None

    def _extract_event_metadata(self, payload: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
        meta: Dict[int, Dict[str, Any]] = {}

        def handle_block(block: Dict[str, Any]):
            if not isinstance(block, dict):
                return
            base_info = {
                "season_guid": block.get("guid"),
                "season_label": block.get("label"),
                "season_type": block.get("season_type"),
                "group_guid": block.get("guid"),
                "group_label": block.get("label"),
                "group_start": block.get("start_date"),
                "group_end": block.get("end_date"),
            }
            for event_id in block.get("event_ids", []):
                if event_id is None:
                    continue
                meta.setdefault(int(event_id), base_info)

        for block in payload.get("current_season", []) or []:
            handle_block(block)

        current_group = payload.get("current_group")
        if current_group:
            handle_block(current_group)

        return meta

    async def _fetch_and_store_events(
        self,
        session: aiohttp.ClientSession,
        sport: str,
        event_ids: List[int],
        event_meta: Dict[int, Dict[str, Any]],
    ) -> int:
        sem = asyncio.Semaphore(self.max_event_concurrency)
        stored_records: List[Dict[str, Any]] = []

        async def fetch_event(event_id: int):
            async with sem:
                url = f"{self.BASE_URL}/{sport}/events/{event_id}"
                try:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            logger.warning("Event fetch failed", sport=sport, event_id=event_id, status=resp.status)
                            return
                        data = await resp.json()
                        record = self._build_record(sport, event_id, data, event_meta.get(event_id, {}))
                        if record:
                            stored_records.append(record)
                except Exception as exc:
                    logger.error("Event request error", sport=sport, event_id=event_id, error=str(exc))

        await asyncio.gather(*[fetch_event(eid) for eid in event_ids])

        if not stored_records:
            return 0

        await self._bulk_store_events(stored_records)
        return len(stored_records)

    def _build_record(
        self, sport: str, event_id: int, data: Dict[str, Any], meta: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        if not isinstance(data, dict):
            return None

        def parse_dt(value: Optional[str]) -> Optional[str]:
            if not value:
                return None
            try:
                dt = datetime.strptime(value, "%a, %d %b %Y %H:%M:%S %z")
                return dt.isoformat()
            except ValueError:
                return value

        home_team = data.get("home_team") or {}
        away_team = data.get("away_team") or {}
        box_score = data.get("box_score") or {}
        score = box_score.get("score") or {}

        odds = data.get("odd") or {}
        event_status = data.get("status")

        record = {
            "sport": sport,
            "event_id": event_id,
            "season_guid": meta.get("season_guid"),
            "season_label": meta.get("season_label"),
            "season_type": meta.get("season_type"),
            "group_guid": meta.get("group_guid"),
            "group_label": meta.get("group_label"),
            "group_start": meta.get("group_start"),
            "group_end": meta.get("group_end"),
            "week": data.get("week"),
            "game_date": parse_dt(data.get("game_date")),
            "status": data.get("status"),
            "event_status": data.get("event_status"),
            "location": data.get("location"),
            "stadium": data.get("stadium"),
            "station": data.get("station"),
            "attendance": data.get("attendance"),
            "home_team_id": home_team.get("id"),
            "home_team_name": home_team.get("full_name") or home_team.get("name"),
            "away_team_id": away_team.get("id"),
            "away_team_name": away_team.get("full_name") or away_team.get("name"),
            "home_score": (score.get("home") or {}).get("score"),
            "away_score": (score.get("away") or {}).get("score"),
            "odds_line": odds.get("line"),
            "odds_over_under": odds.get("over_under"),
            "odds_closing": odds.get("closing"),
            "raw_event_json": json.dumps(data),
        }

        return record

    async def _bulk_store_events(self, records: List[Dict[str, Any]]) -> None:
        is_sqlite = "sqlite" in self.database.database_url.lower()
        if is_sqlite:
            insert_sql = """
                INSERT OR REPLACE INTO thescore_games (
                    sport, event_id, season_guid, season_label, season_type,
                    group_guid, group_label, group_start, group_end, week,
                    game_date, status, event_status, location, stadium, station,
                    attendance, home_team_id, home_team_name, away_team_id, away_team_name,
                    home_score, away_score, odds_line, odds_over_under, odds_closing,
                    raw_event_json, updated_at
                ) VALUES (
                    :sport, :event_id, :season_guid, :season_label, :season_type,
                    :group_guid, :group_label, :group_start, :group_end, :week,
                    :game_date, :status, :event_status, :location, :stadium, :station,
                    :attendance, :home_team_id, :home_team_name, :away_team_id, :away_team_name,
                    :home_score, :away_score, :odds_line, :odds_over_under, :odds_closing,
                    :raw_event_json, CURRENT_TIMESTAMP
                )
            """
        else:
            insert_sql = """
                INSERT INTO thescore_games (
                    sport, event_id, season_guid, season_label, season_type,
                    group_guid, group_label, group_start, group_end, week,
                    game_date, status, event_status, location, stadium, station,
                    attendance, home_team_id, home_team_name, away_team_id, away_team_name,
                    home_score, away_score, odds_line, odds_over_under, odds_closing,
                    raw_event_json, updated_at
                ) VALUES (
                    :sport, :event_id, :season_guid, :season_label, :season_type,
                    :group_guid, :group_label, :group_start, :group_end, :week,
                    :game_date, :status, :event_status, :location, :stadium, :station,
                    :attendance, :home_team_id, :home_team_name, :away_team_id, :away_team_name,
                    :home_score, :away_score, :odds_line, :odds_over_under, :odds_closing,
                    :raw_event_json, NOW()
                )
                ON CONFLICT (event_id) DO UPDATE SET
                    season_guid = EXCLUDED.season_guid,
                    season_label = EXCLUDED.season_label,
                    season_type = EXCLUDED.season_type,
                    group_guid = EXCLUDED.group_guid,
                    group_label = EXCLUDED.group_label,
                    group_start = EXCLUDED.group_start,
                    group_end = EXCLUDED.group_end,
                    week = EXCLUDED.week,
                    game_date = EXCLUDED.game_date,
                    status = EXCLUDED.status,
                    event_status = EXCLUDED.event_status,
                    location = EXCLUDED.location,
                    stadium = EXCLUDED.stadium,
                    station = EXCLUDED.station,
                    attendance = EXCLUDED.attendance,
                    home_team_id = EXCLUDED.home_team_id,
                    home_team_name = EXCLUDED.home_team_name,
                    away_team_id = EXCLUDED.away_team_id,
                    away_team_name = EXCLUDED.away_team_name,
                    home_score = EXCLUDED.home_score,
                    away_score = EXCLUDED.away_score,
                    odds_line = EXCLUDED.odds_line,
                    odds_over_under = EXCLUDED.odds_over_under,
                    odds_closing = EXCLUDED.odds_closing,
                    raw_event_json = EXCLUDED.raw_event_json,
                    updated_at = NOW()
            """

        async with self.database.session_maker() as session:
            await session.execute(text(insert_sql), records)
            await session.commit()

    async def _progress_status(self, sport: str, date_str: str) -> bool:
        query = text(
            "SELECT status FROM thescore_ingestion_progress WHERE sport = :sport AND target_date = :date"
        )
        async with self.database.session_maker() as session:
            result = await session.execute(query, {"sport": sport, "date": date_str})
            row = result.fetchone()
            if not row:
                return False
            return row[0] == "completed"

    async def _record_progress(
        self, sport: str, date_str: str, status: str, count: int = 0, error: Optional[str] = None
    ):
        is_sqlite = "sqlite" in self.database.database_url.lower()
        if is_sqlite:
            sql = """
                INSERT OR REPLACE INTO thescore_ingestion_progress (
                    sport, target_date, status, event_count, error, updated_at
                ) VALUES (
                    :sport, :target_date, :status, :event_count, :error, CURRENT_TIMESTAMP
                )
            """
        else:
            sql = """
                INSERT INTO thescore_ingestion_progress (
                    sport, target_date, status, event_count, error, updated_at
                ) VALUES (
                    :sport, :target_date, :status, :event_count, :error, NOW()
                )
                ON CONFLICT (sport, target_date)
                DO UPDATE SET
                    status = EXCLUDED.status,
                    event_count = EXCLUDED.event_count,
                    error = EXCLUDED.error,
                    updated_at = NOW()
            """
        params = {
            "sport": sport,
            "target_date": date_str,
            "status": status,
            "event_count": count,
            "error": error,
        }
        async with self.database.session_maker() as session:
            await session.execute(text(sql), params)
            await session.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest theScore schedules & events.")
    parser.add_argument(
        "--sports",
        type=str,
        default="nfl",
        help="Comma-separated sports list (nfl,nba,mlb,nhl,wnba).",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=datetime.utcnow().strftime("%Y-%m-%d"),
        help="Starting date (YYYY-MM-DD) inclusive (default: today).",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default="2016-01-01",
        help="End date (YYYY-MM-DD) inclusive (default: 2016-01-01).",
    )
    parser.add_argument(
        "--utc-offset",
        type=int,
        default=-18000,
        help="UTC offset in seconds (default: -18000 for ET).",
    )
    parser.add_argument(
        "--max-event-concurrency",
        type=int,
        default=5,
        help="Max concurrent event detail requests.",
    )
    return parser.parse_args()


def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


async def async_main(args: argparse.Namespace):
    sports = [s.strip() for s in args.sports.split(",") if s.strip()]
    start_date = parse_date(args.start_date)
    end_date = parse_date(args.end_date)

    ingestor = TheScoreGameIngestor(
        sports=sports,
        start_date=start_date,
        end_date=end_date,
        utc_offset=args.utc_offset,
        max_event_concurrency=args.max_event_concurrency,
    )
    results = await ingestor.ingest()

    print("\n📊 theScore Ingestion Summary")
    print("=" * 60)
    for sport, info in results["sports"].items():
        print(f"{sport.upper()}: {info['events_stored']} events stored across {info['dates_processed']} dates")
    if results["errors"]:
        print("\nErrors:")
        for err in results["errors"]:
            print(f" - {err}")


def main():
    args = parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
