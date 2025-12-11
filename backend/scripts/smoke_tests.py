#!/usr/bin/env python3
"""
Smoke tests for KashRock API deployment.

Tests critical endpoints that rely on the historical database to ensure
the Railway deployment is working correctly.

Usage:
    python scripts/smoke_tests.py [--url URL] [--api-key KEY]
"""

import argparse
import asyncio
import sys
from typing import Dict, Any, List
import httpx
import structlog
from datetime import datetime

logger = structlog.get_logger()


class SmokeTestRunner:
    """Run smoke tests against deployed KashRock API."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.results: List[Dict[str, Any]] = []
    
    async def run_all_tests(self):
        """Run all smoke tests."""
        print("=" * 70)
        print("🧪 KashRock API Smoke Tests")
        print("=" * 70)
        print(f"🌐 Base URL: {self.base_url}")
        print(f"🔑 API Key: {self.api_key[:8]}...")
        print(f"⏰ Started: {datetime.utcnow().isoformat()}")
        print("=" * 70)
        print()
        
        tests = [
            self.test_health_check,
            self.test_historical_games,
            self.test_nba_boxscore,
            self.test_esports_matches,
            self.test_esports_player_stats,
            self.test_nba_player_boxscores,
            self.test_stats_endpoint,
            self.test_odds_endpoint,
        ]
        
        for test in tests:
            await self.run_test(test)
        
        # Summary
        print()
        print("=" * 70)
        print("📊 Test Summary")
        print("=" * 70)
        
        passed = sum(1 for r in self.results if r['passed'])
        failed = sum(1 for r in self.results if not r['passed'])
        total = len(self.results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {failed}/{total}")
        print()
        
        if failed > 0:
            print("Failed tests:")
            for result in self.results:
                if not result['passed']:
                    print(f"  - {result['name']}: {result['error']}")
            print()
        
        print(f"⏰ Completed: {datetime.utcnow().isoformat()}")
        print("=" * 70)
        
        return failed == 0
    
    async def run_test(self, test_func):
        """Run a single test and record results."""
        test_name = test_func.__name__.replace('test_', '').replace('_', ' ').title()
        print(f"🧪 Testing: {test_name}...", end=' ', flush=True)
        
        try:
            await test_func()
            print("✅ PASS")
            self.results.append({
                'name': test_name,
                'passed': True,
                'error': None
            })
        except Exception as e:
            print(f"❌ FAIL: {str(e)}")
            self.results.append({
                'name': test_name,
                'passed': False,
                'error': str(e)
            })
    
    async def test_health_check(self):
        """Test basic health check endpoint."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/health")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert data.get('status') == 'healthy', f"Expected healthy status, got {data}"
    
    async def test_historical_games(self):
        """Test historical games endpoint (TheScore data)."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/v6/historical/games",
                params={'sport': 'nba', 'limit': 10},
                headers=self.headers
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert 'games' in data, "Response missing 'games' field"
            assert len(data['games']) > 0, "No games returned"
    
    async def test_nba_boxscore(self):
        """Test NBA box score endpoint."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Use a known NBA game ID
            game_id = 401584876
            response = await client.get(
                f"{self.base_url}/v6/boxscore/{game_id}",
                params={'sport': 'nba'},
                headers=self.headers
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert 'box_score' in data, "Response missing 'box_score' field"
    
    async def test_esports_matches(self):
        """Test esports matches endpoint."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/v6/esports/matches",
                params={'discipline': 'lol', 'limit': 10},
                headers=self.headers
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert 'matches' in data, "Response missing 'matches' field"
    
    async def test_esports_player_stats(self):
        """Test esports player stats endpoint."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/v6/esports/player-stats",
                params={
                    'discipline': 'lol',
                    'start_date': '2024-01-01',
                    'end_date': '2024-12-31',
                    'limit': 10
                },
                headers=self.headers
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert 'players' in data, "Response missing 'players' field"
    
    async def test_nba_player_boxscores(self):
        """Test NBA player boxscores from historical DB."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/v6/historical/player-boxscores",
                params={'sport': 'nba', 'limit': 10},
                headers=self.headers
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert 'boxscores' in data, "Response missing 'boxscores' field"
    
    async def test_stats_endpoint(self):
        """Test stats endpoint for live data."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/v6/games",
                params={'sport': 'nfl', 'league': 'nfl'},
                headers=self.headers
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert isinstance(data, list), "Expected list response"
    
    async def test_odds_endpoint(self):
        """Test odds endpoint."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/v6/odds",
                params={'sport': 'americanfootball_nfl', 'books': 'draftkings,fanduel'},
                headers=self.headers
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert 'odds' in data or 'events' in data, "Response missing odds data"


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run smoke tests against KashRock API deployment"
    )
    parser.add_argument(
        '--url',
        default='http://localhost:8000',
        help='Base URL of the API (default: http://localhost:8000)'
    )
    parser.add_argument(
        '--api-key',
        required=True,
        help='API key for authentication'
    )
    
    args = parser.parse_args()
    
    runner = SmokeTestRunner(args.url, args.api_key)
    success = await runner.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
