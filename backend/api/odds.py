"""
Comprehensive Odds API endpoints similar to The Odds API
Provides sports, odds, events, scores, and market data
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel
import structlog

from streamers.novig import NovigStreamer
from streamers.splashsports import SplashSportsStreamer
from streamers.bovada import BovadaStreamer
from streamers.betonline import BetOnlineStreamer
from streamers.prizepicks import PrizePicksStreamer
from streamers.dabble import DabbleStreamer
from streamers.rebet import RebetStreamer
from streamers.prophetx import ProphetXStreamer
from streamers.propscash import PropsCashStreamer
from streamers.underdog import UnderdogStreamer
from datetime import datetime, timezone
from streamers.fliff import FliffStreamer
from streamers.pick6 import Pick6Streamer
from streamers.pinnacle import PinnacleStreamer

router = APIRouter()
logger = structlog.get_logger()

# Unified book map used by props endpoints
BOOK_MAP: Dict[str, Any] = {
    "novig": NovigStreamer,
    "splashsports": SplashSportsStreamer,
    "bovada": BovadaStreamer,
    "betonline": BetOnlineStreamer,
    "prizepicks": PrizePicksStreamer,
    "dabble": DabbleStreamer,
    "rebet": RebetStreamer,
    "fliff": FliffStreamer,
    "prophetx": ProphetXStreamer,
    "propscash": PropsCashStreamer,
    "underdog": UnderdogStreamer,
    "pick6": Pick6Streamer,
    "pinnacle": PinnacleStreamer,
}

# ----------------------------------------------------------------------------
# DABBLE NORMALIZATION HELPER (used when normalize=true on /props endpoints)
# ----------------------------------------------------------------------------
def _normalize_dabble_props(raw_props: List[Dict[str, Any]] | Dict[str, Any], sport_hint: str) -> Dict[str, Any]:
    """Return Dabble props in the pretty-printed schema provided by the user."""
    def _prop_type(mg: str) -> str:
        mg_l = (mg or "").strip().lower()
        if "point" in mg_l:
            return "points"
        if "rebound" in mg_l:
            return "rebounds"
        if "assist" in mg_l:
            return "assists"
        return mg_l or "unknown"

    # Expecting raw_props to be a list of dicts from Dabble streamer
    props_list: List[Dict[str, Any]] = []
    if isinstance(raw_props, list):
        props_list = raw_props
    elif isinstance(raw_props, dict):
        # Attempt to locate a list within a dict wrapper if streamer changes shape
        candidate = raw_props.get("data") or raw_props.get("raw_api_response")
        if isinstance(candidate, list):
            props_list = candidate

    normalized_props: List[Dict[str, Any]] = []
    for p in (props_list or []):
        try:
            normalized_props.append({
                "game_id": p.get("fixtureId"),
                "game_name": p.get("fixtureName"),
                "game_date": p.get("fixtureDate"),
                "player_id": p.get("playerId"),
                "player_name": p.get("playerName"),
                "player_position": p.get("playerPosition"),
                "team_id": p.get("teamId"),
                "team_name": p.get("teamName"),
                "team_abbreviation": p.get("teamAbbreviation"),
                "prop_type": _prop_type(p.get("marketGroupName") or p.get("market_group")),
                "prop_category": "Normal",
                "line": p.get("propValue"),
                # Standardize to implied odds for Dabble standard picks
                "over_odds": -122,
                "under_odds": -122,
                "last_five_performances": p.get("lastFive", []),
            })
        except Exception:
            continue

    sport_name = None
    if props_list:
        comp = props_list[0].get("competition") or {}
        if isinstance(comp, dict):
            sport_name = comp.get("name")

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "sport": sport_name or sport_hint,
        "book": "Dabble",
        "generated_at": generated_at,
        "props": normalized_props,
    }

# ----------------------------------------------------------------------------
# PRIZEPICKS PLAYER NAME ENRICHMENT (esports and all PP sports)
# ----------------------------------------------------------------------------
def _enrich_prizepicks_with_player_names(raw: Any) -> Any:
    """Attach player_name/player_id onto each projection using included players map.

    Accepts the PrizePicks streamer raw dict and mutates its combined projections
    to include resolved player_name where possible.
    """
    try:
        if not isinstance(raw, dict):
            return raw

        players_by_id: Dict[str, Any] = raw.get("players_by_id") or {}
        # If not present, try to build from raw_response.included minimally
        if not players_by_id and isinstance(raw.get("raw_response"), dict):
            included = raw["raw_response"].get("included") or []
            tmp: Dict[str, Any] = {}
            for item in included:
                if not isinstance(item, dict):
                    continue
                t = (item.get("type") or "").lower()
                if t not in ("new_player", "player"):
                    continue
                pid = str(item.get("id"))
                attrs = item.get("attributes") or {}
                name = (
                    attrs.get("display_name")
                    or attrs.get("name")
                    or attrs.get("full_name")
                    or attrs.get("nickname")
                )
                if pid and name:
                    tmp[pid] = {"name": name, "attributes": attrs}
            players_by_id = tmp

        rr = raw.get("raw_response") or {}
        combined: List[Dict[str, Any]] = rr.get("combined") or []

        def extract_player_id(proj: Dict[str, Any]) -> Optional[str]:
            rel = proj.get("relationships") or {}
            for key in ("new_player", "player"):
                node = rel.get(key) or {}
                data = node.get("data") or {}
                pid = data.get("id")
                if pid:
                    return str(pid)
            attrs = proj.get("attributes") or {}
            for k in ("new_player_id", "player_id", "athlete_id"):
                if attrs.get(k):
                    return str(attrs[k])
            if proj.get("new_player_id"):
                return str(proj["new_player_id"])
            if proj.get("player_id"):
                return str(proj["player_id"])
            return None

        changed = False
        for proj in combined:
            if not isinstance(proj, dict):
                continue
            pid = extract_player_id(proj)
            if not pid:
                continue
            player = players_by_id.get(str(pid))
            if not player:
                continue
            name = player.get("name") or (player.get("attributes") or {}).get("display_name")
            if name:
                proj.setdefault("player_id", pid)
                proj.setdefault("player_name", name)
                changed = True

        if changed:
            # Ensure back is reflected
            raw["raw_response"]["combined"] = combined
        return raw
    except Exception:
        return raw

# ============================================================================
# SPORTS ENDPOINTS
# ============================================================================

@router.get("/sports")
async def get_sports(
    all: bool = Query(False, description="Include out-of-season sports"),
    active: bool = Query(True, description="Only active sports")
):
    """
    Get list of available sports across all books
    Similar to The Odds API /sports endpoint
    """
    sports = []
    
    # Collect sports from all books
    books = [
        ("novig", NovigStreamer),
        ("splashsports", SplashSportsStreamer),
        ("bovada", BovadaStreamer),
        ("betonline", BetOnlineStreamer),
        ("prizepicks", PrizePicksStreamer),
        ("dabble", DabbleStreamer),
        ("rebet", RebetStreamer),
        ("prophetx", ProphetXStreamer),
        ("propscash", PropsCashStreamer),
        ("underdog", UnderdogStreamer),
    ]
    
    for book_key, streamer_class in books:
        try:
            book_sports = streamer_class.get_supported_sports()
            for sport in book_sports:
                sports.append({
                    "key": sport,
                    "book": book_key,
                    "title": sport.replace("_", " ").title(),
                    "active": True,
                    "has_outrights": False
                })
        except Exception as e:
            logger.warning(f"Failed to get sports from {book_key}: {e}")
    
    # Remove duplicates and filter
    unique_sports = {}
    for sport in sports:
        key = sport["key"]
        if key not in unique_sports:
            unique_sports[key] = sport
        else:
            # Add book to existing sport
            if "books" not in unique_sports[key]:
                unique_sports[key]["books"] = [unique_sports[key]["book"]]
            unique_sports[key]["books"].append(sport["book"])
    
    result = list(unique_sports.values())
    
    if not active:
        # In a real implementation, you'd have inactive sports too
        pass
    
    return {
        "data": result,
        "count": len(result),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/sports/{sport_key}")
async def get_sport_details(
    sport_key: str = Path(..., description="Sport key (e.g., football_nfl)")
):
    """Get detailed information about a specific sport"""
    return {
        "key": sport_key,
        "title": sport_key.replace("_", " ").title(),
        "description": f"{sport_key.replace('_', ' ').title()} betting markets",
        "active": True,
        "has_outrights": False,
        "available_books": ["novig", "splashsports", "bovada", "betonline", "prizepicks", "prophetx", "propscash", "underdog"],
        "markets": ["h2h", "spreads", "totals", "player_props"],
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# EVENTS ENDPOINTS
# ============================================================================

@router.get("/events")
async def get_events(
    sport: str = Query(..., description="Sport key"),
    book: Optional[str] = Query(None, description="Specific book to query"),
    limit: int = Query(50, description="Number of events to return"),
    date_from: Optional[str] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[str] = Query(None, description="End date (ISO format)")
):
    """
    Get upcoming events for a sport
    Similar to The Odds API /events endpoint
    """
    try:
        # Use Novig as default for events
        streamer = NovigStreamer(f"novig_{sport}", {"sport": sport, "limit": limit})
        events_data = await streamer.fetch_data(limit=limit)
        
        events = []
        if isinstance(events_data, list):
            for event in events_data:
                if isinstance(event, dict) and "id" in event:
                    events.append({
                        "id": event["id"],
                        "sport_key": sport,
                        "commence_time": event.get("scheduled_start", datetime.utcnow().isoformat()),
                        "home_team": event.get("home_team", "TBD"),
                        "away_team": event.get("away_team", "TBD"),
                        "status": event.get("status", "scheduled"),
                        "league": event.get("league", sport.replace("_", " ").title())
                    })
        
        return {
            "data": events[:limit],
            "count": len(events),
            "sport": sport,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get events for {sport}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")

@router.get("/events/{event_id}")
async def get_event_details(
    event_id: str = Path(..., description="Event ID")
):
    """Get detailed information about a specific event"""
    return {
        "id": event_id,
        "status": "scheduled",
        "commence_time": datetime.utcnow().isoformat(),
        "home_team": "TBD",
        "away_team": "TBD",
        "sport_key": "football_nfl",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# ODDS ENDPOINTS
# ============================================================================

@router.get("/odds")
async def get_odds(
    sport: str = Query(..., description="Sport key"),
    book: Optional[str] = Query(None, description="Specific book"),
    markets: str = Query("h2h,spreads,totals", description="Comma-separated markets"),
    regions: str = Query("us", description="Comma-separated regions"),
    odds_format: str = Query("american", description="Odds format (american/decimal)"),
    limit: int = Query(50, description="Number of events")
):
    """
    Get odds for upcoming events
    Similar to The Odds API /odds endpoint
    """
    try:
        # Parse markets
        market_list = [m.strip() for m in markets.split(",")]
        
        # Use appropriate streamer based on book preference
        if book == "novig" or book is None:
            streamer = NovigStreamer(f"novig_{sport}", {"sport": sport, "limit": limit})
            # Fetch data
            events_data = await streamer.fetch_data(limit=limit)
        elif book == "splashsports":
            streamer = SplashSportsStreamer()
        elif book == "bovada":
            streamer = BovadaStreamer()
        elif book == "dabble":
            streamer = DabbleStreamer()
        elif book == "rebet":
            streamer = RebetStreamer()
        elif book == "betonline":
            streamer = BetOnlineStreamer()
        elif book == "prizepicks":
            streamer = PrizePicksStreamer()
        elif book == "prophetx":
            streamer = ProphetXStreamer()
        elif book == "propscash":
            streamer = PropsCashStreamer()
        elif book == "underdog":
            streamer = UnderdogStreamer()
        else:
            streamer = NovigStreamer(f"novig_{sport}", {"sport": sport, "limit": limit})  # Default fallback

        # Connect to streamer first
        await streamer.connect()

        # Fetch data
        events_data = await streamer.fetch_data(limit=limit)
        
        # Disconnect from streamer
        await streamer.disconnect()
        
        # Format response similar to The Odds API
        formatted_events = []
        if isinstance(events_data, list):
            for event in events_data[:limit]:
                if isinstance(event, dict):
                    formatted_event = {
                        "id": event.get("id", "unknown"),
                        "sport_key": sport,
                        "commence_time": event.get("scheduled_start", datetime.utcnow().isoformat()),
                        "home_team": event.get("home_team", "TBD"),
                        "away_team": event.get("away_team", "TBD"),
                        "bookmakers": []
                    }
                    
                    # Add bookmaker data
                    bookmaker = {
                        "key": book or "novig",
                        "title": book or "NoVig",
                        "last_update": datetime.utcnow().isoformat(),
                        "markets": []
                    }
                    
                    # Add markets based on available data
                    if "markets" in event:
                        for market in event["markets"]:
                            if market.get("type") in market_list:
                                bookmaker["markets"].append({
                                    "key": market.get("type", "h2h").lower(),
                                    "outcomes": market.get("outcomes", [])
                                })
                    
                    formatted_event["bookmakers"].append(bookmaker)
                    formatted_events.append(formatted_event)
        
        return {
            "data": formatted_events,
            "count": len(formatted_events),
            "sport": sport,
            "markets": market_list,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get odds for {sport}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch odds: {str(e)}")

@router.get("/events/{event_id}/odds")
async def get_event_odds(
    event_id: str = Path(..., description="Event ID"),
    markets: str = Query("h2h,spreads,totals", description="Comma-separated markets"),
    regions: str = Query("us", description="Comma-separated regions"),
    odds_format: str = Query("american", description="Odds format")
):
    """Get odds for a specific event"""
    return {
        "id": event_id,
        "sport_key": "football_nfl",
        "commence_time": datetime.utcnow().isoformat(),
        "home_team": "TBD",
        "away_team": "TBD",
        "bookmakers": [],
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# SCORES ENDPOINTS
# ============================================================================

@router.get("/scores")
async def get_scores(
    sport: str = Query(..., description="Sport key"),
    days_from: int = Query(1, description="Days to look back"),
    limit: int = Query(50, description="Number of scores")
):
    """
    Get live scores and completed games
    Similar to The Odds API /scores endpoint
    """
    try:
        # This would typically fetch live scores
        # For now, return mock data structure
        scores = []
        
        return {
            "data": scores,
            "count": len(scores),
            "sport": sport,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get scores for {sport}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch scores: {str(e)}")

# ============================================================================
# MARKETS ENDPOINTS
# ============================================================================

@router.get("/markets")
async def get_markets(
    sport: str = Query(..., description="Sport key")
):
    """Get available markets for a sport"""
    markets = [
        {
            "key": "h2h",
            "title": "Head to Head",
            "description": "Moneyline betting"
        },
        {
            "key": "spreads",
            "title": "Point Spreads",
            "description": "Spread betting"
        },
        {
            "key": "totals",
            "title": "Totals",
            "description": "Over/Under betting"
        },
        {
            "key": "player_props",
            "title": "Player Props",
            "description": "Player performance betting"
        }
    ]
    
    return {
        "data": markets,
        "count": len(markets),
        "sport": sport,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/events/{event_id}/markets")
async def get_event_markets(
    event_id: str = Path(..., description="Event ID")
):
    """Get available markets for a specific event"""
    return {
        "event_id": event_id,
        "markets": [
            {"key": "h2h", "title": "Head to Head"},
            {"key": "spreads", "title": "Point Spreads"},
            {"key": "totals", "title": "Totals"}
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# PARTICIPANTS ENDPOINTS
# ============================================================================

@router.get("/participants")
async def get_participants(
    sport: str = Query(..., description="Sport key"),
    limit: int = Query(100, description="Number of participants")
):
    """Get teams/participants for a sport"""
    return {
        "data": [],
        "count": 0,
        "sport": sport,
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# HISTORICAL ENDPOINTS
# ============================================================================

@router.get("/historical/events")
async def get_historical_events(
    sport: str = Query(..., description="Sport key"),
    date_from: str = Query(..., description="Start date (ISO format)"),
    date_to: str = Query(..., description="End date (ISO format)"),
    limit: int = Query(100, description="Number of events")
):
    """Get historical events"""
    return {
        "data": [],
        "count": 0,
        "sport": sport,
        "date_from": date_from,
        "date_to": date_to,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/historical/events/{event_id}/odds")
async def get_historical_event_odds(
    event_id: str = Path(..., description="Event ID"),
    date: str = Query(..., description="Date (ISO format)"),
    markets: str = Query("h2h", description="Comma-separated markets")
):
    """Get historical odds for a specific event"""
    return {
        "event_id": event_id,
        "date": date,
        "markets": markets.split(","),
        "data": [],
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/props")
async def get_props(
    sport: str = Query(..., description="Sport to get player props/DFS data for"),
    books: str = Query(..., description="Comma-separated list of books (e.g., fliff,dabble,prizepicks)"),
    normalize: bool = Query(False, description="Normalize output when supported (Dabble-only)"),
) -> Dict[str, Any]:
    """
    Fetch raw player props/DFS data per book.
    Returns raw streamer output per requested book with minimal wrapping.
    """
    book_list = [b.strip() for b in books.split(",") if b.strip()]
    results: Dict[str, Any] = {}

    for book_name in book_list:
        try:
            if book_name not in BOOK_MAP:
                results[book_name] = {
                    "status": "error",
                    "error": f"Unknown book: {book_name}",
                    "data": [],
                    "sport": sport,
                }
                continue

            streamer_class = BOOK_MAP[book_name]

            # Per-book config
            if book_name == "fliff":
                config = FliffStreamer.get_default_config(sport)
                streamer = streamer_class(f"fliff_{sport}", config)
            elif book_name == "novig":
                config = {"sport": sport, "limit": 50}
                streamer = streamer_class(f"novig_{sport}", config)
            elif book_name == "dabble":
                config = {"sport": sport, "market_groups": [], "limit": 5000}
                streamer = streamer_class(f"dabble_{sport}", config)
            elif book_name == "prophetx":
                config = {"sport": sport}
                streamer = streamer_class(f"prophetx_{sport}", config)
            elif book_name == "betonline":
                config = {"sport": sport}
                streamer = streamer_class(f"betonline_{sport}", config)
            elif book_name == "propscash":
                config = {"sport": sport}
                streamer = streamer_class(f"propscash_{sport}", config)
            elif book_name == "underdog":
                config = {"sport": sport}
                streamer = streamer_class(f"underdog_{sport}", config)
            else:
                config = {"sport": sport}
                streamer = streamer_class(f"{book_name}_{sport}", config)

            # Connect/fetch/disconnect
            if hasattr(streamer, "connect"):
                await streamer.connect()
            raw_data = await streamer.fetch_data(limit=50) if book_name == "novig" else await streamer.fetch_data()
            if hasattr(streamer, "disconnect"):
                await streamer.disconnect()

            # PrizePicks: enrich with player names (including esports)
            if book_name == "prizepicks":
                try:
                    raw_data = _enrich_prizepicks_with_player_names(raw_data)
                except Exception:
                    pass

            # Apply normalization for Dabble only when requested
            data_out: Any
            if book_name == "dabble" and normalize:
                try:
                    data_out = _normalize_dabble_props(raw_data, sport)
                except Exception:
                    data_out = raw_data
            else:
                data_out = raw_data

            results[book_name] = {
                "status": "success",
                "data": data_out,
                "sport": sport,
                "book": book_name,
            }
        except Exception as e:
            results[book_name] = {
                "status": "error",
                "error": str(e),
                "data": [],
                "sport": sport,
                "book": book_name,
            }

    return {
        "sport": sport,
        "books": book_list,
        "results": results,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/props/{book}")
async def get_props_single(
    book: str,
    sport: str = Query(..., description="Sport to get player props/DFS data for"),
    normalize: bool = Query(False, description="Normalize output when supported (Dabble-only)"),
) -> Dict[str, Any]:
    """Fetch raw player props/DFS data for a single book."""
    if book not in BOOK_MAP:
        raise HTTPException(status_code=400, detail=f"Unknown book: {book}")

    streamer_class = BOOK_MAP[book]

    try:
        if book == "fliff":
            config = FliffStreamer.get_default_config(sport)
            streamer = streamer_class(f"fliff_{sport}", config)
        elif book == "novig":
            config = {"sport": sport, "limit": 50}
            streamer = streamer_class(f"novig_{sport}", config)
        elif book == "dabble":
            config = {"sport": sport, "market_groups": [], "limit": 5000}
            streamer = streamer_class(f"dabble_{sport}", config)
        elif book == "prophetx":
            config = {"sport": sport}
            streamer = streamer_class(f"prophetx_{sport}", config)
        elif book == "betonline":
            config = {"sport": sport}
            streamer = streamer_class(f"betonline_{sport}", config)
        elif book == "propscash":
            config = {"sport": sport}
            streamer = streamer_class(f"propscash_{sport}", config)
        elif book == "underdog":
            config = {"sport": sport}
            streamer = streamer_class(f"underdog_{sport}", config)
        else:
            config = {"sport": sport}
            streamer = streamer_class(f"{book}_{sport}", config)

        if hasattr(streamer, "connect"):
            await streamer.connect()
        raw_data = await streamer.fetch_data(limit=50) if book == "novig" else await streamer.fetch_data()
        if hasattr(streamer, "disconnect"):
            await streamer.disconnect()

        # PrizePicks: enrich with player names (including esports)
        if book == "prizepicks":
            try:
                raw_data = _enrich_prizepicks_with_player_names(raw_data)
            except Exception:
                pass

        data_out = _normalize_dabble_props(raw_data, sport) if (book == "dabble" and normalize) else raw_data
        return {
            "status": "success",
            "sport": sport,
            "book": book,
            "data": data_out,
            "generated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
