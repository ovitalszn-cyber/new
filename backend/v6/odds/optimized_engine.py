"""Optimized V6 Odds Engine with lazy initialization, caching, and metrics."""

from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog

from streamers.lunosoft_books import LUNOSOFT_BOOK_STREAMERS
from streamers.sharp_odds import SHARP_ODDS_STREAMERS

# Combine all odds sources
ALL_BOOK_STREAMERS = {**LUNOSOFT_BOOK_STREAMERS, **SHARP_ODDS_STREAMERS}

from v6.common.cache import get_odds_cache, cache_key
from v6.common.metrics import get_metrics, TimedOperation
from v6.common.rate_limiter import get_lunosoft_limiter, RateLimitedSemaphore

logger = structlog.get_logger()


class OptimizedOddsEngine:
    """Optimized V6 Odds Engine with production features."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.streamers: Dict[str, Any] = {}
        self.max_concurrency = max(1, int(self.config.get("max_concurrency", 4)))
        self.enable_cache = self.config.get("enable_cache", True)
        self.cache_ttl = int(self.config.get("cache_ttl", 30))
        
        # Rate limiting: 4 concurrent, 10 req/s per book
        self.semaphore = RateLimitedSemaphore(
            self.max_concurrency, 
            get_lunosoft_limiter()
        )
        
        self.metrics = get_metrics()
        self.cache = get_odds_cache()
        self._initialized_books: set = set()

    async def initialize_book(self, book_key: str) -> bool:
        """Lazy initialization of a single sportsbook."""
        if book_key in self._initialized_books:
            return True
            
        if book_key not in ALL_BOOK_STREAMERS:
            logger.error("Sportsbook not found in registry", book=book_key)
            return False

        try:
            streamer_cls = ALL_BOOK_STREAMERS[book_key]
            streamer = streamer_cls(book_key, self.config)
            connected = await streamer.connect()
            
            if connected:
                self.streamers[book_key] = streamer
                self._initialized_books.add(book_key)
                self.metrics.increment("books_initialized", tags={"book": book_key})
                logger.info("Initialized sportsbook", book=book_key)
                return True
            else:
                self.metrics.error("book_connection_failed", book_key)
                logger.warning("Failed to connect sportsbook", book=book_key)
                return False
                
        except Exception as exc:
            self.metrics.error("book_initialization_error", book_key)
            logger.error("Error initializing sportsbook", book=book_key, error=str(exc))
            return False

    async def initialize(self, books: Optional[List[str]] = None) -> None:
        """Initialize specified sportsbooks (lazy initialization)."""
        target_books = books or list(ALL_BOOK_STREAMERS.keys())
        logger.info("Initializing Optimized Odds Engine", target_books=len(target_books))
        
        # Initialize a few key books immediately, rest on-demand
        priority_books = ["draftkings", "fanduel", "betmgm"][:len(target_books)]
        init_tasks = []
        
        for book_key in target_books:
            if book_key in priority_books:
                init_tasks.append(self.initialize_book(book_key))
        
        if init_tasks:
            await asyncio.gather(*init_tasks, return_exceptions=True)
        
        logger.info("Optimized Odds Engine ready", 
                   initialized=len(self._initialized_books),
                   total=len(target_books))

    async def shutdown(self) -> None:
        """Shutdown all streamers."""
        logger.info("Shutting down Optimized Odds Engine")
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
        logger.info("Optimized Odds Engine shutdown complete")

    async def get_odds_by_book(
        self, book_key: str, sport: Optional[str] = None, use_cache: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Get odds from a specific sportsbook with caching."""
        use_cache = use_cache if use_cache is not None else self.enable_cache
        
        # Check cache first
        if use_cache:
            cache_key_str = cache_key("odds", book_key, sport or "all")
            cached_result = self.cache.get(cache_key_str)
            if cached_result:
                self.metrics.increment("cache_hits", tags={"type": "odds"})
                return cached_result
            else:
                self.metrics.increment("cache_misses", tags={"type": "odds"})

        # Lazy initialize if needed
        if book_key not in self._initialized_books:
            if not await self.initialize_book(book_key):
                return {"error": f"Failed to initialize sportsbook {book_key}"}

        streamer = self.streamers[book_key]
        
        async with TimedOperation("get_odds_by_book", {"book": book_key, "sport": sport or "all"}):
            try:
                self.metrics.book_request(book_key, "odds")
                
                raw_data = await streamer.fetch_data(sport)
                processed_data = await streamer.process_data(raw_data)
                
                # Extract traditional markets from processed data (includes field mapping)
                games_data = processed_data.get("games", [])
                
                result = {
                    "book": {
                        "key": book_key,
                        "id": streamer.BOOK_ID,
                        "name": streamer.BOOK_NAME,
                    },
                    "sport": sport,
                    "games": games_data,
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "player_props_count": len(processed_data.get("player_props", [])),
                    "cached": False,
                }
                result = self._apply_branding(result, book_key)
                
                # Cache the result
                if use_cache and "error" not in result:
                    self.cache.set(cache_key_str, result, self.cache_ttl)
                
                self.metrics.book_success(book_key, "odds")
                return result
                
            except Exception as exc:
                self.metrics.error("get_odds_by_book_error", book_key)
                logger.error("Error fetching odds from sportsbook", book=book_key, error=str(exc))
                return {"error": f"Failed to fetch odds from {book_key}: {str(exc)}"}

    async def get_all_odds(self, sport: Optional[str] = None, books: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get odds from multiple books with concurrency control."""
        target_books = books or list(self._initialized_books)
        
        if not target_books:
            # Initialize some books if none are ready
            await self.initialize()
            target_books = list(self._initialized_books)[:5]  # Limit to 5 for performance

        async with TimedOperation("get_all_odds", {"sport": sport or "all", "books": len(target_books)}):
            # Create tasks with semaphore control
            async def fetch_with_semaphore(book_key: str):
                async with self.semaphore:
                    return await self.get_odds_by_book(book_key, sport)
            
            tasks = []
            for book_key in target_books:
                task = asyncio.create_task(fetch_with_semaphore(book_key))
                tasks.append((book_key, task))

            results = {}
            successful = 0
            
            for book_key, task in tasks:
                try:
                    result = await task
                    results[book_key] = result
                    if "error" not in result:
                        successful += 1
                except Exception as exc:
                    self.metrics.error("get_all_odds_book_error", book_key)
                    logger.error("Error fetching odds", book=book_key, error=str(exc))
                    results[book_key] = {"error": str(exc)}

            self.metrics.gauge("odds_fetch_success_rate", successful / len(target_books) if target_books else 0)
            
            return {
                "books": results,
                "sport": sport,
                "total_books": len(results),
                "successful_books": successful,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

    def _apply_branding(self, payload: Any, book_key: Optional[str] = None) -> Any:
        """Ensure payload carries KashRock branding."""
        if isinstance(payload, list):
            return [self._apply_branding(item, book_key) for item in payload]

        if not isinstance(payload, dict):
            return payload

        inferred_book = book_key
        book_section = payload.get("book")
        if not inferred_book and isinstance(book_section, dict):
            inferred_book = book_section.get("key") or book_section.get("name")

        branding_dict: Dict[str, Any] = payload.get("branding", {}) if isinstance(payload.get("branding"), dict) else {}
        branding_dict["source"] = "kashrock"
        payload["source"] = "kashrock"

        if inferred_book:
            branding_dict["book_source"] = inferred_book
            payload.setdefault("book_source", inferred_book)

        payload["branding"] = branding_dict

        for key, value in list(payload.items()):
            if key == "branding":
                continue
            payload[key] = self._apply_branding(value, inferred_book)

        return payload

    async def get_main_sports_odds(self, books: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get odds for main sports with optimized caching."""
        main_sports = ["americanfootball_nfl", "basketball_nba", "baseball_mlb", "icehockey_nhl"]
        target_books = books or list(self._initialized_books)[:8]  # Limit for performance

        async with TimedOperation("get_main_sports_odds", {"books": len(target_books)}):
            results = {}
            
            # Process sports in parallel with rate limiting
            sport_tasks = []
            for sport in main_sports:
                task = asyncio.create_task(self.get_all_odds(sport, target_books))
                sport_tasks.append((sport, task))
            
            for sport, task in sport_tasks:
                try:
                    sport_result = await task
                    results[sport] = sport_result.get("books", {})
                except Exception as exc:
                    self.metrics.error("get_main_sports_sport_error")
                    logger.error("Error fetching sport odds", sport=sport, error=str(exc))
                    results[sport] = {}

            return {
                "sports": results,
                "target_books": target_books,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

    async def get_signal_snapshot(self, sport: str) -> Dict[str, Any]:
        """
        Fetch a minimal snapshot from a Signal Book to detect changes.
        Returns a dict containing the hash and the timestamp.
        """
        # Determine signal book based on sport (using major US books as reliable signals)
        signal_book = "draftkings"  # Default signal book
        if sport == "basketball_nba":
            signal_book = "draftkings"
        elif sport == "americanfootball_nfl":
            signal_book = "fanduel"
            
        # Ensure we have a valid key for the signal book
        if signal_book not in self._initialized_books:
            # Try to init, if fails fallback to any initialized book
            if not await self.initialize_book(signal_book):
                 available = list(self._initialized_books)
                 if available:
                     signal_book = available[0]
                 else:
                     return {"hash": None, "error": "No books available for signal"}

        logger.info("Fetching signal snapshot", sport=sport, signal_book=signal_book)

        try:
            # Fetch fresh data (bypass cache to get real current state)
            result = await self.get_odds_by_book(signal_book, sport, use_cache=False)
            
            if "error" in result:
                return {"hash": None, "error": result["error"]}

            games = result.get("games", [])
            
            # Create a minimal representation of the market state
            # We care about: Game IDs, Spreads, Totals, Moneylines
            minimal_state = []
            
            # sort games to ensure stable hash
            sorted_games = sorted(games, key=lambda x: x.get("game_id") or "")
            
            for game in sorted_games:
                game_state = {
                    "id": game.get("game_id"),
                    "status": game.get("status"),
                }
                
                # Extract main lines if available
                odds = game.get("odds", [])
                if odds:
                    # Sort odds to ensure stable hash
                    sorted_odds = sorted(
                        [o for o in odds if isinstance(o, dict)], 
                        key=lambda x: (x.get("market_type", ""), x.get("name", ""), x.get("price", 0))
                    )
                    # Simplified odds representation
                    simple_odds = []
                    for o in sorted_odds:
                        # Only include key fields that affect the line
                        simple_odds.append(f"{o.get('market_type')}:{o.get('name')}:{o.get('price')}:{o.get('point')}")
                    
                    game_state["lines"] = simple_odds
                
                minimal_state.append(game_state)
            
            # Generate SHA256 hash of this state
            state_str = json.dumps(minimal_state, sort_keys=True)
            snapshot_hash = hashlib.sha256(state_str.encode()).hexdigest()
            
            return {
                "hash": snapshot_hash,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "signal_book": signal_book,
                "games_count": len(games)
            }
            
        except Exception as exc:
            logger.error("Error generating signal snapshot", sport=sport, error=str(exc))
            return {"hash": None, "error": str(exc)}

    async def _extract_games_data(
        self, raw_data: Dict[str, Any], sport: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract and format traditional markets data."""
        games = []
        
        for sport_section in raw_data.get("sports", []):
            if sport and sport_section.get("sport") != sport:
                continue
                
            traditional_markets = sport_section.get("traditional_markets", [])
            if not isinstance(traditional_markets, list):
                continue

            for game_data in traditional_markets:
                if not isinstance(game_data, dict):
                    continue

                game = {
                    "game_id": game_data.get("GameID"),
                    "start_time": game_data.get("StartTime"),
                    "start_time_str": game_data.get("StartTimeStr"),
                    "status": game_data.get("Status"),
                    "away_team": {
                        "abbrev": game_data.get("AwayTeamAbbrev"),
                        "score": game_data.get("AwayScore"),
                        "color": game_data.get("AwayTeamColor"),
                        "color_light": game_data.get("AwayTeamColorLight"),
                    },
                    "home_team": {
                        "abbrev": game_data.get("HomeTeamAbbrev"),
                        "score": game_data.get("HomeScore"),
                        "color": game_data.get("HomeTeamColor"),
                        "color_light": game_data.get("HomeTeamColorLight"),
                    },
                }

                odds_data = game_data.get("Odds", [])
                if isinstance(odds_data, list):
                    game["odds"] = odds_data

                opening_odds = game_data.get("OpeningOdds", [])
                if isinstance(opening_odds, list):
                    game["opening_odds"] = opening_odds

                games.append(game)

        return games

    def get_available_books(self) -> List[Dict[str, Any]]:
        """Get list of available sportsbooks."""
        books = []
        for book_key in ALL_BOOK_STREAMERS.keys():
            books.append({
                "key": book_key,
                "initialized": book_key in self._initialized_books,
                "connected": book_key in self.streamers,
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

        return {
            "total_books": total_books,
            "healthy_books": healthy_books,
            "unhealthy_books": total_books - healthy_books,
            "book_status": results,
            "overall_healthy": healthy_books > 0,
            "cache_stats": cache_stats,
            "metrics": metrics_summary,
        }
