import os
import json
import sys
from pathlib import Path

import pytest
from httpx import AsyncClient

# Ensure project root is on sys.path so `import main` works when running pytest
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main import app


API_KEY = os.getenv("V6_SMOKE_API_KEY", "kr_test_key")


@pytest.mark.asyncio
async def test_v6_cached_game_bundle_smoke():
    """Smoke test: /v6/game_bundle returns a bundle for at least one cached NBA game."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Discover games from cache
        resp_match = await client.get(
            "/v6/match",
            params={"sport": "basketball_nba"},
            headers={"Authorization": f"Bearer {API_KEY}"},
        )
        assert resp_match.status_code == 200
        data = resp_match.json()
        games = data.get("games") or []
        if not games:
            pytest.skip("No NBA games in cache yet; background worker may still be warming up")

        game = games[0]
        home = game.get("home_team")
        away = game.get("away_team")
        assert home and away

        resp_bundle = await client.get(
            "/v6/game_bundle",
            params={
                "sport": "basketball_nba",
                "home_team": home,
                "away_team": away,
                "books": "betmgm,prizepicks,underdog",
            },
            headers={"Authorization": f"Bearer {API_KEY}"},
        )
        assert resp_bundle.status_code == 200
        bundle = resp_bundle.json()
        assert bundle.get("match")
        assert bundle.get("markets") is not None
        assert bundle.get("player_props") is not None

        # Print a truncated sample so we can visually inspect the shape when
        # running `pytest -s tests/test_v6_smoke.py`.
        print("\n=== V6 GAME_BUNDLE SAMPLE ===")
        print(json.dumps(bundle, indent=2)[:2000])


@pytest.mark.asyncio
async def test_v6_unified_health_and_books_smoke():
    """Smoke test: unified /v6 health + books endpoints respond and have basic structure."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        resp_health = await client.get("/v6/health")
        assert resp_health.status_code == 200
        data = resp_health.json()
        assert data.get("status") in {"healthy", "degraded"}

        resp_books = await client.get("/v6/books")
        assert resp_books.status_code == 200
        books_data = resp_books.json()
        assert "odds_books" in books_data
        assert "props_books" in books_data

        print("\n=== V6 UNIFIED HEALTH ===")
        print(json.dumps(data, indent=2)[:1000])
        print("\n=== V6 UNIFIED BOOKS SAMPLE ===")
        print(json.dumps(books_data, indent=2)[:1000])


@pytest.mark.asyncio
async def test_v6_stats_health_and_boxscore_smoke():
    """Smoke test: stats /v6/stats/health + boxscore respond.

    Boxscore test is best-effort: we skip if no game_id works in current env.
    """
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Stats health
        resp_health = await client.get("/v6/stats/health")
        assert resp_health.status_code == 200
        print("\n=== V6 STATS HEALTH ===")
        print(json.dumps(resp_health.json(), indent=2)[:1000])

        # Try to find at least one game and then hit its boxscore
        resp_games = await client.get("/v6/stats/games", params={"sport": "nba", "league": "nba"})
        if resp_games.status_code != 200:
            pytest.skip("Stats games endpoint not ready in this environment")
        games = resp_games.json() or []
        if not games:
            pytest.skip("No games returned from /v6/stats/games; cannot smoke-test boxscore")

        game_id = games[0].get("id")
        if not game_id:
            pytest.skip("First game has no id; skipping boxscore smoke test")

        resp_box = await client.get("/v6/stats/boxscore/%s" % game_id, params={"sport": "nba"})
        assert resp_box.status_code in {200, 404}
        if resp_box.status_code == 200:
            print("\n=== V6 STATS BOX_SCORE SAMPLE ===")
            print(json.dumps(resp_box.json(), indent=2)[:1500])


@pytest.mark.asyncio
async def test_v6_export_smoke():
    """Smoke test: /v6/export responds and streams something small."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        resp = await client.get(
            "/v6/export",
            params={
                "format": "json",
                "datasets": "live_odds",
                "scope": "live",
                "limit": 10,
            },
        )
        # Export might be empty but endpoint should exist and respond
        assert resp.status_code in {200, 204}
        if resp.status_code == 200:
            # Streaming NDJSON: show first chunk only
            text = resp.text.splitlines()[:5]
            print("\n=== V6 EXPORT LIVE_ODDS SAMPLE (first lines) ===")
            print("\n".join(text))
