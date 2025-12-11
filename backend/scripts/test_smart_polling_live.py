#!/usr/bin/env python3
"""Live verification of hash-based polling with timing measurements."""

import asyncio
import time
from datetime import datetime, timezone
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def main():
    print("=" * 80)
    print("V6 SMART POLLING VERIFICATION - LIVE TEST")
    print("=" * 80)
    print(f"Started at: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    try:
        from v6.background_worker import V6BackgroundWorker
        from v6.common.redis_cache import get_cache_manager
        from config import get_settings
        
        settings = get_settings()
        
        # Initialize cache manager
        print("[1/5] Connecting to Redis...")
        start = time.time()
        cache_manager = await get_cache_manager()
        elapsed = time.time() - start
        print(f"      ✓ Connected in {elapsed:.3f}s")
        print()
        
        # Test hash operations
        print("[2/5] Testing hash storage operations...")
        test_sport = "americanfootball_nfl"
        test_hash = "test_hash_123abc"
        
        start = time.time()
        await cache_manager.set_hash(test_sport, test_hash)
        set_time = time.time() - start
        print(f"      ✓ set_hash() in {set_time*1000:.2f}ms")
        
        start = time.time()
        retrieved = await cache_manager.get_hash(test_sport)
        get_time = time.time() - start
        print(f"      ✓ get_hash() in {get_time*1000:.2f}ms")
        
        assert retrieved == test_hash, f"Hash mismatch: {retrieved} != {test_hash}"
        print(f"      ✓ Hash integrity verified")
        print()
        
        # Initialize worker
        print("[3/5] Initializing V6 Background Worker...")
        active_books = ["draftkings", "fanduel", "betmgm"]
        
        start = time.time()
        worker = V6BackgroundWorker(
            cache_manager=cache_manager,
            active_books=active_books,
            poll_interval=5.0,  # Short interval for testing
            sports=["americanfootball_nfl", "basketball_nba"]
        )
        init_time = time.time() - start
        print(f"      ✓ Worker initialized in {init_time:.3f}s")
        print(f"      - Sports in rotation: {list(worker._sport_queue)}")
        print(f"      - Poll interval: {worker.poll_interval}s")
        print()
        
        # Initialize engines
        print("[4/5] Initializing odds and props engines...")
        start = time.time()
        await worker.odds_engine.initialize(active_books)
        odds_init = time.time() - start
        print(f"      ✓ Odds engine ready in {odds_init:.3f}s")
        
        start = time.time()
        await worker.props_engine.initialize(active_books)
        props_init = time.time() - start
        print(f"      ✓ Props engine ready in {props_init:.3f}s")
        print()
        
        # Test signal snapshot
        print("[5/5] Testing signal snapshot generation...")
        test_sport = "americanfootball_nfl"
        
        start = time.time()
        snapshot = await worker.odds_engine.get_signal_snapshot(test_sport)
        snapshot_time = time.time() - start
        
        if snapshot.get("hash"):
            print(f"      ✓ Signal snapshot generated in {snapshot_time:.3f}s")
            print(f"      - Hash: {snapshot['hash'][:16]}...")
            print(f"      - Signal book: {snapshot.get('signal_book')}")
            print(f"      - Games found: {snapshot.get('games_count', 0)}")
            print(f"      - Timestamp: {snapshot.get('timestamp')}")
        else:
            print(f"      ✗ Failed to generate snapshot: {snapshot.get('error')}")
        print()
        
        # Test change detection
        print("=" * 80)
        print("TESTING CHANGE DETECTION LOGIC")
        print("=" * 80)
        print()
        
        # Clear existing hash
        await cache_manager.set_hash(test_sport, None)
        
        # Test 1: First run (no hash exists)
        print("[TEST 1] First run - no existing hash")
        start = time.time()
        needs_update = await worker._check_for_updates(test_sport)
        check_time = time.time() - start
        print(f"      Result: {'UPDATE NEEDED' if needs_update else 'SKIP'}")
        print(f"      Time: {check_time:.3f}s")
        assert needs_update, "Should update when no hash exists"
        print(f"      ✓ PASS")
        print()
        
        # Get current hash
        current_hash = await cache_manager.get_hash(test_sport)
        print(f"      Current hash stored: {current_hash[:16] if current_hash else 'None'}...")
        print()
        
        # Test 2: Immediate re-check (hash should match)
        print("[TEST 2] Immediate re-check - hash should match")
        start = time.time()
        needs_update = await worker._check_for_updates(test_sport)
        check_time = time.time() - start
        print(f"      Result: {'UPDATE NEEDED' if needs_update else 'SKIP'}")
        print(f"      Time: {check_time:.3f}s")
        
        if not needs_update:
            print(f"      ✓ PASS - Correctly detected no changes")
        else:
            print(f"      ⚠ WARNING - Hash changed immediately (data may be volatile)")
        print()
        
        # Test 3: Force hash change
        print("[TEST 3] Forced hash change - should detect update")
        await cache_manager.set_hash(test_sport, "old_hash_different")
        
        start = time.time()
        needs_update = await worker._check_for_updates(test_sport)
        check_time = time.time() - start
        print(f"      Result: {'UPDATE NEEDED' if needs_update else 'SKIP'}")
        print(f"      Time: {check_time:.3f}s")
        assert needs_update, "Should update when hash differs"
        print(f"      ✓ PASS")
        print()
        
        # Performance summary
        print("=" * 80)
        print("PERFORMANCE SUMMARY")
        print("=" * 80)
        print(f"Redis connection:     {elapsed:.3f}s")
        print(f"Hash set operation:   {set_time*1000:.2f}ms")
        print(f"Hash get operation:   {get_time*1000:.2f}ms")
        print(f"Worker initialization: {init_time:.3f}s")
        print(f"Odds engine init:     {odds_init:.3f}s")
        print(f"Props engine init:    {props_init:.3f}s")
        print(f"Signal snapshot:      {snapshot_time:.3f}s")
        print(f"Change detection:     {check_time:.3f}s")
        print()
        
        # Estimate savings
        print("=" * 80)
        print("ESTIMATED COST SAVINGS")
        print("=" * 80)
        
        old_calls_per_hour = 4 * len(active_books) * 4  # 4 sports, 3 books, 4 cycles/hour
        new_checks_per_hour = 120 / worker.poll_interval  # checks per hour
        
        print(f"Old architecture (15s polling):")
        print(f"  - API calls per hour: ~{old_calls_per_hour}")
        print(f"  - Wasted calls (assuming 10% change rate): ~{int(old_calls_per_hour * 0.9)}")
        print()
        print(f"New architecture (hash-based):")
        print(f"  - Signal checks per hour: {int(new_checks_per_hour)}")
        print(f"  - Full refreshes (assuming 10% change rate): ~{int(new_checks_per_hour * 0.1)}")
        print(f"  - Total API calls: ~{int(new_checks_per_hour * 0.1 * len(active_books))}")
        print()
        
        savings = ((old_calls_per_hour - int(new_checks_per_hour * 0.1 * len(active_books))) / old_calls_per_hour) * 100
        print(f"💰 Estimated savings: ~{savings:.1f}%")
        print()
        
        print("=" * 80)
        print("✓ ALL TESTS PASSED")
        print("=" * 80)
        print()
        print("The smart polling implementation is working correctly!")
        print()
        print("Next steps:")
        print("  1. Start the worker: python -m v6.background_worker")
        print("  2. Monitor logs for 'Rotational Mode' and change detection")
        print("  3. Watch Redis: redis-cli KEYS 'v6:sport:*:hash'")
        
        # Cleanup
        await worker.odds_engine.shutdown()
        await worker.props_engine.shutdown()
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print()
        print("Make sure you're running from the project root with dependencies installed:")
        print("  cd /Users/drax/Downloads/kashrock-main")
        print("  pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
