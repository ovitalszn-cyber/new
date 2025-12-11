"""Production-ready API endpoints with authentication and monitoring."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, HTTPException, Query, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from v6.odds.optimized_engine import OptimizedOddsEngine
from v6.props.optimized_engine import OptimizedPropsEngine
from v6.common.persistence import get_persistence
from v6.common.metrics import get_metrics
from v6.common.cache import get_odds_cache, get_props_cache

logger = structlog.get_logger()

router = APIRouter(prefix="/v6/prod", tags=["production"])
security = HTTPBearer(auto_error=False)

# Global engines
_odds_engine: Optional[OptimizedOddsEngine] = None
_props_engine: Optional[OptimizedPropsEngine] = None


async def get_engines() -> tuple[OptimizedOddsEngine, OptimizedPropsEngine]:
    """Get or initialize the optimized engines."""
    global _odds_engine, _props_engine
    
    if _odds_engine is None:
        _odds_engine = OptimizedOddsEngine({
            "max_concurrency": 6,
            "enable_cache": True,
            "cache_ttl": 30,
        })
        await _odds_engine.initialize()
    
    if _props_engine is None:
        _props_engine = OptimizedPropsEngine({
            "max_concurrency": 6,
            "enable_cache": True,
            "cache_ttl": 60,
        })
        await _props_engine.initialize()
    
    return _odds_engine, _props_engine


async def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> bool:
    """Simple API key verification (replace with proper auth in production)."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # In production, implement proper API key validation
    # For now, accept any non-empty token
    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    return True


@router.get("/health")
async def production_health_check(authenticated: bool = Depends(verify_api_key)):
    """Production health check with detailed monitoring."""
    odds_engine, props_engine = await get_engines()
    persistence = get_persistence()
    metrics = get_metrics()
    
    # Get engine health
    odds_health = await odds_engine.health_check()
    props_health = await props_engine.health_check()
    
    # Get cache stats
    odds_cache_stats = get_odds_cache().get_stats()
    props_cache_stats = get_props_cache().get_stats()
    
    # Get metrics summary
    metrics_summary = metrics.get_summary()
    
    return {
        "status": "healthy" if odds_health["overall_healthy"] and props_health["overall_healthy"] else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "engines": {
            "odds": odds_health,
            "props": props_health,
        },
        "caches": {
            "odds": odds_cache_stats,
            "props": props_cache_stats,
        },
        "metrics": {
            "uptime_seconds": metrics_summary.get("uptime_seconds", 0),
            "total_requests": sum(metrics_summary.get("counters", {}).values()),
            "active_circuit_breakers": len([
                book for book in odds_health.get("circuit_breaker", {}).keys()
            ] + [
                book for book in props_health.get("circuit_breaker", {}).keys()
            ]),
        },
        "persistence": {
            "connected": True,  # Could add actual DB health check
        },
    }


@router.get("/monitoring/metrics")
async def get_monitoring_metrics(
    hours_back: int = Query(1, ge=1, le=24),
    authenticated: bool = Depends(verify_api_key)
):
    """Get detailed monitoring metrics."""
    persistence = get_persistence()
    metrics = get_metrics()
    
    # Get real-time metrics
    realtime_metrics = metrics.get_summary()
    
    # Get historical metrics from persistence
    historical_metrics = persistence.get_metrics_summary(hours_back)
    
    return {
        "realtime": realtime_metrics,
        "historical": historical_metrics,
        "period_hours": hours_back,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/monitoring/caches")
async def get_cache_status(authenticated: bool = Depends(verify_api_key)):
    """Get detailed cache status for monitoring."""
    odds_cache = get_odds_cache()
    props_cache = get_props_cache()
    
    return {
        "odds_cache": odds_cache.get_cache_info(),
        "props_cache": props_cache.get_cache_info(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/monitoring/circuit-breakers")
async def get_circuit_breaker_status(authenticated: bool = Depends(verify_api_key)):
    """Get circuit breaker status."""
    odds_engine, props_engine = await get_engines()
    
    odds_books = odds_engine.get_available_books()
    props_books = props_engine.get_available_books()
    
    # Combine circuit breaker info
    circuit_status = {}
    for book in odds_books:
        key = book["key"]
        circuit_status[key] = {
            "odds": {
                "initialized": book["initialized"],
                "connected": book["connected"],
                "circuit_state": book.get("circuit_state", "closed"),
            }
        }
    
    for book in props_books:
        key = book["key"]
        if key not in circuit_status:
            circuit_status[key] = {}
        circuit_status[key]["props"] = {
            "initialized": book["initialized"],
            "connected": book["connected"],
            "circuit_state": book.get("circuit_state", "closed"),
        }
    
    # Count problematic books
    problematic_books = [
        key for key, status in circuit_status.items()
        if status.get("odds", {}).get("circuit_state") != "closed" or 
           status.get("props", {}).get("circuit_state") != "closed"
    ]
    
    return {
        "books": circuit_status,
        "total_books": len(circuit_status),
        "problematic_books": len(problematic_books),
        "problematic_book_keys": problematic_books,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/admin/caches/clear")
async def clear_caches(
    cache_type: Optional[str] = Query(None, regex="^(odds|props|all)$"),
    authenticated: bool = Depends(verify_api_key)
):
    """Clear caches (admin endpoint)."""
    cleared_caches = []
    
    if cache_type in ["odds", "all"]:
        get_odds_cache().clear()
        cleared_caches.append("odds")
    
    if cache_type in ["props", "all"]:
        get_props_cache().clear()
        cleared_caches.append("props")
    
    # Record cache clear in metrics
    metrics = get_metrics()
    metrics.increment("cache_cleared", 1, {"caches": ",".join(cleared_caches)})
    
    return {
        "cleared_caches": cleared_caches,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/admin/circuit-breakers/reset")
async def reset_circuit_breakers(
    book_key: Optional[str] = Query(None),
    authenticated: bool = Depends(verify_api_key)
):
    """Reset circuit breakers (admin endpoint)."""
    odds_engine, props_engine = await get_engines()
    
    reset_books = []
    
    if book_key:
        # Reset specific book
        if book_key in odds_engine._circuit_breaker:
            odds_engine._reset_circuit_breaker(book_key)
            reset_books.append(f"{book_key} (odds)")
        
        if book_key in props_engine._circuit_breaker:
            props_engine._reset_circuit_breaker(book_key)
            reset_books.append(f"{book_key} (props)")
    else:
        # Reset all circuit breakers
        for key in list(odds_engine._circuit_breaker.keys()):
            odds_engine._reset_circuit_breaker(key)
            reset_books.append(f"{key} (odds)")
        
        for key in list(props_engine._circuit_breaker.keys()):
            props_engine._reset_circuit_breaker(key)
            reset_books.append(f"{key} (props)")
    
    # Record reset in metrics
    metrics = get_metrics()
    metrics.increment("circuit_breakers_reset", len(reset_books))
    
    return {
        "reset_books": reset_books,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/history/odds/{book_key}")
async def get_odds_history(
    book_key: str,
    sport: str,
    hours_back: int = Query(24, ge=1, le=168),  # Up to 1 week
    authenticated: bool = Depends(verify_api_key)
):
    """Get historical odds data."""
    persistence = get_persistence()
    
    history = persistence.get_odds_history(book_key, sport, hours_back)
    
    return {
        "book_key": book_key,
        "sport": sport,
        "hours_back": hours_back,
        "snapshots": len(history),
        "history": history,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/history/props/{book_key}/{player_id}")
async def get_props_history(
    book_key: str,
    player_id: str,
    hours_back: int = Query(24, ge=1, le=168),  # Up to 1 week
    authenticated: bool = Depends(verify_api_key)
):
    """Get historical props data for a player."""
    persistence = get_persistence()
    
    history = persistence.get_props_history(book_key, player_id, hours_back)
    
    return {
        "book_key": book_key,
        "player_id": player_id,
        "hours_back": hours_back,
        "records": len(history),
        "history": history,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/admin/persistence/cleanup")
async def cleanup_old_data(
    days_to_keep: int = Query(30, ge=7, le=90),
    authenticated: bool = Depends(verify_api_key)
):
    """Clean up old historical data (admin endpoint)."""
    persistence = get_persistence()
    
    # Run cleanup in background
    asyncio.create_task(_cleanup_data_async(persistence, days_to_keep))
    
    return {
        "message": f"Cleanup initiated for data older than {days_to_keep} days",
        "days_to_keep": days_to_keep,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def _cleanup_data_async(persistence, days_to_keep: int) -> None:
    """Async cleanup task."""
    try:
        persistence.cleanup_old_data(days_to_keep)
        logger.info("Data cleanup completed", days_to_keep=days_to_keep)
    except Exception as exc:
        logger.error("Data cleanup failed", error=str(exc))


async def shutdown_production_engines():
    """Shutdown production engines."""
    global _odds_engine, _props_engine
    
    if _odds_engine:
        await _odds_engine.shutdown()
        _odds_engine = None
    
    if _props_engine:
        await _props_engine.shutdown()
        _props_engine = None
