"""Core export service for assembling datasets into row streams."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, AsyncIterator, Dict, Iterable, List, Optional

from v6.export import ExportJob


class ExportService:
    """Generate row streams for requested export datasets."""

    def __init__(
        self,
        odds_engine,
        props_engine,
        stats_engine,
        historical_db,
    ):
        self.odds_engine = odds_engine
        self.props_engine = props_engine
        self.stats_engine = stats_engine
        self.historical_db = historical_db

    async def iterate(self, job: ExportJob) -> AsyncIterator[Dict[str, Any]]:
        """Yield normalized rows for each requested dataset."""
        dataset_map = {
            "live_odds": self._iter_live_odds,
            "live_props": self._iter_live_props,
            "game_stats": self._iter_game_stats,
            "historical_odds": self._iter_historical_odds,
            "historical_props": self._iter_historical_props,
            "historical_games": self._iter_historical_games,
            "historical_team_stats": self._iter_historical_team_stats,
            "historical_team_stat_leaders": self._iter_historical_team_stat_leaders,
            "historical_players": self._iter_historical_players,
            "historical_player_boxscores": self._iter_historical_player_boxscores,
        }

        for dataset in job.datasets:
            iterator = dataset_map.get(dataset)
            if not iterator:
                continue
            async for row in iterator(job):
                row.setdefault("dataset", dataset)
                row.setdefault("scope", job.scope)
                row.setdefault("exported_at", job.generated_at)
                yield row

    async def shutdown(self) -> None:
        """Release underlying resources."""
        if hasattr(self.stats_engine, "close"):
            await self.stats_engine.close()

    # -------------------------------------------------------------------------
    # Dataset iterators
    # -------------------------------------------------------------------------
    async def _iter_live_odds(self, job: ExportJob) -> AsyncIterator[Dict[str, Any]]:
        sport = job.filters.get("sport")
        books_filter = _parse_books(job.filters.get("books"))

        odds_snapshot = await self.odds_engine.get_all_odds(sport)
        fetched_at = odds_snapshot.get("fetched_at")

        for book_key, book_payload in odds_snapshot.get("books", {}).items():
            if books_filter and book_key not in books_filter:
                continue
            if not isinstance(book_payload, dict) or "games" not in book_payload:
                continue
            book_meta = book_payload.get("book", {})
            for game in book_payload.get("games", []):
                odds_list = game.get("odds", [])
                if not isinstance(odds_list, list):
                    continue
                for odds_entry in odds_list:
                    record = {
                        "sport": sport or odds_snapshot.get("sport"),
                        "book_key": book_key,
                        "book_name": book_meta.get("name"),
                        "game_id": game.get("game_id"),
                        "event_time": game.get("start_time") or game.get("start_time_str"),
                        "market_type": odds_entry.get("MarketType") or odds_entry.get("market_type"),
                        "odds_payload": odds_entry,
                        "source_fetched_at": fetched_at,
                    }
                    yield record

    async def _iter_live_props(self, job: ExportJob) -> AsyncIterator[Dict[str, Any]]:
        sport = job.filters.get("sport")
        books_filter = _parse_books(job.filters.get("books"))

        if not books_filter:
            if not self.props_engine.streamers:
                await self.props_engine.initialize()
            books_filter = list(self.props_engine.streamers.keys())[:5]

        props_snapshot = await self.props_engine.get_all_props(sport, books_filter)
        fetched_at = props_snapshot.get("fetched_at")

        for book_key, book_payload in props_snapshot.get("books", {}).items():
            if not isinstance(book_payload, dict) or "props" not in book_payload:
                continue
            book_meta = book_payload.get("book", {})
            for prop in book_payload.get("props", []):
                record = {
                    "sport": sport or props_snapshot.get("sport"),
                    "book_key": book_key,
                    "book_name": book_meta.get("name"),
                    "player_name": prop.get("player_name"),
                    "player_id": prop.get("player_id"),
                    "team_name": prop.get("team_name") or prop.get("player_team"),
                    "stat_type": prop.get("stat_type"),
                    "line": prop.get("line"),
                    "direction": prop.get("direction"),
                    "odds": prop.get("odds"),
                    "game_id": prop.get("game_id"),
                    "prop_payload": prop,
                    "source_fetched_at": fetched_at,
                }
                yield record

    async def _iter_game_stats(self, job: ExportJob) -> AsyncIterator[Dict[str, Any]]:
        sport = job.filters.get("sport") or "americanfootball_nfl"
        games = await self.stats_engine.get_games(sport, sport)
        for game in games:
            if hasattr(game, "model_dump"):
                payload = game.model_dump()
            elif hasattr(game, "dict"):
                payload = game.dict()
            else:
                payload = dict(game)
            record = {
                "sport": sport,
                "game_id": payload.get("id"),
                "status": payload.get("status"),
                "scheduled_at": payload.get("scheduled_at"),
                "home_team": payload.get("home_team"),
                "away_team": payload.get("away_team"),
                "score": payload.get("score"),
                "game_payload": payload,
            }
            yield record

    async def _iter_historical_odds(self, job: ExportJob) -> AsyncIterator[Dict[str, Any]]:
        await self._ensure_historical_connected()
        rows = await self.historical_db.fetch_odds(
            sport=job.filters.get("sport"),
            date_from=_parse_datetime(job.filters.get("date_from")),
            date_to=_parse_datetime(job.filters.get("date_to")),
            book_name=job.filters.get("book_name"),
            limit=int(job.filters.get("limit")),
        )
        for row in rows:
            record = {
                "sport": row.get("sport"),
                "captured_at": row.get("captured_at"),
                "event_id": row.get("event_id"),
                "book_name": row.get("book_name"),
                "book_id": row.get("book_id"),
                "market_type": row.get("market_type"),
                "market_data": row.get("market_data"),
                "home_team": row.get("home_team"),
                "away_team": row.get("away_team"),
                "commence_time": row.get("commence_time"),
            }
            yield record

    async def _iter_historical_props(self, job: ExportJob) -> AsyncIterator[Dict[str, Any]]:
        await self._ensure_historical_connected()
        rows = await self.historical_db.fetch_player_props(
            sport=job.filters.get("sport"),
            date_from=_parse_datetime(job.filters.get("date_from")),
            date_to=_parse_datetime(job.filters.get("date_to")),
            book_name=job.filters.get("book_name"),
            limit=int(job.filters.get("limit")),
        )
        for row in rows:
            record = {
                "sport": row.get("sport"),
                "captured_at": row.get("captured_at"),
                "event_id": row.get("event_id"),
                "player_name": row.get("player_name"),
                "player_team": row.get("player_team"),
                "stat_type": row.get("stat_type"),
                "stat_value": row.get("stat_value"),
                "direction": row.get("direction"),
                "odds": row.get("odds"),
                "book_name": row.get("book_name"),
                "book_id": row.get("book_id"),
                "sportsbook_id": row.get("sportsbook_id"),
                "prop_data": row.get("prop_data"),
            }
            yield record

    async def _iter_historical_games(self, job: ExportJob) -> AsyncIterator[Dict[str, Any]]:
        await self._ensure_historical_connected()
        rows = await self.historical_db.fetch_thescore_games(
            limit=int(job.filters.get("limit")) if job.filters.get("limit") is not None else None,
        )
        for row in rows:
            base = dict(row)

            # Parse raw_event_json if present to enrich flattened schema
            raw_json = base.get("raw_event_json")
            details: Dict[str, Any] = {}
            if isinstance(raw_json, str):
                try:
                    import json

                    details = json.loads(raw_json)
                except Exception:
                    details = {}

            record: Dict[str, Any] = {
                "sport": base.get("sport") or details.get("league", {}).get("slug"),
                "season_year": base.get("season_year") or details.get("season_week", "").split("-")[0] or None,
                "season_type": base.get("season_type"),
                "season_label": base.get("season_label"),
                "week": base.get("week"),
                "event_id": base.get("event_id") or details.get("id"),
                "game_date": base.get("game_date") or details.get("game_date"),
                "status": base.get("status") or details.get("status"),
                "event_status": base.get("event_status") or details.get("event_status"),
                "home_team_id": base.get("home_team_id") or details.get("home_team", {}).get("id"),
                "home_team_name": base.get("home_team_name") or details.get("home_team", {}).get("full_name"),
                "away_team_id": base.get("away_team_id") or details.get("away_team", {}).get("id"),
                "away_team_name": base.get("away_team_name") or details.get("away_team", {}).get("full_name"),
                "home_score": base.get("home_score"),
                "away_score": base.get("away_score"),
                "stadium": base.get("stadium") or details.get("stadium"),
                "location": base.get("location") or details.get("location"),
                "odds_line": base.get("odds_line"),
                "odds_over_under": base.get("odds_over_under"),
                "odds_closing": base.get("odds_closing"),
                "raw_event_json": raw_json,
                "created_at": base.get("created_at"),
                "updated_at": base.get("updated_at"),
            }

            yield record

    async def _iter_historical_team_stats(self, job: ExportJob) -> AsyncIterator[Dict[str, Any]]:
        await self._ensure_historical_connected()
        rows = await self.historical_db.fetch_nfl_team_statistics(
            limit=int(job.filters.get("limit")) if job.filters.get("limit") is not None else None,
        )
        for row in rows:
            yield dict(row)

    async def _iter_historical_team_stat_leaders(self, job: ExportJob) -> AsyncIterator[Dict[str, Any]]:
        await self._ensure_historical_connected()
        rows = await self.historical_db.fetch_realvg_team_stat_leaders(
            sport=job.filters.get("sport"),
            limit=int(job.filters.get("limit")) if job.filters.get("limit") is not None else None,
        )
        for row in rows:
            yield dict(row)

    async def _iter_historical_players(self, job: ExportJob) -> AsyncIterator[Dict[str, Any]]:
        await self._ensure_historical_connected()
        rows = await self.historical_db.fetch_nfl_modeling_players(
            limit=int(job.filters.get("limit")) if job.filters.get("limit") is not None else None,
        )
        for row in rows:
            yield dict(row)

    async def _iter_historical_player_boxscores(self, job: ExportJob) -> AsyncIterator[Dict[str, Any]]:
        await self._ensure_historical_connected()
        rows = await self.historical_db.fetch_nba_player_boxscores(
            sport=job.filters.get("sport"),
            date_from=_parse_datetime(job.filters.get("date_from")),
            date_to=_parse_datetime(job.filters.get("date_to")),
            team_id=job.filters.get("team_id"),
            player_id=job.filters.get("player_id"),
            game_id=job.filters.get("game_id"),
            limit=int(job.filters.get("limit")) if job.filters.get("limit") is not None else 5000,
        )
        for row in rows:
            yield dict(row)

    async def _ensure_historical_connected(self) -> None:
        if getattr(self.historical_db, "_connected", False):
            return
        if hasattr(self.historical_db, "connect"):
            await self.historical_db.connect()


def _parse_books(value: Optional[Any]) -> Optional[List[str]]:
    if not value:
        return None
    if isinstance(value, (list, tuple)):
        return [str(v).strip() for v in value if v]
    return [part.strip() for part in str(value).split(",") if part.strip()]


def _parse_datetime(value: Optional[Any]) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None
