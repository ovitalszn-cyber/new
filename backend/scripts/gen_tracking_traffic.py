#!/usr/bin/env python3
import asyncio
import httpx
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_KEY = "kr_live_kttd843q599k9x0jgcwtb"

async def make_requests():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    print(f"🕵️‍♂️ GENERATING TRAFFIC PATTERN WITH KEY: {API_KEY[:10]}...")
    print(f"Started at: {datetime.utcnow().isoformat()} UTC")
    print("-" * 50)

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Pattern: 3 NBA calls
        print("1. Calling NBA Odds (3 times)...")
        for i in range(3):
            await client.get(f"{BASE_URL}/v6/odds/live?sport=basketball_nba", headers=headers)
            print(f"   - Request {i+1}/3 sent")
            await asyncio.sleep(0.5)

        # Pattern: 2 NFL Props calls
        print("\n2. Calling NFL Props (2 times)...")
        for i in range(2):
            await client.get(f"{BASE_URL}/v6/props?sport=americanfootball_nfl", headers=headers)
            print(f"   - Request {i+1}/2 sent")
            await asyncio.sleep(0.5)
            
        # Pattern: 1 NHL Odds call
        print("\n3. Calling NHL Odds (1 time)...")
        await client.get(f"{BASE_URL}/v6/odds/live?sport=icehockey_nhl", headers=headers)
        print("   - Request 1/1 sent")

    print("-" * 50)
    print("✅ Traffic generation complete.")

if __name__ == "__main__":
    asyncio.run(make_requests())
