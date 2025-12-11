
import asyncio
import httpx
import time
import sys

BASE_URL = "http://localhost:8000"
HEADERS = {"Authorization": "Bearer kr_test_key"} 

async def benchmark_endpoint(client, url, name):
    print(f"Testing {name} ({url})...")
    start = time.perf_counter()
    try:
        response = await client.get(url, headers=HEADERS)
        elapsed = time.perf_counter() - start
        
        status = response.status_code
        size = len(response.content)
        
        print(f"  Status: {status}")
        print(f"  Time:   {elapsed:.4f}s")
        print(f"  Size:   {size} bytes")
        
        if status == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else len(data.get('games', []))
            print(f"  Items:  {count}")
            return elapsed
        else:
            print(f"  Error: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"  Exception: {e}")
        return None

async def main():
    print("🚀 Starting API Benchmark")
    print("-" * 40)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Test /v6/odds/live (The one we refactored)
        await benchmark_endpoint(client, f"{BASE_URL}/v6/odds/live?sport=basketball_nba", "Result: Live Odds (Unified)")
        
        # 2. Test /v6/odds/history (Cached via Aggregator?)
        # await benchmark_endpoint(client, f"{BASE_URL}/v6/odds/live/basketball_nba", "Result: Live Odds (Unified List)")

        # 3. Test /v6/match (Redis Discovery)
        await benchmark_endpoint(client, f"{BASE_URL}/v6/match?sport=basketball_nba", "Result: Cached Match Discovery")

    print("-" * 40)
    print("Done.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
