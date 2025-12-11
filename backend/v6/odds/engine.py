"""V6 Odds Engine - Per-book odds aggregation using Lunosoft streamers."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog

from streamers.lunosoft_books import LUNOSOFT_BOOK_STREAMERS
from streamers.sharp_odds import SHARP_ODDS_STREAMERS

# Combine all odds sources
ALL_BOOK_STREAMERS = {**LUNOSOFT_BOOK_STREAMERS, **SHARP_ODDS_STREAMERS}

logger = structlog.get_logger()


class OddsEngine:
    """V6 Odds Engine that aggregates odds by sportsbook."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.streamers: Dict[str, Any] = {}
        self.max_concurrency = max(1, int(self.config.get("max_concurrency", 32)))
        self._semaphore: Optional[asyncio.Semaphore] = None

    async def initialize(self, books: Optional[List[str]] = None) -> None:
        """Initialize all sportsbook streamers concurrently."""
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrency)

        target_books = ALL_BOOK_STREAMERS
        if books:
            # Filter to only requested books that exist in our registry
            target_books = {k: v for k, v in ALL_BOOK_STREAMERS.items() if k in books}

        logger.info("Initializing V6 Odds Engine", books=len(target_books))

        async def init_book(book_key: str, streamer_cls: Any) -> None:
            try:
                streamer = streamer_cls(book_key, self.config)
                # Use a small timeout for connection to prevent hanging
                try:
                    connected = await asyncio.wait_for(streamer.connect(), timeout=10.0)
                except asyncio.TimeoutError:
                    logger.warning("Timeout connecting sportsbook", book=book_key)
                    return

                if connected:
                    self.streamers[book_key] = streamer
                    logger.info("Connected sportsbook", book=book_key)
                else:
                    logger.warning("Failed to connect sportsbook", book=book_key)
            except Exception as exc:
                logger.error("Error initializing sportsbook", book=book_key, error=str(exc))

        # Initialize all books concurrently
        tasks = [init_book(k, v) for k, v in target_books.items()]
        if tasks:
            await asyncio.gather(*tasks)

        logger.info("V6 Odds Engine initialized", connected_books=len(self.streamers))

    async def shutdown(self) -> None:
        """Shutdown all streamers."""
        logger.info("Shutting down V6 Odds Engine")
        tasks = []
        for book_key, streamer in self.streamers.items():
            try:
                tasks.append(streamer.disconnect())
            except Exception as exc:
                logger.error("Error disconnecting sportsbook", book=book_key, error=str(exc))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self.streamers.clear()
        logger.info("V6 Odds Engine shutdown complete")

    async def get_odds_by_book(
        self, book_key: str, sport: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get odds from a specific sportsbook."""
        if book_key not in self.streamers:
            logger.error("Sportsbook not available", book=book_key)
            return {"error": f"Sportsbook {book_key} not available"}

        streamer = self.streamers[book_key]
        try:
            raw_data = await streamer.fetch_data(sport)
            processed_data = await streamer.process_data(raw_data)
            
            # Use processed traditional markets (games) only, not player props
            games_data = processed_data.get("games", [])
            main_markets_count = len(games_data)
            
            return {
                "book": {
                    "id": streamer.BOOK_ID,
                    "name": streamer.BOOK_NAME,
                },
                "sport": sport,
                "games": games_data,
                "main_markets_count": main_markets_count,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            logger.error("Error fetching odds from sportsbook", book=book_key, error=str(exc))
            return {"error": f"Failed to fetch odds from {book_key}: {str(exc)}"}

    async def get_all_odds(self, sport: Optional[str] = None) -> Dict[str, Any]:
        """Get odds from all available sportsbooks."""
        if not self.streamers:
            await self.initialize()

        tasks = []
        for book_key in self.streamers.keys():
            async with (self._semaphore or asyncio.Semaphore(self.max_concurrency)):
                task = asyncio.create_task(self.get_odds_by_book(book_key, sport))
                tasks.append((book_key, task))

        results = {}
        for book_key, task in tasks:
            try:
                result = await task
                results[book_key] = result
            except Exception as exc:
                logger.error("Error fetching odds", book=book_key, error=str(exc))
                results[book_key] = {"error": str(exc)}

        return {
            "books": results,
            "sport": sport,
            "total_books": len(results),
            "successful_books": len([r for r in results.values() if "error" not in r]),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_main_sports_odds(self, books: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get odds for main sports (NFL, NBA, MLB, NHL) from specified books."""
        main_sports = ["americanfootball_nfl", "basketball_nba", "baseball_mlb", "icehockey_nhl"]
        target_books = books or list(self.streamers.keys())[:10]  # Limit to 10 books by default

        results = {}
        for sport in main_sports:
            sport_results = {}
            for book_key in target_books:
                if book_key in self.streamers:
                    try:
                        odds_data = await self.get_odds_by_book(book_key, sport)
                        sport_results[book_key] = odds_data
                    except Exception as exc:
                        logger.error("Error fetching sport odds", sport=sport, book=book_key, error=str(exc))
                        sport_results[book_key] = {"error": str(exc)}
            results[sport] = sport_results

        return {
            "sports": results,
            "target_books": target_books,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _extract_games_data(
        self, raw_data: Dict[str, Any], sport: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract and format traditional markets data from raw response."""
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

                # Extract basic game info
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

                # Extract odds data
                odds_data = game_data.get("Odds", [])
                if isinstance(odds_data, list):
                    game["odds"] = odds_data

                # Extract opening odds for line history
                opening_odds = game_data.get("OpeningOdds", [])
                if isinstance(opening_odds, list):
                    game["opening_odds"] = opening_odds

                games.append(game)

        return games

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

    async def get_signal_snapshot(self, sport: str) -> Dict[str, Any]:
        """
        Get a lightweight snapshot to check for updates.
        Currently uses a time-based hash (30s window) as we lack a global ETag from providers.
        """
        import time
        import hashlib
        
        # Change hash every 30 seconds to allow updates but prevent excessive polling
        period = int(time.time() / 30)
        s = f"{sport}:{period}"
        h = hashlib.md5(s.encode()).hexdigest()
        
        return {"hash": h, "timestamp": time.time()}

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
