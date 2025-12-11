
import asyncio
import httpx
import time
import sys

# Constants
BASE_URL = "http://localhost:8000"
API_KEY = "kr_test_key"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

async def benchmark_endpoint(client, name, url):
    print(f"Testing {name} ({url})...")
    start = time.time()
    try:
        resp = await client.get(url, headers=HEADERS, timeout=60.0)
        duration = time.time() - start
        
        status = resp.status_code
        size = len(resp.content)
        
        try:
            data = resp.json()
            if isinstance(data, list):
                items = len(data)
            elif isinstance(data, dict):
                # heuristic for count
                if "results" in data: items = len(data["results"])
                elif "games" in data: items = len(data["games"])
                elif "props" in data: items = len(data["props"]) # v6/props
                elif "events" in data: items = len(data["events"])
                elif "books" in data: items = len(data["books"])
                else: items = 1
            else:
                items = 0
        except:
            items = 0
            
        print(f"  Status: {status}")
        print(f"  Time:   {duration:.4f}s")
        print(f"  Size:   {size} bytes")
        print(f"  Items:  {items}")
        
        if status != 200:
            print(f"  Error: {resp.text[:200]}")
            
    except Exception as e:
        print(f"  Failed: {e}")

async def main():
    print("🚀 Starting Full API Suite Benchmark\n")
    print("-" * 40)
    
    async with httpx.AsyncClient() as client:
        # 1. Odds (Match Discovery)
        await benchmark_endpoint(client, "Odds (Match Discovery)", f"{BASE_URL}/v6/match?sport=basketball_nba")
        
        # 2. Props (Unified + EV)
        await benchmark_endpoint(client, "Props (Basketball)", f"{BASE_URL}/v6/props?sport=basketball_nba")
        
        # 3. Stats (Games - NBA)
        await benchmark_endpoint(client, "Stats (Games - NBA)", f"{BASE_URL}/v6/games?sport=nba")

        # 4. Books Registry (To confirm EV source presence)
        await benchmark_endpoint(client, "Books Registry", f"{BASE_URL}/v6/books")

        # 5. Export
        await benchmark_endpoint(client, "Export (Live Odds JSON)", f"{BASE_URL}/v6/export?datasets=live_odds&format=json&sport=basketball_nba&limit=10")

    print("-" * 40)
    print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
