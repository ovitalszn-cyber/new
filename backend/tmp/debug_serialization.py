import asyncio
import os
import sys
sys.path.insert(0, '/Users/drax/Documents/KashRockAPI')

from api.v5 import initialize_v5_services
from v5.background_worker import BackgroundWorker

async def debug_serialization():
    # Clear any debug filters to run with all books
    if 'V5_DEBUG_SOURCE_FILTER' in os.environ:
        del os.environ['V5_DEBUG_SOURCE_FILTER']
    if 'V5_DEBUG_EVENT_FILTER' in os.environ:
        del os.environ['V5_DEBUG_EVENT_FILTER']
    
    initialize_v5_services()
    from api.v5 import cache_manager, ACTIVE_BOOKS
    
    print(f'Debugging EventResponse serialization...')
    worker = BackgroundWorker(
        cache_manager=cache_manager,
        active_books=ACTIVE_BOOKS,
        poll_interval=30.0,
        sports=['basketball_nba'],
    )
    
    await worker.process_cycle()
    print('Pipeline completed - check serialization debug output!')

asyncio.run(debug_serialization())
