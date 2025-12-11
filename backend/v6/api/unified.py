"""V6 Unified API Endpoint - Main sports odds and props aggregation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import structlog
from fastapi import APIRouter, HTTPException, Query

from streamers.lunosoft_books import LUNOSOFT_BOOK_STREAMERS
from v6.common.redis_cache import get_cache_manager
from v6.odds.engine import OddsEngine
from v6.props.engine import PropsEngine

logger = structlog.get_logger()

router = APIRouter(prefix="/v6", tags=["v6"])

ACTIVE_BOOKS: List[str] = list(LUNOSOFT_BOOK_STREAMERS.keys())
MAIN_SPORTS: List[str] = [
    "americanfootball_nfl",
    "basketball_nba",
    "baseball_mlb",
    "icehockey_nhl",
]

_odds_engine: Optional[OddsEngine] = None
_props_engine: Optional[PropsEngine] = None


async def get_odds_engine() -> OddsEngine:
    """Get or initialize the odds engine."""
    global _odds_engine

    if _odds_engine is None:
        odds_config: Dict[str, Any] = {
            "max_concurrency": 32,
            "odds_date_horizon_days": 0,
        }
        _odds_engine = OddsEngine(odds_config)
        await _odds_engine.initialize()

    return _odds_engine


async def get_props_engine() -> PropsEngine:
    """Legacy helper for callers (e.g., export) that still need PropsEngine."""
    global _props_engine

    if _props_engine is None:
        _props_engine = PropsEngine()
        await _props_engine.initialize()

    return _props_engine


async def get_engines() -> Tuple[OddsEngine, PropsEngine]:
    """Backward-compatible helper returning both engines."""
    return await get_odds_engine(), await get_props_engine()


async def _get_cache_manager():
    return await get_cache_manager()


def _parse_books_param(books: Optional[str]) -> List[str]:
    if not books:
        return ACTIVE_BOOKS
    parsed = [book.strip() for book in books.split(",") if book.strip()]
    return parsed or ACTIVE_BOOKS


def _ensure_sport(sport: Optional[str]) -> str:
    return sport or "basketball_nba"


def _parse_cached_payload(data: Any) -> Optional[Dict[str, Any]]:
    if data is None:
        return None
    if isinstance(data, dict):
        return data
    if isinstance(data, (bytes, bytearray)):
        try:
            decoded = data.decode("utf-8")
        except UnicodeDecodeError:
            return None
        return _parse_cached_payload(decoded)
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            logger.error("Failed to decode cached props payload", payload_preview=data[:200])
            return None
    return None


async def _get_cached_book_props(cache_manager, book_key: str, sport: str) -> Optional[Dict[str, Any]]:
    cached = await cache_manager.get_book_data(book_key, sport, "props")
    payload = _parse_cached_payload(cached)
    if payload:
        payload.setdefault("sport", sport)
        payload.setdefault("book", {"key": book_key})
    return payload


async def _fetch_cached_props_for_books(
    book_keys: List[str],
    sport: str,
    cache_manager=None,
) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
    cache_manager = cache_manager or (await _get_cache_manager())
    results: Dict[str, Dict[str, Any]] = {}
    missing: List[str] = []

    for book_key in book_keys:
        payload = await _get_cached_book_props(cache_manager, book_key, sport)
        if payload:
            results[book_key] = payload
        else:
            missing.append(book_key)

    return results, missing


def _calculate_total_props(payload: Dict[str, Any]) -> int:
    if "total_props" in payload and isinstance(payload["total_props"], int):
        return payload["total_props"]
    return len(payload.get("props", []))


async def _available_books_for_sport(cache_manager, sport: str) -> List[str]:
    pattern = f"v6:book:*:{sport}:props"
    keys = await cache_manager.get_keys(pattern)
    books: set[str] = set()
    for key in keys:
        parts = key.split(":")
        if len(parts) >= 5:
            books.add(parts[2])
    return sorted(books)


@router.get("/health")
async def health_check():
    odds_engine = await get_odds_engine()
    odds_health = await odds_engine.health_check()

    cache_manager = await _get_cache_manager()
    props_health = await cache_manager.health_check()

    status_ok = odds_health.get("overall_healthy", False) and props_health.get("connected", False)

    return {
        "status": "healthy" if status_ok else "degraded",
        "odds_engine": odds_health,
        "props_cache": props_health,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/books")
async def get_available_books():
    odds_engine = await get_odds_engine()
    odds_books = odds_engine.get_available_books()

    cache_manager = await _get_cache_manager()
    props_books_by_sport: Dict[str, List[str]] = {}
    props_books_union: set[str] = set()
    for sport in MAIN_SPORTS:
        books = await _available_books_for_sport(cache_manager, sport)
        props_books_by_sport[sport] = books
        props_books_union.update(books)

    return {
        "odds_books": odds_books,
        "props_books": sorted(props_books_union),
        "props_books_by_sport": props_books_by_sport,
        "total_odds_books": len(odds_books),
        "total_props_books": len(props_books_union),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/odds/{book_key}")
async def get_odds_by_book(
    book_key: str,
    sport: Optional[str] = Query(None, description="Sport filter (e.g., basketball_nba, americanfootball_nfl)"),
):
    odds_engine = await get_odds_engine()
    result = await odds_engine.get_odds_by_book(book_key, sport)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/odds")
async def get_all_odds(
    sport: Optional[str] = Query(None, description="Sport filter"),
    source: str = Query(
        "cache",
        description="Data source preference: cache (default) or live (fallback)",
    ),
):
    sport_key = _ensure_sport(sport)
    cache_manager = await _get_cache_manager()

    # 1) Always try the freshest final snapshot first
    snapshot = await cache_manager.get_sport_snapshot(sport_key)
    if snapshot:
        books = snapshot.get("books") or {}
        snapshot.setdefault("sport", sport_key)
        snapshot.setdefault("total_books", len(books))
        successful = snapshot.get("successful_books")
        if successful is None:
            snapshot["successful_books"] = len([bk for bk in books.values() if bk.get("games")])
        snapshot["source"] = "cache"
        snapshot.setdefault("fetched_at", datetime.now(timezone.utc).isoformat())
        return snapshot

    # 2) Fallback to normalized stage (canonical events, markets merged)
    normalized_stage = await cache_manager.get_feed_stage(sport_key, "normalized")
    if normalized_stage:
        normalized_stage["source"] = "normalized"
        normalized_stage.setdefault("fetched_at", datetime.now(timezone.utc).isoformat())
        return normalized_stage

    # 3) Fallback to raw scrape payload for instant access
    raw_stage = await cache_manager.get_feed_stage(sport_key, "raw")
    if raw_stage:
        raw_stage["source"] = "raw"
        raw_stage.setdefault("fetched_at", datetime.now(timezone.utc).isoformat())
        return raw_stage

    if source == "cache":
        raise HTTPException(status_code=503, detail="Cached data unavailable yet. Background worker warming up.")

    odds_engine = await get_odds_engine()
    result = await odds_engine.get_all_odds(sport_key)
    result["source"] = "live"
    return result


@router.get("/props/{book_key}")
async def get_props_by_book(
    book_key: str,
    sport: Optional[str] = Query(None, description="Sport filter"),
):
    sport_key = _ensure_sport(sport)
    cache_manager = await _get_cache_manager()
    payload = await _get_cached_book_props(cache_manager, book_key, sport_key)
    if not payload:
        raise HTTPException(
            status_code=404,
            detail=f"No cached props for book '{book_key}' and sport '{sport_key}'",
        )
    return payload


@router.get("/props")
async def get_all_props(
    sport: Optional[str] = Query(None, description="Sport filter"),
    books: Optional[str] = Query(None, description="Comma-separated list of book keys"),
):
    sport_key = _ensure_sport(sport)
    cache_manager = await _get_cache_manager()

    if books:
        requested_books = _parse_books_param(books)
    else:
        requested_books = await _available_books_for_sport(cache_manager, sport_key)

    # First try per-book cached props (fast path)
    results, missing = await _fetch_cached_props_for_books(
        requested_books,
        sport_key,
        cache_manager,
    )

    # Fallback: if no per-book cache exists yet, build directly from the raw feed stage
    if not results:
        raw_stage = await cache_manager.get_feed_stage(sport_key, "raw")
        props_section = raw_stage.get("props") if isinstance(raw_stage, dict) else None

        if isinstance(props_section, dict):
            raw_books = props_section.get("books") or {}

            if books:
                target_books = [bk for bk in requested_books if bk in raw_books]
            else:
                # Discover all books that currently have props
                target_books = sorted(raw_books.keys())
                requested_books = target_books

            results = {bk: raw_books[bk] for bk in target_books}
            missing = [bk for bk in requested_books if bk not in results]

    total_props = sum(_calculate_total_props(payload) for payload in results.values())

    return {
        "sport": sport_key,
        "books": results,
        "requested_books": requested_books,
        "missing_books": missing,
        "total_books": len(results),
        "successful_books": len(results),
        "total_props": total_props,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/main-sports")
async def get_main_sports_data(
    books: Optional[str] = Query(None, description="Comma-separated list of book keys"),
    include_odds: bool = Query(True, description="Include traditional odds"),
    include_props: bool = Query(True, description="Include player props"),
):
    odds_engine = await get_odds_engine()

    book_filter = None
    if books:
        book_filter = [book.strip() for book in books.split(",") if book.strip()]

    result: Dict[str, Any] = {
        "sports": {},
        "target_books": book_filter,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    if include_odds:
        try:
            odds_data = await odds_engine.get_main_sports_odds(book_filter)
            for sport, sport_data in odds_data.get("sports", {}).items():
                result["sports"].setdefault(sport, {"books": {}})
                for book_key, book_data in sport_data.items():
                    result["sports"][sport]["books"].setdefault(book_key, {})
                    result["sports"][sport]["books"][book_key]["odds"] = book_data

            result["odds_summary"] = {
                "successful_books": odds_data.get("successful_books", 0),
                "total_books": odds_data.get("total_books", 0),
            }
        except Exception as exc:
            logger.error("Error fetching odds data", error=str(exc))
            result["odds_error"] = str(exc)

    if include_props:
        cache_manager = await _get_cache_manager()
        props_success = 0
        props_total = 0

        for sport in MAIN_SPORTS:
            available_books = await _available_books_for_sport(cache_manager, sport)
            if book_filter:
                target_books = [book for book in book_filter if book in available_books]
            else:
                target_books = available_books

            sport_payloads, _ = await _fetch_cached_props_for_books(target_books, sport, cache_manager)
            if not sport_payloads:
                continue

            props_success += len(sport_payloads)
            props_total += sum(_calculate_total_props(payload) for payload in sport_payloads.values())

            result["sports"].setdefault(sport, {"books": {}})
            for book_key, payload in sport_payloads.items():
                result["sports"][sport]["books"].setdefault(book_key, {})
                result["sports"][sport]["books"][book_key]["props"] = payload

        result["props_summary"] = {
            "successful_books": props_success,
            "total_books": props_success,
            "total_props": props_total,
        }

    return result


@router.get("/player/{player_name}")
async def get_player_data(
    player_name: str,
    sport: Optional[str] = Query(None, description="Sport filter"),
    books: Optional[str] = Query(None, description="Comma-separated list of book keys"),
):
    sport_key = _ensure_sport(sport)
    cache_manager = await _get_cache_manager()

    if books:
        requested_books = _parse_books_param(books)
    else:
        requested_books = await _available_books_for_sport(cache_manager, sport_key)

    payloads, missing = await _fetch_cached_props_for_books(requested_books, sport_key, cache_manager)
    target = player_name.lower()

    results: Dict[str, Any] = {}
    total_props = 0
    for book_key, payload in payloads.items():
        player_props = [
            prop
            for prop in payload.get("props", [])
            if prop.get("player_name", "").lower() == target
        ]
        if player_props:
            results[book_key] = {
                "book": payload.get("book", {"key": book_key}),
                "player_props": player_props,
                "total_props": len(player_props),
                "fetched_at": payload.get("stored_at") or payload.get("fetched_at"),
            }
            total_props += len(player_props)

    return {
        "player": player_name,
        "sport": sport_key,
        "books": results,
        "total_props": total_props,
        "requested_books": requested_books,
        "missing_books": missing,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/stat/{stat_type}")
async def get_stat_type_data(
    stat_type: str,
    sport: Optional[str] = Query(None, description="Sport filter"),
    books: Optional[str] = Query(None, description="Comma-separated list of book keys"),
):
    sport_key = _ensure_sport(sport)
    cache_manager = await _get_cache_manager()

    if books:
        requested_books = _parse_books_param(books)
    else:
        requested_books = await _available_books_for_sport(cache_manager, sport_key)

    payloads, missing = await _fetch_cached_props_for_books(requested_books, sport_key, cache_manager)
    stat_key = stat_type.lower()

    results: Dict[str, Any] = {}
    total_props = 0
    for book_key, payload in payloads.items():
        stat_props = [
            prop
            for prop in payload.get("props", [])
            if prop.get("stat_type_name", "").lower() == stat_key
            or prop.get("market_type", "").lower() == stat_key
        ]
        if stat_props:
            results[book_key] = {
                "book": payload.get("book", {"key": book_key}),
                "stat_props": stat_props,
                "total_props": len(stat_props),
                "fetched_at": payload.get("stored_at") or payload.get("fetched_at"),
            }
            total_props += len(stat_props)

    return {
        "stat_type": stat_type,
        "sport": sport_key,
        "books": results,
        "total_props": total_props,
        "requested_books": requested_books,
        "missing_books": missing,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


async def shutdown_engines():
    global _odds_engine
    if _odds_engine:
        await _odds_engine.shutdown()
        _odds_engine = None
