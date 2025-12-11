"""Optimized V6 Props Engine with lazy initialization, caching, and metrics."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog

from streamers.lunosoft_books import LUNOSOFT_BOOK_STREAMERS
from processing.stat_canonicalizer import canonicalize_stat_type
from v6.common.cache import get_props_cache, cache_key
from v6.common.metrics import get_metrics, TimedOperation
from v6.common.rate_limiter import get_lunosoft_limiter, RateLimitedSemaphore

logger = structlog.get_logger()


class OptimizedPropsEngine:
    """Optimized V6 Props Engine with production features."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.streamers: Dict[str, Any] = {}
        self.max_concurrency = max(1, int(self.config.get("max_concurrency", 4)))
        self.enable_cache = self.config.get("enable_cache", True)
        self.cache_ttl = int(self.config.get("cache_ttl", 60))
        
        # Rate limiting: 4 concurrent, 10 req/s per book
        self.semaphore = RateLimitedSemaphore(
            self.max_concurrency, 
            get_lunosoft_limiter()
        )
        
        self.metrics = get_metrics()
        self.cache = get_props_cache()
        self._initialized_books: set = set()
        self._circuit_breaker: Dict[str, Dict[str, Any]] = {}  # Circuit breaker state

    async def initialize_book(self, book_key: str) -> bool:
        """Lazy initialization of a single sportsbook."""
        if book_key in self._initialized_books:
            return True
            
        # Check circuit breaker
        if self._is_circuit_open(book_key):
            logger.warning("Circuit breaker open for sportsbook", book=book_key)
            return False
            
        if book_key not in LUNOSOFT_BOOK_STREAMERS:
            # Ignore Sharp books in Props Engine (handled by Proptimizer)
            if book_key.startswith("sharp_"):
                return False
            logger.error("Sportsbook not found in registry", book=book_key)
            return False

        try:
            streamer_cls = LUNOSOFT_BOOK_STREAMERS[book_key]
            streamer = streamer_cls(f"lunosoft_{book_key}", self.config)
            connected = await streamer.connect()
            
            if connected:
                self.streamers[book_key] = streamer
                self._initialized_books.add(book_key)
                self._reset_circuit_breaker(book_key)
                self.metrics.increment("books_initialized", tags={"book": book_key})
                logger.info("Initialized sportsbook", book=book_key)
                return True
            else:
                self._record_failure(book_key)
                self.metrics.error("book_connection_failed", book_key)
                logger.warning("Failed to connect sportsbook", book=book_key)
                return False
                
        except Exception as exc:
            self._record_failure(book_key)
            self.metrics.error("book_initialization_error", book_key)
            logger.error("Error initializing sportsbook", book=book_key, error=str(exc))
            return False

    async def initialize(self, books: Optional[List[str]] = None) -> None:
        """Initialize specified sportsbooks (lazy initialization)."""
        target_books = books or list(LUNOSOFT_BOOK_STREAMERS.keys())
        logger.info("Initializing Optimized Props Engine", target_books=len(target_books))
        
        # Initialize a few key books immediately, rest on-demand
        priority_books = ["draftkings", "fanduel", "betmgm"][:len(target_books)]
        init_tasks = []
        
        for book_key in target_books:
            if book_key in priority_books:
                init_tasks.append(self.initialize_book(book_key))
        
        if init_tasks:
            await asyncio.gather(*init_tasks, return_exceptions=True)
        
        logger.info("Optimized Props Engine ready", 
                   initialized=len(self._initialized_books),
                   total=len(target_books))

    async def shutdown(self) -> None:
        """Shutdown all streamers."""
        logger.info("Shutting down Optimized Props Engine")
        tasks = []
        for book_key, streamer in self.streamers.items():
            try:
                tasks.append(streamer.disconnect())
            except Exception as exc:
                logger.error("Error disconnecting sportsbook", book=book_key, error=str(exc))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self.streamers.clear()
        self._initialized_books.clear()
        self._circuit_breaker.clear()
        logger.info("Optimized Props Engine shutdown complete")

    async def get_props_by_book(
        self, book_key: str, sport: Optional[str] = None, use_cache: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Get player props from a specific sportsbook with caching."""
        use_cache = use_cache if use_cache is not None else self.enable_cache
        
        # Check cache first
        if use_cache:
            cache_key_str = cache_key("props", book_key, sport or "all")
            cached_result = self.cache.get(cache_key_str)
            if cached_result:
                self.metrics.increment("cache_hits", tags={"type": "props"})
                return cached_result
            else:
                self.metrics.increment("cache_misses", tags={"type": "props"})

        # Check circuit breaker
        if self._is_circuit_open(book_key):
            return {"error": f"Circuit breaker open for sportsbook {book_key}"}

        # Lazy initialize if needed
        if book_key not in self._initialized_books:
            if not await self.initialize_book(book_key):
                return {"error": f"Failed to initialize sportsbook {book_key}"}

        streamer = self.streamers[book_key]
        
        async with TimedOperation("get_props_by_book", {"book": book_key, "sport": sport or "all"}):
            try:
                self.metrics.book_request(book_key, "props")
                
                raw_data = await streamer.fetch_data(sport)
                processed_data = await streamer.process_data(raw_data)
                
                # Normalize and group props
                normalized_props = self._normalize_props(processed_data.get("player_props", []))
                grouped_props = self._group_props_by_game(normalized_props)
                
                result = {
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
                    "cached": False,
                }
                
                # Cache the result
                if use_cache and "error" not in result:
                    self.cache.set(cache_key_str, result, self.cache_ttl)
                
                self.metrics.book_success(book_key, "props")
                self._reset_circuit_breaker(book_key)
                return result
                
            except Exception as exc:
                self._record_failure(book_key)
                self.metrics.error("get_props_by_book_error", book_key)
                logger.error("Error fetching props from sportsbook", book=book_key, error=str(exc))
                return {"error": f"Failed to fetch props from {book_key}: {str(exc)}"}

    async def get_all_props(self, sport: Optional[str] = None, books: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get player props from multiple books with concurrency control."""
        target_books = books or list(self._initialized_books)
        
        if not target_books:
            # Initialize some books if none are ready
            await self.initialize()
            target_books = list(self._initialized_books)[:5]  # Limit to 5 for performance

        async with TimedOperation("get_all_props", {"sport": sport or "all", "books": len(target_books)}):
            # Create tasks with semaphore control
            async def fetch_with_semaphore(book_key: str):
                async with self.semaphore:
                    return await self.get_props_by_book(book_key, sport)
            
            tasks = []
            for book_key in target_books:
                task = asyncio.create_task(fetch_with_semaphore(book_key))
                tasks.append((book_key, task))

            results = {}
            successful = 0
            total_props = 0
            
            for book_key, task in tasks:
                try:
                    result = await task
                    results[book_key] = result
                    if "error" not in result:
                        successful += 1
                        total_props += result.get("total_props", 0)
                except Exception as exc:
                    self.metrics.error("get_all_props_book_error", book_key)
                    logger.error("Error fetching props", book=book_key, error=str(exc))
                    results[book_key] = {"error": str(exc)}

            self.metrics.gauge("props_fetch_success_rate", successful / len(target_books) if target_books else 0)
            
            return {
                "books": results,
                "sport": sport,
                "total_books": len(results),
                "successful_books": successful,
                "total_props": total_props,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

    async def get_main_sports_props(self, books: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get player props for main sports with optimized caching."""
        main_sports = ["americanfootball_nfl", "basketball_nba", "baseball_mlb", "icehockey_nhl"]
        target_books = books or list(self._initialized_books)[:8]  # Limit for performance

        async with TimedOperation("get_main_sports_props", {"books": len(target_books)}):
            results = {}
            total_props = 0
            
            # Process sports in parallel with rate limiting
            sport_tasks = []
            for sport in main_sports:
                task = asyncio.create_task(self.get_all_props(sport, target_books))
                sport_tasks.append((sport, task))
            
            for sport, task in sport_tasks:
                try:
                    sport_result = await task
                    sport_data = sport_result.get("books", {})
                    results[sport] = sport_data
                    total_props += sport_result.get("total_props", 0)
                except Exception as exc:
                    self.metrics.error("get_main_sports_sport_error")
                    logger.error("Error fetching sport props", sport=sport, error=str(exc))
                    results[sport] = {}

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
        target_books = books or list(self._initialized_books)
        
        async with TimedOperation("get_player_props", {"player": player_name, "books": len(target_books)}):
            results = {}
            total_props = 0

            for book_key in target_books:
                if book_key not in self._initialized_books:
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
                    total_props += len(player_props)
                except Exception as exc:
                    results[book_key] = {"error": str(exc)}

            return {
                "player": player_name,
                "sport": sport,
                "books": results,
                "total_props": total_props,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

    def _normalize_props(self, props: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize props data for consistent format."""
        normalized = []
        
        for prop in props:
            if not isinstance(prop, dict):
                continue
            
            prop_source = (
                prop.get("source")
                or prop.get("book", {}).get("key")
                or prop.get("sportsbook_name")
                or prop.get("sportsbook_id")
            )
            
            # Canonicalize stat type to prevent duplicates
            raw_stat_type = prop.get("stat_type_name") or prop.get("market_type", "")
            sport = prop.get("sport", "")
            player_name = prop.get("player_name", "")
            canonical_stat = canonicalize_stat_type(raw_stat_type, sport, player_name)

            normalized_prop = {
                "sport": prop.get("sport"),
                "sport_name": prop.get("sport_name"),
                "game_id": prop.get("game_id"),
                "game_start": prop.get("game_start"),
                "home_team": prop.get("home_team_abbrev"),
                "away_team": prop.get("away_team_abbrev"),
                "player_id": prop.get("player_id"),
                "player_name": player_name,
                "player_first_name": prop.get("player_first_name"),
                "player_last_name": prop.get("player_last_name"),
                "player_team_id": prop.get("player_team_id"),
                "stat_type_id": prop.get("stat_type_id"),
                "stat_type_name": canonical_stat,  # Use canonical stat type
                "stat_value": prop.get("stat_value") or prop.get("value"),
                "direction": prop.get("direction"),
                "odds": prop.get("odds") or prop.get("over_odds") or prop.get("under_odds"),
                "over_odds": prop.get("over_odds"),
                "under_odds": prop.get("under_odds"),
                "sportsbook_id": prop.get("sportsbook_id"),
                "sportsbook_name": prop.get("sportsbook_name"),
                "source": "kashrock",
                "line": prop.get("line") or prop.get("value"),
                "market_type": canonical_stat,  # Use canonical stat type for market_type too
            }

            if prop_source:
                normalized_prop["book_source"] = prop_source
                
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

    def _is_circuit_open(self, book_key: str) -> bool:
        """Check if circuit breaker is open for a book."""
        breaker = self._circuit_breaker.get(book_key, {})
        if not breaker:
            return False
        
        # Check if we should try again (half-open after timeout)
        if breaker.get("state") == "open":
            if time.time() - breaker.get("opened_at", 0) > 300:  # 5 minutes
                breaker["state"] = "half_open"
                return False
            return True
        
        return False

    def _record_failure(self, book_key: str) -> None:
        """Record a failure for circuit breaker."""
        if book_key not in self._circuit_breaker:
            self._circuit_breaker[book_key] = {
                "failures": 0,
                "state": "closed",
                "opened_at": 0,
            }
        
        breaker = self._circuit_breaker[book_key]
        breaker["failures"] += 1
        
        # Open circuit after 5 consecutive failures
        if breaker["failures"] >= 5:
            breaker["state"] = "open"
            breaker["opened_at"] = time.time()
            logger.warning("Circuit breaker opened", book=book_key, failures=breaker["failures"])

    def _reset_circuit_breaker(self, book_key: str) -> None:
        """Reset circuit breaker on success."""
        if book_key in self._circuit_breaker:
            self._circuit_breaker[book_key] = {
                "failures": 0,
                "state": "closed",
                "opened_at": 0,
            }

    def get_available_books(self) -> List[Dict[str, Any]]:
        """Get list of available sportsbooks."""
        books = []
        for book_key in LUNOSOFT_BOOK_STREAMERS.keys():
            breaker = self._circuit_breaker.get(book_key, {})
            books.append({
                "key": book_key,
                "initialized": book_key in self._initialized_books,
                "connected": book_key in self.streamers,
                "circuit_state": breaker.get("state", "closed"),
            })
        return books

    async def health_check(self) -> Dict[str, Any]:
        """Check health with detailed metrics."""
        results = {}
        tasks = []

        for book_key in self._initialized_books:
            if book_key in self.streamers:
                task = asyncio.create_task(self.streamers[book_key].health_check())
                tasks.append((book_key, task))

        for book_key, task in tasks:
            try:
                is_healthy = await task
                results[book_key] = {"healthy": is_healthy}
            except Exception as exc:
                results[book_key] = {"healthy": False, "error": str(exc)}

        total_books = len(results)
        healthy_books = len([r for r in results.values() if r.get("healthy", False)])

        # Include cache and metrics info
        cache_stats = self.cache.get_stats()
        metrics_summary = self.metrics.get_summary()
        circuit_breaker_stats = {
            book: breaker for book, breaker in self._circuit_breaker.items()
            if breaker.get("state") != "closed"
        }

        return {
            "total_books": total_books,
            "healthy_books": healthy_books,
            "unhealthy_books": total_books - healthy_books,
            "book_status": results,
            "overall_healthy": healthy_books > 0,
            "cache_stats": cache_stats,
            "metrics": metrics_summary,
            "circuit_breaker": circuit_breaker_stats,
        }
