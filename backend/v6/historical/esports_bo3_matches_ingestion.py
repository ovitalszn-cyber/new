#!/usr/bin/env python3
"""Esports matches ingestion from BO3.gg into kashrock_historical.db.

This script fetches match data from BO3.gg for multiple esports titles
(LoL, CS2, Valorant, Dota2) over a date range and stores them in the
esports_matches table.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import structlog
from sqlalchemy import text

import sys

# Ensure project root on path for DB helper
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from v6.historical.database import get_historical_db, HistoricalOddsDatabase  # type: ignore

logger = structlog.get_logger(__name__)


class Bo3EsportsMatchesIngestor:
    """Ingest match data from BO3.gg into the historical DB."""

    BASE_URL = "https://api.bo3.gg/api/v1"

    DISCIPLINE_CONFIG: Dict[str, Dict[str, Any]] = {
        "lol": {
            "discipline_id": 2,
            "name": "League of Legends",
        },
        "cs2": {
            "discipline_id": 1,
            "name": "Counter-Strike 2",
        },
        "dota2": {
            "discipline_id": 3,
            "name": "Dota 2",
        },
        "val": {
            "discipline_id": 4,
            "name": "Valorant",
        },
    }

    # Headers captured from a real mobile browser session
    DEFAULT_HEADERS: Dict[str, str] = {
        "accept": "*/*",
        "origin": "https://bo3.gg",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "user-agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.2 "
            "Mobile/15E148 Safari/604.1"
        ),
        "referer": "https://bo3.gg/",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=3, i",
    }

    def __init__(self, database: HistoricalOddsDatabase) -> None:
        self.database = database

    async def ensure_table(self) -> bool:
        """Create esports_matches table and indexes if they don't exist."""
        is_sqlite = "sqlite" in self.database.database_url.lower()

        if is_sqlite:
            table_sql = """
            CREATE TABLE IF NOT EXISTS esports_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sport TEXT NOT NULL,
                discipline TEXT NOT NULL,
                match_id INTEGER NOT NULL,
                slug TEXT,
                start_date TEXT NOT NULL,
                end_date TEXT,
                team1_id INTEGER,
                team1_name TEXT,
                team2_id INTEGER,
                team2_name TEXT,
                winner_team_id INTEGER,
                loser_team_id INTEGER,
                team1_score INTEGER,
                team2_score INTEGER,
                bo_type INTEGER,
                status TEXT,
                tournament_id INTEGER,
                tier TEXT,
                raw_stats_json TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(sport, match_id)
            )
            """
        else:
            table_sql = """
            CREATE TABLE IF NOT EXISTS esports_matches (
                id BIGSERIAL PRIMARY KEY,
                sport TEXT NOT NULL,
                discipline TEXT NOT NULL,
                match_id INTEGER NOT NULL,
                slug TEXT,
                start_date TIMESTAMPTZ NOT NULL,
                end_date TIMESTAMPTZ,
                team1_id INTEGER,
                team1_name TEXT,
                team2_id INTEGER,
                team2_name TEXT,
                winner_team_id INTEGER,
                loser_team_id INTEGER,
                team1_score INTEGER,
                team2_score INTEGER,
                bo_type INTEGER,
                status TEXT,
                tournament_id INTEGER,
                tier TEXT,
                raw_stats_json JSONB NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE(sport, match_id)
            )
            """

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_esports_matches_discipline_date ON esports_matches(discipline, start_date)",
            "CREATE INDEX IF NOT EXISTS idx_esports_matches_tournament ON esports_matches(tournament_id)",
        ]

        try:
            async with self.database.engine.begin() as conn:  # type: ignore[attr-defined]
                await conn.execute(text(table_sql))
                for sql in indexes:
                    await conn.execute(text(sql))
            logger.info("Esports matches table ready")
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to create esports_matches table", error=str(exc))
            return False

        return True

    async def ingest(
        self,
        disciplines: List[str],
        start_date: str,
        end_date: str,
        page_limit: int = 50,
    ) -> Dict[str, Any]:
        """Ingest matches for all requested disciplines over the date range."""
        if not await self.ensure_table():
            raise RuntimeError("Failed to initialize esports_matches table")

        timeout = aiohttp.ClientTimeout(total=60)
        connector = aiohttp.TCPConnector(limit=20, ssl=False)

        summary: Dict[str, Any] = {"disciplines": {}, "errors": []}

        async with aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=self.DEFAULT_HEADERS,
        ) as session:
            for discipline in disciplines:
                discipline = discipline.strip().lower()
                if not discipline:
                    continue
                try:
                    stats = await self._ingest_discipline(
                        session=session,
                        discipline=discipline,
                        start_date=start_date,
                        end_date=end_date,
                        page_limit=page_limit,
                    )
                    summary["disciplines"][discipline] = stats
                except Exception as exc:  # pragma: no cover - defensive
                    logger.error(
                        "Failed to ingest BO3.gg matches",
                        discipline=discipline,
                        error=str(exc),
                    )
                    summary["errors"].append(
                        {
                            "discipline": discipline,
                            "error": str(exc),
                        }
                    )
        return summary

    async def _ingest_discipline(
        self,
        session: aiohttp.ClientSession,
        discipline: str,
        start_date: str,
        end_date: str,
        page_limit: int,
    ) -> Dict[str, Any]:
        """Ingest all pages of BO3.gg matches for a single discipline."""
        config = self.DISCIPLINE_CONFIG.get(discipline, {})
        discipline_id = config.get("discipline_id")
        if not discipline_id:
            raise ValueError(f"No discipline_id configured for {discipline}")

        url = f"{self.BASE_URL}/matches"

        params: Dict[str, Any] = {
            "page[offset]": 0,
            "page[limit]": page_limit,
            "filter[discipline_id]": discipline_id,
            "filter[start_date][gt]": start_date,
            "filter[start_date][lt]": end_date,
        }

        total_count: Optional[int] = None
        matches_stored = 0

        while True:
            logger.info(
                "Fetching BO3.gg matches page",
                discipline=discipline,
                offset=params["page[offset]"],
                limit=params["page[limit]"],
                start_date=start_date,
                end_date=end_date,
            )
            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                payload = await resp.json()

            results: List[Dict[str, Any]] = payload.get("results") or []
            if not results:
                break

            await self._store_matches_batch(
                discipline=discipline,
                results=results,
            )

            matches_stored += len(results)

            total_meta = payload.get("total") or {}
            if total_count is None:
                total_count = int(total_meta.get("count") or matches_stored)

            # Pagination
            params["page[offset]"] += page_limit
            if total_count is not None and params["page[offset]"] >= total_count:
                break

        logger.info(
            "Completed BO3.gg matches ingestion",
            discipline=discipline,
            matches_stored=matches_stored,
            total_count=total_count,
        )

        return {
            "matches_stored": matches_stored,
            "total_reported": total_count or matches_stored,
        }

    async def _store_matches_batch(
        self,
        discipline: str,
        results: List[Dict[str, Any]],
    ) -> None:
        """Store a batch of match rows into esports_matches."""
        if not results:
            return

        sport = discipline

        rows: List[Dict[str, Any]] = []
        for item in results:
            rows.append(
                {
                    "sport": sport,
                    "discipline": discipline,
                    "match_id": item.get("id"),
                    "slug": item.get("slug"),
                    "start_date": item.get("start_date"),
                    "end_date": item.get("end_date"),
                    "team1_id": item.get("team1_id"),
                    "team1_name": None,  # Would need to join team data
                    "team2_id": item.get("team2_id"),
                    "team2_name": None,  # Would need to join team data
                    "winner_team_id": item.get("winner_team_id"),
                    "loser_team_id": item.get("loser_team_id"),
                    "team1_score": item.get("team1_score"),
                    "team2_score": item.get("team2_score"),
                    "bo_type": item.get("bo_type"),
                    "status": item.get("status"),
                    "tournament_id": item.get("tournament_id"),
                    "tier": item.get("tier"),
                    "raw_stats_json": json.dumps(item),
                }
            )

        insert_sql = text(
            """
            INSERT OR IGNORE INTO esports_matches (
                sport,
                discipline,
                match_id,
                slug,
                start_date,
                end_date,
                team1_id,
                team1_name,
                team2_id,
                team2_name,
                winner_team_id,
                loser_team_id,
                team1_score,
                team2_score,
                bo_type,
                status,
                tournament_id,
                tier,
                raw_stats_json
            ) VALUES (
                :sport,
                :discipline,
                :match_id,
                :slug,
                :start_date,
                :end_date,
                :team1_id,
                :team1_name,
                :team2_id,
                :team2_name,
                :winner_team_id,
                :loser_team_id,
                :team1_score,
                :team2_score,
                :bo_type,
                :status,
                :tournament_id,
                :tier,
                :raw_stats_json
            )
            """
        )

        try:
            async with self.database.session_maker() as session:  # type: ignore[attr-defined]
                await session.execute(insert_sql, rows)
                await session.commit()
            logger.info(
                "Stored esports matches batch",
                discipline=discipline,
                count=len(rows),
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error(
                "Failed to store esports matches batch",
                discipline=discipline,
                count=len(rows),
                error=str(exc),
            )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Ingest esports matches from BO3.gg into kashrock_historical.db "
            "for a given date range."
        )
    )

    parser.add_argument(
        "--disciplines",
        type=str,
        default="lol,cs2,val,dota2",
        help=(
            "Comma-separated list of BO3 disciplines to ingest "
            "(e.g. 'lol,cs2,val,dota2')."
        ),
    )

    parser.add_argument(
        "--start-date",
        type=str,
        default="2025-01-01",
        help="Start date (YYYY-MM-DD), default: 2025-01-01",
    )

    parser.add_argument(
        "--end-date",
        type=str,
        default=date.today().isoformat(),
        help="End date (YYYY-MM-DD), default: today",
    )

    parser.add_argument(
        "--page-limit",
        type=int,
        default=50,
        help="BO3.gg page[limit] page size (default: 50)",
    )

    return parser.parse_args()


async def _async_main() -> None:
    args = _parse_args()

    disciplines = [d.strip() for d in args.disciplines.split(",") if d.strip()]

    # Basic date validation
    try:
        datetime.strptime(args.start_date, "%Y-%m-%d")
        datetime.strptime(args.end_date, "%Y-%m-%d")
    except ValueError as exc:  # pragma: no cover - defensive
        raise SystemExit(f"Invalid date format: {exc}")

    db = await get_historical_db()
    ingestor = Bo3EsportsMatchesIngestor(db)

    summary = await ingestor.ingest(
        disciplines=disciplines,
        start_date=args.start_date,
        end_date=args.end_date,
        page_limit=args.page_limit,
    )

    print(json.dumps(summary, indent=2))


def main() -> None:
    asyncio.run(_async_main())


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
