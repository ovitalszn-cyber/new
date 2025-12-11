"""V6 API endpoints serving from Redis cache."""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Any, Dict, List, Optional, Set

import structlog
from fastapi import APIRouter, HTTPException, Query, Path, Header

from v6.common.redis_cache import get_cache_manager
from v6.background_worker import get_background_worker
from v6.common.market_normalizer import normalize_market_key, is_player_prop_market
from auth import validate_api_key
from utils.time_utils import format_eastern_datetime
from processing.stat_canonicalizer import canonicalize_stat_type
from utils.team_names import canonicalize_team
from control_plane.api_keys import api_key_service

try:
    from data.team_aliases import SPORT_TEAM_ID_MAP
except ImportError:  # pragma: no cover - fallback for packages missing data module
    SPORT_TEAM_ID_MAP: Dict[str, Dict[int, str]] = {}

logger = structlog.get_logger()


async def _require_valid_api_key(authorization: Optional[str]) -> None:
    """Validate API key against control-plane service with legacy fallback.

    This allows production dashboard-generated kr_live_* keys (stored in auth.db)
    to authenticate, while still accepting legacy in-memory test keys.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Use Authorization: Bearer <your-key>",
        )

    # Primary: database-backed API keys
    ctx = await api_key_service.resolve_key(authorization)
    if ctx:
        return

    # Fallback: legacy in-memory API key manager
    if validate_api_key(authorization):
        return

    raise HTTPException(
        status_code=401,
        detail="Invalid or inactive API key",
    )

# EV source sport support mapping for filtering
EV_SOURCE_SPORTS_SUPPORT = {
    'walter': ['americanfootball_nfl', 'basketball_nba'],
    'rotowire': ['americanfootball_nfl', 'basketball_nba', 'icehockey_nhl', 'baseball_mlb', 'soccer'],
    # Proply supports multiple sports; enable for NFL and NBA initially
    'proply': ['americanfootball_nfl', 'basketball_nba'],
    # Sharp Props (EV) - DFS/Pick'em books
    'sharp_props': [
        'americanfootball_nfl', 
        'americanfootball_ncaaf', 
        'basketball_nba', 
        'basketball_ncaab', 
        'icehockey_nhl', 
        'baseball_mlb'
    ],
}

def get_supported_ev_sources(sport: str) -> list:
    """Get list of EV sources that support the requested sport."""
    supported_sources = []
    for source, supported_sports in EV_SOURCE_SPORTS_SUPPORT.items():
        if sport in supported_sports:
            supported_sources.append(source)
    return supported_sources

router = APIRouter(prefix="/v6", tags=["v6-cached"])


def convert_to_eastern_time(utc_datetime_str: str) -> str:
    """Backward compatible wrapper around format_eastern_datetime."""
    return format_eastern_datetime(utc_datetime_str, include_date=True)


EV_BOOK_ALIASES: Dict[str, Set[str]] = {
    "ballybet": {"ballybet"},
    "betmgm": {"betmgm", "betmgm-sb"},
    "betparx": {"betparx"},
    "betrivers": {"betrivers", "betrivers-sb"},
    "betr": {"betr", "betr_us_dfs"},
    "bovada": {"bovada"},
    "caesars": {"caesars", "caesars-sb", "williamhill_us"},
    "draftkings": {"draftkings", "draftkings-sb"},
    "espnbet": {"espnbet"},
    "fanatics": {"fanatics"},
    "fanduel": {"fanduel", "fanduel-sb"},
    "fliff": {"fliff"},
    "hardrockbet": {"hardrockbet", "hardrock-sb", "hardrock"},
    "novig": {"novig"},
    "pick6": {"pick6"},
    "pinnacle": {"pinnacle"},
    "prizepicks": {"prizepicks"},
    "sleeper": {"sleeper"},
    "underdog": {"underdog"},
    "williamhill_us": {"williamhill_us"},  # allow direct access if requested explicitly
}

EV_BOOK_ALIAS_LOOKUP: Dict[str, str] = {}
for canonical_name, aliases in EV_BOOK_ALIASES.items():
    all_aliases = set(aliases) | {canonical_name}
    for alias in all_aliases:
        EV_BOOK_ALIAS_LOOKUP[alias.lower()] = canonical_name

def normalize_book_name(book_name: Optional[str]) -> Optional[str]:
    """Normalize raw bookmaker name (from EV sources or user input) to canonical key."""
    if not book_name:
        return None
    return EV_BOOK_ALIAS_LOOKUP.get(book_name.strip().lower())


def _resolve_team_name_from_id(team_id: Any, sport: Optional[str]) -> Optional[str]:
    """Translate a numeric team_id (e.g., from Proply) into a canonical name."""
    if team_id in (None, ""):
        return None
    try:
        team_id_int = int(team_id)
    except (ValueError, TypeError):
        return None

    sport_key = (sport or "").strip().lower()
    sport_lookup = SPORT_TEAM_ID_MAP.get(sport_key) or SPORT_TEAM_ID_MAP.get(sport or "")
    if not sport_lookup:
        return None

    team_name = sport_lookup.get(team_id_int)
    if not team_name:
        return None
    return canonicalize_team(team_name, sport_key) or team_name


def _normalize_book_list(books_param: Optional[str]) -> Set[str]:
    """Parse the books query param into canonical bookmaker keys."""
    if not books_param:
        raise HTTPException(
            status_code=400,
            detail="books parameter is required (comma-separated list of sportsbooks)"
        )
    
    requested: Set[str] = set()
    for raw_book in books_param.split(","):
        book = raw_book.strip()
        if not book:
            continue
        canonical = normalize_book_name(book) or book.lower()
        requested.add(canonical)
    
    if not requested:
        raise HTTPException(
            status_code=400,
            detail="No valid sportsbooks provided in books parameter"
        )
    return requested


def _build_team_aliases(*values: Optional[str]) -> Set[str]:
    aliases: Set[str] = set()
    for value in values:
        if not value:
            continue
        alias = str(value).lower().strip()
        if alias:
            aliases.add(alias)
            aliases.add(alias.replace(" ", ""))
    return aliases


def _expand_market_entries(
    odd: Dict[str, Any],
    canonical_market: str,
    home_team: str,
    away_team: str,
) -> List[Dict[str, Any]]:
    """Split combined bookmaker odds into per-team entries when selection is missing."""
    if canonical_market == "h2h" and not odd.get("selection"):
        expanded: List[Dict[str, Any]] = []
        home_price = odd.get("home_price") or odd.get("home_odds")
        away_price = odd.get("away_price") or odd.get("away_odds")
        if home_price is not None:
            entry = dict(odd)
            entry["selection"] = home_team
            entry["odds"] = home_price
            entry.setdefault("direction", "home")
            expanded.append(entry)
        if away_price is not None:
            entry = dict(odd)
            entry["selection"] = away_team
            entry["odds"] = away_price
            entry.setdefault("direction", "away")
            expanded.append(entry)
        if expanded:
            return expanded
    elif canonical_market == "spreads" and not odd.get("selection"):
        expanded = []
        home_price = odd.get("home_price") or odd.get("home_odds")
        away_price = odd.get("away_price") or odd.get("away_odds")
        home_handicap = odd.get("home_handicap")
        away_handicap = odd.get("away_handicap")
        if home_price is not None and home_handicap is not None:
            entry = dict(odd)
            entry["selection"] = home_team
            entry["odds"] = home_price
            entry["line"] = home_handicap
            entry.setdefault("direction", "home")
            expanded.append(entry)
        if away_price is not None and away_handicap is not None:
            entry = dict(odd)
            entry["selection"] = away_team
            entry["odds"] = away_price
            entry["line"] = away_handicap
            entry.setdefault("direction", "away")
            expanded.append(entry)
        if expanded:
            return expanded
    elif canonical_market in ("totals", "team_totals") and not odd.get("selection"):
        expanded = []
        total_line = odd.get("total") or odd.get("line")
        over_price = odd.get("over_price") or odd.get("over_odds")
        under_price = odd.get("under_price") or odd.get("under_odds")
        if total_line is not None and over_price is not None:
            entry = dict(odd)
            entry["selection"] = "over"
            entry["line"] = total_line
            entry["odds"] = over_price
            entry.setdefault("direction", "over")
            expanded.append(entry)
        if total_line is not None and under_price is not None:
            entry = dict(odd)
            entry["selection"] = "under"
            entry["line"] = total_line
            entry["odds"] = under_price
            entry.setdefault("direction", "under")
            expanded.append(entry)
        if expanded:
            return expanded
    return [odd]


def _selection_team(selection: str, home_aliases: Set[str], away_aliases: Set[str]) -> Optional[str]:
    if not selection:
        return None
    normalized = selection.lower().strip()
    normalized_no_space = normalized.replace(" ", "")
    if normalized in home_aliases or normalized_no_space in home_aliases:
        return "home"
    if normalized in away_aliases or normalized_no_space in away_aliases:
        return "away"
    return None


def _extract_main_markets(
    event_data: Dict[str, Any],
    requested_books: Set[str],
    home_team: str,
    away_team: str,
) -> Dict[str, List[Dict[str, Any]]]:
    markets = {
        "home_team": [],
        "away_team": [],
        "totals": [],
    }
    
    home_aliases = _build_team_aliases(
        home_team,
        event_data.get("home_team_abbrev"),
        event_data.get("home_team_id"),
        event_data.get("home_team_market")
    )
    away_aliases = _build_team_aliases(
        away_team,
        event_data.get("away_team_abbrev"),
        event_data.get("away_team_id"),
        event_data.get("away_team_market")
    )
    
    odds_by_book = event_data.get("odds_by_book") or {}
    books_section = event_data.get("books") or {}
    
    def iter_book_odds(raw_book: str, book_payload: Dict[str, Any]):
        canonical_book = normalize_book_name(raw_book) or raw_book.lower()
        if canonical_book not in requested_books:
            return []
        
        odds_entries: List[Dict[str, Any]] = []
        odds_list = book_payload.get("odds")
        if isinstance(odds_list, list):
            odds_entries.extend(odds_list)
        markets_section = book_payload.get("markets")
        if isinstance(markets_section, list):
            odds_entries.extend(markets_section)
        elif isinstance(markets_section, dict):
            for value in markets_section.values():
                if isinstance(value, list):
                    odds_entries.extend(value)
        return [(canonical_book, odd) for odd in odds_entries if isinstance(odd, dict)]
    
    compiled_odds: List[tuple[str, Dict[str, Any]]] = []
    for book_name, book_data in odds_by_book.items():
        if not isinstance(book_data, dict):
            continue
        compiled_odds.extend(iter_book_odds(book_name, book_data))
    
    # Fallback to books section if odds_by_book missing entries
    if not compiled_odds and books_section:
        for book_name, book_data in books_section.items():
            if not isinstance(book_data, dict):
                continue
            compiled_odds.extend(iter_book_odds(book_name, book_data))
    
    for book_name, odd in compiled_odds:
        canonical_market = normalize_market_key(
            odd.get("market_type", ""),
            odd.get("market_key", "")
        )
        normalized_odds = _expand_market_entries(odd, canonical_market, home_team, away_team)
        for normalized in normalized_odds:
            selection = normalized.get("selection") or normalized.get("team")
            entry = {
                "book": book_name,
                "market": canonical_market,
                "selection": selection,
                "odds": normalized.get("odds"),
                "line": normalized.get("line"),
                "direction": normalized.get("direction") or normalized.get("side"),
                "timestamp": normalized.get("timestamp"),
            }
        
            if canonical_market == "h2h":
                team_key = _selection_team(selection, home_aliases, away_aliases)
                if team_key == "home":
                    entry["market"] = "moneyline"
                    markets["home_team"].append(entry)
                elif team_key == "away":
                    entry["market"] = "moneyline"
                    markets["away_team"].append(entry)
            elif canonical_market == "spreads":
                team_key = _selection_team(selection, home_aliases, away_aliases)
                if team_key == "home":
                    markets["home_team"].append(entry)
                elif team_key == "away":
                    markets["away_team"].append(entry)
            elif canonical_market in ("totals", "team_totals"):
                markets["totals"].append(entry)
    
    return markets


def _gather_event_props(event_data: Dict[str, Any]) -> List[tuple[str, Dict[str, Any]]]:
    gathered: List[tuple[str, Dict[str, Any]]] = []
    books_section = event_data.get("books") or {}
    for book_name, book_data in books_section.items():
        if not isinstance(book_data, dict):
            continue
        props_candidates = []
        if isinstance(book_data.get("props"), list):
            props_candidates.extend(book_data["props"])
        if isinstance(book_data.get("player_props"), list):
            props_candidates.extend(book_data["player_props"])
        if isinstance(book_data.get("props_by_market"), dict):
            for market_props in book_data["props_by_market"].values():
                if isinstance(market_props, list):
                    props_candidates.extend(market_props)
        for prop in props_candidates:
            if isinstance(prop, dict):
                gathered.append((book_name, prop))
    
    props_by_book = event_data.get("props_by_book") or {}
    for book_name, props in props_by_book.items():
        if isinstance(props, list):
            for prop in props:
                if isinstance(prop, dict):
                    gathered.append((book_name, prop))
    
    return gathered


def _resolve_prop_team(
    prop: Dict[str, Any],
    home_aliases: Set[str],
    away_aliases: Set[str]
) -> str:
    team_keys = [
        prop.get("player_team"),
        prop.get("team"),
        prop.get("team_name"),
        prop.get("player_team_abbrev"),
        prop.get("team_abbrev"),
        prop.get("player_team_id"),
    ]
    for key in team_keys:
        team_key = _selection_team(key or "", home_aliases, away_aliases)
        if team_key:
            return team_key
    return "unknown"


def _extract_player_props_by_team(
    event_data: Dict[str, Any],
    requested_books: Set[str],
    home_team: str,
    away_team: str,
) -> Dict[str, Any]:
    home_aliases = _build_team_aliases(
        home_team,
        event_data.get("home_team_abbrev"),
        event_data.get("home_team_id"),
        event_data.get("home_team_market")
    )
    away_aliases = _build_team_aliases(
        away_team,
        event_data.get("away_team_abbrev"),
        event_data.get("away_team_id"),
        event_data.get("away_team_market")
    )
    
    players_by_team: Dict[str, Dict[str, Dict[str, Any]]] = {
        "home": {},
        "away": {},
        "unknown": {},
    }
    
    seen_keys: Set[tuple] = set()
    raw_props = _gather_event_props(event_data)
    
    for raw_book, prop in raw_props:
        canonical_book = normalize_book_name(raw_book) or raw_book.lower()
        if canonical_book not in requested_books:
            continue
        
        canonical_stat = canonicalize_stat_type(
            prop.get("stat_type") or prop.get("stat_type_name") or prop.get("market_type") or "",
            prop.get("sport") or event_data.get("sport") or ""
        )
        player_name = prop.get("player_name") or ""
        if not player_name or not canonical_stat:
            continue
        
        line_value = prop.get("line") or prop.get("value") or prop.get("stat_value")
        direction = prop.get("direction")
        dedupe_key = (
            player_name.lower(),
            canonical_stat,
            line_value,
            direction,
            canonical_book,
        )
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        
        team_bucket = _resolve_prop_team(prop, home_aliases, away_aliases)
        player_id = prop.get("player_id") or prop.get("player_uuid") or player_name.lower()
        bucket = players_by_team[team_bucket]
        if player_id not in bucket:
            bucket[player_id] = {
                "player_id": prop.get("player_id"),
                "player_name": player_name,
                "props": []
            }
        
        bucket[player_id]["props"].append({
            "stat_type": canonical_stat,
            "stat_display": canonical_to_display_name(canonical_stat),
            "line": line_value,
            "direction": direction,
            "odds": prop.get("odds") or prop.get("price"),
            "book": canonical_book,
            "market_type": canonical_stat,
            "source": prop.get("source"),
        })
    
    def format_team(team_key: str, team_name: str) -> Dict[str, Any]:
        players = list(players_by_team[team_key].values())
        return {
            "team_name": team_name,
            "players": players,
            "total_props": sum(len(player["props"]) for player in players)
        }
    
    result = {
        "home_team": format_team("home", home_team),
        "away_team": format_team("away", away_team),
    }
    
    if players_by_team["unknown"]:
        result["unknown_team"] = format_team("unknown", "unknown")
    
    return result


def _normalize_for_ai(cached_event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize cached event data for AI consumption.
    
    Transforms raw sportsbook data into clean, structured format
    that's easy for AI systems to understand and process.
    """
    try:
        # Prefer explicit start_time, but fall back to commence_time from canonical events
        start_time = cached_event.get("start_time") or cached_event.get("commence_time")

        normalized = {
            "event_id": cached_event.get("canonical_event_id"),
            "sport": cached_event.get("sport"),
            "home_team": cached_event.get("home_team"),
            "away_team": cached_event.get("away_team"),
            "start_time": start_time,
            "status": cached_event.get("status", "scheduled"),
            
            # Normalized markets
            "markets": {
                "h2h": [],
                "spreads": [],
                "totals": [],
                "team_totals": [],
                "player_props": []
            },
            
            # Raw book data for reference
            "books": cached_event.get("books", {}),
            "provenance": cached_event.get("provenance", {})
        }
        
        # Prefer explicit odds_by_book / props_by_book if present; otherwise derive from
        # the canonical event structure stored by the V6 background worker.
        books_section = cached_event.get("books") or {}

        odds_by_book = cached_event.get("odds_by_book")
        if not isinstance(odds_by_book, dict):
            odds_by_book = {}
            if isinstance(books_section, dict):
                for book_name, book_data in books_section.items():
                    if not isinstance(book_data, dict):
                        continue
                    odds_list = book_data.get("odds") or []
                    if isinstance(odds_list, list) and odds_list:
                        odds_by_book[book_name] = {"odds": odds_list}
        for book_name, book_data in odds_by_book.items():
            if not isinstance(book_data, dict):
                continue
                
            odds = book_data.get("odds", [])
            if not isinstance(odds, list):
                continue
            
            for odd in odds:
                if not isinstance(odd, dict):
                    continue
                
                # Extract market info
                market_type = odd.get("market_type", "")
                market_key = odd.get("market_key", "")
                
                # Normalize market type
                canonical_market = normalize_market_key(market_type, market_key)
                
                # Build normalized odd entry
                normalized_odd = {
                    "book": book_name,
                    "market_type": canonical_market,
                    "selection": odd.get("selection", ""),
                    "odds": odd.get("odds"),
                    "line": odd.get("line"),
                    "timestamp": odd.get("timestamp")
                }
                
                # Add to appropriate market category
                if canonical_market in normalized["markets"]:
                    normalized["markets"][canonical_market].append(normalized_odd)
        
        # Normalize player props
        props_by_book = cached_event.get("props_by_book")
        if not isinstance(props_by_book, dict):
            props_by_book = {}
            # First, try per-book props stored under books[book]["props"]
            if isinstance(books_section, dict):
                for book_name, book_data in books_section.items():
                    if not isinstance(book_data, dict):
                        continue
                    props_list = book_data.get("props") or []
                    if isinstance(props_list, list) and props_list:
                        props_by_book[book_name] = props_list

            # Also fold in any flattened props list that carries a source/book field
            flat_props = cached_event.get("props") or []
            if isinstance(flat_props, list):
                for prop in flat_props:
                    if not isinstance(prop, dict):
                        continue
                    book_name = prop.get("source") or prop.get("book") or "unknown"
                    props_by_book.setdefault(book_name, []).append(prop)
        all_player_props = []
        
        for book_name, book_props in props_by_book.items():
            if not isinstance(book_props, list):
                continue
            
            for prop in book_props:
                if not isinstance(prop, dict):
                    continue
                
                # Build normalized prop entry
                normalized_prop = {
                    "book": book_name,
                    "player_id": prop.get("player_id"),
                    "player_name": prop.get("player_name"),
                    "player_team": prop.get("player_team"),
                    "stat_type": prop.get("stat_type"),
                    "stat_value": prop.get("stat_value") or prop.get("value"),
                    "direction": prop.get("direction"),  # over/under
                    "odds": prop.get("odds"),
                    "market_type": "player_props",  # All props normalized to this
                    "game_start": prop.get("game_start")
                }
                
                all_player_props.append(normalized_prop)
        
        # Group player props by player and stat type for easier AI consumption
        player_props_grouped = {}
        for prop in all_player_props:
            player_key = f"{prop['player_name']}_{prop['stat_type']}"
            if player_key not in player_props_grouped:
                player_props_grouped[player_key] = {
                    "player_name": prop["player_name"],
                    "player_id": prop["player_id"],
                    "player_team": prop["player_team"],
                    "stat_type": prop["stat_type"],
                    "stat_value": prop["stat_value"],
                    "books": []
                }
            
            player_props_grouped[player_key]["books"].append({
                "book": prop["book"],
                "direction": prop["direction"],
                "odds": prop["odds"]
            })
        
        normalized["markets"]["player_props"] = list(player_props_grouped.values())
        
        # Add summary stats for AI
        normalized["summary"] = {
            "total_books": len(set(list(odds_by_book.keys()) + list(props_by_book.keys()))),
            "has_odds": len([m for market in normalized["markets"].values() if market for m in market]) > 0,
            "has_player_props": len(normalized["markets"]["player_props"]) > 0,
            "player_prop_count": len(normalized["markets"]["player_props"]),
            "market_types": [k for k, v in normalized["markets"].items() if v]
        }
        
        return normalized
        
    except Exception as exc:
        logger.error("Error normalizing event for AI", error=str(exc), exc_info=True)
        # Return original data if normalization fails
        return cached_event


@router.get("/event/{canonical_event_id}")
async def get_cached_event(
    canonical_event_id: str = Path(..., description="Canonical event ID"),
    include: str = Query("props,books", description="Comma-separated list: props,books,ev_slips (default: props,books)"),
    normalize: bool = Query(True, description="Return AI-friendly normalized data (default: true)"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """
    Get unified event from Redis cache with AI-friendly normalization.
    
    This endpoint serves pre-processed data from Redis cache, providing
    instant responses without hitting rate-limited external APIs.
    
    When normalize=true, returns clean structured data optimized for AI consumption:
    - Markets grouped by type (h2h, spreads, totals, player_props)
    - Player props grouped by player and stat type
    - Consistent market naming across all sportsbooks
    - Summary statistics for easy processing
    """
    # Validate API key
    if not validate_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    cache_manager = await get_cache_manager()
    
    # Look up event from cache
    cached_event = await cache_manager.get_event(canonical_event_id)
    
    if not cached_event:
        raise HTTPException(
            status_code=404,
            detail=f"Event not found: {canonical_event_id}. Event may not be in cache yet. Use /v6/match to discover events."
        )
    
    # Normalize data for AI consumption if requested
    if normalize:
        response_data = _normalize_for_ai(cached_event)
    else:
        response_data = cached_event
    
    # Parse include flags
    include_flags = set(flag.strip() for flag in str(include).split(","))
    
    # Filter response based on include flags
    response = dict(response_data)
    
    if "props" not in include_flags:
        response["props"] = None
    if "books" not in include_flags:
        response["books"] = None
    if "ev_slips" not in include_flags:
        response["ev_slips"] = None
    
    return response


@router.get("/match")
async def get_cached_match(
    sport: str = Query(..., description="Sport key (e.g., basketball_nba)"),
    home_team: Optional[str] = Query(None, description="Home team name (optional)"),
    away_team: Optional[str] = Query(None, description="Away team name (optional)"),
    markets: str = Query("h2h,spreads,totals", description="Comma-separated markets to include"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """
    Discovery endpoint for finding cached events.
    
    This endpoint queries Redis cache to find pre-processed event stories.
    """
    # Validate API key against control-plane (with legacy fallback)
    await _require_valid_api_key(authorization)
    
    cache_manager = await get_cache_manager()
    
    try:
        # If specific match requested, find canonical_event_id
        if home_team and away_team:
            # Look up canonical_event_id by teams
            canonical_id = await cache_manager.get_lookup_key(sport, home_team, away_team)
            
            if canonical_id:
                # Get event data
                event_data = await cache_manager.get_event(canonical_id)
                
                if event_data:
                    # Filter by markets if needed
                    markets_list = [m.strip() for m in str(markets).split(",")]
                    if markets_list and "all" not in markets_list:
                        # Filter markets in response
                        if "markets" in event_data and event_data["markets"]:
                            filtered_markets = [
                                market for market in event_data["markets"]
                                if market.get("key", "").lower() in [m.lower() for m in markets_list]
                            ]
                            event_data["markets"] = filtered_markets
                    
                    return {
                        "events": [event_data],
                        "count": 1,
                        "sport": sport,
                        "generated_at": datetime.utcnow().isoformat()
                    }
                else:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Match found but event data not available yet. Try again in a few seconds."
                    )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Match not found: {home_team} vs {away_team} in {sport}. Event may not be in cache yet."
                )
        else:
            # Return all events for this sport
            event_ids = await cache_manager.get_sport_events(sport)
            
            if not event_ids:
                return {
                    "sport": sport,
                    "games": [],
                    "count": 0,
                    "message": "No events found in cache. Background worker may still be processing.",
                    "generated_at": datetime.utcnow().isoformat()
                }
            
            # Fetch all events
            games_list = []
            for event_id in event_ids[:10000]:  # Limit to prevent memory issues
                event_data = await cache_manager.get_event(event_id)
                
                if event_data:
                    # Build complete game entry with all books' odds
                    games_list.append({
                        "canonical_event_id": event_data.get("canonical_event_id"),
                        "home_team": event_data.get("home_team"),
                        "away_team": event_data.get("away_team"),
                        "sport": event_data.get("sport"),
                        "commence_time": event_data.get("commence_time"),
                        "markets": event_data.get("markets", {}),
                        "books": event_data.get("books", {}),
                        "props": event_data.get("props", []),
                        "provenance": event_data.get("provenance", {}),
                        "source_count": event_data.get("provenance", {}).get("source_count", 0)
                    })
            
            return {
                "sport": sport,
                "games": games_list,
                "count": len(games_list),
                "generated_at": datetime.utcnow().isoformat()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in cached match discovery", sport=sport, home_team=home_team, away_team=away_team, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/match/ev")
async def get_ev_match(
    sport: str = Query(..., description="Sport key (e.g., basketball_nba)"),
    canonical_event_id: Optional[str] = Query(None, description="Canonical event ID (optional if home_team and away_team provided)"),
    home_team: Optional[str] = Query(None, description="Home team name (optional if canonical_event_id provided)"),
    away_team: Optional[str] = Query(None, description="Away team name (optional if canonical_event_id provided)"),
    books: Optional[str] = Query(None, description="Optional comma-separated list of sportsbooks to include"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """Get EV-enhanced player prop markets for a single event from cache.

    Returns a clean event + markets + offers + provenance structure for
    easier consumption by clients.
    """

    # Validate API key against control-plane (with legacy fallback)
    await _require_valid_api_key(authorization)

    cache_manager = await get_cache_manager()

    # Resolve canonical_event_id
    canonical_id = canonical_event_id
    if not canonical_id:
        if home_team and away_team:
            canonical_id = await cache_manager.get_lookup_key(sport, home_team, away_team)
            if not canonical_id:
                raise HTTPException(
                    status_code=404,
                    detail=f"Match not found: {home_team} vs {away_team} in {sport}. Event may not be in cache yet.",
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Must provide either canonical_event_id or both home_team and away_team",
            )

    event_data = await cache_manager.get_event(canonical_id)
    if not event_data:
        raise HTTPException(
            status_code=404,
            detail=f"Event not found: {canonical_id}. Event may not be in cache yet.",
        )

    # Optional sportsbook filter
    requested_books: Optional[Set[str]] = None
    if books:
        requested_books = _normalize_book_list(books)

    # Build event envelope
    home = event_data.get("home_team")
    away = event_data.get("away_team")
    commence_time = event_data.get("commence_time") or event_data.get("start_time")
    sport_value = event_data.get("sport") or sport

    game_string = None
    if home and away and commence_time:
        game_string = f"{away} @ {home} {commence_time}"

    event_payload: Dict[str, Any] = {
        "canonical_event_id": event_data.get("canonical_event_id") or canonical_id,
        "sport": sport_value,
        "home_team": home,
        "away_team": away,
        "commence_time": commence_time,
        "game_string": game_string,
    }

    # Extract EV props for this event from books section
    books_section = event_data.get("books") or {}
    ev_props: List[Dict[str, Any]] = []

    for source_name, book_payload in books_section.items():
        if not isinstance(book_payload, dict):
            continue

        props_candidates: List[Dict[str, Any]] = []
        if isinstance(book_payload.get("props"), list):
            props_candidates.extend(book_payload["props"])
        if isinstance(book_payload.get("player_props"), list):
            props_candidates.extend(book_payload["player_props"])
        if isinstance(book_payload.get("props_by_market"), dict):
            for market_props in book_payload["props_by_market"].values():
                if isinstance(market_props, list):
                    props_candidates.extend(market_props)

        for prop in props_candidates:
            if not isinstance(prop, dict):
                continue

            has_ev_indicators = (
                prop.get("ev_edge_value") is not None
                or prop.get("walter_probability") is not None
                or prop.get("walter_value") is not None
                or prop.get("expected_value") is not None
                or prop.get("best_ev") is not None
                or prop.get("no_vig_odds") is not None
                or prop.get("no_vig_probability") is not None
                or prop.get("model_edge") is not None
                or source_name in ["walter", "rotowire", "proply"]
                or prop.get("source") in ["walter", "rotowire", "proply"]
            )
            if not has_ev_indicators:
                continue

            # Determine canonical sportsbook name
            book_name = (
                normalize_book_name(prop.get("book"))
                or normalize_book_name(source_name)
                or (prop.get("book") or source_name).strip().lower()
            )

            if requested_books and book_name not in requested_books:
                continue

            # Attach event context
            ev_prop = dict(prop)
            ev_prop.update(
                {
                    "event_id": event_payload["canonical_event_id"],
                    "home_team": home,
                    "away_team": away,
                    "sport": sport_value,
                    "event_time": ev_prop.get("event_time") or commence_time,
                    "book": book_name,
                }
            )
            ev_props.append(ev_prop)

    # If no EV props found, return empty markets
    provenance = event_data.get("provenance", {})
    if not ev_props:
        return {
            "event": event_payload,
            "markets": [],
            "provenance": {
                "source": provenance.get("sources") or ["kashrock"],
                "engine_version": provenance.get("engine_version", "v6"),
                "fetched_at": provenance.get("fetched_at", datetime.now(timezone.utc).isoformat()),
            },
        }

    # Group EV props into markets + offers
    markets_by_key: Dict[tuple, Dict[str, Any]] = {}

    for prop in ev_props:
        try:
            player_name = (prop.get("player_name") or "").strip()
            if not player_name:
                continue

            raw_stat = (
                prop.get("prop")
                or prop.get("stat_type_name")
                or prop.get("stat_type")
                or prop.get("market_type")
                or ""
            )
            canonical_id = canonicalize_stat_type(raw_stat, sport_value)
            if not canonical_id or canonical_id == "UNKNOWN_STAT":
                continue

            line_value = prop.get("line", prop.get("value"))
            period = prop.get("period") or "full_game"

            player_id = prop.get("player_id") or prop.get("player_uuid") or player_name.lower()
            team = prop.get("team") or prop.get("player_team")
            opponent = prop.get("opponent")
            if not opponent and team and home and away:
                if team == home:
                    opponent = away
                elif team == away:
                    opponent = home

            market_key = (player_id, canonical_id, line_value, period)

            if market_key not in markets_by_key:
                markets_by_key[market_key] = {
                    "market": {
                        "prop_id": prop.get("prop_id"),
                        "player_id": player_id,
                        "player_name": player_name,
                        "team": team,
                        "opponent": opponent,
                        "stat_type": canonical_to_display_name(canonical_id),
                        "market_type": canonical_id,
                        "line": line_value,
                        "period": period,
                    },
                    "offers": [],
                }

            offer = {
                "book": prop.get("book"),
                "direction": prop.get("direction"),
                "odds": prop.get("odds"),
                "no_vig_odds": prop.get("no_vig_odds"),
                "no_vig_probability": prop.get("no_vig_probability"),
                "ev_edge_value": prop.get("ev_edge_value", prop.get("model_edge")),
                "expected_value": prop.get("expected_value"),
                "best_ev": prop.get("best_ev"),
                "link_to_sportsbook": prop.get("link_to_sportsbook") or prop.get("sportsbook_url"),
                "last_updated": prop.get("ev_timestamp") or provenance.get("fetched_at"),
            }

            # Drop null fields for cleaner offers
            clean_offer = {k: v for k, v in offer.items() if v is not None}
            markets_by_key[market_key]["offers"].append(clean_offer)

        except Exception:
            # Skip any malformed EV prop rather than failing the whole response
            continue

    markets = [
        {"market": entry["market"], "offers": entry["offers"]}
        for entry in markets_by_key.values()
        if entry["offers"]
    ]

    return {
        "event": event_payload,
        "markets": markets,
        "provenance": {
            "source": provenance.get("sources") or ["kashrock"],
            "engine_version": provenance.get("engine_version", "v6"),
            "fetched_at": provenance.get("fetched_at", datetime.now(timezone.utc).isoformat()),
        },
    }


@router.get("/spreads")
async def get_cached_spreads(
    sport: str = Query(..., description="Sport key (e.g., basketball_nba)"),
    home_team: Optional[str] = Query(None, description="Home team name (optional)"),
    away_team: Optional[str] = Query(None, description="Away team name (optional)"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """
    Get spread markets from Redis cache.
    
    This endpoint queries Redis cache for point spreads from pre-processed events.
    """
    # Validate API key
    if not validate_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    cache_manager = await get_cache_manager()
    
    try:
        games_list: List[Dict[str, Any]] = []

        def extract_spreads(event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Extract spread markets from event data."""
            spreads = []
            
            # Extract from odds_by_book (traditional markets stored as game objects)
            odds_by_book = event_data.get("odds_by_book", {})
            for book_name, game_data in odds_by_book.items():
                if isinstance(game_data, dict):
                    # Look for markets/odds array in the game data
                    markets = game_data.get("markets", [])
                    for market in markets:
                        if market.get("market_type", "").lower() == "spread":
                            spreads.append({**market, "book": book_name})
                    
                    # Also check for direct odds array
                    odds = game_data.get("odds", [])
                    for odd in odds:
                        if odd.get("market_type", "").lower() == "spread":
                            spreads.append({**odd, "book": book_name})
            
            return spreads

        if home_team and away_team:
            # Find specific match
            canonical_id = await cache_manager.get_lookup_key(sport, home_team, away_team)
            
            if canonical_id:
                event_data = await cache_manager.get_event(canonical_id)
                
                if event_data:
                    spreads = extract_spreads(event_data)
                    if spreads:
                        games_list.append({
                            "match": {
                                "home_team": event_data.get("home_team"),
                                "away_team": event_data.get("away_team"),
                                "sport": event_data.get("sport"),
                                "commence_time": event_data.get("commence_time"),
                            },
                            "spreads": spreads
                        })
        else:
            # Get all events for sport
            event_ids = await cache_manager.get_sport_events(sport)
            
            for event_id in event_ids:
                event_data = await cache_manager.get_event(event_id)
                
                if event_data:
                    spreads = extract_spreads(event_data)
                    if spreads:
                        games_list.append({
                            "match": {
                                "home_team": event_data.get("home_team"),
                                "away_team": event_data.get("away_team"),
                                "sport": event_data.get("sport"),
                                "commence_time": event_data.get("commence_time"),
                            },
                            "spreads": spreads
                        })

        return {
            "sport": sport,
            "games": games_list,
            "total_games": len(games_list),
        }

    except Exception as exc:
        logger.error("Error fetching spreads from cache", sport=sport, error=str(exc))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/ev-props")
async def get_cached_ev_props(
    sport: str = Query(..., description="Sport key (e.g., basketball_nba)"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """Get KashRock EV-enhanced player props from Redis cache.

    This endpoint serves player props with Expected Value (EV) calculations
    and edge analysis from KashRock EV sources, helping clients identify
    value betting opportunities.
    """

    # Validate API key against control-plane (with legacy fallback)
    await _require_valid_api_key(authorization)
    
    cache_manager = await get_cache_manager()
    
    try:
        ev_props_list: List[Dict[str, Any]] = []

        def extract_ev_props(event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Extract EV-enhanced props from event data."""
            ev_props = []
            
            # Read from props_by_book for Walter props
            props_by_book = event_data.get("props_by_book", {})
            
            for book_name, props in props_by_book.items():
                if not isinstance(props, list):
                    continue
                
                for prop in props:
                    # Include all EV source props (Walter, Lunosoft, Rotowire) - deduplication happens later
                    ev_props.append({
                        **prop,
                        "book": book_name,
                        "event_id": event_data.get("canonical_event_id"),
                        "home_team": event_data.get("home_team"),
                        "away_team": event_data.get("away_team"),
                        "sport": event_data.get("sport"),
                        "start_time": event_data.get("start_time")
                    })
            
            return ev_props

        # Get all events for sport
        event_ids = await cache_manager.get_sport_events(sport)
        
        for event_id in event_ids:
            event_data = await cache_manager.get_event(event_id)
            
            if event_data:
                ev_props = extract_ev_props(event_data)
                ev_props_list.extend(ev_props)

        # Group by player and stat for better organization
        grouped_props = {}
        for prop in ev_props_list:
            player_key = f"{prop.get('player_name', '')}_{prop.get('stat_type', '')}"
            if player_key not in grouped_props:
                grouped_props[player_key] = {
                    "player_name": prop.get("player_name"),
                    "player_team": prop.get("player_team"),
                    "stat_type": prop.get("stat_type"),
                    "stat_value": prop.get("stat_value"),
                    "home_team": prop.get("home_team"),
                    "away_team": prop.get("away_team"),
                    "sport": prop.get("sport"),
                    "start_time": prop.get("start_time"),
                    "books": []
                }
            
            grouped_props[player_key]["books"].append({
                "book": prop.get("book"),
                "direction": prop.get("direction"),
                "odds": prop.get("odds"),
                "ev_edge_value": prop.get("ev_edge_value"),
                "walter_probability": prop.get("walter_probability"),
                "no_vig_odds": prop.get("no_vig_odds"),
                "no_vig_probability": prop.get("no_vig_probability")
            })
        
        # Sort by best EV edge
        sorted_props = sorted(
            grouped_props.values(),
            key=lambda x: max([book.get("ev_edge_value", 0) for book in x["books"]] or [0]),
            reverse=True
        )

        return {
            "sport": sport,
            "ev_props": sorted_props,
            "total_props": len(sorted_props),
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as exc:
        logger.error("Error fetching EV props from cache", sport=sport, error=str(exc))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/player_props")
async def get_cached_player_props(
    sport: str = Query(..., description="Sport key (e.g., basketball_nba)"),
    home_team: Optional[str] = Query(None, description="Home team name (optional)"),
    away_team: Optional[str] = Query(None, description="Away team name (optional)"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """Get player props from Redis cache.

    This endpoint queries Redis cache for player props from pre-processed events.
    """

    # Validate API key against control-plane (with legacy fallback)
    await _require_valid_api_key(authorization)
    
    cache_manager = await get_cache_manager()
    
    try:
        games_list: List[Dict[str, Any]] = []

        def extract_player_props(event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Extract player props from event data, filtering out traditional markets."""
            all_props = []
            
            # Try new V6 structure: books[book_name].props
            books = event_data.get("books", {})
            if books:
                for book_name, book_data in books.items():
                    if isinstance(book_data, dict):
                        props = book_data.get("props", [])
                        if isinstance(props, list):
                            for prop in props:
                                # Filter out traditional markets that have team matchups as player_name
                                player_name = prop.get("player_name", "")
                                market_type = prop.get("market_type", "").lower()
                                
                                # Skip if it's a traditional market or player_name looks like a matchup
                                if market_type in ["spread", "total", "moneyline"]:
                                    continue
                                if " vs " in player_name or " @ " in player_name:
                                    continue

                                # Skip any props coming from EV providers entirely
                                if str(prop.get("source") or "").lower() in {"walter", "rotowire", "proply"}:
                                    continue
                                
                                # Filter out any props with EV calculations or EV fair-value fields
                                if (
                                    prop.get("ev_edge_value") is not None
                                    or prop.get("walter_probability") is not None
                                    or prop.get("walter_value") is not None
                                    or prop.get("expected_value") is not None
                                    or prop.get("best_ev") is not None
                                    or prop.get("no_vig_odds") is not None
                                    or prop.get("no_vig_probability") is not None
                                    or prop.get("model_edge") is not None
                                ):
                                    continue
                                
                                # Ensure stat_value is included from value field if missing
                                if prop.get("stat_value") is None and prop.get("value") is not None:
                                    prop = dict(prop)  # Make a copy to avoid modifying original
                                    prop["stat_value"] = prop["value"]

                                # Attach canonical mapping fields
                                sport_value = prop.get("sport") or event_data.get("sport") or sport
                                raw_stat = (
                                    prop.get("stat_type_name")
                                    or prop.get("stat_type")
                                    or prop.get("market_type")
                                    or ""
                                )
                                canonical_id = canonicalize_stat_type(raw_stat, sport_value)

                                prop = dict(prop)
                                prop["canonical_stat_type"] = canonical_id

                                # Drop raw stat fields and any legacy stat_display; rely only on canonical_stat_type
                                for _k in ("stat_type_name", "stat_type", "market_type", "stat_display"):
                                    prop.pop(_k, None)
                                
                                # Remove player_link field for privacy/data minimization
                                prop.pop("player_link", None)
                                    
                                all_props.append(prop)
            
            if all_props:
                return all_props
            
            # Fallback: try props_by_book structure
            props_by_book = event_data.get("props_by_book", {})
            if props_by_book:
                for book_name, props in props_by_book.items():
                    if isinstance(props, list):
                        for prop in props:
                            player_name = prop.get("player_name", "")
                            market_type = prop.get("market_type", "").lower()
                            
                            if market_type in ["spread", "total", "moneyline"]:
                                continue
                            if " vs " in player_name or " @ " in player_name:
                                continue

                            # Skip any props coming from EV providers entirely
                            if str(prop.get("source") or "").lower() in {"walter", "rotowire", "proply"}:
                                continue
                            
                            # Filter out any props with EV calculations or EV fair-value fields
                            if (
                                prop.get("ev_edge_value") is not None
                                or prop.get("walter_probability") is not None
                                or prop.get("walter_value") is not None
                                or prop.get("expected_value") is not None
                                or prop.get("best_ev") is not None
                                or prop.get("no_vig_odds") is not None
                                or prop.get("no_vig_probability") is not None
                                or prop.get("model_edge") is not None
                            ):
                                continue
                            
                            # Ensure stat_value is included from value field if missing
                            if prop.get("stat_value") is None and prop.get("value") is not None:
                                prop = dict(prop)  # Make a copy to avoid modifying original
                                prop["stat_value"] = prop["value"]

                            # Attach canonical mapping fields
                            sport_value = prop.get("sport") or event_data.get("sport") or sport
                            raw_stat = (
                                prop.get("stat_type_name")
                                or prop.get("stat_type")
                                or prop.get("market_type")
                                or ""
                            )
                            canonical_id = canonicalize_stat_type(raw_stat, sport_value)

                            prop = dict(prop)
                            prop["canonical_stat_type"] = canonical_id

                            # Drop raw stat fields and any legacy stat_display; rely only on canonical_stat_type
                            for _k in ("stat_type_name", "stat_type", "market_type", "stat_display"):
                                prop.pop(_k, None)
                                
                            all_props.append(prop)
            
            if all_props:
                return all_props
            
            # Final fallback: try flat props field, with full filtering to ensure no EV props leak through
            props = event_data.get("props", [])
            if props:
                cleaned_props: List[Dict[str, Any]] = []
                for prop in props:
                    try:
                        player_name = prop.get("player_name", "")
                        market_type = str(prop.get("market_type", "")).lower()

                        # Skip traditional markets or matchup-style player names
                        if market_type in ["spread", "total", "moneyline"]:
                            continue
                        if " vs " in player_name or " @ " in player_name:
                            continue

                        # Filter out any props with EV calculations
                        if (
                            prop.get("ev_edge_value") is not None
                            or prop.get("walter_probability") is not None
                            or prop.get("model_edge") is not None
                            or prop.get("expected_value") is not None
                            or prop.get("best_ev") is not None
                            or prop.get("no_vig_odds") is not None
                            or prop.get("no_vig_probability") is not None
                        ):
                            continue

                        # Ensure stat_value is included from value field if missing
                        if prop.get("stat_value") is None and prop.get("value") is not None:
                            prop = dict(prop)
                            prop["stat_value"] = prop["value"]

                        # Attach canonical mapping fields
                        sport_value = prop.get("sport") or event_data.get("sport") or sport
                        raw_stat = (
                            prop.get("stat_type_name")
                            or prop.get("stat_type")
                            or prop.get("market_type")
                            or ""
                        )
                        canonical_id = canonicalize_stat_type(raw_stat, sport_value)

                        prop = dict(prop)
                        prop["canonical_stat_type"] = canonical_id

                        # Drop raw stat fields and any legacy stat_display; rely only on canonical_stat_type
                        for _k in ("stat_type_name", "stat_type", "market_type", "stat_display"):
                            prop.pop(_k, None)

                        # Remove player_link field for privacy/data minimization
                        prop.pop("player_link", None)

                        cleaned_props.append(prop)
                    except Exception:
                        # If anything goes wrong with a single prop, skip it rather than failing the whole response
                        continue

                if cleaned_props:
                    return cleaned_props
            
            return []

        if home_team and away_team:
            # Find specific match
            canonical_id = await cache_manager.get_lookup_key(sport, home_team, away_team)
            
            if canonical_id:
                event_data = await cache_manager.get_event(canonical_id)
                
                if event_data:
                    props = extract_player_props(event_data)
                    if props:
                        games_list.append({
                            "match": {
                                "home_team": event_data.get("home_team"),
                                "away_team": event_data.get("away_team"),
                                "sport": event_data.get("sport"),
                                "commence_time": event_data.get("commence_time"),
                            },
                            "player_props": props
                        })
        else:
            # Get all events for sport and extract props
            event_ids = await cache_manager.get_sport_events(sport)
            
            for event_id in event_ids[:5000]:  # Limit to prevent memory issues
                event_data = await cache_manager.get_event(event_id)
                
                if event_data:
                    props = extract_player_props(event_data)
                    if props:
                        games_list.append({
                            "match": {
                                "home_team": event_data.get("home_team"),
                                "away_team": event_data.get("away_team"),
                                "sport": event_data.get("sport"),
                                "commence_time": event_data.get("commence_time"),
                            },
                            "player_props": props
                        })
        
        return {
            "sport": sport,
            "games": games_list,
            "count": len(games_list),
            "generated_at": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error("Error fetching cached player props", sport=sport, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/game_bundle")
async def get_game_bundle(
    sport: str = Query(..., description="Sport key (e.g., basketball_nba)"),
    home_team: str = Query(..., description="Home team name"),
    away_team: str = Query(..., description="Away team name"),
    books: str = Query(..., description="Comma-separated list of sportsbooks to include"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """Return a single-game bundle containing main markets and player props.

    Data is served directly from the Redis cache populated by the background
    worker, so responses stay fast and consistent with the /v6 cache endpoints.
    """

    # Validate API key against control-plane (with legacy fallback)
    await _require_valid_api_key(authorization)
    
    requested_books = _normalize_book_list(books)
    cache_manager = await get_cache_manager()
    
    # Lookup canonical event
    canonical_event_id = await cache_manager.get_lookup_key(sport, home_team, away_team)
    if not canonical_event_id:
        raise HTTPException(
            status_code=404,
            detail=f"Match not found: {home_team} vs {away_team} in {sport}. Event may not be cached yet."
        )
    
    event_data = await cache_manager.get_event(canonical_event_id)
    if not event_data:
        raise HTTPException(
            status_code=404,
            detail="Event data not available yet. Try again shortly."
        )
    
    event_start = event_data.get("commence_time")
    try:
        if event_start:
            # convert to datetime for comparison
            parsed_start = datetime.fromisoformat(event_start.replace("Z", "+00:00"))
        else:
            parsed_start = None
    except ValueError:
        parsed_start = None
    
    if parsed_start and parsed_start < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=404,
            detail="Event expired"
        )
    normalized_home = event_data.get("home_team", home_team)
    normalized_away = event_data.get("away_team", away_team)
    
    # Build sections
    markets = _extract_main_markets(event_data, requested_books, normalized_home, normalized_away)
    player_props = _extract_player_props_by_team(event_data, requested_books, normalized_home, normalized_away)
    
    # Compute metadata about coverage
    market_books = {
        entry["book"]
        for section in markets.values()
        for entry in section
    }
    props_books = {
        prop["book"]
        for team in player_props.values()
        if isinstance(team, dict)
        for player in team.get("players", [])
        for prop in player.get("props", [])
    }
    covered_books = sorted(set(market_books) | props_books)

    # Fallback: if no data for the requested books, automatically expand to all
    # books present on the event so callers still get a usable bundle.
    if not covered_books:
        books_section = event_data.get("books") or {}
        all_books_in_event: Set[str] = set()
        if isinstance(books_section, dict):
            for raw_book in books_section.keys():
                canonical = normalize_book_name(raw_book) or raw_book.lower()
                all_books_in_event.add(canonical)

        if all_books_in_event:
            # Rebuild sections using all available books
            requested_books = all_books_in_event
            markets = _extract_main_markets(event_data, requested_books, normalized_home, normalized_away)
            player_props = _extract_player_props_by_team(event_data, requested_books, normalized_home, normalized_away)

            market_books = {
                entry["book"]
                for section in markets.values()
                for entry in section
            }
            props_books = {
                prop["book"]
                for team in player_props.values()
                if isinstance(team, dict)
                for player in team.get("players", [])
                for prop in player.get("props", [])
            }
            covered_books = sorted(set(market_books) | props_books)
    
    commence_time = convert_to_eastern_time(event_data.get("commence_time", ""))
    
    return {
        "sport": sport,
        "canonical_event_id": canonical_event_id,
        "match": {
            "home_team": normalized_home,
            "away_team": normalized_away,
            "event_time": commence_time,
            "league": event_data.get("league"),
            "venue": event_data.get("venue"),
        },
        "markets": markets,
        "player_props": player_props,
        "requested_books": sorted(requested_books),
        "books_with_data": covered_books,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/health/cache")
async def get_cache_health(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """Get Redis cache health status.

    Returns cache performance metrics and connection status.
    """

    # Validate API key against control-plane (with legacy fallback)
    await _require_valid_api_key(authorization)
    
    cache_manager = await get_cache_manager()
    worker = await get_background_worker()
    
    # Get cache health
    cache_health = await cache_manager.health_check()
    
    # Get worker status
    worker_status = await worker.get_worker_status() if worker else {"running": False}
    
    return {
        "cache": cache_health,
        "worker": worker_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/stats")
async def get_cache_stats(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """Get cache statistics and metrics.

    Returns information about cached events, books, and performance.
    """

    # Validate API key against control-plane (with legacy fallback)
    await _require_valid_api_key(authorization)
    
    cache_manager = await get_cache_manager()
    
    try:
        # Get metrics from cache
        metrics = await cache_manager.get_metrics()
        
        # Count events by sport
        sports = ["americanfootball_nfl", "basketball_nba", "baseball_mlb", "icehockey_nhl"]
        sport_counts = {}
        
        for sport in sports:
            event_ids = await cache_manager.get_sport_events(sport)
            sport_counts[sport] = len(event_ids)
        
        return {
            "metrics": metrics or {},
            "events_by_sport": sport_counts,
            "total_events": sum(sport_counts.values()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
    except Exception as e:
        logger.error("Error fetching cache stats", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/admin/cache/clear")
async def clear_cache(
    pattern: Optional[str] = Query(None, description="Key pattern to clear (default: all v6 keys)"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """Clear cache entries (admin endpoint).

    Clears cache entries matching pattern. Use with caution.
    """

    # Validate API key against control-plane (with legacy fallback)
    await _require_valid_api_key(authorization)
    
    cache_manager = await get_cache_manager()
    
    try:
        if pattern is None:
            # Clear all v6 keys
            deleted = await cache_manager.clear_pattern("v6:*")
            message = f"Cleared all V6 cache entries"
        else:
            # Clear specific pattern
            deleted = await cache_manager.clear_pattern(pattern)
            message = f"Cleared cache entries matching pattern: {pattern}"
        
        return {
            "message": message,
            "deleted_keys": deleted,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
    except Exception as e:
        logger.error("Error clearing cache", pattern=pattern, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/")
async def v6_cached_root():
    """
    V6 Cached API - Redis-based News Agency Architecture.
    
    This API serves pre-processed data from Redis cache, providing
    instant responses while protecting external APIs from rate limits.
    
    Architecture:
    1. V6 Background Worker fetches data using optimized engines
    2. Data is processed and stored in Redis cache
    3. API endpoints serve instantly from cache
    
    This combines rate-limit protection with V6's performance optimizations.
    """
    return {
        "version": "6.0.0-cached",
        "description": "Redis-based News Agency with V6 optimized engines",
        "architecture": "V6 Hybrid Model",
        "components": {
            "background_worker": {
                "role": "Fetch data using V6 optimized engines",
                "engines": ["OptimizedOddsEngine", "OptimizedPropsEngine"],
                "features": ["Lazy initialization", "Caching", "Rate limiting", "Circuit breaker"]
            },
            "redis_cache": {
                "role": "Store pre-processed data for instant access",
                "key_structure": "Optimized for V6 performance",
                "ttl": "1 hour for events, 5 minutes for metrics"
            },
            "api_endpoints": {
                "role": "Serve data instantly from Redis cache",
                "benefits": ["No rate limits", "Sub-millisecond responses", "High availability"]
            }
        },
        "primary_endpoints": {
            "GET /v6/event/{canonical_event_id}": "Get unified event from cache",
            "GET /v6/match": "Discovery endpoint for finding events",
            "GET /v6/player_props": "Get player props from cache"
        },
        "monitoring_endpoints": {
            "GET /v6/health/cache": "Cache health and worker status",
            "GET /v6/stats": "Cache statistics and metrics",
            "POST /v6/admin/cache/clear": "Clear cache (admin)"
        },
        "benefits": [
            "Rate limit protection (clients read from Redis, not live APIs)",
            "V6 performance optimizations (lazy loading, caching, circuit breakers)",
            "Optimized V6 key structure for maximum performance",
            "Production ready (metrics, monitoring, error handling)"
        ],
        "usage": "Use /v6/match to discover events, then /v6/event/{canonical_event_id} for full data"
    }


@router.get("/ev")
async def get_kashrock_ev(
    sport: str = Query(..., description="Sport key (e.g., americanfootball_nfl)"),
    books: Optional[str] = Query(None, description="Comma-separated list of sportsbooks to include"),
    raw: bool = Query(False, description="Return raw EV data without canonicalization"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """Get KashRock EV data from Redis cache.
    
    This endpoint serves pre-processed EV data from Redis cache, providing
    instant responses while protecting external APIs from rate limits.
    """

    if not event_data:
        return []
    # Validate API key against control-plane (with legacy fallback)
    await _require_valid_api_key(authorization)
    
    cache_manager = await get_cache_manager()
    
    try:
        ev_props_list: List[Dict[str, Any]] = []
        player_props_list: List[Dict[str, Any]] = []

        def extract_player_props_from_cache(event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Extract player props from cached event data."""
            all_props = []
            
            # Try new V6 structure: books[book_name].props
            books = event_data.get("books", {})
            if books:
                for book_name, book_data in books.items():
                    if isinstance(book_data, dict):
                        props = book_data.get("props", [])
                        if isinstance(props, list):
                            for prop in props:
                                # Filter out traditional markets that have team matchups as player_name
                                player_name = prop.get("player_name", "")
                                market_type = prop.get("market_type", "").lower()
                                
                                # Skip if it's a traditional market or player_name looks like a matchup
                                if market_type in ["spread", "total", "moneyline"]:
                                    continue
                                if " vs " in player_name or " @ " in player_name:
                                    continue
                                
                                # Skip any props coming from EV providers entirely
                                if str(prop.get("source") or "").lower() in {"walter", "rotowire", "proply"}:
                                    continue
                                
                                # Filter out any props with EV calculations or EV fair-value fields
                                if (
                                    prop.get("ev_edge_value") is not None
                                    or prop.get("walter_probability") is not None
                                    or prop.get("walter_value") is not None
                                    or prop.get("expected_value") is not None
                                    or prop.get("best_ev") is not None
                                    or prop.get("no_vig_odds") is not None
                                    or prop.get("no_vig_probability") is not None
                                    or prop.get("model_edge") is not None
                                ):
                                    continue
                                
                                # Ensure stat_value is included from value field if missing
                                if prop.get("stat_value") is None and prop.get("value") is not None:
                                    prop = dict(prop)  # Make a copy to avoid modifying original
                                    prop["stat_value"] = prop["value"]

                                # Attach canonical mapping fields
                                sport_value = prop.get("sport") or event_data.get("sport") or sport
                                raw_stat = (
                                    prop.get("stat_type_name")
                                    or prop.get("stat_type")
                                    or prop.get("market_type")
                                    or ""
                                )
                                canonical_id = canonicalize_stat_type(raw_stat, sport_value)

                                prop = dict(prop)
                                prop["canonical_stat_type"] = canonical_id

                                # Drop raw stat fields and any legacy stat_display; rely only on canonical_stat_type
                                for _k in ("stat_type_name", "stat_type", "market_type", "stat_display"):
                                    prop.pop(_k, None)
                                
                                # Remove player_link field for privacy/data minimization
                                prop.pop("player_link", None)
                                    
                                all_props.append(prop)
            
            if all_props:
                return all_props
            
            # Fallback: try props_by_book structure
            props_by_book = event_data.get("props_by_book", {})
            if props_by_book:
                for book_name, props in props_by_book.items():
                    if isinstance(props, list):
                        for prop in props:
                            player_name = prop.get("player_name", "")
                            market_type = prop.get("market_type", "").lower()
                            
                            if market_type in ["spread", "total", "moneyline"]:
                                continue
                            if " vs " in player_name or " @ " in player_name:
                                continue

                            # Skip any props coming from EV providers entirely
                            if str(prop.get("source") or "").lower() in {"walter", "rotowire", "proply"}:
                                continue
                            
                            # Filter out any props with EV calculations or EV fair-value fields
                            if (
                                prop.get("ev_edge_value") is not None
                                or prop.get("walter_probability") is not None
                                or prop.get("walter_value") is not None
                                or prop.get("expected_value") is not None
                                or prop.get("best_ev") is not None
                                or prop.get("no_vig_odds") is not None
                                or prop.get("no_vig_probability") is not None
                                or prop.get("model_edge") is not None
                            ):
                                continue
                            
                            # Ensure stat_value is included from value field if missing
                            if prop.get("stat_value") is None and prop.get("value") is not None:
                                prop = dict(prop)  # Make a copy to avoid modifying original
                                prop["stat_value"] = prop["value"]

                            # Attach canonical mapping fields
                            sport_value = prop.get("sport") or event_data.get("sport") or sport
                            raw_stat = (
                                prop.get("stat_type_name")
                                or prop.get("stat_type")
                                or prop.get("market_type")
                                or ""
                            )
                            canonical_id = canonicalize_stat_type(raw_stat, sport_value)

                            prop = dict(prop)
                            prop["canonical_stat_type"] = canonical_id

                            # Drop raw stat fields and any legacy stat_display; rely only on canonical_stat_type
                            for _k in ("stat_type_name", "stat_type", "market_type", "stat_display"):
                                prop.pop(_k, None)
                                
                            all_props.append(prop)
            
            if all_props:
                return all_props
            
            # Final fallback: try flat props field, with full filtering to ensure no EV props leak through
            props = event_data.get("props", [])
            if props:
                cleaned_props: List[Dict[str, Any]] = []
                for prop in props:
                    try:
                        player_name = prop.get("player_name", "")
                        market_type = str(prop.get("market_type", "")).lower()

                        # Skip traditional markets or matchup-style player names
                        if market_type in ["spread", "total", "moneyline"]:
                            continue
                        if " vs " in player_name or " @ " in player_name:
                            continue

                        # Filter out any props with EV calculations
                        if (
                            prop.get("ev_edge_value") is not None
                            or prop.get("walter_probability") is not None
                            or prop.get("walter_value") is not None
                            or prop.get("expected_value") is not None
                            or prop.get("best_ev") is not None
                            or prop.get("no_vig_odds") is not None
                            or prop.get("no_vig_probability") is not None
                        ):
                            continue

                        # Ensure stat_value is included from value field if missing
                        if prop.get("stat_value") is None and prop.get("value") is not None:
                            prop = dict(prop)
                            prop["stat_value"] = prop["value"]

                        # Attach canonical mapping fields
                        sport_value = prop.get("sport") or event_data.get("sport") or sport
                        raw_stat = (
                            prop.get("stat_type_name")
                            or prop.get("stat_type")
                            or prop.get("market_type")
                            or ""
                        )
                        canonical_id = canonicalize_stat_type(raw_stat, sport_value)

                        prop = dict(prop)
                        prop["canonical_stat_type"] = canonical_id

                        # Drop raw stat fields and any legacy stat_display; rely only on canonical_stat_type
                        for _k in ("stat_type_name", "stat_type", "market_type", "stat_display"):
                            prop.pop(_k, None)

                        # Remove player_link field for privacy/data minimization
                        prop.pop("player_link", None)

                        cleaned_props.append(prop)
                    except Exception:
                        # If anything goes wrong with a single prop, skip it rather than failing the whole response
                        continue

                if cleaned_props:
                    # Add event information as fallback
                    event_time = event_data.get("start_time") or event_data.get("commence_time", "")
                    for prop in cleaned_props:
                        if not prop.get("event_time"):
                            prop["event_time"] = event_time
                    return cleaned_props
            return []

        def extract_ev_props_from_cache(event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Extract EV-enhanced props from cached event data."""
            ev_props = []
            
            # Read from props_by_book for EV source props
            props_by_book = event_data.get("props_by_book", {})
            
            for book_name, props in props_by_book.items():
                if not isinstance(props, list):
                    continue
                
                for prop in props:
                    # Include props from EV sources - look for any EV-related indicators
                    # Check for EV-specific fields or source names
                    has_ev_indicators = (
                        prop.get("ev_edge_value") is not None or 
                        prop.get("walter_probability") is not None or
                        prop.get("model_edge") is not None or
                        book_name in ["walter", "rotowire", "proply"] or
                        prop.get("source") in ["walter", "rotowire", "proply"]
                    )
                    
                    if has_ev_indicators:
                        ev_props.append({
                            **prop,
                            # Use the book from the prop data, not the EV source name
                            "event_id": event_data.get("canonical_event_id"),
                            "home_team": event_data.get("home_team"),
                            "away_team": event_data.get("away_team"),
                            "sport": event_data.get("sport"),
                            "start_time": event_data.get("start_time")
                        })
            
            # Also check flat props field for EV data
            flat_props = event_data.get("props", [])
            if isinstance(flat_props, list):
                for prop in flat_props:
                    has_ev_indicators = (
                        prop.get("ev_edge_value") is not None or 
                        prop.get("walter_probability") is not None or
                        prop.get("model_edge") is not None or
                        prop.get("source") in ["walter", "rotowire", "proply"]
                    )
                    
                    if has_ev_indicators:
                        ev_props.append({
                            **prop,
                            # Book field should already be correct from the prop data
                            "event_id": event_data.get("canonical_event_id"),
                            "home_team": event_data.get("home_team"),
                            "away_team": event_data.get("away_team"),
                            "sport": event_data.get("sport"),
                            "start_time": event_data.get("start_time")
                        })
            event_time = event_data.get("start_time") or event_data.get("commence_time", "")
            for prop in ev_props:
                if not prop.get("event_time"):
                    prop["event_time"] = event_time
        # Get all events for sport from cache
        event_ids = await cache_manager.get_sport_events(sport)
        
        for event_id in event_ids:
            event_data = await cache_manager.get_event(event_id)
            
            if event_data:
                # Get all player props for this event
                player_props_list.extend(player_props)
                
                # Get EV props for this event
                ev_props = extract_ev_props_from_cache(event_data)
                ev_props_list.extend(ev_props)

        # Create EV lookup for enrichment
        ev_lookup: Dict[tuple, Dict[str, Any]] = {}
        for ev_prop in ev_props_list:
            try:
                canonical_prop = canonicalize_stat_type(ev_prop.get("prop", ""), ev_prop.get("sport", ""))
                key = (
                    (ev_prop.get("player_name") or "").strip().lower(),
                    canonical_prop,
                    ev_prop.get("line"),
                    ev_prop.get("direction"),
                    (ev_prop.get("book") or "").lower(),
                )
                ev_lookup[key] = ev_prop
            except Exception:
                continue

        # Enrich player props with EV data
        enriched_props = []
        for prop in player_props_list:
            try:
                canonical_prop = prop.get("canonical_stat_type", "")
                key = (
                    (prop.get("player_name") or "").strip().lower(),
                    canonical_prop,
                    prop.get("line"),
                    prop.get("direction"),
                    (prop.get("book") or "").lower(),
                )
                
                ev_data = ev_lookup.get(key)
                if ev_data:
                    # Merge EV fields into the prop
                    enriched_prop = dict(prop)
                    enriched_prop.update({
                        "ev_edge_value": ev_data.get("ev_edge_value", ev_data.get("model_edge", 0)),
                        "fair_value": {
                            "no_vig_odds": ev_data.get("no_vig_odds"),
                            "no_vig_probability": ev_data.get("no_vig_probability")
                        },
                        "ev_timestamp": ev_data.get("ev_timestamp", ev_data.get("ev_timestamp")),
                    })
                    enriched_props.append(enriched_prop)
                else:
                    # Include prop even without EV data
                    enriched_props.append(prop)
            except Exception:
                # If enrichment fails, include the prop as-is
                enriched_props.append(prop)

        # Process enriched props similar to the live endpoint
        requested_books: Optional[Set[str]] = None
        if books:
            requested_books = {
                normalize_book_name(book_name) or book_name.strip().lower()
                for book_name in books.split(",")
                if book_name.strip()
            }
            requested_books = {b for b in requested_books if b}
            if not requested_books:
                return {
                    "sport": sport,
                    "ev_props": [],
                    "total_props": 0,
                    "message": "No valid bookmakers after normalization",
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
        
        available_books: Set[str] = set()
        
        # Process enriched props into standardized format
        kashrock_ev_props = []
        
        for prop in enriched_props:
            try:
                # Extract event time
                eastern_event_time = prop.get("event_time", "")
                
                # Extract team data
                raw_team = prop.get("team", prop.get("player_team", ""))
                opponent_name = prop.get("opponent", "")
                
                # Standardize prop format
                book_name = normalize_book_name(prop.get("book", "")) or prop.get("book", "")
                if requested_books and book_name.lower() not in requested_books:
                    continue
                
                available_books.add(book_name.lower())
                
                standardized_prop = {
                    "source": "kashrock",
                    "player_name": prop.get("player_name", ""),
                    "prop": prop.get("canonical_stat_type", ""),
                    "line": prop.get("line", prop.get("value", 0)),
                    "odds": prop.get("odds", prop.get("price", 0)),
                    "direction": prop.get("direction", ""),
                    "book": book_name,
                    "event_time": eastern_event_time,
                    "sport": _normalize_sport_for_display(prop.get("sport", sport)),
                    "team": raw_team,
                    "opponent": opponent_name,
                    "fair_value": prop.get("fair_value", {}),
                    "ev_edge_value": prop.get("ev_edge_value", 0),
                    "ev_timestamp": prop.get("ev_timestamp", ""),
                }
                
                # Only include props with valid player name and prop type
                if standardized_prop["player_name"] and standardized_prop["prop"]:
                    kashrock_ev_props.append(standardized_prop)
                    
            except Exception as e:
                logger.warning(f"Failed to process enriched prop: {e}")
                continue
        
        logger.info(f"Final standardized cached EV props count: {len(kashrock_ev_props)}")
        
        # Deduplicate props (after canonicalization)
        seen_keys: Set[tuple] = set()
        deduped_props: List[Dict[str, Any]] = []
        for prop in kashrock_ev_props:
            key = (
                (prop.get("player_name") or "").strip().lower(),
                prop.get("prop", ""),
                prop.get("line"),
                prop.get("direction"),
                (prop.get("book") or "").lower(),
            )
            if key in seen_keys:
                continue
            seen_keys.add(key)
            deduped_props.append(prop)
        kashrock_ev_props = deduped_props
        
        logger.info("Deduplicated cached EV props", total=len(kashrock_ev_props))
        
        return {
            "sport": sport,
            "source": "kashrock",
            "raw": raw,
            "ev_props": kashrock_ev_props,
            "total_props": len(kashrock_ev_props),
            "ev_sources": ["cached"],  # Indicate this is from cache
            "sportsbooks": sorted(available_books),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error("Error in cached KashRock EV endpoint", sport=sport, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch cached EV data: {str(e)}")


def _normalize_sport_for_display(sport: str) -> str:
    """Normalize sport codes for display in API responses."""
    if not sport:
        return sport
    
    sport_lower = sport.lower()
    if sport_lower == "cbb":
        return "baseball_mlb"
    # Add other mappings as needed
    return sport


def canonical_to_display_name(canonical_id: str) -> str:
    if not canonical_id or canonical_id == "UNKNOWN_STAT":
        return canonical_id
    
    # Remove sport prefix (e.g., "NFL_RECEIVING_YARDS" -> "RECEIVING_YARDS")
    parts = canonical_id.split("_", 1)
    if len(parts) > 1:
        stat_name = parts[1]
    else:
        stat_name = canonical_id
    
    # Convert to title case and replace underscores with spaces
    display_name = stat_name.replace("_", " ").title()
    
    # Handle special cases for better readability
    display_name = display_name.replace("Yds", "Yards")
    display_name = display_name.replace("Tds", "Touchdowns")
    display_name = display_name.replace("Fg", "Field Goals")
    display_name = display_name.replace("Ft", "Free Throws")
    display_name = display_name.replace("Pts", "Points")
    display_name = display_name.replace("Rebs", "Rebounds")
    display_name = display_name.replace("Asts", "Assists")
    display_name = display_name.replace("Stl", "Steals")
    display_name = display_name.replace("Blk", "Blocks")
    
    return display_name


def repackage_to_kashrock(ev_props: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Repackage EV props with consistent KashRock branding and remove source attribution."""
    kashrock_props = []
    
    for prop in ev_props:
        # Apply stat canonicalization
        original_prop = prop.get("prop", "")
        sport = prop.get("sport", "")
        canonical_id = canonicalize_stat_type(original_prop, sport)
        
        # Create KashRock-branded prop
        kashrock_prop = {
            "source": "kashrock",
            "player_name": prop.get("player_name"),
            "prop": canonical_id,  # Use canonical ID directly as prop name
            "line": prop.get("line"),
            "odds": prop.get("odds"),
            "direction": prop.get("direction"),
            "book": prop.get("book"),  # Keep legitimate sportsbook attribution
            "event_time": prop.get("event_time"),
            "sport": prop.get("sport"),
            "team": prop.get("team"),
            "opponent": prop.get("opponent"),
            "fair_value": prop.get("fair_value"),
            # Rebrand EV edge to KashRock
            "kashrock_edge": prop.get("ev_edge_value", 0),
            "ev_timestamp": prop.get("ev_timestamp"),
        }
        
        # Remove source-specific fields that reveal attribution
        # No rationale, pick_id, model_edge, or other source identifiers
        
        kashrock_props.append(kashrock_prop)
    
    return kashrock_props
