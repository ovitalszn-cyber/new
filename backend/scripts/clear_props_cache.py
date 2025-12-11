import asyncio
from v6.common.redis_cache import get_cache_manager

async def clear_props_cache():
    cm = await get_cache_manager()
    # Clear all props cache
    await cm.clear_pattern("v6:book:*:*:props")
    print("Props cache cleared")

if __name__ == "__main__":
    asyncio.run(clear_props_cache())
