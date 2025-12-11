"""V6 Background Worker - Populates Redis cache using optimized engines."""

from __future__ import annotations

import asyncio
from collections import deque
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Set
from zoneinfo import ZoneInfo

import structlog

from v6.odds.optimized_engine import OptimizedOddsEngine
from v6.props.optimized_engine import OptimizedPropsEngine
from v6.common.redis_cache import RedisCacheManager
from v6.common.metrics import get_metrics
from v6.common.snapshot_builder import build_sport_snapshot
from streamers.ev_sources import create_ev_streamer, DEFAULT_EV_SOURCES
from v6.historical.database import get_historical_db

logger = structlog.get_logger()


# EV source sport support mapping (kept in sync with v6.api.cached)
EV_SOURCE_SPORTS_SUPPORT: Dict[str, List[str]] = {
    "walter": ["americanfootball_nfl", "basketball_nba"],
    "rotowire": [
        "americanfootball_nfl",
        "basketball_nba",
        "icehockey_nhl",
        "baseball_mlb",
        "soccer",
    ],
    # Proply supports multiple sports; enable for NFL and NBA initially
    "proply": ["americanfootball_nfl", "basketball_nba"],
    # Sharp Props (EV) - DFS/Pick'em books
    "sharp_props": [
        "americanfootball_nfl", 
        "americanfootball_ncaaf", 
        "basketball_nba", 
        "basketball_ncaab", 
        "icehockey_nhl", 
        "baseball_mlb"
    ],
}


class V6BackgroundWorker:
    """Background worker that populates Redis cache using V6 optimized engines."""
    
    def __init__(
        self,
        cache_manager: RedisCacheManager,
        active_books: List[str],
        poll_interval: float = 30.0,
        sports: Optional[List[str]] = None,
        sport_key_mapping: Optional[Dict[str, str]] = None
    ):
        """
        Initialize V6 background worker.
        
        Args:
            cache_manager: Redis cache manager
            active_books: List of sportsbooks to fetch from
            poll_interval: Polling interval in seconds
            sports: List of sports to process
            sport_key_mapping: Mapping for sport keys
        """
        self.cache_manager = cache_manager
        self.active_books = active_books
        self.poll_interval = poll_interval
        self.sports = sports or ["americanfootball_nfl", "basketball_nba", "baseball_mlb", "icehockey_nhl"]
        self.sport_key_mapping = sport_key_mapping or {}
        
        # Initialize V6 engines
        self.odds_engine = OptimizedOddsEngine({
            "max_concurrency": 16,
            "enable_cache": True,
            "cache_ttl": 30,
        })
        self.props_engine = OptimizedPropsEngine({
            "max_concurrency": 16,
            "enable_cache": True,
            "cache_ttl": 60,
        })
        
        # Historical database for persistent storage
        self.historical_db = get_historical_db()
        
        self.metrics = get_metrics()
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None
        self._tz = ZoneInfo("America/New_York")
        self._current_local_date = datetime.now(self._tz).date()
        
        # Rotational queue for sports
        self._sport_queue = deque(self.sports)
        
        logger.info("V6 background worker initialized", 
                   books=len(active_books), 
                   sports=len(self.sports),
                   poll_interval=poll_interval)
    
    async def start(self) -> None:
        """Start the background worker."""
        if self._running:
            logger.warning("V6 background worker already running")
            return
        
        logger.info("Starting V6 background worker...")
        
        # Initialize engines
        await self.odds_engine.initialize(self.active_books)
        await self.props_engine.initialize(self.active_books)
        
        self._running = True
        self._worker_task = asyncio.create_task(self._worker_loop())
        
        logger.info("V6 background worker started")
    
    def _apply_branding(self, payload: Any, book_key: Optional[str] = None) -> Any:
        """Ensure payload (and nested items) carry KashRock branding."""
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
            if key == "book" and isinstance(value, dict):
                payload[key] = self._apply_branding(value, inferred_book or book_key)
            else:
                payload[key] = self._apply_branding(value, inferred_book)

        return payload
    
    async def stop(self) -> None:
        """Stop the background worker."""
        if not self._running:
            return
        
        logger.info("Stopping V6 background worker...")
        self._running = False
        
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        
        # Shutdown engines
        await self.odds_engine.shutdown()
        await self.props_engine.shutdown()
        
        logger.info("V6 background worker stopped")
    
    async def _worker_loop(self) -> None:
        """Main worker loop with rotational scheduling."""
        logger.info("V6 worker loop started (Rotational Mode)")
        
        while self._running:
            try:
                await self._maybe_rotate_daily()
                
                # Check next sport in rotation
                if self._sport_queue:
                    sport = self._sport_queue[0]
                    self._sport_queue.rotate(-1)  # Move to end
                    
                    await self._process_sport(sport)
                
                # Wait for next heartbeat
                await asyncio.sleep(self.poll_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Error in worker loop", error=str(exc), exc_info=True)
                self.metrics.increment("worker_loop_errors")
                await asyncio.sleep(min(self.poll_interval, 60))  
    
    async def _maybe_rotate_daily(self) -> None:
        """Rotate cached data at local midnight while preserving intraday state."""
        try:
            now_local = datetime.now(self._tz).date()
            if self._current_local_date == now_local:
                return

            logger.info(
                "Detected new trading day, rotating V6 cache",
                previous_date=str(self._current_local_date),
                current_date=str(now_local),
            )

            prefix = getattr(self.cache_manager, "key_prefix", "v6")
            patterns = [
                f"{prefix}:event:*",
                f"{prefix}:sport:*:events",
                f"{prefix}:lookup:*",
                f"{prefix}:book:*",
            ]

            for pattern in patterns:
                await self.cache_manager.clear_pattern(pattern)

            self._current_local_date = now_local

        except Exception as exc:
            logger.error("Failed during daily cache rotation", error=str(exc), exc_info=True)

    async def _write_raw_stage(
        self,
        sport: str,
        odds_data: Dict[str, Any],
        props_data: Optional[Dict[str, Any]],
        ev_data: Optional[Dict[str, Any]],
        stage_label: str,
    ) -> None:
        try:
            payload: Dict[str, Any] = {
                "sport": sport,
                "stage": stage_label,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "odds": odds_data,
            }
            if props_data is not None:
                payload["props"] = props_data
            if ev_data is not None:
                payload["ev"] = ev_data

            await self.cache_manager.store_feed_stage(
                sport,
                "raw",
                payload,
                ttl=int(self.poll_interval * 2),
            )

            if props_data and isinstance(props_data, dict):
                books = props_data.get("books") or {}
                total_books = len(books)
                total_props = sum(
                    int(book_payload.get("total_props") or len(book_payload.get("props") or []))
                    for book_payload in books.values()
                    if isinstance(book_payload, dict) and "error" not in book_payload
                )

                logger.info(
                    "Storing per-book props in Redis",
                    sport=sport,
                    stage=stage_label,
                    total_books=total_books,
                    total_props=total_props,
                )

                for book_key, book_payload in books.items():
                    if isinstance(book_payload, dict) and "error" not in book_payload:
                        await self.cache_manager.store_book_data(
                            book_key,
                            sport,
                            "props",
                            book_payload,
                            ttl=None,
                        )
        except Exception as exc:
            logger.error(
                "Failed to write raw feed stage",
                sport=sport,
                stage=stage_label,
                error=str(exc),
                exc_info=True,
            )

    async def _check_for_updates(self, sport: str) -> bool:
        """
        Check if data has changed by comparing minimal snapshot hashes.
        Returns True if update is needed.
        """
        try:
            snapshot = await self.odds_engine.get_signal_snapshot(sport)
            new_hash = snapshot.get("hash")
            
            if not new_hash:
                logger.warning("Could not generate hash, forcing update", sport=sport)
                return True
                
            old_hash = await self.cache_manager.get_hash(sport)
            
            if new_hash != old_hash:
                logger.info("Change detected", sport=sport, old_hash=old_hash, new_hash=new_hash)
                # Update hash immediately to prevent other workers from picking it up? 
                # Better to update after full fetch, or optimistically here.
                # Here we return True and update hash at the end of successful processing.
                return True
            else:
                logger.debug("No change detected", sport=sport, hash=new_hash)
                return False
                
        except Exception as exc:
            logger.error("Error checking for updates", sport=sport, error=str(exc))
            return True # Fail open -> update

    async def _process_sport(self, sport: str) -> None:
        """Process odds and props if changes detected."""
        
        
    # 1. Check for updates first
    if not await self._check_for_updates(sport):
        logger.info("Skipping full refresh (no changes)", sport=sport)
        return
    
        sport_start = datetime.now(timezone.utc)
        
        logger.info("=== STARTING SPORT PROCESSING (Active Update) ===", sport=sport, worker_running=self._running)
        
        # Fetch odds, props, and EV data concurrently to reduce cycle latency
        odds_task = asyncio.create_task(self.odds_engine.get_all_odds(sport, self.active_books))
        props_task = asyncio.create_task(self.props_engine.get_all_props(sport, self.active_books))
        ev_task = asyncio.create_task(self._fetch_ev_data(sport))
        
        odds_data = await odds_task
        if isinstance(odds_data, Exception):
            logger.error("Failed to fetch odds data", sport=sport, error=str(odds_data))
            odds_data = {"books": {}}
        
        # Store odds-only payload immediately so API can begin serving data
        await self._write_raw_stage(
            sport,
            odds_data=odds_data,
            props_data=None,
            ev_data=None,
            stage_label="odds_only",
        )

        props_result, ev_result = await asyncio.gather(
            props_task, ev_task, return_exceptions=True
        )
        
        props_data = props_result
        ev_data = ev_result
        
        if isinstance(props_data, Exception):
            logger.error("Failed to fetch props data", sport=sport, error=str(props_data))
            props_data = {"books": {}}
        if isinstance(ev_data, Exception):
            logger.error("Failed to fetch EV data", sport=sport, error=str(ev_data))
            ev_data = None
        
        # Update raw payload once props/EV data finish
        await self._write_raw_stage(
            sport,
            odds_data=odds_data,
            props_data=props_data,
            ev_data=ev_data,
            stage_label="odds_props",
        )

        # Convert to canonical envelopes and merge
        canonical_events = self._create_canonical_events(sport, odds_data, props_data, ev_data)

        await self.cache_manager.store_feed_stage(
            sport,
            "normalized",
            {
                "sport": sport,
                "events": canonical_events,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            },
            ttl=self.poll_interval * 2,
        )
        
        # Store in Redis cache
        await self._store_events_in_cache(sport, canonical_events)
        
        # 2. Update the hash now that we have updated the cache
        # Re-calculate hash to be sure (or just use the one that triggered it)
        # Using the one from start allows for race conditions if it changed again during fetch.
        # Safer to just get a fresh snapshot hash or trust the trigger?
        # Let's re-fetch the snapshot hash quickly to stamp it current.
        # Let's re-fetch the snapshot hash quickly to stamp it current.
        final_snapshot = await self.odds_engine.get_signal_snapshot(sport)
        if final_snapshot.get("hash"):
             await self.cache_manager.set_hash(sport, final_snapshot.get("hash"))

        sport_time = (datetime.now(timezone.utc) - sport_start).total_seconds()
        self.metrics.timing("sport_processing_time", sport_time, tags={"sport": sport})
        
        logger.info("Completed sport processing", 
                   sport=sport,
                   events=len(canonical_events),
                   duration_seconds=sport_time)
    
    def _create_canonical_events(
        self, 
        sport: str,
        odds_data: Dict[str, Any], 
        props_data: Dict[str, Any],
        ev_data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Create canonical events from V6 engine data."""
        canonical_events = []
        
        # Extract games from odds data
        games_by_book = {}
        for book_key, book_data in odds_data.get("books", {}).items():
            if "error" not in book_data:
                games_by_book[book_key] = book_data.get("games", [])
        
        # Extract props from props data
        props_by_book = {}
        for book_key, book_data in props_data.get("books", {}).items():
            if "error" not in book_data:
                props_by_book[book_key] = book_data.get("props", [])
        
        # Group by game (simplified - in production would use proper entity resolution)
        game_groups = self._group_by_game(games_by_book, props_by_book, ev_data)
        
        # Create canonical events for each game
        for game_key, game_data in game_groups.items():
            try:
                canonical_event = self._build_canonical_event(sport, game_key, game_data)
                if canonical_event:
                    canonical_events.append(canonical_event)
            except Exception as exc:
                logger.error("Error building canonical event", game_key=game_key, error=str(exc))
        
        return canonical_events
    
    async def _fetch_ev_data(self, sport: str) -> Dict[str, Any]:
        """Fetch EV data from all KashRock EV sources in parallel."""
        ev_data: Dict[str, Any] = {"sources": {}}

        async def fetch_source(source_name: str) -> None:
            try:
                logger.info("Fetching EV data", source=source_name, sport=sport)

                # Create EV streamer instance
                ev_streamer = create_ev_streamer(source_name, {})

                # Connect if needed
                if not ev_streamer.is_connected:
                    await ev_streamer.connect()

                try:
                    # Fetch data
                    source_data = await ev_streamer.fetch_data(sport=sport)

                    # Process data
                    processed_data = await ev_streamer.process_data(source_data)

                    # Extract player props and format for caching
                    player_props = processed_data.get("player_props", [])

                    ev_data["sources"][source_name] = {
                        "props": player_props,
                        "game_projections": processed_data.get("game_projections", []),
                        "error": None,
                    }

                    logger.info(
                        "Successfully fetched EV data",
                        source=source_name,
                        sport=sport,
                        props_count=len(player_props),
                    )
                finally:
                    await ev_streamer.disconnect()

            except Exception as e:
                logger.error(
                    "Failed to fetch EV data",
                    source=source_name,
                    sport=sport,
                    error=str(e),
                )

                ev_data["sources"][source_name] = {
                    "props": [],
                    "game_projections": [],
                    "error": str(e),
                }

        # Only run EV sources that support this sport
        supported_sources = [
            source_name
            for source_name in DEFAULT_EV_SOURCES
            if sport in EV_SOURCE_SPORTS_SUPPORT.get(source_name, [])
        ]

        if not supported_sources:
            logger.info("No EV sources configured for sport", sport=sport)
            return ev_data

        tasks = [asyncio.create_task(fetch_source(source_name)) for source_name in supported_sources]

        if tasks:
            await asyncio.gather(*tasks)

        return ev_data
    
    def _group_by_game(self, games_by_book: Dict[str, List], props_by_book: Dict[str, List], ev_data: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, Any]]:
        """Group odds and props by game using game IDs from V6 optimized engines."""
        game_groups = {}
        
        # Group odds by game using game_id from V6 engines
        for book_key, games in games_by_book.items():
            for game in games:
                game_id = game.get("game_id")
                if not game_id:
                    # Fallback: create ID from teams and time
                    game_id = f"{game.get('home_team', '')}_{game.get('away_team', '')}_{game.get('start_time', '')}"
                
                if game_id not in game_groups:
                    game_groups[game_id] = {
                        "game_info": game,
                        "odds_by_book": {},
                        "props_by_book": {}
                    }
                
                game_groups[game_id]["odds_by_book"][book_key] = game
        
        # Group props by game using game_id from V6 engines
        for book_key, props in props_by_book.items():
            for prop in props:
                game_id = prop.get("game_id")
                if not game_id:
                    # Fallback: create ID from teams and time
                    game_id = f"{prop.get('home_team', '')}_{prop.get('away_team', '')}_{prop.get('game_start', '')}"
                
                if game_id not in game_groups:
                    # Create game group if it doesn't exist (props-only game)
                    game_groups[game_id] = {
                        "game_info": {
                            "game_id": game_id,
                            "home_team": prop.get("home_team"),
                            "away_team": prop.get("away_team"),
                            "start_time": prop.get("game_start"),
                        },
                        "odds_by_book": {},
                        "props_by_book": {}
                    }
                
                # Categorize markets based on market_type
                market_type = prop.get("market_type", "").lower()
                if market_type in ["spread", "total", "moneyline"]:
                    # Traditional markets go to odds_by_book
                    if book_key not in game_groups[game_id]["odds_by_book"]:
                        game_groups[game_id]["odds_by_book"][book_key] = []
                    game_groups[game_id]["odds_by_book"][book_key].append(prop)
                else:
                    # Actual player props go to props_by_book
                    if book_key not in game_groups[game_id]["props_by_book"]:
                        game_groups[game_id]["props_by_book"][book_key] = []
                    game_groups[game_id]["props_by_book"][book_key].append(prop)
        
        # Add EV data to props_by_book structure
        if ev_data and "sources" in ev_data:
            for source_name, source_info in ev_data["sources"].items():
                ev_props = source_info.get("props", [])
                if ev_props:
                    for prop in ev_props:
                        # Skip EV props without valid team data
                        home_team = prop.get("home_team")
                        away_team = prop.get("away_team")
                        
                        # Only include EV props if they have valid team information
                        if not home_team or not away_team or home_team == "Unknown" or away_team == "Unknown":
                            logger.debug(
                                "Skipping EV prop without valid team data",
                                source=source_name,
                                player=prop.get("player_name"),
                                home_team=home_team,
                                away_team=away_team
                            )
                            continue
                        
                        # Use event_id as game_id for EV props
                        game_id = prop.get("event_id") or prop.get("game_id")
                        if not game_id:
                            # Create fallback game ID from teams
                            game_id = f"{home_team}_{away_team}_{prop.get('game_start', '')}"
                        
                        if game_id not in game_groups:
                            # Create game group for EV-only games
                            game_groups[game_id] = {
                                "game_info": {
                                    "game_id": game_id,
                                    "home_team": home_team,
                                    "away_team": away_team,
                                    "start_time": prop.get("game_start", ""),
                                },
                                "odds_by_book": {},
                                "props_by_book": {}
                            }
                        
                        # Add EV prop under source name as book key
                        if source_name not in game_groups[game_id]["props_by_book"]:
                            game_groups[game_id]["props_by_book"][source_name] = []
                        game_groups[game_id]["props_by_book"][source_name].append(prop)

        
        logger.info("Grouped data by game", 
                   total_games=len(game_groups),
                   books_with_odds=len(games_by_book),
                   books_with_props=len(props_by_book),
                   ev_sources=len(ev_data.get("sources", {})) if ev_data else 0)
        
        return game_groups
    
    def _build_canonical_event(self, sport: str, game_key: str, game_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build a canonical event from grouped data."""
        try:
            game_info = game_data.get("game_info", {})
            odds_by_book = game_data.get("odds_by_book", {})
            props_by_book = game_data.get("props_by_book", {})
            
            # Extract team names with defensive type checking
            home_team_raw = game_info.get("home_team", "")
            away_team_raw = game_info.get("away_team", "")
            start_time = game_info.get("start_time", "")
            
            # Handle case where team data might be dicts
            if isinstance(home_team_raw, dict):
                home_team = home_team_raw.get("name") or home_team_raw.get("team_name") or str(home_team_raw)
            else:
                home_team = str(home_team_raw) if home_team_raw else ""
            
            if isinstance(away_team_raw, dict):
                away_team = away_team_raw.get("name") or away_team_raw.get("team_name") or str(away_team_raw)
            else:
                away_team = str(away_team_raw) if away_team_raw else ""
            
            if not home_team or not away_team:
                logger.warning("Skipping event without teams", game_key=game_key, home_team=home_team_raw, away_team=away_team_raw)
                return None
            
            canonical_event_id = self._generate_canonical_event_id(sport, home_team, away_team, start_time)
            
            # Build markets
            markets = self._build_markets(odds_by_book, props_by_book)
            
            # Build books data
            books = self._build_books_data(odds_by_book, props_by_book)
            
            # Build props list
            props_list = self._build_props_list(props_by_book)
            
            # Enrich props with event information
            for prop in props_list:
                # Set team from player_team if missing
                if not prop.get("team") and prop.get("player_team"):
                    prop["team"] = prop["player_team"]
                
                # Set opponent based on team and event teams
                if not prop.get("opponent") and prop.get("team"):
                    if prop["team"] == home_team:
                        prop["opponent"] = away_team
                    elif prop["team"] == away_team:
                        prop["opponent"] = home_team
                
                # Set event time if missing
                if not prop.get("event_time"):
                    prop["event_time"] = start_time
                    
                # Set event teams if missing
                if not prop.get("home_team"):
                    prop["home_team"] = home_team
                if not prop.get("away_team"):
                    prop["away_team"] = away_team
            
            # Build provenance
            provenance = {
                "sources": list(set(list(odds_by_book.keys()) + list(props_by_book.keys()))),
                "source_count": len(set(list(odds_by_book.keys()) + list(props_by_book.keys()))),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "engine_version": "v6"
            }
            
            canonical_event = {
                "canonical_event_id": canonical_event_id,
                "sport": sport,
                "home_team": home_team,
                "away_team": away_team,
                "commence_time": start_time,
                "markets": markets,
                "books": books,
                "props": props_list,
                "provenance": provenance,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return canonical_event
            
        except Exception as exc:
            logger.error("Error building canonical event", game_key=game_key, error=str(exc))
            return None
    
    def _generate_canonical_event_id(self, sport: str, home_team: str, away_team: str, start_time: str) -> str:
        """Generate canonical event ID."""
        from utils.canonical_id_generator import generate_canonical_event_id
        return generate_canonical_event_id(sport, home_team, away_team, start_time)
    
    def _build_markets(self, odds_by_book: Dict[str, Any], props_by_book: Dict[str, Any]) -> Dict[str, Any]:
        """Build merged markets from all books."""
        markets = {}
        
        # Process traditional markets
        all_odds = []
        for book_key, game_data in odds_by_book.items():
            book_odds = game_data.get("odds", [])
            if isinstance(book_odds, list):
                for odds in book_odds:
                    odds["source"] = book_key
                    all_odds.append(odds)
        
        # Group by market type
        markets_by_type = {}
        for odds in all_odds:
            market_type = odds.get("market_type", "h2h")
            if market_type not in markets_by_type:
                markets_by_type[market_type] = {"runners": [], "sources": []}
            markets_by_type[market_type]["runners"].append(odds)
            markets_by_type[market_type]["sources"].append(odds.get("source"))
        
        # Convert to list format
        markets_list = []
        for market_type, market_data in markets_by_type.items():
            market_data["key"] = market_type
            markets_list.append(market_data)
        
        return markets_list
    
    def _build_books_data(self, odds_by_book: Dict[str, Any], props_by_book: Dict[str, Any]) -> Dict[str, Any]:
        """Build per-book data."""
        books = {}
        
        # Add odds data
        for book_key, game_data in odds_by_book.items():
            books[book_key] = {
                "odds": game_data.get("odds", []),
                "has_odds": True,
                "has_props": False,
            }
        
        # Add props data
        for book_key, props in props_by_book.items():
            if book_key not in books:
                books[book_key] = {"has_odds": False, "has_props": True}
            books[book_key]["props"] = props
            books[book_key]["has_props"] = True
        
        return books
    
    def _build_props_list(self, props_by_book: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build consolidated props list."""
        all_props = []
        
        for book_key, props in props_by_book.items():
            for prop in props:
                # Skip EV props - they should only be accessed via EV endpoints
                if book_key in ["walter", "rotowire", "proply"]:
                    continue
                    
                prop_copy = dict(prop)
                # Regular prop - set source to book_key if not already set
                if "source" not in prop_copy or not prop_copy["source"]:
                    prop_copy["source"] = book_key
                all_props.append(prop_copy)
        
        return all_props
    
    async def _store_events_in_cache(self, sport: str, canonical_events: List[Dict[str, Any]]) -> None:
        """Store canonical events in Redis cache AND historical database."""
        try:
            logger.info("Starting data storage", sport=sport, events_to_store=len(canonical_events))
            
            # Store each event in Redis cache
            event_ids = []
            for i, event in enumerate(canonical_events):
                event_id = event.get("canonical_event_id")
                logger.info(f"Processing event {i+1}/{len(canonical_events)}", event_id=event_id, has_id=bool(event_id))
                
                if event_id:
                    # Store in Redis cache (keep for full trading day; rotation handled separately)
                    success = await self.cache_manager.store_event(event_id, event, ttl=None)
                    if success:
                        event_ids.append(event_id)
                        logger.info(f"Successfully stored event {i+1} in Redis", event_id=event_id)

                        # Store lookup key for fast team-based queries (home/away -> canonical_event_id)
                        home_team = event.get("home_team")
                        away_team = event.get("away_team")
                        if home_team and away_team:
                            lookup_ok = await self.cache_manager.store_lookup_key(
                                sport,
                                home_team,
                                away_team,
                                event_id,
                                ttl=None,
                            )
                            if not lookup_ok:
                                logger.error(
                                    "Failed to store lookup key for event",
                                    sport=sport,
                                    event_id=event_id,
                                    home_team=home_team,
                                    away_team=away_team,
                                )
                    else:
                        logger.error(f"Failed to store event {i+1} in Redis", event_id=event_id)
                    
                    # Store in historical database (persistent)
                    await self._store_event_historical(sport, event)
                else:
                    logger.warning(f"Skipping event {i+1} - no canonical_event_id", event_keys=list(event.keys()))
            
            # Store sport events list in Redis (no TTL; cleared during daily rotation)
            if event_ids:
                logger.info("Storing sport events list", sport=sport, event_count=len(event_ids))
                success = await self.cache_manager.store_sport_events(sport, event_ids, ttl=None)
                if success:
                    logger.info("Successfully stored sport events list", sport=sport, event_count=len(event_ids))
                else:
                    logger.error("Failed to store sport events list", sport=sport)
            else:
                logger.warning("No events to store for sport", sport=sport)

            snapshot = build_sport_snapshot(sport, canonical_events)
            await self.cache_manager.store_sport_snapshot(sport, snapshot, ttl=None)
            
            logger.info("Completed data storage", sport=sport, events_stored=len(event_ids))
            
        except Exception as exc:
            logger.error("Failed to store events", sport=sport, error=str(exc), exc_info=True)
        
        # Store metrics after cache storage
        metrics_data = {
            "last_update": datetime.now(timezone.utc).isoformat(),
            "events_processed": len(canonical_events),
            "sport": sport,
            "active_books": len(self.active_books),
        }
        await self.cache_manager.store_metrics(metrics_data, ttl=300)
        
        logger.info("Stored events in cache", 
                   sport=sport,
                   events=len(canonical_events),
                   duration_seconds=0)
    
    async def _store_event_historical(self, sport: str, event: Dict[str, Any]) -> None:
        """Store event data in historical database for long-term analysis."""
        try:
            if not self.historical_db:
                self.historical_db = await get_historical_db()
            
            event_id = event.get("canonical_event_id")
            home_team = event.get("home_team")
            away_team = event.get("away_team")
            commence_time = event.get("commence_time")
            
            # Store traditional markets (odds)
            odds_by_book = event.get("odds_by_book", {})
            for book_name, game_data in odds_by_book.items():
                if isinstance(game_data, dict):
                    odds_list = game_data.get("odds", [])
                    for odd in odds_list:
                        market_type = odd.get("market_type", "unknown")
                        await self.historical_db.store_odds_snapshot(
                            sport=sport,
                            event_id=event_id,
                            home_team=home_team,
                            away_team=away_team,
                            book_name=book_name,
                            market_type=market_type,
                            market_data=odd,
                            commence_time=commence_time,
                            book_id=odd.get("sportsbook_id")
                        )
            
            # Store player props
            props_by_book = event.get("props_by_book", {})
            for book_name, props_list in props_by_book.items():
                if isinstance(props_list, list):
                    for prop in props_list:
                        await self.historical_db.store_player_prop_snapshot(
                            sport=sport,
                            event_id=event_id,
                            player_name=prop.get("player_name", ""),
                            stat_type=prop.get("stat_type_name") or prop.get("market_type", ""),
                            book_name=book_name,
                            prop_data=prop,
                            game_id=prop.get("game_id"),
                            player_team=prop.get("player_team"),
                            stat_value=prop.get("value"),
                            direction=prop.get("direction"),
                            odds=prop.get("over_odds") or prop.get("under_odds"),
                            book_id=prop.get("book_id"),
                            sportsbook_id=prop.get("sportsbook_id")
                        )
            
            logger.debug("Stored event in historical database", event_id=event_id)
            
        except Exception as e:
            logger.error("Failed to store event in historical database", 
                        event_id=event.get("canonical_event_id"),
                        error=str(e))
    
    async def get_worker_status(self) -> Dict[str, Any]:
        """Get worker status."""
        return {
            "running": self._running,
            "active_books": self.active_books,
            "sports": self.sports,
            "poll_interval": self.poll_interval,
            "odds_engine_initialized": len(self.odds_engine._initialized_books),
            "props_engine_initialized": len(self.props_engine._initialized_books),
            "cache_connected": self.cache_manager._connected,
        }


# Global worker instance
_worker: Optional[V6BackgroundWorker] = None


async def start_background_worker(
    cache_manager: RedisCacheManager,
    active_books: List[str],
    poll_interval: float = 30.0,
    sports: Optional[List[str]] = None,
    sport_key_mapping: Optional[Dict[str, str]] = None
) -> V6BackgroundWorker:
    """Start the V6 background worker."""
    global _worker
    
    if _worker is not None:
        await _worker.stop()
    
    _worker = V6BackgroundWorker(
        cache_manager=cache_manager,
        active_books=active_books,
        poll_interval=poll_interval,
        sports=sports,
        sport_key_mapping=sport_key_mapping
    )
    
    await _worker.start()
    return _worker


async def get_background_worker() -> Optional[V6BackgroundWorker]:
    """Get the global background worker instance."""
    return _worker


async def stop_background_worker():
    """Stop the V6 background worker."""
    global _worker
    if _worker:
        await _worker.stop()
        _worker = None
