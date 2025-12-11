#!/usr/bin/env python3
"""
Test script to run the v5 News Agency pipeline and see what we're working with.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from v5.cache import CacheManager
from v5.background_worker import BackgroundWorker
from api.v5 import ACTIVE_BOOKS
from config import get_settings
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


async def test_pipeline():
    """Test the News Agency pipeline."""
    print("=" * 80)
    print("Testing v5 News Agency Pipeline")
    print("=" * 80)
    print(f"\nACTIVE_BOOKS: {ACTIVE_BOOKS}")
    
    # Initialize cache
    settings = get_settings()
    print(f"\nRedis URL: {settings.redis_url}")
    
    cache_manager = CacheManager(redis_url=settings.redis_url)
    print("Cache manager initialized")
    
    # Create background worker
    worker = BackgroundWorker(
        cache_manager=cache_manager,
        active_books=ACTIVE_BOOKS,
        poll_interval=10.0,  # 10 seconds for testing
        sports=["basketball_nba"]
    )
    
    print("\n" + "=" * 80)
    print("Starting one pipeline cycle...")
    print("=" * 80 + "\n")
    
    try:
        # Run one cycle
        await worker.process_cycle()
        
        print("\n" + "=" * 80)
        print("Pipeline cycle complete!")
        print("=" * 80)
        
        # Check what's in cache
        print("\nChecking cache contents...")
        
        # Try to find any events
        sport_key = "v5:sport:basketball_nba:events"
        event_ids = await cache_manager.get(sport_key)
        
        if event_ids:
            print(f"\nFound {len(event_ids)} events in cache")
            print(f"Event IDs: {event_ids[:5]}...")  # Show first 5
            
            # Try to get one event
            if event_ids:
                event_id = event_ids[0]
                event_key = f"v5:event:{event_id}"
                event_data = await cache_manager.get(event_key)
                
                if event_data:
                    print(f"\nSample event data:")
                    print(f"  Canonical ID: {event_data.get('canonical_event_id')}")
                    print(f"  Sport: {event_data.get('sport')}")
                    print(f"  Teams: {event_data.get('home_team')} vs {event_data.get('away_team')}")
                    print(f"  Markets: {list(event_data.get('markets', {}).keys()) if event_data.get('markets') else 'None'}")
                    print(f"  Books: {list(event_data.get('books', {}).keys()) if event_data.get('books') else 'None'}")
                    print(f"  Props count: {len(event_data.get('props', [])) if event_data.get('props') else 0}")
                    print(f"  EV slips count: {len(event_data.get('ev_slips', [])) if event_data.get('ev_slips') else 0}")
        else:
            print("\nNo events found in cache yet.")
            print("This could mean:")
            print("  - No data was fetched from the books")
            print("  - Data was fetched but processing failed")
            print("  - Events were processed but not stored")
        
        # Check raw archive
        print("\n" + "=" * 80)
        print("Checking raw data archive...")
        print("=" * 80)
        
        from v5.raw_data_archive import RawDataArchive
        archive = RawDataArchive()
        print(f"Archive directory: {archive.archive_dir}")
        
        if archive.archive_dir.exists():
            # Count archived files
            archived_files = list(archive.archive_dir.rglob("*.json.gz"))
            print(f"Total archived files: {len(archived_files)}")
            
            if archived_files:
                print(f"Sample archive: {archived_files[0]}")
        else:
            print("Archive directory doesn't exist yet")
        
    except Exception as e:
        print(f"\n❌ Error during pipeline cycle: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await cache_manager.close()
        print("\n✅ Test complete")


if __name__ == "__main__":
    asyncio.run(test_pipeline())

"""
Test script to run the v5 News Agency pipeline and see what we're working with.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from v5.cache import CacheManager
from v5.background_worker import BackgroundWorker
from api.v5 import ACTIVE_BOOKS
from config import get_settings
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


async def test_pipeline():
    """Test the News Agency pipeline."""
    print("=" * 80)
    print("Testing v5 News Agency Pipeline")
    print("=" * 80)
    print(f"\nACTIVE_BOOKS: {ACTIVE_BOOKS}")
    
    # Initialize cache
    settings = get_settings()
    print(f"\nRedis URL: {settings.redis_url}")
    
    cache_manager = CacheManager(redis_url=settings.redis_url)
    print("Cache manager initialized")
    
    # Create background worker
    worker = BackgroundWorker(
        cache_manager=cache_manager,
        active_books=ACTIVE_BOOKS,
        poll_interval=10.0,  # 10 seconds for testing
        sports=["basketball_nba"]
    )
    
    print("\n" + "=" * 80)
    print("Starting one pipeline cycle...")
    print("=" * 80 + "\n")
    
    try:
        # Run one cycle
        await worker.process_cycle()
        
        print("\n" + "=" * 80)
        print("Pipeline cycle complete!")
        print("=" * 80)
        
        # Check what's in cache
        print("\nChecking cache contents...")
        
        # Try to find any events
        sport_key = "v5:sport:basketball_nba:events"
        event_ids = await cache_manager.get(sport_key)
        
        if event_ids:
            print(f"\nFound {len(event_ids)} events in cache")
            print(f"Event IDs: {event_ids[:5]}...")  # Show first 5
            
            # Try to get one event
            if event_ids:
                event_id = event_ids[0]
                event_key = f"v5:event:{event_id}"
                event_data = await cache_manager.get(event_key)
                
                if event_data:
                    print(f"\nSample event data:")
                    print(f"  Canonical ID: {event_data.get('canonical_event_id')}")
                    print(f"  Sport: {event_data.get('sport')}")
                    print(f"  Teams: {event_data.get('home_team')} vs {event_data.get('away_team')}")
                    print(f"  Markets: {list(event_data.get('markets', {}).keys()) if event_data.get('markets') else 'None'}")
                    print(f"  Books: {list(event_data.get('books', {}).keys()) if event_data.get('books') else 'None'}")
                    print(f"  Props count: {len(event_data.get('props', [])) if event_data.get('props') else 0}")
                    print(f"  EV slips count: {len(event_data.get('ev_slips', [])) if event_data.get('ev_slips') else 0}")
        else:
            print("\nNo events found in cache yet.")
            print("This could mean:")
            print("  - No data was fetched from the books")
            print("  - Data was fetched but processing failed")
            print("  - Events were processed but not stored")
        
        # Check raw archive
        print("\n" + "=" * 80)
        print("Checking raw data archive...")
        print("=" * 80)
        
        from v5.raw_data_archive import RawDataArchive
        archive = RawDataArchive()
        print(f"Archive directory: {archive.archive_dir}")
        
        if archive.archive_dir.exists():
            # Count archived files
            archived_files = list(archive.archive_dir.rglob("*.json.gz"))
            print(f"Total archived files: {len(archived_files)}")
            
            if archived_files:
                print(f"Sample archive: {archived_files[0]}")
        else:
            print("Archive directory doesn't exist yet")
        
    except Exception as e:
        print(f"\n❌ Error during pipeline cycle: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await cache_manager.close()
        print("\n✅ Test complete")


if __name__ == "__main__":
    asyncio.run(test_pipeline())

