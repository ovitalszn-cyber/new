#!/usr/bin/env python3
"""Start the V6 background worker to populate Redis cache."""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def main():
    from v6.background_worker import V6BackgroundWorker
    from v6.common.redis_cache import get_cache_manager
    
    print("=" * 80)
    print("STARTING V6 BACKGROUND WORKER")
    print("=" * 80)
    print()
    
    # Initialize cache manager
    cache_manager = await get_cache_manager()
    
    # Active books for polling
    active_books = ["draftkings", "fanduel", "betmgm"]
    
    # Initialize worker
    worker = V6BackgroundWorker(
        cache_manager=cache_manager,
        active_books=active_books,
        poll_interval=30.0,  # 30 second heartbeat
        sports=["americanfootball_nfl", "basketball_nba"]
    )
    
    print(f"Worker configured:")
    print(f"  - Books: {active_books}")
    print(f"  - Sports: {worker.sports}")
    print(f"  - Poll interval: {worker.poll_interval}s")
    print(f"  - Mode: Rotational (hash-based)")
    print()
    
    # Start worker
    await worker.start()
    
    print("✓ Worker started successfully!")
    print()
    print("Press Ctrl+C to stop...")
    print()
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping worker...")
        await worker.stop()
        print("✓ Worker stopped")

if __name__ == "__main__":
    asyncio.run(main())
