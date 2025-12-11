#!/usr/bin/env python3
"""
API Key System Verification Script

This script tests the API key authentication and tracking system.
Run this AFTER you've generated an API key from the frontend dashboard.
"""

import asyncio
import httpx
import sys
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000"

async def test_api_key_system(api_key: str):
    """Test the API key system with various endpoints."""
    
    print("=" * 80)
    print("KASHROCK API KEY SYSTEM VERIFICATION")
    print("=" * 80)
    print(f"Testing with API key: {api_key[:20]}...")
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Health check (no auth required)
        print("[TEST 1] Health Check (no auth)")
        try:
            response = await client.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                print("  ✓ PASS - API is accessible")
            else:
                print(f"  ✗ FAIL - Status: {response.status_code}")
        except Exception as e:
            print(f"  ✗ ERROR - {e}")
        print()
        
        # Test 2: Books endpoint (no auth required)
        print("[TEST 2] Books Endpoint (no auth)")
        try:
            response = await client.get(f"{BASE_URL}/v1/books")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ PASS - Found {data.get('total_books', 0)} books")
                print(f"    - Sportsbooks: {data.get('sportsbooks', 0)}")
                print(f"    - EV Sources: {data.get('ev_sources', 0)}")
            else:
                print(f"  ✗ FAIL - Status: {response.status_code}")
        except Exception as e:
            print(f"  ✗ ERROR - {e}")
        print()
        
        # Test 3: V6 Live Odds (requires auth)
        print("[TEST 3] V6 Live Odds Endpoint (requires auth)")
        try:
            response = await client.get(
                f"{BASE_URL}/v6/odds/live",
                headers=headers,
                params={"sport": "americanfootball_nfl"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ PASS - Authenticated successfully")
                print(f"    - Sport: {data.get('sport', 'unknown')}")
                print(f"    - Events: {len(data.get('events', []))}")
                print(f"    - Books: {len(data.get('books', {}))}")
                print(f"    - Cached: {data.get('cached', False)}")
            elif response.status_code == 401:
                print(f"  ✗ FAIL - Authentication failed")
                print(f"    Response: {response.text[:200]}")
            else:
                print(f"  ✗ FAIL - Status: {response.status_code}")
                print(f"    Response: {response.text[:200]}")
        except Exception as e:
            print(f"  ✗ ERROR - {e}")
        print()
        
        # Test 4: V6 Props Endpoint (requires auth)
        print("[TEST 4] V6 Props Endpoint (requires auth)")
        try:
            response = await client.get(
                f"{BASE_URL}/v6/props",
                headers=headers,
                params={"sport": "americanfootball_nfl"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ PASS - Props endpoint working")
                print(f"    - Sport: {data.get('sport', 'unknown')}")
                print(f"    - Total props: {data.get('total_props', 0)}")
            elif response.status_code == 401:
                print(f"  ✗ FAIL - Authentication failed")
            else:
                print(f"  ✗ FAIL - Status: {response.status_code}")
        except Exception as e:
            print(f"  ✗ ERROR - {e}")
        print()
        
        # Test 5: Invalid API Key
        print("[TEST 5] Invalid API Key Test")
        try:
            bad_headers = {"Authorization": "Bearer invalid_key_12345"}
            response = await client.get(
                f"{BASE_URL}/v6/odds/live",
                headers=bad_headers,
                params={"sport": "americanfootball_nfl"}
            )
            if response.status_code == 401:
                print(f"  ✓ PASS - Invalid key correctly rejected")
            else:
                print(f"  ✗ FAIL - Invalid key not rejected (status: {response.status_code})")
        except Exception as e:
            print(f"  ✗ ERROR - {e}")
        print()
        
        # Test 6: Rate limiting (Burst Test)
        print("[TEST 6] Rate Limiting Test (25 rapid requests - Burst Limit: 20/s)")
        success_count = 0
        rate_limited_count = 0
        
        start_time = datetime.now()
        for i in range(25):
            try:
                response = await client.get(
                    f"{BASE_URL}/v6/odds/live",
                    headers=headers,
                    params={"sport": "basketball_nba"}
                )
                if response.status_code == 200:
                    success_count += 1
                    print(".", end="", flush=True)
                elif response.status_code == 429:
                    rate_limited_count += 1
                    print("x", end="", flush=True)
            except Exception as e:
                pass
        
        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n  - Time: {duration:.2f}s")
        print(f"  - Successful: {success_count}/25")
        print(f"  - Rate limited: {rate_limited_count}/25")
        
        if rate_limited_count > 0:
            print(f"  ✓ PASS - Burst limit enforced!")
        elif success_count == 25:
             print(f"  ⚠ NOTE - No rate limit hit (took {duration:.2f}s, > 1s?)")
        print()
        
    print("=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    print()
    print("Next: Check the dashboard at http://localhost:3000 to view:")
    print("  - API usage statistics")
    print("  - Request logs")
    print("  - Key usage tracking")
    print()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_api_key_system.py <YOUR_API_KEY>")
        print()
        print("Steps:")
        print("  1. Open http://localhost:3000")
        print("  2. Sign in with Google")
        print("  3. Generate an API key from the dashboard")
        print("  4. Copy the key and run:")
        print("     python3 scripts/test_api_key_system.py kr_live_xxxxx...")
        sys.exit(1)
    
    api_key = sys.argv[1]
    asyncio.run(test_api_key_system(api_key))

if __name__ == "__main__":
    main()
