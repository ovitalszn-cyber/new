#!/usr/bin/env python3
"""Esports player stats ingestion from BO3.gg into kashrock_historical.db.

This script fetches aggregated player statistics from BO3.gg for multiple
esports titles (e.g., LoL, CS2, Valorant, R6S, Dota2) over a given date
range and stores them in a dedicated `esports_player_stats` table in the
historical database.

It mirrors the structure and style of other historical ingestion scripts
such as `thescore_game_ingestion.py`.
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


class Bo3EsportsPlayerStatsIngestor:
    """Ingest aggregated player stats from BO3.gg into the historical DB."""

    BASE_URL = "https://api.bo3.gg/api/v1"

    DEFAULT_DATE_FILTERS = {
        "gt": "filter[matches.start_date][gt]",
        "lt": "filter[matches.start_date][lt]",
    }

    DISCIPLINE_CONFIG: Dict[str, Dict[str, Any]] = {
        "lol": {
            "remote_slug": "lol",
            "sort": "-avg_kills",
            "with": "player",
            "filter_dates": True,
        },
        "dota2": {
            "remote_slug": "dota2",
            "sort": "-avg_assists",
            "with": "player",
            "filter_dates": True,
        },
        # Valorant uses a separate namespace and exposes only aggregate averages
        "val": {
            "remote_slug": "vlr",
            "sort": "-avg_combat_score",
            "with": "player,",
            "filter_dates": False,
        },
        # CS2 leverages the global players stats_list endpoint with different filters
        "cs2": {
            "endpoint": "players/stats_list",
            "sort": "-rounds_winrate",
            "with": "player,team,country",
            "filter_dates": True,
            "date_filters": {
                "gt": "filter[game_begin_at][gt]",
                "lt": "filter[game_begin_at][lt]",
            },
            "extra_params": {},
        },
        # BO3.gg currently does not expose Rainbow Six player stat leaderboards
        "r6s": {
            "supported": False,
            "reason": "BO3.gg does not publish aggregated Rainbow Six player stats",
        },
    }

    DEFAULT_CONFIG: Dict[str, Any] = {
        "remote_slug": None,
        "sort": "-avg_kills",
        "with": "player",
        "filter_dates": True,
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
        "referer": "https://bo3.gg/lol/players",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=3, i",
    }

    def __init__(self, database: HistoricalOddsDatabase) -> None:
        self.database = database

    async def ensure_table(self) -> bool:
        """Create esports_player_stats table and indexes if they don't exist."""
        is_sqlite = "sqlite" in self.database.database_url.lower()

        if is_sqlite:
            table_sql = """
            CREATE TABLE IF NOT EXISTS esports_player_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sport TEXT NOT NULL,
                discipline TEXT NOT NULL,
                player_id INTEGER NOT NULL,
                player_slug TEXT,
                nickname TEXT,
                first_name TEXT,
                last_name TEXT,
                team_id INTEGER,
                team_name TEXT,
                country_code TEXT,
                country_name TEXT,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                maps_played INTEGER,
                total_kills INTEGER,
                avg_kills REAL,
                total_deaths INTEGER,
                avg_deaths REAL,
                total_assists INTEGER,
                avg_assists REAL,
                kp REAL,
                total_damage INTEGER,
                avg_damage REAL,
                -- CS2 / advanced metrics from BO3.gg stats_list
                games_count INTEGER,
                rounds_count INTEGER,
                rounds_win INTEGER,
                rounds_winrate REAL,
                avg_player_rating_value REAL,
                avg_player_rating REAL,
                avg_death REAL,
                avg_kd_rate REAL,
                kd_diff_sum INTEGER,
                avg_first_kills REAL,
                avg_first_death REAL,
                avg_trade_kills REAL,
                avg_trade_death REAL,
                avg_shots REAL,
                avg_shots_accuracy REAL,
                avg_headshots REAL,
                avg_headshots_accuracy REAL,
                avg_headshot_kills_accuracy REAL,
                avg_hits REAL,
                avg_flash_assists REAL,
                avg_flash_hits REAL,
                avg_flash_duration REAL,
                avg_molotov_damage REAL,
                avg_he_damage REAL,
                avg_total_equipment_value REAL,
                avg_saved REAL,
                avg_spent REAL,
                avg_kill_cost REAL,
                avg_hundred_damage_cost REAL,
                avg_multikills REAL,
                multikills_vs_2 INTEGER,
                multikills_vs_3 INTEGER,
                multikills_vs_4 INTEGER,
                multikills_vs_5 INTEGER,
                clutches_vs_1 INTEGER,
                clutches_vs_2 INTEGER,
                clutches_vs_3 INTEGER,
                clutches_vs_4 INTEGER,
                clutches_vs_5 INTEGER,
                raw_stats_json TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(sport, player_id, start_date, end_date)
            )
            """
        else:
            table_sql = """
            CREATE TABLE IF NOT EXISTS esports_player_stats (
                id BIGSERIAL PRIMARY KEY,
                sport TEXT NOT NULL,
                discipline TEXT NOT NULL,
                player_id INTEGER NOT NULL,
                player_slug TEXT,
                nickname TEXT,
                first_name TEXT,
                last_name TEXT,
                team_id INTEGER,
                team_name TEXT,
                country_code TEXT,
                country_name TEXT,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                maps_played INTEGER,
                total_kills INTEGER,
                avg_kills DOUBLE PRECISION,
                total_deaths INTEGER,
                avg_deaths DOUBLE PRECISION,
                total_assists INTEGER,
                avg_assists DOUBLE PRECISION,
                kp DOUBLE PRECISION,
                total_damage BIGINT,
                avg_damage DOUBLE PRECISION,
                -- CS2 / advanced metrics from BO3.gg stats_list
                games_count INTEGER,
                rounds_count INTEGER,
                rounds_win INTEGER,
                rounds_winrate DOUBLE PRECISION,
                avg_player_rating_value DOUBLE PRECISION,
                avg_player_rating DOUBLE PRECISION,
                avg_death DOUBLE PRECISION,
                avg_kd_rate DOUBLE PRECISION,
                kd_diff_sum INTEGER,
                avg_first_kills DOUBLE PRECISION,
                avg_first_death DOUBLE PRECISION,
                avg_trade_kills DOUBLE PRECISION,
                avg_trade_death DOUBLE PRECISION,
                avg_shots DOUBLE PRECISION,
                avg_shots_accuracy DOUBLE PRECISION,
                avg_headshots DOUBLE PRECISION,
                avg_headshots_accuracy DOUBLE PRECISION,
                avg_headshot_kills_accuracy DOUBLE PRECISION,
                avg_hits DOUBLE PRECISION,
                avg_flash_assists DOUBLE PRECISION,
                avg_flash_hits DOUBLE PRECISION,
                avg_flash_duration DOUBLE PRECISION,
                avg_molotov_damage DOUBLE PRECISION,
                avg_he_damage DOUBLE PRECISION,
                avg_total_equipment_value DOUBLE PRECISION,
                avg_saved DOUBLE PRECISION,
                avg_spent DOUBLE PRECISION,
                avg_kill_cost DOUBLE PRECISION,
                avg_hundred_damage_cost DOUBLE PRECISION,
                avg_multikills DOUBLE PRECISION,
                multikills_vs_2 INTEGER,
                multikills_vs_3 INTEGER,
                multikills_vs_4 INTEGER,
                multikills_vs_5 INTEGER,
                clutches_vs_1 INTEGER,
                clutches_vs_2 INTEGER,
                clutches_vs_3 INTEGER,
                clutches_vs_4 INTEGER,
                clutches_vs_5 INTEGER,
                raw_stats_json TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_esports_stats_player ON esports_player_stats(sport, player_id)",
            "CREATE INDEX IF NOT EXISTS idx_esports_stats_discipline ON esports_player_stats(discipline, player_id)",
            "CREATE INDEX IF NOT EXISTS idx_esports_stats_date ON esports_player_stats(sport, start_date, end_date)",
        ]

        try:
            async with self.database.engine.begin() as conn:  # type: ignore[attr-defined]
                await conn.execute(text(table_sql))
                for sql in indexes:
                    await conn.execute(text(sql))
            logger.info("Esports player stats table ready")
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to create esports_player_stats table", error=str(exc))
            return False

        # Lightweight, best-effort schema evolution for new metrics columns.
        # If columns already exist, we ignore the error so ingestion still works.
        alter_statements: List[str] = []
        if is_sqlite:
            prefix = "ALTER TABLE esports_player_stats ADD COLUMN "
            alter_statements = [
                prefix + "games_count INTEGER",
                prefix + "rounds_count INTEGER",
                prefix + "rounds_win INTEGER",
                prefix + "rounds_winrate REAL",
                prefix + "avg_player_rating_value REAL",
                prefix + "avg_player_rating REAL",
                prefix + "avg_death REAL",
                prefix + "avg_kd_rate REAL",
                prefix + "kd_diff_sum INTEGER",
                prefix + "avg_first_kills REAL",
                prefix + "avg_first_death REAL",
                prefix + "avg_trade_kills REAL",
                prefix + "avg_trade_death REAL",
                prefix + "avg_shots REAL",
                prefix + "avg_shots_accuracy REAL",
                prefix + "avg_headshots REAL",
                prefix + "avg_headshots_accuracy REAL",
                prefix + "avg_headshot_kills_accuracy REAL",
                prefix + "avg_hits REAL",
                prefix + "avg_flash_assists REAL",
                prefix + "avg_flash_hits REAL",
                prefix + "avg_flash_duration REAL",
                prefix + "avg_molotov_damage REAL",
                prefix + "avg_he_damage REAL",
                prefix + "avg_total_equipment_value REAL",
                prefix + "avg_saved REAL",
                prefix + "avg_spent REAL",
                prefix + "avg_kill_cost REAL",
                prefix + "avg_hundred_damage_cost REAL",
                prefix + "avg_multikills REAL",
                prefix + "multikills_vs_2 INTEGER",
                prefix + "multikills_vs_3 INTEGER",
                prefix + "multikills_vs_4 INTEGER",
                prefix + "multikills_vs_5 INTEGER",
                prefix + "clutches_vs_1 INTEGER",
                prefix + "clutches_vs_2 INTEGER",
                prefix + "clutches_vs_3 INTEGER",
                prefix + "clutches_vs_4 INTEGER",
                prefix + "clutches_vs_5 INTEGER",
            ]
        else:
            prefix = "ALTER TABLE esports_player_stats ADD COLUMN IF NOT EXISTS "
            alter_statements = [
                prefix + "games_count INTEGER",
                prefix + "rounds_count INTEGER",
                prefix + "rounds_win INTEGER",
                prefix + "rounds_winrate DOUBLE PRECISION",
                prefix + "avg_player_rating_value DOUBLE PRECISION",
                prefix + "avg_player_rating DOUBLE PRECISION",
                prefix + "avg_death DOUBLE PRECISION",
                prefix + "avg_kd_rate DOUBLE PRECISION",
                prefix + "kd_diff_sum INTEGER",
                prefix + "avg_first_kills DOUBLE PRECISION",
                prefix + "avg_first_death DOUBLE PRECISION",
                prefix + "avg_trade_kills DOUBLE PRECISION",
                prefix + "avg_trade_death DOUBLE PRECISION",
                prefix + "avg_shots DOUBLE PRECISION",
                prefix + "avg_shots_accuracy DOUBLE PRECISION",
                prefix + "avg_headshots DOUBLE PRECISION",
                prefix + "avg_headshots_accuracy DOUBLE PRECISION",
                prefix + "avg_headshot_kills_accuracy DOUBLE PRECISION",
                prefix + "avg_hits DOUBLE PRECISION",
                prefix + "avg_flash_assists DOUBLE PRECISION",
                prefix + "avg_flash_hits DOUBLE PRECISION",
                prefix + "avg_flash_duration DOUBLE PRECISION",
                prefix + "avg_molotov_damage DOUBLE PRECISION",
                prefix + "avg_he_damage DOUBLE PRECISION",
                prefix + "avg_total_equipment_value DOUBLE PRECISION",
                prefix + "avg_saved DOUBLE PRECISION",
                prefix + "avg_spent DOUBLE PRECISION",
                prefix + "avg_kill_cost DOUBLE PRECISION",
                prefix + "avg_hundred_damage_cost DOUBLE PRECISION",
                prefix + "avg_multikills DOUBLE PRECISION",
                prefix + "multikills_vs_2 INTEGER",
                prefix + "multikills_vs_3 INTEGER",
                prefix + "multikills_vs_4 INTEGER",
                prefix + "multikills_vs_5 INTEGER",
                prefix + "clutches_vs_1 INTEGER",
                prefix + "clutches_vs_2 INTEGER",
                prefix + "clutches_vs_3 INTEGER",
                prefix + "clutches_vs_4 INTEGER",
                prefix + "clutches_vs_5 INTEGER",
            ]

        if alter_statements:
            try:
                async with self.database.engine.begin() as conn:  # type: ignore[attr-defined]
                    for stmt in alter_statements:
                        try:
                            await conn.execute(text(stmt))
                        except Exception:
                            # Column might already exist; ignore to keep ingestion running.
                            continue
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning(
                    "Failed to apply esports_player_stats schema migrations",
                    error=str(exc),
                )

        return True

    async def ingest(
        self,
        disciplines: List[str],
        start_date: str,
        end_date: str,
        page_limit: int = 40,
    ) -> Dict[str, Any]:
        """Ingest stats for all requested disciplines over the date range."""
        if not await self.ensure_table():
            raise RuntimeError("Failed to initialize esports_player_stats table")

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
                        "Failed to ingest BO3.gg player stats",
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
        """Ingest all pages of BO3.gg player stats for a single discipline."""
        # Determine remote slug and parameter strategy per discipline.
        config = dict(self.DEFAULT_CONFIG)
        config.update(self.DISCIPLINE_CONFIG.get(discipline, {}))

        if not config.get("supported", True):
            reason = config.get("reason", "Discipline not supported by BO3.gg")
            logger.warning("Skipping unsupported discipline", discipline=discipline, reason=reason)
            return {
                "players_stored": 0,
                "total_reported": 0,
                "note": reason,
            }

        endpoint = config.get("endpoint")
        if endpoint:
            endpoint = endpoint.lstrip("/")
            url = f"{self.BASE_URL}/{endpoint}"
        else:
            remote_slug = config.get("remote_slug") or discipline
            url = f"{self.BASE_URL}/{remote_slug}/stats/players/tops"

        params: Dict[str, Any] = {
            "page[offset]": 0,
            "page[limit]": page_limit,
        }

        sort_field = config.get("sort")
        if sort_field:
            params["sort"] = sort_field

        with_param = config.get("with")
        if with_param:
            params["with"] = with_param

        date_filters: Optional[Dict[str, str]] = None
        if config.get("filter_dates", True):
            date_filters = config.get("date_filters") or self.DEFAULT_DATE_FILTERS

        if date_filters:
            params[date_filters["gt"]] = start_date
            params[date_filters["lt"]] = end_date

        extra_params = config.get("extra_params") or {}
        params.update(extra_params)

        # Valorant endpoint was observed with "with=player,", others use "player".
        if discipline == "val":
            params["with"] = config.get("with", "player,")

        # Backwards compatibility: ensure page[offset] always numeric
        params["page[offset]"] = int(params["page[offset]"])

        total_count: Optional[int] = None
        players_stored = 0

        while True:
            logger.info(
                "Fetching BO3.gg player stats page",
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

            await self._store_stats_batch(
                discipline=discipline,
                start_date=start_date,
                end_date=end_date,
                results=results,
            )

            players_stored += len(results)

            total_meta = payload.get("total") or {}
            if total_count is None:
                total_count = int(total_meta.get("count") or players_stored)

            # Pagination: BO3.gg uses offset/limit semantics
            params["page[offset]"] = int(params["page[offset]"]) + page_limit
            if total_count is not None and params["page[offset]"] >= total_count:
                break

        logger.info(
            "Completed BO3.gg player stats ingestion",
            discipline=discipline,
            players_stored=players_stored,
            total_count=total_count,
        )

        return {
            "players_stored": players_stored,
            "total_reported": total_count or players_stored,
        }

    async def _store_stats_batch(
        self,
        discipline: str,
        start_date: str,
        end_date: str,
        results: List[Dict[str, Any]],
    ) -> None:
        """Store a batch of player stats rows into esports_player_stats.

        The `sport` column uses the short discipline code directly (e.g. "lol",
        "dota2", "cs2"), rather than a prefixed value like "esports_lol".
        """
        if not results:
            return

        # Use the discipline slug directly as the sport identifier to keep
        # values like "lol" / "dota2" instead of "esports_lol" / etc.
        sport = discipline

        rows: List[Dict[str, Any]] = []
        for item in results:
            # Resolve player / team information; Valorant nests this under
            # "vlr_player" while lol/dota2 expose "player" directly.
            player = item.get("player") or {}
            if not player and "vlr_player" in item:
                player = (item.get("vlr_player") or {}).get("player") or {}

            country = player.get("country") or {}
            team = player.get("team") or {}

            # Advanced metrics (primarily CS2 stats_list, but also reused if
            # other games expose the same fields). We mirror the BO3.gg field
            # names to make modeling easier for clients.
            games_count = item.get("games_count")
            rounds_count = item.get("rounds_count")
            rounds_win = item.get("rounds_win")
            rounds_winrate = item.get("rounds_winrate")
            avg_player_rating_value = item.get("avg_player_rating_value")
            avg_player_rating = item.get("avg_player_rating")
            avg_death = item.get("avg_death")
            avg_kd_rate = item.get("avg_kd_rate")
            kd_diff_sum = item.get("kd_diff_sum")
            avg_first_kills = item.get("avg_first_kills")
            avg_first_death = item.get("avg_first_death")
            avg_trade_kills = item.get("avg_trade_kills")
            avg_trade_death = item.get("avg_trade_death")
            avg_shots = item.get("avg_shots")
            avg_shots_accuracy = item.get("avg_shots_accuracy")
            avg_headshots = item.get("avg_headshots")
            avg_headshots_accuracy = item.get("avg_headshots_accuracy")
            avg_headshot_kills_accuracy = item.get("avg_headshot_kills_accuracy")
            avg_hits = item.get("avg_hits")
            avg_flash_assists = item.get("avg_flash_assists")
            avg_flash_hits = item.get("avg_flash_hits")
            avg_flash_duration = item.get("avg_flash_duration")
            avg_molotov_damage = item.get("avg_molotov_damage")
            avg_he_damage = item.get("avg_he_damage")
            avg_total_equipment_value = item.get("avg_total_equipment_value")
            avg_saved = item.get("avg_saved")
            avg_spent = item.get("avg_spent")
            avg_kill_cost = item.get("avg_kill_cost")
            avg_hundred_damage_cost = item.get("avg_hundred_damage_cost")
            avg_multikills = item.get("avg_multikills")
            multikills_vs_2 = item.get("multikills_vs_2")
            multikills_vs_3 = item.get("multikills_vs_3")
            multikills_vs_4 = item.get("multikills_vs_4")
            multikills_vs_5 = item.get("multikills_vs_5")
            clutches_vs_1 = item.get("clutches_vs_1")
            clutches_vs_2 = item.get("clutches_vs_2")
            clutches_vs_3 = item.get("clutches_vs_3")
            clutches_vs_4 = item.get("clutches_vs_4")
            clutches_vs_5 = item.get("clutches_vs_5")

            # Discipline-specific metric mapping into generic columns.
            if discipline in {"lol", "dota2"}:
                maps_played = item.get("maps_played")
                total_kills = item.get("total_kills")
                avg_kills = item.get("avg_kills")
                total_deaths = item.get("total_deaths")
                avg_deaths = item.get("avg_deaths")
                total_assists = item.get("total_assists")
                avg_assists = item.get("avg_assists")
                kp = item.get("kp")
                total_damage = item.get("total_damage")
                avg_damage = item.get("avg_damage")
            elif discipline == "val":
                maps_played = item.get("games_count")
                total_kills = item.get("kills_sum")
                avg_kills = item.get("avg_kills")
                total_deaths = item.get("deaths_sum")
                avg_deaths = item.get("avg_deaths")
                total_assists = item.get("assists_sum")
                avg_assists = item.get("avg_assists")
                kp = None
                total_damage = item.get("damage_sum")
                avg_damage = item.get("avg_damage")
            else:
                maps_played = item.get("maps_played") or item.get("games_count")
                total_kills = item.get("total_kills") or item.get("kills_sum")
                avg_kills = item.get("avg_kills")
                total_deaths = item.get("total_deaths") or item.get("deaths_sum")
                avg_deaths = item.get("avg_deaths")
                total_assists = item.get("total_assists") or item.get("assists_sum")
                avg_assists = item.get("avg_assists")
                kp = item.get("kp")
                total_damage = item.get("total_damage") or item.get("damage_sum")
                avg_damage = item.get("avg_damage")

            rows.append(
                {
                    "sport": sport,
                    "discipline": discipline,
                    "player_id": item.get("player_id"),
                    "player_slug": player.get("slug"),
                    "nickname": player.get("nickname"),
                    "first_name": player.get("first_name"),
                    "last_name": player.get("last_name"),
                    "team_id": team.get("id"),
                    "team_name": team.get("name"),
                    "country_code": country.get("code"),
                    "country_name": country.get("name"),
                    "start_date": start_date,
                    "end_date": end_date,
                    "maps_played": maps_played,
                    "total_kills": total_kills,
                    "avg_kills": avg_kills,
                    "total_deaths": total_deaths,
                    "avg_deaths": avg_deaths,
                    "total_assists": total_assists,
                    "avg_assists": avg_assists,
                    "kp": kp,
                    "total_damage": total_damage,
                    "avg_damage": avg_damage,
                    "raw_stats_json": json.dumps(item),
                    "games_count": games_count,
                    "rounds_count": rounds_count,
                    "rounds_win": rounds_win,
                    "rounds_winrate": rounds_winrate,
                    "avg_player_rating_value": avg_player_rating_value,
                    "avg_player_rating": avg_player_rating,
                    "avg_death": avg_death,
                    "avg_kd_rate": avg_kd_rate,
                    "kd_diff_sum": kd_diff_sum,
                    "avg_first_kills": avg_first_kills,
                    "avg_first_death": avg_first_death,
                    "avg_trade_kills": avg_trade_kills,
                    "avg_trade_death": avg_trade_death,
                    "avg_shots": avg_shots,
                    "avg_shots_accuracy": avg_shots_accuracy,
                    "avg_headshots": avg_headshots,
                    "avg_headshots_accuracy": avg_headshots_accuracy,
                    "avg_headshot_kills_accuracy": avg_headshot_kills_accuracy,
                    "avg_hits": avg_hits,
                    "avg_flash_assists": avg_flash_assists,
                    "avg_flash_hits": avg_flash_hits,
                    "avg_flash_duration": avg_flash_duration,
                    "avg_molotov_damage": avg_molotov_damage,
                    "avg_he_damage": avg_he_damage,
                    "avg_total_equipment_value": avg_total_equipment_value,
                    "avg_saved": avg_saved,
                    "avg_spent": avg_spent,
                    "avg_kill_cost": avg_kill_cost,
                    "avg_hundred_damage_cost": avg_hundred_damage_cost,
                    "avg_multikills": avg_multikills,
                    "multikills_vs_2": multikills_vs_2,
                    "multikills_vs_3": multikills_vs_3,
                    "multikills_vs_4": multikills_vs_4,
                    "multikills_vs_5": multikills_vs_5,
                    "clutches_vs_1": clutches_vs_1,
                    "clutches_vs_2": clutches_vs_2,
                    "clutches_vs_3": clutches_vs_3,
                    "clutches_vs_4": clutches_vs_4,
                    "clutches_vs_5": clutches_vs_5,
                }
            )

        insert_sql = text(
            """
            INSERT INTO esports_player_stats (
                sport,
                discipline,
                player_id,
                player_slug,
                nickname,
                first_name,
                last_name,
                team_id,
                team_name,
                country_code,
                country_name,
                start_date,
                end_date,
                maps_played,
                total_kills,
                avg_kills,
                total_deaths,
                avg_deaths,
                total_assists,
                avg_assists,
                kp,
                total_damage,
                avg_damage,
                games_count,
                rounds_count,
                rounds_win,
                rounds_winrate,
                avg_player_rating_value,
                avg_player_rating,
                avg_death,
                avg_kd_rate,
                kd_diff_sum,
                avg_first_kills,
                avg_first_death,
                avg_trade_kills,
                avg_trade_death,
                avg_shots,
                avg_shots_accuracy,
                avg_headshots,
                avg_headshots_accuracy,
                avg_headshot_kills_accuracy,
                avg_hits,
                avg_flash_assists,
                avg_flash_hits,
                avg_flash_duration,
                avg_molotov_damage,
                avg_he_damage,
                avg_total_equipment_value,
                avg_saved,
                avg_spent,
                avg_kill_cost,
                avg_hundred_damage_cost,
                avg_multikills,
                multikills_vs_2,
                multikills_vs_3,
                multikills_vs_4,
                multikills_vs_5,
                clutches_vs_1,
                clutches_vs_2,
                clutches_vs_3,
                clutches_vs_4,
                clutches_vs_5,
                raw_stats_json
            ) VALUES (
                :sport,
                :discipline,
                :player_id,
                :player_slug,
                :nickname,
                :first_name,
                :last_name,
                :team_id,
                :team_name,
                :country_code,
                :country_name,
                :start_date,
                :end_date,
                :maps_played,
                :total_kills,
                :avg_kills,
                :total_deaths,
                :avg_deaths,
                :total_assists,
                :avg_assists,
                :kp,
                :total_damage,
                :avg_damage,
                :games_count,
                :rounds_count,
                :rounds_win,
                :rounds_winrate,
                :avg_player_rating_value,
                :avg_player_rating,
                :avg_death,
                :avg_kd_rate,
                :kd_diff_sum,
                :avg_first_kills,
                :avg_first_death,
                :avg_trade_kills,
                :avg_trade_death,
                :avg_shots,
                :avg_shots_accuracy,
                :avg_headshots,
                :avg_headshots_accuracy,
                :avg_headshot_kills_accuracy,
                :avg_hits,
                :avg_flash_assists,
                :avg_flash_hits,
                :avg_flash_duration,
                :avg_molotov_damage,
                :avg_he_damage,
                :avg_total_equipment_value,
                :avg_saved,
                :avg_spent,
                :avg_kill_cost,
                :avg_hundred_damage_cost,
                :avg_multikills,
                :multikills_vs_2,
                :multikills_vs_3,
                :multikills_vs_4,
                :multikills_vs_5,
                :clutches_vs_1,
                :clutches_vs_2,
                :clutches_vs_3,
                :clutches_vs_4,
                :clutches_vs_5,
                :raw_stats_json
            )
            """
        )

        try:
            async with self.database.session_maker() as session:  # type: ignore[attr-defined]
                await session.execute(insert_sql, rows)
                await session.commit()
            logger.info(
                "Stored esports player stats batch",
                discipline=discipline,
                count=len(rows),
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error(
                "Failed to store esports player stats batch",
                discipline=discipline,
                count=len(rows),
                error=str(exc),
            )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Ingest esports player stats from BO3.gg into kashrock_historical.db "
            "for a given date range."
        )
    )

    parser.add_argument(
        "--disciplines",
        type=str,
        default="lol,cs2,val,r6s,dota2",
        help=(
            "Comma-separated list of BO3 disciplines to ingest "
            "(e.g. 'lol,cs2,val,r6s,dota2')."
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
        default=40,
        help="BO3.gg page[limit] page size (default: 40)",
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
    ingestor = Bo3EsportsPlayerStatsIngestor(db)

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
