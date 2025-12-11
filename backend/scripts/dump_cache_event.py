
import asyncio
from v6.common.redis_cache import get_cache_manager

async def main():
    cm = await get_cache_manager()
    sport = "basketball_nba"
    ids = await cm.get_sport_events(sport)
    print(f"Found {len(ids)} events.")
    if ids:
        ev = await cm.get_event(ids[0])
        import json
        # Handle datetime serialization if needed? 
        # Redis stores JSON strings usually, so get_event returns Dict.
        # But datetime objects might be inside if deserialized?
        # get_event returns dict from JSON.
        print(json.dumps(ev, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
