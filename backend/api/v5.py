"""
KashRock API v5 - Plug and Play Unified Odds
ONE CALL gets ALL books' odds for ANY match.

So simple, a 5th grader could use it.
"""

from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, Path, Header, Depends
from pydantic import BaseModel, Field
import structlog
import asyncio
import hashlib
import json
from collections import defaultdict

from auth import validate_api_key
# from v5.cache import CacheManager
# from v5.constants import V5_BOOK_MAP
# from v5.utils import (
build_event_lookup_key,
map_sport_key,
normalize_team_name,
normalize_v5_team_name,

router = APIRouter()
logger = structlog.get_logger()

# ACTIVE BOOKS - Start with Novig, add more one by one as they're tested
ACTIVE_BOOKS = [
    "novig",
    "pinnacle", 
    "bovada",
    "rebet",
    "dabble",
    "prizepicks",
    "splashsports",  # DFS-style book like Dabble
    "underdog",      # DFS pick'em book
    "fanduel",
    "rotowire",      # Meta-aggregator with multi-book odds + projections
    "proply",        # Model-driven picks with edge calculations
    "bettingpros",   # Props with projections and bet ratings
    "propgpt",       # AI-analyzed top bets with grades
    "walter",        # 693 props with EV edge across 16 books
    "lunosoft",      # Live Scores & Odds multi-book player props
]  # Novig (sharp probabilities) + Pinnacle (sharp book) + Dabble (soft DFS book) + PrizePicks (DFS pick'em) + SplashSports (DFS book) + Underdog (DFS pick'em) + Rotowire (meta-aggregator) + FanDuel + Proply (picks with edge) + BettingPros (projections) + Rithtim (consensus) + PropGPT (AI analysis) + Walter (EV edge)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class EventResponse(BaseModel):
    """Unified event response with all books, props, merged odds, and EV slips."""
    canonical_event_id: str
    sport: str
    home_team: str
    away_team: str
    commence_time: str
    markets: Optional[Dict[str, Any]] = None  # Merged markets
    books: Optional[Dict[str, Any]] = None  # Per-book odds with full provenance
    props: Optional[List[Dict[str, Any]]] = None  # Player props
    ev_slips: Optional[List[Dict[str, Any]]] = None  # EV slip candidates
    provenance: Dict[str, Any] = Field(default_factory=dict)  # Full provenance tracking
    generated_at: str


class ConnectorHealth(BaseModel):
    """Connector health metrics."""
    source: str
    status: str  # "healthy", "degraded", "down"
    freshness_seconds: Optional[float] = None
    last_success: Optional[str] = None
    error_rate: float = 0.0
    last_error: Optional[str] = None


# ============================================================================
# GLOBAL SERVICES (Initialized on startup)
# ============================================================================

cache_manager: Optional[CacheManager] = None


def initialize_v5_services():
    """Initialize v5 services."""
    global cache_manager
    
    logger.info("Initializing v5 services...")
    
    # Initialize cache manager
    from config import get_settings
    settings = get_settings()
    cache_manager = CacheManager(redis_url=settings.redis_url)
    
    logger.info("v5 services initialized successfully")


async def start_v5_background_worker():
    """Start the v5 background worker (called from main.py startup)."""
    global cache_manager
    
    if not cache_manager:
        initialize_v5_services()
    
    # Map internal sport keys to external ones for sources that need different keys
    sport_key_mapping = {
        "americanfootball_nfl": "football_nfl",
        "americanfootball_ncaaf": "football_cfb",
        # Keep basketball and hockey as-is since most sources support them
        "basketball_nba": "basketball_nba",
        "basketball_ncaab": "basketball_ncaa",
        "icehockey_nhl": "icehockey_nhl",
    }
    
    # Start background worker
    # from v5.background_worker import start_background_worker
    await start_background_worker(
        cache_manager=cache_manager,
        active_books=ACTIVE_BOOKS,
        poll_interval=30.0,  # Poll every 30 seconds
        sports=list(sport_key_mapping.keys()),  # Use internal keys
        sport_key_mapping=sport_key_mapping,  # Pass mapping to worker
    )
    logger.info("v5 background worker started")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/event/{canonical_event_id}")
async def get_unified_event(
    canonical_event_id: str = Path(..., description="Canonical event ID"),
    include: str = Query("props,books", description="Comma-separated list: props,books,ev_slips (default: props,books)"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """
    THE NEWSSTAND - Get unified event by canonical_event_id.
    
    This is the PRIMARY endpoint. It represents "The Newsstand" in our News Agency architecture.
    The API does NOT fetch, process, or calculate anything. It simply looks up the pre-processed
    "event story" from the master database (Redis cache) and delivers it instantly.
    
    The event story was prepared by our background pipeline:
    - Reporters fetched raw data
    - Editors cleaned and standardized it
    - Story builders merged all odds
    - Opportunity finders calculated EV slips
    - Everything stored in the master database
    
    Args:
        canonical_event_id: The canonical event ID (use /match to discover)
        include: Comma-separated list of what to include (props,books,ev_slips)
    
    Returns:
        Complete EventResponse with merged odds, props, and EV slips (pre-processed)
    """
    # Validate API key
    if not validate_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    # Initialize cache if needed
    if not cache_manager:
        initialize_v5_services()
    
    # Look up event from cache
    cache_key = f"v5:event:{canonical_event_id}"
    cached_event = await cache_manager.get(cache_key) if cache_manager else None
    
    if not cached_event:
        raise HTTPException(
            status_code=404,
            detail=f"Event not found: {canonical_event_id}. Event may not be in cache yet. Use /v5/match to discover events."
        )
    
    # Parse include flags
    include_flags = set(flag.strip() for flag in str(include).split(","))
    
    # Filter response based on include flags
    response = dict(cached_event)
    
    if "props" not in include_flags:
        response["props"] = None
    if "books" not in include_flags:
        response["books"] = None
    if "ev_slips" not in include_flags:
        response["ev_slips"] = None
    
    return response


@router.get("/health/connectors")
async def get_connector_health(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """
    Get health status of all connectors (streamers).
    
    Returns available books and their status.
    """
    if not validate_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    health_data = {}
    for book_key in V5_BOOK_MAP.keys():
        health_data[book_key] = {
            "status": "available",
            "streamer_class": V5_BOOK_MAP[book_key].__name__
        }
    
    return {
        "connectors": health_data,
        "total_books": len(V5_BOOK_MAP),
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/match")
async def get_match_unified(
    sport: str = Query(..., description="Sport key (e.g., basketball_nba)"),
    home_team: Optional[str] = Query(None, description="Home team name (optional - if not provided, returns all games)"),
    away_team: Optional[str] = Query(None, description="Away team name (optional - if not provided, returns all games)"),
    markets: str = Query("h2h,spreads,totals", description="Comma-separated markets to include (player_props available on /v5/player_props endpoint)"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """
    THE NEWSSTAND - Discovery endpoint for finding events.
    
    This endpoint helps you discover canonical_event_ids by sport and team names.
    It queries the master database (Redis cache) to find pre-processed event stories.
    
    The News Agency pipeline has already:
    - Fetched raw data from all reporters
    - Archived every raw payload
    - Cleaned and standardized the data
    - Merged odds from all books
    - Calculated EV slips
    - Stored everything in the master database
    
    This endpoint simply looks up the pre-processed data - no fetching or processing.
    
    Usage:
    - All games: GET /v5/match?sport=basketball_nba
    - Specific match: GET /v5/match?sport=basketball_nba&home_team=Lakers&away_team=Warriors
    
    Returns:
        Pre-processed event data from master database, or list of available events
    """
    # Validate API key
    if not validate_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    # Initialize cache if needed
    if not cache_manager:
        initialize_v5_services()
    
    try:
        canonical_sport = map_sport_key(sport)

        # If specific match requested, find canonical_event_id
        if home_team and away_team:
            # Look up canonical_event_id by teams
            lookup_key = build_event_lookup_key(canonical_sport, home_team, away_team)
            print(f"[DEBUG] Querying lookup key: {lookup_key}")
            canonical_id = await cache_manager.get(lookup_key) if cache_manager else None
            print(f"[DEBUG] Found canonical_id: {canonical_id}")
            
            if canonical_id:
                # Redirect to /event/{canonical_event_id} endpoint
                # But for now, just fetch and return the event
                event_key = f"v5:event:{canonical_id}"
                event_data = await cache_manager.get(event_key) if cache_manager else None
                
                if event_data:
                    # Filter by markets if needed
                    markets_list = [m.strip() for m in str(markets).split(",")]
                    if markets_list and "all" not in markets_list:
                        # Filter markets in response
                        if "markets" in event_data and event_data["markets"]:
                            filtered_markets = {
                                k: v for k, v in event_data["markets"].items()
                                if k.lower() in [m.lower() for m in markets_list]
                            }
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
            sport_key = f"v5:sport:{canonical_sport}:events"
            event_ids = await cache_manager.get(sport_key) if cache_manager else []
            
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
            for event_id in event_ids[:5000000]:  
                event_key = f"v5:event:{event_id}"
                event_data = await cache_manager.get(event_key) if cache_manager else None
                
                if event_data:
                    # Build complete game entry with all books' odds
                    games_list.append({
                        "canonical_event_id": event_data.get("canonical_event_id"),
                        "home_team": event_data.get("home_team"),
                        "away_team": event_data.get("away_team"),
                        "sport": event_data.get("sport"),
                        "commence_time": event_data.get("commence_time"),
                        "markets": event_data.get("markets", {}),
                        "books": event_data.get("books", {}),  # Include all books' odds
                        "props": event_data.get("props", []),  # Include all props with sources
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
        logger.error("Error in match discovery", sport=sport, home_team=home_team, away_team=away_team, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/player_props")
async def get_player_props(
    sport: str = Query(..., description="Sport key (e.g., basketball_nba)"),
    home_team: Optional[str] = Query(None, description="Home team name (optional)"),
    away_team: Optional[str] = Query(None, description="Away team name (optional)"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """
    THE NEWSSTAND - Get player props from pre-processed cache.
    
    This endpoint queries the master database (Redis cache) for player props.
    All data comes from pre-processed event stories prepared by the News Agency pipeline.
    
    The pipeline has already:
    - Fetched and archived raw data
    - Standardized player names and stats
    - Merged odds from all books
    - Calculated EV opportunities
    
    This endpoint simply looks up and filters the pre-processed data.
    """
    # Validate API key
    if not validate_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    # Initialize cache if needed
    if not cache_manager:
        initialize_v5_services()
    
    try:
        canonical_sport = map_sport_key(sport)
        games_list: List[Dict[str, Any]] = []

        def extract_player_props(event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Extract player props from event data (from props field or markets)."""
            # First try props field
            props = event_data.get("props", [])
            if props:
                return props
            # If not in props, extract from markets
            markets = event_data.get("markets", {})
            player_props_market = markets.get("player_props", {})
            if player_props_market and isinstance(player_props_market, dict):
                runners = player_props_market.get("runners", [])
                if runners:
                    props_collected: List[Dict[str, Any]] = []
                    for runner in runners:
                        props_collected.append({
                            "player_name": runner.get("player_name"),
                            "stat_type": runner.get("stat_type"),
                            "line": runner.get("line"),
                            "direction": runner.get("direction"),
                            "odds": runner.get("odds"),
                            "sources": runner.get("sources", []),
                            "sources_with_odds": runner.get("sources_with_odds", []),
                            "sources_without_odds": runner.get("sources_without_odds", []),
                            "all_odds": runner.get("all_odds", []),
                        })
                    return props_collected
            return []

        if home_team and away_team:
            # Find specific match
            lookup_key = build_event_lookup_key(canonical_sport, home_team, away_team)
            canonical_id = await cache_manager.get(lookup_key) if cache_manager else None
            
            if canonical_id:
                event_key = f"v5:event:{canonical_id}"
                event_data = await cache_manager.get(event_key) if cache_manager else None
                
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
            sport_key = f"v5:sport:{canonical_sport}:events"
            event_ids = await cache_manager.get(sport_key) if cache_manager else []
            
            for event_id in event_ids[:5000000]:  
                event_key = f"v5:event:{event_id}"
                event_data = await cache_manager.get(event_key) if cache_manager else None
                
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
        logger.error("Error fetching player props", sport=sport, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/events")
async def discover_events(
    sport: str = Query(..., description="Sport key (e.g., basketball_nba)"),
    home_team: Optional[str] = Query(None, description="Home team name"),
    away_team: Optional[str] = Query(None, description="Away team name"),
    limit: int = Query(2000000, description="Maximum number of events to return"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """
    Discover events from v5 cache - use /match endpoint for direct access instead.
    
    This endpoint is for discovery only. For getting full event data, use /event/{id} or /match with teams directly.
    """
    # Validate API key
    if not validate_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    # Get events from v5 cache
    try:
        canonical_sport = map_sport_key(sport)

        # Get all event keys for this sport from cache
        if not cache_manager:
            raise HTTPException(status_code=503, detail="Cache not available")
        
        # Get sport-specific event list
        sport_events_key = f"v5:sport:{canonical_sport}:events"
        event_ids = await cache_manager.get(sport_events_key) or []
        
        if not event_ids:
            return {
                "events": [],
                "count": 0,
                "sport": sport,
                "generated_at": datetime.utcnow().isoformat()
            }
        
        # Filter by team names if specified
        if home_team or away_team:
            filtered_events = []
            for event_id in event_ids[:limit * 2000000]:  
                event_key = f"v5:event:{event_id}"
                event_data = await cache_manager.get(event_key)
                if event_data:
                    event_home = normalize_v5_team_name(event_data.get("home_team", ""), canonical_sport)
                    event_away = normalize_v5_team_name(event_data.get("away_team", ""), canonical_sport)

                    match = True
                    if home_team and normalize_v5_team_name(home_team, canonical_sport) not in event_home:
                        match = False
                    if away_team and normalize_v5_team_name(away_team, canonical_sport) not in event_away:
                        match = False
                    
                    if match:
                        filtered_events.append(event_data)
                        if len(filtered_events) >= limit:
                            break
            
            events_list = filtered_events
        else:
            # Get events up to limit
            events_list = []
            for event_id in event_ids[:limit]:
                event_key = f"v5:event:{event_id}"
                event_data = await cache_manager.get(event_key)
                if event_data:
                    events_list.append(event_data)
        
        return {
            "events": events_list,
            "count": len(events_list),
            "sport": sport,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to discover events", error=str(e), sport=sport)
        raise HTTPException(status_code=500, detail="Failed to discover events")


@router.get("/")
async def v5_root():
    """
    v5 API - The News Agency Architecture
    
    Our system follows a "News Agency" model: we proactively prepare all data
    in the background, so the API (The Newsstand) can deliver it instantly.
    
    THE NEWS AGENCY PIPELINE (Background Worker):
    
    1. THE REPORTERS (ConnectorAdapter)
       - Specialized agents for each sportsbook
       - Fetch raw odds data as fast as possible
       - Overcome Cloudflare, cookies, rate limits
    
    2. RAW DATA ARCHIVES (RawDataArchive)
       - Every raw payload immediately stored permanently
       - Like a library of every report we've ever received
       - For replays, audits, and debugging
    
    3. THE EDITORS
       - Standardizers (MappingWorker): Clean and normalize data
       - Matchmakers (EntityResolver): Link related data, assign canonical_event_ids
    
    4. THE STORY BUILDERS (MergeService)
       - Combine all odds from all books into unified event stories
       - Preserve full provenance (where each odd came from)
    
    5. THE OPPORTUNITY FINDERS (EVEngine)
       - Analyze events for profitable betting opportunities
       - Calculate Expected Value slips with ROI
    
    6. THE MASTER DATABASE (Redis Cache)
       - Store complete, pre-processed event stories
       - Super-fast lookup and retrieval
    
    7. THE NEWSSTAND (This API)
       - API endpoints that ONLY query the master database
       - NO fetching, NO processing, NO calculations
       - Just instant delivery of pre-prepared data
    
    PRIMARY ENDPOINT: GET /v5/event/{canonical_event_id}
    DISCOVERY ENDPOINT: GET /v5/match
    """
    return {
        "version": "5.0.0",
        "description": "The News Agency - Proactive data preparation pipeline",
        "architecture": "News Agency Model",
        "pipeline_stages": {
            "1_the_reporters": {
                "component": "ConnectorAdapter",
                "role": "Fetch raw data from all sportsbooks as fast as possible",
                "output": "Raw envelopes with full payloads"
            },
            "2_raw_data_archives": {
                "component": "RawDataArchive",
                "role": "Store every raw payload permanently (like a library)",
                "output": "Archived raw data for replays, audits, debugging"
            },
            "3_the_editors": {
                "standardizers": {
                    "component": "MappingWorker",
                    "role": "Clean and normalize data (standardize team names, markets)"
                },
                "matchmakers": {
                    "component": "EntityResolver",
                    "role": "Link related data, assign canonical_event_ids"
                },
                "output": "Clean, standardized, universally identified events"
            },
            "4_the_story_builders": {
                "component": "MergeService",
                "role": "Combine all odds from all books into unified event stories",
                "output": "Complete event stories with merged odds and provenance"
            },
            "5_the_opportunity_finders": {
                "component": "EVEngine",
                "role": "Analyze events for profitable betting opportunities",
                "output": "EV slips with calculated ROI"
            },
            "6_the_master_database": {
                "component": "Redis Cache",
                "role": "Store complete, pre-processed event stories",
                "output": "Fast lookup database ready for instant retrieval"
            },
            "7_the_newsstand": {
                "component": "FastAPI Endpoints",
                "role": "Deliver pre-prepared data instantly - NO fetching or processing",
                "output": "Instant API responses from master database"
            }
        },
        "primary_endpoint": {
            "GET /v5/event/{canonical_event_id}": {
                "description": "Get unified event by canonical ID - PRIMARY endpoint",
                "note": "All data from pre-processed cache, not generated on-demand",
                "parameters": {
                    "canonical_event_id": "Canonical event ID (use /match to discover)",
                    "include": "Comma-separated: props,books,ev_slips (default: props,books)"
                },
                "example": "/v5/event/evt_abc123?include=props,books,ev_slips"
            }
        },
        "discovery_endpoints": {
            "GET /v5/match": {
                "description": "Discovery endpoint - finds canonical_event_id by sport/teams",
                "examples": [
                    "/v5/match?sport=basketball_nba  (returns all games from cache)",
                    "/v5/match?sport=basketball_nba&home_team=Lakers&away_team=Warriors  (specific match)"
                ],
                "note": "Returns data from pre-processed cache"
            },
            "GET /v5/player_props": {
                "description": "Get player props from pre-processed cache",
                "example": "/v5/player_props?sport=basketball_nba&home_team=Lakers&away_team=Warriors"
            }
        },
        "other_endpoints": {
            "GET /v5/health/connectors": "Check connector health status"
        },
        "features": [
            "Pre-processed canonical data store",
            "Background pipeline architecture",
            "Entity resolution with canonical_event_ids",
            "Merged odds with full provenance",
            "EV slip calculation",
            "Zero on-demand fetching from API endpoints"
        ],
        "usage": "Use /v5/match to discover events, then /v5/event/{canonical_event_id} for full data"
    }

