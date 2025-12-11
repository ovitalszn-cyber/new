"""Standalone runner for the V6 background worker.

Use this when you need the cache-refresh worker to stay alive even if the API
process restarts (e.g., during deploys or uvicorn reloads). Run with:

    python workers/v6_worker_service.py

Environment variables:
    V6_WORKER_POLL_INTERVAL   -> seconds between refresh cycles (default: 15)
    V6_WORKER_SPORTS          -> comma-separated sports list
    V6_WORKER_BOOKS           -> comma-separated book keys (default: Lunosoft set)
"""

from __future__ import annotations

import asyncio
import os
import signal
from typing import List, Optional

import structlog

from streamers.lunosoft_books import LUNOSOFT_BOOK_STREAMERS
from streamers.sharp_odds import SHARP_ODDS_STREAMERS
from v6.background_worker import start_background_worker, stop_background_worker
from v6.common.redis_cache import get_cache_manager, shutdown_cache_manager
from v6.common.redis_pool import get_redis_pool, shutdown_redis_pool

logger = structlog.get_logger()


class WorkerService:
    """Coordinates lifecycle for a long-lived V6 background worker."""

    def __init__(
        self,
        poll_interval: float,
        sports: List[str],
        books: List[str],
    ):
        self.poll_interval = poll_interval
        self.sports = sports
        self.books = books
        self._stop_event = asyncio.Event()
        self._started = False

    def _install_signal_handlers(self) -> None:
        loop = asyncio.get_running_loop()
        for signame in ("SIGINT", "SIGTERM"):
            if hasattr(signal, signame):
                loop.add_signal_handler(
                    getattr(signal, signame),
                    lambda s=signame: self.request_shutdown(s),
                )

    def request_shutdown(self, signal_name: str) -> None:
        if not self._stop_event.is_set():
            logger.info("Worker shutdown requested", signal=signal_name)
            self._stop_event.set()

    async def run(self) -> None:
        if self._started:
            logger.warning("Worker service already running")
            return

        self._install_signal_handlers()
        self._started = True

        logger.info(
            "Starting standalone V6 worker",
            poll_interval=self.poll_interval,
            sports=self.sports,
            book_count=len(self.books),
        )

        # Bootstrap shared resources
        redis_pool = await get_redis_pool()
        if not redis_pool.is_connected:
            raise RuntimeError("Unable to connect to Redis")

        cache_manager = await get_cache_manager()
        if not cache_manager._connected:
            raise RuntimeError("Unable to initialize Redis cache manager")

        await start_background_worker(
            cache_manager=cache_manager,
            active_books=self.books,
            poll_interval=self.poll_interval,
            sports=self.sports,
        )

        logger.info("V6 worker is live and refreshing cache")
        await self._stop_event.wait()

        logger.info("Stopping standalone V6 worker")
        await stop_background_worker()
        await shutdown_cache_manager()
        await shutdown_redis_pool()
        logger.info("Standalone V6 worker stopped cleanly")


def _parse_env_list(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


async def main():
    poll_interval = float(os.getenv("V6_WORKER_POLL_INTERVAL", "15"))
    sports = _parse_env_list(os.getenv("V6_WORKER_SPORTS"))
    if not sports:
        sports = ["americanfootball_nfl", "basketball_nba", "baseball_mlb", "icehockey_nhl"]

    books = _parse_env_list(os.getenv("V6_WORKER_BOOKS"))
    if not books:
        books = list(LUNOSOFT_BOOK_STREAMERS.keys()) + list(SHARP_ODDS_STREAMERS.keys())

    service = WorkerService(
        poll_interval=poll_interval,
        sports=sports,
        books=books,
    )
    await service.run()


if __name__ == "__main__":
    asyncio.run(main())
