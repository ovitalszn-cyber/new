"""V6 Props Engine - Per-book player props aggregation using Lunosoft streamers."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog

from streamers.lunosoft_books import LUNOSOFT_BOOK_STREAMERS
from processing.stat_canonicalizer import canonicalize_stat_type

logger = structlog.get_logger()


class PropsEngine:
    """V6 Props Engine that aggregates player props by sportsbook."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.streamers: Dict[str, Any] = {}
        self.max_concurrency = max(1, int(self.config.get("max_concurrency", 4)))
        self._semaphore: Optional[asyncio.Semaphore] = None
        self.default_books: List[str] = list(LUNOSOFT_BOOK_STREAMERS.keys())

    async def initialize(self, books: Optional[List[str]] = None) -> None:
        """Initialize all sportsbook streamers concurrently."""
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrency)

        target_books = LUNOSOFT_BOOK_STREAMERS
        if books:
            # For props, we need to map the "book_key" to the Lunosoft key or handle filtering.
            # LUNOSOFT_BOOK_STREAMERS keys are the raw book names (e.g. "pinnacle").
            # The active_books list might contain "sharp_pinnacle" too. We only care about Lunosoft keys here.
            target_books = {k: v for k, v in LUNOSOFT_BOOK_STREAMERS.items() if k in books}

        logger.info("Initializing V6 Props Engine", books=len(target_books))

        async def init_book(book_key: str, streamer_cls: Any) -> None:
            try:
                # Lunosoft streamers expect "lunosoft_bookname" as the name arg usually
                streamer = streamer_cls(f"lunosoft_{book_key}", self.config)
                try:
                    connected = await asyncio.wait_for(streamer.connect(), timeout=10.0)
                except asyncio.TimeoutError:
                    logger.warning("Timeout connecting propsbook", book=book_key)
                    return

                if connected:
                    self.streamers[book_key] = streamer
                    logger.info("Connected sportsbook", book=book_key)
                else:
                    logger.warning("Failed to connect sportsbook", book=book_key)
            except Exception as exc:
                logger.error("Error initializing sportsbook", book=book_key, error=str(exc))

        tasks = [init_book(k, v) for k, v in target_books.items()]
        if tasks:
            await asyncio.gather(*tasks)

        logger.info("V6 Props Engine initialized", connected_books=len(self.streamers))

    async def shutdown(self) -> None:
        """Shutdown all streamers."""
        logger.info("Shutting down V6 Props Engine")
        tasks = []
        for book_key, streamer in self.streamers.items():
            try:
                tasks.append(streamer.disconnect())
            except Exception as exc:
                logger.error("Error disconnecting sportsbook", book=book_key, error=str(exc))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self.streamers.clear()
        logger.info("V6 Props Engine shutdown complete")

    async def get_props_by_book(
        self, book_key: str, sport: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get player props from a specific sportsbook."""
        if book_key not in self.streamers:
            logger.error("Sportsbook not available", book=book_key)
            return {"error": f"Sportsbook {book_key} not available"}

        streamer = self.streamers[book_key]
        try:
            raw_data = await streamer.fetch_data(sport)
            processed_data = await streamer.process_data(raw_data)
            
            # Normalize props data
            normalized_props = self._normalize_props(processed_data.get("player_props", []))
            
            # Group props by game and player
            grouped_props = self._group_props_by_game(normalized_props)
            
            return {
                "book": {
                    "key": book_key,
                    "id": streamer.BOOK_ID,
                    "name": streamer.BOOK_NAME,
                },
                "sport": sport,
                "props": normalized_props,
                "grouped_props": grouped_props,
                "total_props": len(normalized_props),
                "unique_players": len(set(p.get("player_id") for p in normalized_props if p.get("player_id"))),
                "unique_games": len(set(p.get("game_id") for p in normalized_props if p.get("game_id"))),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            logger.error("Error fetching props from sportsbook", book=book_key, error=str(exc))
            return {"error": f"Failed to fetch props from {book_key}: {str(exc)}"}

    async def get_all_props(self, sport: Optional[str] = None, books: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get player props from the requested sportsbooks."""
        if not books:
            raise ValueError("books parameter is required when fetching props")

        if not self.streamers:
            await self.initialize()

        # Filter to only initialized books, keep list for error reporting
        available_books = list(self.streamers.keys())
        target_books = [book for book in books if book in available_books]
        missing_books = [book for book in books if book not in available_books]

        if not target_books:
            return {
                "books": {},
                "sport": sport,
                "requested_books": books,
                "missing_books": missing_books,
                "total_books": 0,
                "successful_books": 0,
                "total_props": 0,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrency)
        semaphore = self._semaphore

        async def fetch_with_semaphore(book_key: str):
            async with semaphore:
                return await self.get_props_by_book(book_key, sport)

        tasks = [(book_key, asyncio.create_task(fetch_with_semaphore(book_key))) for book_key in target_books]

        results: Dict[str, Any] = {}
        total_props = 0
        successful_books = 0

        for book_key, task in tasks:
            try:
                result = await task
                results[book_key] = result
                if "error" not in result:
                    successful_books += 1
                    total_props += result.get("total_props", 0)
            except Exception as exc:
                logger.error("Error fetching props", book=book_key, error=str(exc))
                results[book_key] = {"error": str(exc)}

        result_payload = {
            "books": results,
            "sport": sport,
            "requested_books": books,
            "missing_books": missing_books,
            "total_books": len(results),
            "successful_books": successful_books,
            "total_props": total_props,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

        return result_payload

    async def get_main_sports_props(self, books: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get player props for main sports (NFL, NBA, MLB, NHL) from specified books."""
        main_sports = ["americanfootball_nfl", "basketball_nba", "baseball_mlb", "icehockey_nhl"]
        target_books = books or list(self.streamers.keys())[:10]  # Limit to 10 books by default

        results = {}
        for sport in main_sports:
            sport_results = {}
            for book_key in target_books:
                if book_key in self.streamers:
                    try:
                        props_data = await self.get_props_by_book(book_key, sport)
                        sport_results[book_key] = props_data
                    except Exception as exc:
                        logger.error("Error fetching sport props", sport=sport, book=book_key, error=str(exc))
                        sport_results[book_key] = {"error": str(exc)}
            results[sport] = sport_results

        # Calculate totals
        total_props = 0
        for sport_data in results.values():
            for book_data in sport_data.values():
                if "total_props" in book_data:
                    total_props += book_data["total_props"]

        return {
            "sports": results,
            "target_books": target_books,
            "total_props": total_props,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_player_props(
        self, player_name: str, sport: Optional[str] = None, books: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get props for a specific player across books."""
        target_books = books or list(self.streamers.keys())
        results = {}

        for book_key in target_books:
            if book_key not in self.streamers:
                continue
            
            try:
                book_data = await self.get_props_by_book(book_key, sport)
                player_props = [
                    prop for prop in book_data.get("props", [])
                    if prop.get("player_name", "").lower() == player_name.lower()
                ]
                
                results[book_key] = {
                    "book": book_data.get("book"),
                    "player_props": player_props,
                    "total_props": len(player_props),
                }
            except Exception as exc:
                results[book_key] = {"error": str(exc)}

        return {
            "player": player_name,
            "sport": sport,
            "books": results,
            "total_props": sum(r.get("total_props", 0) for r in results.values() if "total_props" in r),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_stat_type_props(
        self, stat_type: str, sport: Optional[str] = None, books: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get props for a specific stat type across books."""
        target_books = books or list(self.streamers.keys())
        results = {}

        for book_key in target_books:
            if book_key not in self.streamers:
                continue
            
            try:
                book_data = await self.get_props_by_book(book_key, sport)
                stat_props = [
                    prop for prop in book_data.get("props", [])
                    if prop.get("stat_type_name", "").lower() == stat_type.lower()
                ]
                
                results[book_key] = {
                    "book": book_data.get("book"),
                    "stat_props": stat_props,
                    "total_props": len(stat_props),
                }
            except Exception as exc:
                results[book_key] = {"error": str(exc)}

        return {
            "stat_type": stat_type,
            "sport": sport,
            "books": results,
            "total_props": sum(r.get("total_props", 0) for r in results.values() if "total_props" in r),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    def _normalize_props(self, props: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize props data for consistent format and deduplicate rows."""
        normalized: List[Dict[str, Any]] = []
        seen_keys = set()

        for prop in props:
            if not isinstance(prop, dict):
                continue

            stat_type_raw = (
                prop.get("stat_type")
                or prop.get("stat_type_name")
                or prop.get("market_type")
                or ""
            )
            sport_key = prop.get("sport")
            canonical_stat = canonicalize_stat_type(stat_type_raw, sport_key or "")
            stat_type = canonical_stat or stat_type_raw

            line_value = prop.get("line") or prop.get("value")

            # Dedupe key to avoid duplicate lines for the same player/market/line/book
            dedupe_key = (
                prop.get("sport"),
                prop.get("game_id"),
                prop.get("player_id") or prop.get("player_name"),
                stat_type,
                line_value,
                prop.get("direction"),
                prop.get("sportsbook_id") or prop.get("sportsbook_name"),
            )
            if dedupe_key in seen_keys:
                continue
            seen_keys.add(dedupe_key)

            normalized_prop = {
                "sport": prop.get("sport"),
                "sport_name": prop.get("sport_name"),
                "game_id": prop.get("game_id"),
                "game_start": prop.get("game_start"),
                "home_team": prop.get("home_team_abbrev"),
                "away_team": prop.get("away_team_abbrev"),
                "player_id": prop.get("player_id"),
                "player_name": prop.get("player_name"),
                "player_first_name": prop.get("player_first_name"),
                "player_last_name": prop.get("player_last_name"),
                "player_team_id": prop.get("player_team_id"),
                "stat_type_id": prop.get("stat_type_id"),
                "stat_type_name": stat_type,
                "stat_value": prop.get("stat_value") or prop.get("value"),
                "direction": prop.get("direction"),
                "odds": prop.get("odds") or prop.get("over_odds") or prop.get("under_odds"),
                "sportsbook_id": prop.get("sportsbook_id"),
                "sportsbook_name": prop.get("sportsbook_name"),
                # Public API branding: always report KashRock as the data source
                "source": "kashrock",
                "line": line_value,
                "market_type": stat_type,
            }

            # Clean up None values
            normalized_prop = {k: v for k, v in normalized_prop.items() if v is not None}
            normalized.append(normalized_prop)

        return normalized

    def _group_props_by_game(self, props: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Group props by game and then by player."""
        grouped = {}
        
        for prop in props:
            game_id = prop.get("game_id")
            if not game_id:
                continue
                
            if game_id not in grouped:
                game_info = {
                    "game_id": game_id,
                    "game_start": prop.get("game_start"),
                    "home_team": prop.get("home_team"),
                    "away_team": prop.get("away_team"),
                    "players": {},
                }
                grouped[game_id] = game_info
            
            player_id = prop.get("player_id")
            if not player_id:
                continue
                
            if player_id not in grouped[game_id]["players"]:
                player_info = {
                    "player_id": player_id,
                    "player_name": prop.get("player_name"),
                    "player_team_id": prop.get("player_team_id"),
                    "props": [],
                }
                grouped[game_id]["players"][player_id] = player_info
            
            # Add prop to player
            prop_copy = dict(prop)
            prop_copy.pop("game_id", None)
            prop_copy.pop("home_team", None)
            prop_copy.pop("away_team", None)
            prop_copy.pop("player_id", None)
            prop_copy.pop("player_name", None)
            prop_copy.pop("player_team_id", None)
            
            grouped[game_id]["players"][player_id]["props"].append(prop_copy)
        
        return grouped

    def get_available_books(self) -> List[Dict[str, Any]]:
        """Get list of available sportsbooks."""
        books = []
        for book_key, streamer in self.streamers.items():
            books.append({
                "key": book_key,
                "id": streamer.BOOK_ID,
                "name": streamer.BOOK_NAME,
                "connected": True,
            })
        return books

    async def health_check(self) -> Dict[str, Any]:
        """Check health of all connected sportsbooks."""
        results = {}
        tasks = []

        for book_key, streamer in self.streamers.items():
            task = asyncio.create_task(streamer.health_check())
            tasks.append((book_key, task))

        for book_key, task in tasks:
            try:
                is_healthy = await task
                results[book_key] = {"healthy": is_healthy}
            except Exception as exc:
                results[book_key] = {"healthy": False, "error": str(exc)}

        total_books = len(results)
        healthy_books = len([r for r in results.values() if r.get("healthy", False)])

        return {
            "total_books": total_books,
            "healthy_books": healthy_books,
            "unhealthy_books": total_books - healthy_books,
            "book_status": results,
            "overall_healthy": healthy_books > 0,
        }
