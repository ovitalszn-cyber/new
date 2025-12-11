"""
KashRock API v4 - Clean structure similar to The Odds API
Provides sports, odds, events, scores, and market data in a unified format
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Query, Path, Header
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
# from streamers.parlayplay import ParlayPlayStreamer
from streamers.propscash import PropsCashStreamer
from streamers.betr import BetrStreamer
from streamers.underdog import UnderdogStreamer
from streamers.fliff import FliffStreamer
# from streamers.theesportslab import TheEsportsLabStreamer
# from streamers.espn import ESPNStreamer
# from streamers.nba import NBAStreamer
from streamers.pick6 import Pick6Streamer
from streamers.pinnacle import PinnacleStreamer
from streamers.fanduel import FanDuelStreamer
from streamers.draftkings import DraftKingsStreamer
# from streamers.bwin import BwinStreamer

def format_to_12hour(iso_datetime: str) -> str:
    """Convert ISO datetime string to 12-hour format."""
    try:
        # Parse the ISO datetime string
        if iso_datetime.endswith('Z'):
            iso_datetime = iso_datetime.replace('Z', '+00:00')
        
        dt = datetime.fromisoformat(iso_datetime)
        
        # Convert to 12-hour format
        formatted_time = dt.strftime('%I:%M %p')
        
        # Remove leading zero from hour if present (e.g., "09:30 PM" -> "9:30 PM")
        if formatted_time.startswith('0'):
            formatted_time = formatted_time[1:]
            
        return formatted_time
    except Exception:
        # Return original string if parsing fails
        return iso_datetime

router = APIRouter()
logger = structlog.get_logger()

# Book mapping for v4 API
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
    # "parlayplay": ParlayPlayStreamer,
    "propscash": PropsCashStreamer,
    "betr": BetrStreamer,
    "underdog": UnderdogStreamer,
    # "theesportslab": TheEsportsLabStreamer,
    "pick6": Pick6Streamer,
    "pinnacle": PinnacleStreamer,
    "fanduel": FanDuelStreamer,
    "draftkings": DraftKingsStreamer,
    # "bwin": BwinStreamer,
}

# Sport definitions similar to The Odds API
SPORTS = [
    {
        "key": "americanfootball_nfl",
        "group": "American Football",
        "title": "NFL",
        "description": "National Football League",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "americanfootball_ncaaf",
        "group": "American Football", 
        "title": "NCAAF",
        "description": "US College Football",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "basketball_nba",
        "group": "Basketball",
        "title": "NBA", 
        "description": "US Basketball",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "basketball_wnba",
        "group": "Basketball",
        "title": "WNBA",
        "description": "Women's National Basketball Association", 
        "active": True,
        "has_outrights": False
    },
    {
        "key": "basketball_ncaa",
        "group": "Basketball",
        "title": "NCAAB",
        "description": "US College Basketball",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "baseball_mlb",
        "group": "Baseball",
        "title": "MLB",
        "description": "Major League Baseball",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "icehockey_nhl",
        "group": "Ice Hockey",
        "title": "NHL",
        "description": "US Ice Hockey",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_mls",
        "group": "Soccer",
        "title": "MLS",
        "description": "Major League Soccer",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_epl",
        "group": "Soccer",
        "title": "EPL",
        "description": "English Premier League",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_championship",
        "group": "Soccer",
        "title": "Championship",
        "description": "English Football League Championship",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_efl_cup",
        "group": "Soccer",
        "title": "EFL Cup",
        "description": "English Football League Cup",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_serie_a",
        "group": "Soccer",
        "title": "Serie A",
        "description": "Italian Serie A",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_ligue_1",
        "group": "Soccer",
        "title": "Ligue 1",
        "description": "French Ligue 1",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_bundesliga",
        "group": "Soccer",
        "title": "Bundesliga",
        "description": "German Bundesliga",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_premiership",
        "group": "Soccer",
        "title": "Premiership",
        "description": "Scottish Premiership",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_eredivisie",
        "group": "Soccer",
        "title": "Eredivisie",
        "description": "Dutch Eredivisie",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_superliga",
        "group": "Soccer",
        "title": "Superliga",
        "description": "Danish Superliga",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_2_bundesliga",
        "group": "Soccer",
        "title": "2. Bundesliga",
        "description": "German 2. Bundesliga",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_super_lig",
        "group": "Soccer",
        "title": "Super Lig",
        "description": "Turkish Super Lig",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_laliga_2",
        "group": "Soccer",
        "title": "LaLiga 2",
        "description": "Spanish LaLiga 2",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_k_league_1",
        "group": "Soccer",
        "title": "K-League 1",
        "description": "South Korean K-League 1",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_conmebol_sudamericana",
        "group": "Soccer",
        "title": "CONMEBOL Sudamericana",
        "description": "CONMEBOL Sudamericana",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_champions_league",
        "group": "Soccer",
        "title": "UEFA Champions League",
        "description": "UEFA Champions League",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_laliga",
        "group": "Soccer",
        "title": "LaLiga",
        "description": "Spanish LaLiga",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_world_cup_qualification_uefa",
        "group": "Soccer",
        "title": "World Cup Qualification UEFA",
        "description": "FIFA World Cup Qualification UEFA",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "soccer_world_cup_qualification_caf",
        "group": "Soccer",
        "title": "World Cup Qualification CAF",
        "description": "FIFA World Cup Qualification CAF",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "football_cfl",
        "group": "American Football",
        "title": "CFL",
        "description": "Canadian Football League",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "basketball_nbl",
        "group": "Basketball",
        "title": "NBL",
        "description": "National Basketball League",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "hockey_asia_league",
        "group": "Ice Hockey",
        "title": "Asia League",
        "description": "Asia League Ice Hockey",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "handball_ehf_european_league_women",
        "group": "Handball",
        "title": "EHF European League Women",
        "description": "EHF European League Women",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "handball_hla_meisterliga",
        "group": "Handball",
        "title": "HLA Meisterliga",
        "description": "HLA Meisterliga",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "rugby_top_14",
        "group": "Rugby",
        "title": "Top 14",
        "description": "French Rugby Top 14",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "volleyball_super_cup_women",
        "group": "Volleyball",
        "title": "Super Cup Women",
        "description": "Volleyball Super Cup Women",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "tennis_atp",
        "group": "Tennis",
        "title": "ATP",
        "description": "Association of Tennis Professionals",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "tennis_wta",
        "group": "Tennis",
        "title": "WTA",
        "description": "Women's Tennis Association",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "mma_ufc",
        "group": "Mixed Martial Arts",
        "title": "UFC",
        "description": "Ultimate Fighting Championship",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "esports_lol",
        "group": "Esports",
        "title": "League of Legends",
        "description": "League of Legends Esports",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "esports_cs2",
        "group": "Esports",
        "title": "Counter-Strike 2",
        "description": "Counter-Strike 2 Esports",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "esports_valorant",
        "group": "Esports",
        "title": "Valorant",
        "description": "Valorant Esports",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "esports_dota2",
        "group": "Esports",
        "title": "Dota 2",
        "description": "Dota 2 Esports",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "esports_r6",
        "group": "Esports",
        "title": "Rainbow Six",
        "description": "Rainbow Six Siege Esports",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "esports_cod",
        "group": "Esports",
        "title": "Call of Duty",
        "description": "Call of Duty Esports",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "esports_halo",
        "group": "Esports",
        "title": "Halo",
        "description": "Halo Esports",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "esports_rocketleague",
        "group": "Esports",
        "title": "Rocket League",
        "description": "Rocket League Esports",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "esports_apex",
        "group": "Esports",
        "title": "Apex Legends",
        "description": "Apex Legends Esports",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "golf_pga",
        "group": "Golf",
        "title": "PGA",
        "description": "Professional Golfers Association",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "golf_lpga",
        "group": "Golf",
        "title": "LPGA",
        "description": "Ladies Professional Golf Association",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "nascar",
        "group": "Motorsports",
        "title": "NASCAR",
        "description": "National Association for Stock Car Auto Racing",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "f1",
        "group": "Motorsports",
        "title": "Formula 1",
        "description": "Formula 1 Racing",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "cricket",
        "group": "Cricket",
        "title": "Cricket",
        "description": "Cricket",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "boxing",
        "group": "Combat Sports",
        "title": "Boxing",
        "description": "Boxing",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "mma_powerslap",
        "group": "Combat Sports",
        "title": "Power Slap",
        "description": "Power Slap",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "afl",
        "group": "Australian Football",
        "title": "AFL",
        "description": "Australian Football League",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "lacrosse",
        "group": "Lacrosse",
        "title": "Lacrosse",
        "description": "Lacrosse",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "handball",
        "group": "Handball",
        "title": "Handball",
        "description": "Handball",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "beachvolleyball",
        "group": "Volleyball",
        "title": "Beach Volleyball",
        "description": "Beach Volleyball",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "darts",
        "group": "Darts",
        "title": "Darts",
        "description": "Darts",
        "active": True,
        "has_outrights": False
    },
    {
        "key": "pwhl",
        "group": "Hockey",
        "title": "PWHL",
        "description": "Professional Women's Hockey League",
        "active": True,
        "has_outrights": False
    }
]

# Market definitions
MARKETS = {
    "h2h": {"title": "Head to Head", "description": "Moneyline betting"},
    "spreads": {"title": "Point Spreads", "description": "Spread betting"},
    "totals": {"title": "Totals", "description": "Over/Under betting"},
    "player_props": {"title": "Player Props", "description": "Player performance betting"},
    "player_points": {"title": "Player Points", "description": "Player points betting"},
    "player_rebounds": {"title": "Player Rebounds", "description": "Player rebounds betting"},
    "player_assists": {"title": "Player Assists", "description": "Player assists betting"},
    "player_pass_yards": {"title": "Passing Yards", "description": "Player passing yards betting"},
    "player_rush_yards": {"title": "Rushing Yards", "description": "Player rushing yards betting"},
    "player_receiving_yards": {"title": "Receiving Yards", "description": "Player receiving yards betting"},
}

# ============================================================================
# SPORTS ENDPOINT - GET /v4/sports
# ============================================================================

@router.get("/sports")
async def get_sports(
    all: bool = Query(False, description="Include inactive sports"),
    authorization: Optional[str] = Header(default=None, alias="Authorization")
) -> List[Dict[str, Any]]:
    """
    Get list of available sports.
    Similar to The Odds API /v4/sports endpoint.
    """
    # TODO: Add API key validation
    # if not _validate_api_key(authorization):
    #     raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    if all:
        return SPORTS
    else:
        return [sport for sport in SPORTS if sport["active"]]

# ============================================================================
# ODDS ENDPOINT - GET /v4/sports/{sport}/odds
# ============================================================================

@router.get("/sports/{sport}/odds")
async def get_odds(
    sport: str = Path(..., description="Sport key"),
    regions: str = Query("us", description="Comma-separated list of regions"),
    markets: str = Query("h2h,spreads,totals", description="Comma-separated list of markets"),
    oddsFormat: str = Query("american", description="Odds format: american or decimal"),
    dateFormat: str = Query("iso", description="Date format: iso or unix"),
    bookmakers: Optional[str] = Query(None, description="Comma-separated list of bookmakers"),
    authorization: Optional[str] = Header(default=None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Get odds for upcoming events from multiple bookmakers.
    Similar to The Odds API /v4/sports/{sport}/odds endpoint.
    """
    # Validate sport
    sport_keys = [s["key"] for s in SPORTS]
    if sport not in sport_keys:
        raise HTTPException(status_code=400, detail=f"Invalid sport key: {sport}")
    
    # Parse parameters
    regions_list = [r.strip() for r in regions.split(",")]
    markets_list = [m.strip() for m in markets.split(",")]
    bookmakers_list = [b.strip() for b in bookmakers.split(",")] if bookmakers else None
    
    # Get data from available bookmakers
    events_data = []
    available_bookmakers = []
    
    # Filter bookmakers if specified
    target_bookmakers = bookmakers_list if bookmakers_list else list(BOOK_MAP.keys())
    
    for book_key in target_bookmakers:
        if book_key not in BOOK_MAP:
            continue
            
        try:
            streamer_class = BOOK_MAP[book_key]
            internal_sport = _map_sport_key(sport)
            # Get default config which includes curl files if available
            if hasattr(streamer_class, 'get_default_config'):
                config = streamer_class.get_default_config(internal_sport)
            else:
                config = {"sport": internal_sport}
            streamer = streamer_class(f"{book_key}_{internal_sport}", config)
            
            await streamer.connect()
            raw_data = await streamer.fetch_data()
            await streamer.disconnect()
            
            # Process data into Odds API format
            processed_events = _process_bookmaker_data(book_key, raw_data, sport, markets_list, oddsFormat)
            events_data.extend(processed_events)
            available_bookmakers.append(book_key)
            
        except Exception as e:
            logger.warning(f"Failed to fetch data from {book_key}: {e}")
            continue
    
    # Group events by event ID and combine bookmaker data
    events_by_id = {}
    for event in events_data:
        event_id = event["id"]
        if event_id not in events_by_id:
            events_by_id[event_id] = {
                "id": event_id,
                "sport_key": event["sport_key"],
                "commence_time": format_to_12hour(event["commence_time"]),
                "home_team": event["home_team"],
                "away_team": event["away_team"],
                "bookmakers": []
            }
        
        # Add bookmaker data
        for bookmaker in event.get("bookmakers", []):
            events_by_id[event_id]["bookmakers"].append(bookmaker)
    
    return {
        "data": list(events_by_id.values()),
        "count": len(events_by_id),
        "sport": sport,
        "timestamp": format_to_12hour(datetime.utcnow().isoformat())
    }

# ============================================================================
# DETAILED ODDS ENDPOINT - GET /v4/sports/{sport}/odds/detailed
# ============================================================================

@router.get("/sports/{sport}/odds/detailed")
async def get_detailed_odds(
    sport: str = Path(..., description="Sport key"),
    bookmakers: str = Query("bwin", description="Comma-separated list of bookmaker keys (currently only bwin supported)"),
    markets: str = Query("h2h,spreads,totals,player_props", description="Comma-separated list of market types"),
    oddsFormat: str = Query("american", description="Odds format: american or decimal"),
    fixtureIds: str = Query(..., description="Comma-separated list of fixture IDs to get detailed data for"),
    authorization: Optional[str] = Header(default=None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Get detailed odds including player props for specific fixtures.
    Currently only supports bwin bookmaker.
    """
    # Validate sport
    sport_keys = [s["key"] for s in SPORTS]
    if sport not in sport_keys:
        raise HTTPException(status_code=400, detail=f"Invalid sport key: {sport}")
    
    # Validate API key
    if not _validate_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # Parse parameters
        bookmaker_list = [b.strip() for b in bookmakers.split(",")]
        markets_list = [m.strip() for m in markets.split(",")]
        fixture_id_list = [fid.strip() for fid in fixtureIds.split(",")]
        
        # Get the mapped sport key
        mapped_sport = SPORT_KEY_MAPPING.get(sport, sport)
        
        # Validate bookmakers (currently only bwin supported for detailed data)
        if "bwin" not in bookmaker_list:
            raise HTTPException(status_code=400, detail="Detailed odds currently only supported for bwin")
        
        # Validate markets
        valid_markets = ["h2h", "spreads", "totals", "player_props"]
        invalid_markets = [m for m in markets_list if m not in valid_markets]
        if invalid_markets:
            raise HTTPException(status_code=400, detail=f"Invalid market(s): {', '.join(invalid_markets)}")
        
        # Validate odds format
        if oddsFormat not in ["american", "decimal"]:
            raise HTTPException(status_code=400, detail="Invalid odds format. Use 'american' or 'decimal'")
        
        # Fetch detailed data for each fixture
        all_events = []
        
        for fixture_id in fixture_id_list:
            try:
                bwin_streamer = BOOK_MAP["bwin"]
                raw_data = await bwin_streamer.fetch_fixture_details([fixture_id])
                
                if raw_data and "fixture" in raw_data:
                    events = _process_bwin_fixture_details(raw_data, mapped_sport, markets_list, oddsFormat)
                    all_events.extend(events)
                
            except Exception as e:
                logger.warning(f"Failed to fetch detailed data for fixture {fixture_id}: {e}")
                continue
        
        return {
            "data": all_events,
            "count": len(all_events),
            "sport": sport,
            "bookmakers": bookmaker_list,
            "markets": markets_list,
            "oddsFormat": oddsFormat,
            "fixtureIds": fixture_id_list,
            "timestamp": format_to_12hour(datetime.utcnow().isoformat())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_detailed_odds: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# EVENTS ENDPOINT - GET /v4/sports/{sport}/events
# ============================================================================

@router.get("/sports/{sport}/events")
async def get_events(
    sport: str = Path(..., description="Sport key"),
    daysFrom: int = Query(1, description="Number of days from now to fetch events"),
    dateFormat: str = Query("iso", description="Date format: iso or unix"),
    authorization: Optional[str] = Header(default=None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Get upcoming events for a sport.
    Similar to The Odds API /v4/sports/{sport}/events endpoint.
    """
    # Validate sport
    sport_keys = [s["key"] for s in SPORTS]
    if sport not in sport_keys:
        raise HTTPException(status_code=400, detail=f"Invalid sport key: {sport}")
    
    # Get events from a reliable bookmaker (Novig)
    try:
        streamer_class = BOOK_MAP["novig"]
        internal_sport = _map_sport_key(sport)
        config = {"sport": internal_sport, "limit": 100000}
        streamer = streamer_class(f"novig_{internal_sport}", config)
        
        await streamer.connect()
        raw_data = await streamer.fetch_data()
        await streamer.disconnect()
        
        # Process into events format
        events = _process_events_data(raw_data, sport, daysFrom)
        
        return {
            "data": events,
            "count": len(events),
            "sport": sport,
            "timestamp": format_to_12hour(datetime.utcnow().isoformat())
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch events for {sport}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")

# ============================================================================
# SCORES ENDPOINT - GET /v4/sports/{sport}/scores
# ============================================================================

@router.get("/sports/{sport}/scores")
async def get_scores(
    sport: str = Path(..., description="Sport key"),
    date: Optional[str] = Query(None, description="Date to fetch scores (YYYY-MM-DD format)"),
    daysFrom: int = Query(1, description="Number of days from now to fetch scores"),
    dateFormat: str = Query("iso", description="Date format: iso or unix"),
    authorization: Optional[str] = Header(default=None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Get live scores for a sport.
    Similar to The Odds API /v4/sports/{sport}/scores endpoint.
    Powered by ESPN scoreboard data.
    """
    # Validate sport
    sport_keys = [s["key"] for s in SPORTS]
    if sport not in sport_keys:
        raise HTTPException(status_code=400, detail=f"Invalid sport key: {sport}")
    
    # Validate API key
    if not _validate_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # Create ESPN streamer
        espn_config = {"sport": sport}
        if date:
            espn_config["date"] = date
        # espn_# streamer = ESPNStreamer("espn", espn_config)
        
        # Connect and fetch data
        connected = await espn_streamer.connect()
        if not connected:
            logger.warning("Failed to connect to ESPN", sport=sport)
            return {
                "data": [],
                "count": 0,
                "sport": sport,
                "timestamp": format_to_12hour(datetime.utcnow().isoformat()),
                        "error": "Failed to connect to ESPN"
                    }
        
        # Fetch raw data
        raw_data = await espn_streamer.fetch_data()
        await espn_streamer.disconnect()
        
        # Process ESPN data
        events = _process_espn_scores_data(raw_data.get("raw_response", {}), sport, raw_data.get("player_stats", {}))
        
        logger.info("Fetched ESPN scores", sport=sport, count=len(events))
        
        return {
            "data": events,
            "count": len(events),
            "sport": sport,
            "timestamp": format_to_12hour(datetime.utcnow().isoformat()),
            "source": "espn"
        }
        
    except Exception as exc:
        logger.error("Failed to fetch scores", sport=sport, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Failed to fetch scores: {str(exc)}")

@router.get("/sports/{sport}/schedule")
async def get_schedule(
    sport: str = Path(..., description="Sport key"),
    date: Optional[str] = Query(None, description="Date to fetch schedule (YYYY-MM-DD format)"),
    daysFrom: int = Query(1, description="Number of days from now to fetch schedule"),
    dateFormat: str = Query("iso", description="Date format: iso or unix"),
    authorization: Optional[str] = Header(default=None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Get schedule for a sport (all games - past, live, and future).
    Similar to The Odds API /v4/sports/{sport}/schedule endpoint.
    Powered by ESPN scoreboard data.
    
    Use ?date=2024-01-15 to get schedule for a specific date (e.g., two weeks ago).
    """
    # Validate sport
    sport_keys = [s["key"] for s in SPORTS]
    if sport not in sport_keys:
        raise HTTPException(status_code=400, detail=f"Invalid sport key: {sport}")
    
    # Validate API key
    if not _validate_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # Create ESPN streamer
        espn_config = {"sport": sport}
        if date:
            espn_config["date"] = date
        # espn_# streamer = ESPNStreamer("espn", espn_config)
        
        # Connect and fetch data
        connected = await espn_streamer.connect()
        if not connected:
            logger.warning("Failed to connect to ESPN", sport=sport)
            return {
                "data": [],
                "count": 0,
                "sport": sport,
                "timestamp": format_to_12hour(datetime.utcnow().isoformat()),
                "error": "Failed to connect to ESPN"
            }
        
        # Fetch raw data
        raw_data = await espn_streamer.fetch_data()
        await espn_streamer.disconnect()
        
        # Process ESPN data (all games)
        events = _process_espn_schedule_data(raw_data.get("raw_response", {}), sport, raw_data.get("player_stats", {}))
        
        logger.info("Fetched ESPN schedule", sport=sport, count=len(events))
        
        return {
            "data": events,
            "count": len(events),
            "sport": sport,
            "timestamp": format_to_12hour(datetime.utcnow().isoformat()),
            "source": "espn"
        }
        
    except Exception as exc:
        logger.error("Failed to fetch schedule", sport=sport, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Failed to fetch schedule: {str(exc)}")

@router.get("/sports/{sport}/historical")
async def get_historical_data(
    sport: str = Path(..., description="Sport key"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD format)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD format). If not provided, only start_date will be used"),
    include_player_stats: bool = Query(True, description="Whether to include player statistics"),
    authorization: Optional[str] = Header(default=None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Get historical data for a sport across a date range.
    Powered by ESPN scoreboard data.
    
    Examples:
    - /sports/basketball_wnba/historical?start_date=2024-08-01&end_date=2024-08-31
    - /sports/basketball_nba/historical?start_date=2024-10-01 (single day)
    """
    # Validate sport
    sport_keys = [s["key"] for s in SPORTS]
    if sport not in sport_keys:
        raise HTTPException(status_code=400, detail=f"Invalid sport key: {sport}")
    
    # Validate API key
    if not _validate_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Validate dates
    try:
        from datetime import datetime
        datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            datetime.strptime(end_date, "%Y-%m-%d")
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            if start_dt > end_dt:
                raise HTTPException(status_code=400, detail="Start date cannot be after end date")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    try:
        # Create ESPN streamer
        espn_config = {"sport": sport}
        # espn_# streamer = ESPNStreamer("espn", espn_config)
        
        # Connect and fetch historical data
        connected = await espn_streamer.connect()
        if not connected:
            logger.warning("Failed to connect to ESPN", sport=sport)
            return {
                "data": [],
                "count": 0,
                "sport": sport,
                "date_range": f"{start_date} to {end_date or start_date}",
                "timestamp": format_to_12hour(datetime.utcnow().isoformat()),
                "error": "Failed to connect to ESPN"
            }
        
        # Fetch historical data
        raw_data = await espn_streamer.fetch_historical_data(start_date, end_date)
        await espn_streamer.disconnect()
        
        # Process ESPN data
        player_stats = raw_data.get("player_stats", {}) if include_player_stats else {}
        events = _process_espn_schedule_data(raw_data.get("raw_response", {}), sport, player_stats)
        
        logger.info("Fetched historical ESPN data", sport=sport, count=len(events), date_range=f"{start_date} to {end_date or start_date}")
        
        return {
            "data": events,
            "count": len(events),
            "sport": sport,
            "date_range": f"{start_date} to {end_date or start_date}",
            "timestamp": format_to_12hour(datetime.utcnow().isoformat()),
            "source": "espn",
            "historical": True,
            "player_stats_included": include_player_stats
        }
        
    except Exception as exc:
        logger.error("Failed to fetch historical data", sport=sport, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Failed to fetch historical data: {str(exc)}")

# ============================================================================
# PLAYER STATS SUMMARY ENDPOINT - GET /v4/sports/{sport}/player-stats-summary
# ============================================================================

@router.get("/sports/{sport}/player-stats-summary")
async def get_player_stats_summary(
    sport: str,
    date: Optional[str] = Query(None, description="Date to fetch summary (YYYY-MM-DD format)"),
    api_key: str = Query(..., description="API key for authentication")
) -> Dict[str, Any]:
    """Get summary of which games have player statistics available."""
    try:
        # Validate API key
        if not _validate_api_key(api_key):
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Initialize ESPN streamer
        # streamer = ESPNStreamer("espn", {"sport": sport, "date": date})
        await streamer.connect()
        
        # Fetch raw data
        raw_data = await streamer.fetch_data()
        player_stats = raw_data.get("player_stats", {})
        
        # Process data to get games with player stats
        games_with_stats = []
        games_without_stats = []
        
        if "events" in raw_data:
            for event in raw_data["events"]:
                game_id = event.get("id")
                game_info = {
                    "id": game_id,
                    "home_team": None,
                    "away_team": None,
                    "status": event.get("status", {}).get("type", {}).get("description", "Unknown")
                }
                
                # Extract team names
                competitions = event.get("competitions", [])
                if competitions and competitions[0].get("competitors"):
                    for team in competitions[0]["competitors"]:
                        team_info = team.get("team", {})
                        if team.get("homeAway") == "home":
                            game_info["home_team"] = team_info.get("displayName", "Unknown")
                        else:
                            game_info["away_team"] = team_info.get("displayName", "Unknown")
                
                if game_id in player_stats and "players" in player_stats[game_id].get("boxscore", {}):
                    games_with_stats.append(game_info)
                else:
                    games_without_stats.append(game_info)
        
        return {
            "sport": sport,
            "date": date or "current",
            "total_games": len(games_with_stats) + len(games_without_stats),
            "games_with_player_stats": len(games_with_stats),
            "games_without_player_stats": len(games_without_stats),
            "games_with_stats": games_with_stats,
            "games_without_stats": games_without_stats,
            "note": "Player stats are only available for completed games or games in progress. Future games will not have detailed player statistics.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as exc:
        logger.error("Failed to fetch player stats summary", sport=sport, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Failed to fetch player stats summary: {str(exc)}")

# ============================================================================
# ESPN TEAM STATS ENDPOINT - GET /v4/sports/{sport}/teams/{team_id}/stats
# ============================================================================

@router.get("/sports/{sport}/teams/{team_id}/stats")
async def get_team_stats(
    sport: str = Path(..., description="Sport key"),
    team_id: str = Path(..., description="ESPN team ID (e.g., 'bos' for Boston Celtics)"),
    season: str = Query("2025", description="Season year"),
    season_type: str = Query("3", description="Season type: 1=preseason, 2=playoffs, 3=regular season"),
    authorization: Optional[str] = Header(default=None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Get team player statistics from ESPN.
    
    Parameters:
    - sport: Sport key (e.g., 'basketball_nba')
    - team_id: ESPN team ID (e.g., 'bos' for Boston Celtics)
    - season: Season year (e.g., '2025')
    - season_type: Season type (1=preseason, 2=playoffs, 3=regular season)
    
    Example:
    GET /v4/sports/basketball_nba/teams/bos/stats?season=2025&season_type=3
    """
    # Validate API key
    api_key = _extract_api_key(authorization)
    if not _validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Validate sport
    sport_keys = [s["key"] for s in SPORTS]
    if sport not in sport_keys:
        raise HTTPException(status_code=400, detail=f"Invalid sport key: {sport}")
    
    try:
        # Create ESPN streamer with team stats config
        espn_config = {
            "sport": sport,
            "team_id": team_id,
            "season": season,
            "season_type": season_type
        }
        # streamer = ESPNStreamer("espn", espn_config)
        
        # Connect and fetch data
        connected = await streamer.connect()
        if not connected:
            raise HTTPException(status_code=503, detail="Failed to connect to ESPN API")
        
        # Fetch team stats
        raw_data = await streamer.fetch_data()
        await streamer.disconnect()
        
        # Process team stats data
        processed_data = _process_espn_team_stats_data(raw_data)
        
        logger.info("Fetched ESPN team stats", sport=sport, team=team_id, season=season)
        
        return {
            "sport": sport,
            "team_id": team_id,
            "season": season,
            "season_type": season_type,
            "data": processed_data,
            "timestamp": format_to_12hour(datetime.utcnow().isoformat()),
            "source": "espn"
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to fetch team stats", sport=sport, team=team_id, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Failed to fetch team stats: {str(exc)}")

# ============================================================================
# NBA STATS ENDPOINTS - GET /v4/nba/stats/*
# ============================================================================

@router.get("/nba/stats/players")
async def get_nba_player_stats(
    season: str = Query("2025-26", description="NBA season (e.g., '2025-26')"),
    season_type: str = Query("Pre Season", description="Season type: Pre Season, Regular Season, Playoffs"),
    measure_type: str = Query("Base", description="Measure type: Base, Advanced, Four Factors, etc."),
    per_mode: str = Query("Totals", description="Per mode: PerGame, Totals, Per36, etc."),
    team_id: int = Query(0, description="Team ID (0 for all teams)"),
    last_n_games: int = Query(0, description="Last N games (0 for season totals)"),
    month: int = Query(0, description="Month (0 for all months)"),
    authorization: Optional[str] = Header(default=None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Fetch NBA player statistics from NBA Stats API.
    
    Parameters:
    - season: NBA season (e.g., '2025-26')
    - season_type: Season type (Pre Season, Regular Season, Playoffs)
    - measure_type: Measure type (Base, Advanced, Four Factors, etc.)
    - per_mode: Per mode (PerGame, Totals, Per36, etc.)
    - team_id: Team ID (0 for all teams)
    - last_n_games: Last N games (0 for season totals)
    - month: Month (0 for all months)
    
    Example:
    GET /v4/nba/stats/players?season=2025-26&season_type=Regular%20Season&measure_type=Base
    """
    # Validate API key
    api_key = _extract_api_key(authorization)
    if not _validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # Create NBA streamer config
        nba_config = {
            "season": season,
            "season_type": season_type,
            "measure_type": measure_type,
            "per_mode": per_mode,
            "team_id": team_id,
            "last_n_games": last_n_games,
            "month": month
        }
        
        # streamer = NBAStreamer("nba", nba_config)
        
        # Connect and fetch data
        connected = await streamer.connect()
        if not connected:
            raise HTTPException(status_code=503, detail="Failed to connect to NBA Stats API")
        
        # Fetch player stats
        raw_data = await streamer.fetch_data()
        await streamer.disconnect()
        
        # Process NBA stats data
        processed_data = _process_nba_player_stats_data(raw_data)
        
        logger.info("Fetched NBA player stats", season=season, season_type=season_type, measure_type=measure_type)
        
        return {
            "data_type": "nba_player_stats",
            "season": season,
            "season_type": season_type,
            "measure_type": measure_type,
            "per_mode": per_mode,
            "team_id": team_id,
            "data": processed_data,
            "timestamp": format_to_12hour(datetime.utcnow().isoformat()),
            "source": "nba_stats"
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to fetch NBA player stats", season=season, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Failed to fetch NBA player stats: {str(exc)}")

@router.get("/nba/stats/teams/{team_id}")
async def get_nba_team_stats(
    team_id: int = Path(..., description="NBA team ID"),
    season: str = Query("2025-26", description="NBA season (e.g., '2025-26')"),
    season_type: str = Query("Pre Season", description="Season type: Pre Season, Regular Season, Playoffs"),
    measure_type: str = Query("Base", description="Measure type: Base, Advanced, Four Factors, etc."),
    per_mode: str = Query("Totals", description="Per mode: PerGame, Totals, Per36, etc."),
    last_n_games: int = Query(0, description="Last N games (0 for season totals)"),
    month: int = Query(0, description="Month (0 for all months)"),
    authorization: Optional[str] = Header(default=None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Fetch NBA team statistics from NBA Stats API.
    
    Parameters:
    - team_id: NBA team ID
    - season: NBA season (e.g., '2025-26')
    - season_type: Season type (Pre Season, Regular Season, Playoffs)
    - measure_type: Measure type (Base, Advanced, Four Factors, etc.)
    - per_mode: Per mode (PerGame, Totals, Per36, etc.)
    - last_n_games: Last N games (0 for season totals)
    - month: Month (0 for all months)
    
    Example:
    GET /v4/nba/stats/teams/1610612738?season=2025-26&season_type=Regular%20Season
    """
    # Validate API key
    api_key = _extract_api_key(authorization)
    if not _validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # Create NBA streamer config
        nba_config = {
            "season": season,
            "season_type": season_type,
            "measure_type": measure_type,
            "per_mode": per_mode,
            "team_id": team_id,
            "last_n_games": last_n_games,
            "month": month
        }
        
        # streamer = NBAStreamer("nba", nba_config)
        
        # Connect and fetch data
        connected = await streamer.connect()
        if not connected:
            raise HTTPException(status_code=503, detail="Failed to connect to NBA Stats API")
        
        # Fetch team stats
        raw_data = await streamer.fetch_data()
        await streamer.disconnect()
        
        # Process NBA team stats data
        processed_data = _process_nba_team_stats_data(raw_data)
        
        logger.info("Fetched NBA team stats", team_id=team_id, season=season, season_type=season_type)
        
        return {
            "data_type": "nba_team_stats",
            "team_id": team_id,
            "season": season,
            "season_type": season_type,
            "measure_type": measure_type,
            "per_mode": per_mode,
            "data": processed_data,
            "timestamp": format_to_12hour(datetime.utcnow().isoformat()),
            "source": "nba_stats"
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to fetch NBA team stats", team_id=team_id, season=season, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Failed to fetch NBA team stats: {str(exc)}")

@router.get("/nba/stats/players/{player_id}")
async def get_nba_player_detailed_stats(
    player_id: int = Path(..., description="NBA player ID"),
    season: str = Query("2025-26", description="NBA season (e.g., '2025-26')"),
    season_type: str = Query("Pre Season", description="Season type: Pre Season, Regular Season, Playoffs"),
    measure_type: str = Query("Base", description="Measure type: Base, Advanced, Four Factors, etc."),
    per_mode: str = Query("Totals", description="Per mode: PerGame, Totals, Per36, etc."),
    last_n_games: int = Query(0, description="Last N games (0 for season totals)"),
    month: int = Query(0, description="Month (0 for all months)"),
    authorization: Optional[str] = Header(default=None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Fetch detailed NBA player statistics from NBA Stats API.
    
    Parameters:
    - player_id: NBA player ID
    - season: NBA season (e.g., '2025-26')
    - season_type: Season type (Pre Season, Regular Season, Playoffs)
    - measure_type: Measure type (Base, Advanced, Four Factors, etc.)
    - per_mode: Per mode (PerGame, Totals, Per36, etc.)
    - last_n_games: Last N games (0 for season totals)
    - month: Month (0 for all months)
    
    Example:
    GET /v4/nba/stats/players/1629029?season=2025-26&season_type=Regular%20Season
    """
    # Validate API key
    api_key = _extract_api_key(authorization)
    if not _validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # Create NBA streamer config
        nba_config = {
            "season": season,
            "season_type": season_type,
            "measure_type": measure_type,
            "per_mode": per_mode,
            "player_id": player_id,
            "last_n_games": last_n_games,
            "month": month
        }
        
        # streamer = NBAStreamer("nba", nba_config)
        
        # Connect and fetch data
        connected = await streamer.connect()
        if not connected:
            raise HTTPException(status_code=503, detail="Failed to connect to NBA Stats API")
        
        # Fetch player stats
        raw_data = await streamer.fetch_data()
        await streamer.disconnect()
        
        # Process NBA player stats data
        processed_data = _process_nba_player_stats_data(raw_data)
        
        logger.info("Fetched NBA player detailed stats", player_id=player_id, season=season, season_type=season_type)
        
        return {
            "data_type": "nba_player_detailed_stats",
            "player_id": player_id,
            "season": season,
            "season_type": season_type,
            "measure_type": measure_type,
            "per_mode": per_mode,
            "data": processed_data,
            "timestamp": format_to_12hour(datetime.utcnow().isoformat()),
            "source": "nba_stats"
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to fetch NBA player detailed stats", player_id=player_id, season=season, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Failed to fetch NBA player detailed stats: {str(exc)}")

@router.get("/nba/teams")
async def get_nba_teams(
    authorization: Optional[str] = Header(default=None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Get available NBA teams with their IDs.
    
    Example:
    GET /v4/nba/teams
    """
    # Validate API key
    api_key = _extract_api_key(authorization)
    if not _validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # Get team IDs from NBA streamer
        # team_ids = NBAStreamer.get_team_ids()
        
        if not team_ids:
            return {
                "teams": [],
                "count": 0,
                "timestamp": format_to_12hour(datetime.utcnow().isoformat()),
                "source": "nba_stats"
            }
        
        # Format teams data
        teams = []
        for team_name, team_id in team_ids.items():
            teams.append({
                "id": team_id,
                "name": team_name,
                "display_name": team_name.replace("_", " ").title()
            })
        
        logger.info("Fetched NBA teams", count=len(teams))
        
        return {
            "teams": teams,
            "count": len(teams),
            "timestamp": format_to_12hour(datetime.utcnow().isoformat()),
            "source": "nba_stats"
        }
        
    except Exception as exc:
        logger.error("Failed to fetch NBA teams", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Failed to fetch NBA teams: {str(exc)}")

@router.get("/sports/{sport}/teams")
async def get_available_teams(
    sport: str = Path(..., description="Sport key"),
    authorization: Optional[str] = Header(default=None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Get available team IDs for a sport from ESPN.
    
    Parameters:
    - sport: Sport key (e.g., 'basketball_nba')
    
    Example:
    GET /v4/sports/basketball_nba/teams
    """
    # Validate API key
    api_key = _extract_api_key(authorization)
    if not _validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Validate sport
    sport_keys = [s["key"] for s in SPORTS]
    if sport not in sport_keys:
        raise HTTPException(status_code=400, detail=f"Invalid sport key: {sport}")
    
    try:
        # Get team IDs from ESPN streamer
        # team_ids = ESPNStreamer.get_team_ids(sport)
        
        if not team_ids:
            return {
                "sport": sport,
                "teams": [],
                "message": f"No team mapping available for {sport}. Currently supported: basketball_nba",
                "timestamp": format_to_12hour(datetime.utcnow().isoformat())
            }
        
        # Format team data
        teams = []
        for team_name, team_id in team_ids.items():
            teams.append({
                "name": team_name.replace("_", " ").title(),
                "id": team_id,
                "display_name": team_name.replace("_", " ").title()
            })
        
        return {
            "sport": sport,
            "teams": teams,
            "count": len(teams),
            "timestamp": format_to_12hour(datetime.utcnow().isoformat())
        }
        
    except Exception as exc:
        logger.error("Failed to get available teams", sport=sport, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Failed to get available teams: {str(exc)}")

# ============================================================================
# MARKETS ENDPOINT - GET /v4/sports/{sport}/markets
# ============================================================================

@router.get("/sports/{sport}/markets")
async def get_markets(
    sport: str = Path(..., description="Sport key"),
    authorization: Optional[str] = Header(default=None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Get available markets for a sport.
    Similar to The Odds API /v4/sports/{sport}/markets endpoint.
    """
    # Validate sport
    sport_keys = [s["key"] for s in SPORTS]
    if sport not in sport_keys:
        raise HTTPException(status_code=400, detail=f"Invalid sport key: {sport}")
    
    # Return available markets
    market_list = [
        {"key": key, "title": data["title"], "description": data["description"]}
        for key, data in MARKETS.items()
    ]
    
    return {
        "data": market_list,
        "count": len(market_list),
        "sport": sport,
        "timestamp": format_to_12hour(datetime.utcnow().isoformat())
    }

# ============================================================================
# BOOKMAKERS ENDPOINT - GET /v4/bookmakers
# ============================================================================

@router.get("/bookmakers")
async def get_bookmakers(
    authorization: Optional[str] = Header(default=None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Get list of available bookmakers.
    Similar to The Odds API /v4/bookmakers endpoint.
    """
    bookmakers = []
    for book_key, streamer_class in BOOK_MAP.items():
        try:
            sports = streamer_class.get_supported_sports()
            bookmakers.append({
                "key": book_key,
                "title": book_key.replace("_", " ").title(),
                "description": f"{book_key.replace('_', ' ').title()} sportsbook",
                "active": True,
                "supported_sports": sports
            })
        except Exception as e:
            logger.warning(f"Failed to get info for {book_key}: {e}")
            bookmakers.append({
                "key": book_key,
                "title": book_key.replace("_", " ").title(),
                "description": f"{book_key.replace('_', ' ').title()} sportsbook",
                "active": False,
                "supported_sports": []
            })
    
    return {
        "data": bookmakers,
        "count": len(bookmakers),
        "timestamp": format_to_12hour(datetime.utcnow().isoformat())
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _process_bookmaker_data(book_key: str, raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process raw bookmaker data into Odds API format."""
    events = []
    
    try:
        # Handle different bookmaker data formats
        if book_key == "novig":
            events = _process_novig_data(raw_data, sport, markets_list, odds_format)
        elif book_key == "prizepicks":
            events = _process_prizepicks_data(raw_data, sport, markets_list, odds_format)
        elif book_key == "dabble":
            events = _process_dabble_data(raw_data, sport, markets_list, odds_format)
        elif book_key == "fliff":
            events = _process_fliff_data(raw_data, sport, markets_list, odds_format)
        elif book_key == "betonline":
            events = _process_betonline_data(raw_data, sport, markets_list, odds_format)
        elif book_key == "bovada":
            events = _process_bovada_data(raw_data, sport, markets_list, odds_format)
        elif book_key == "rebet":
            events = _process_rebet_data(raw_data, sport, markets_list, odds_format)
        elif book_key == "betr":
            logger.info(f"Processing Betr data for {sport}")
            events = _process_betr_data(raw_data, sport, markets_list, odds_format)
            logger.info(f"Betr processed {len(events)} events")
        elif book_key == "splashsports":
            logger.info(f"Processing SplashSports data for {sport}")
            events = _process_splashsports_data(raw_data, sport, markets_list, odds_format)
            logger.info(f"SplashSports processed {len(events)} events")
        elif book_key == "underdog":
            logger.info(f"Processing Underdog data for {sport}")
            events = _process_underdog_data(raw_data, sport, markets_list, odds_format)
            logger.info(f"Underdog processed {len(events)} events")
        elif book_key == "propscash":
            logger.info(f"Processing PropsCash data for {sport}")
            events = _process_propscash_data(raw_data, sport, markets_list, odds_format)
            logger.info(f"PropsCash processed {len(events)} events")
        elif book_key == "pick6":
            logger.info(f"Processing Pick6 data for {sport}")
            events = _process_pick6_data(raw_data, sport, markets_list, odds_format)
            logger.info(f"Pick6 processed {len(events)} events")
        elif book_key == "pinnacle":
            logger.info(f"Processing Pinnacle data for {sport}")
            events = _process_pinnacle_data(raw_data, sport, markets_list, odds_format)
            logger.info(f"Pinnacle processed {len(events)} events")
        elif book_key == "fanduel":
            logger.info(f"Processing FanDuel data for {sport}")
            events = _process_fanduel_data(raw_data, sport, markets_list, odds_format)
            logger.info(f"FanDuel processed {len(events)} events")
        elif book_key == "theesportslab":
            logger.info(f"Processing TheEsportsLab data for {sport}")
            events = _process_theesportslab_data(raw_data, sport, markets_list, odds_format)
            logger.info(f"TheEsportsLab processed {len(events)} events")
        elif book_key == "draftkings":
            logger.info(f"Processing DraftKings data for {sport}")
            events = _process_draftkings_data(raw_data, sport, markets_list, odds_format)
            logger.info(f"DraftKings processed {len(events)} events")
        elif book_key == "bwin":
            logger.info(f"Processing Bwin data for {sport}")
            events = _process_bwin_data(raw_data, sport, markets_list, odds_format)
            logger.info(f"Bwin processed {len(events)} events")
        # elif book_key == "parlayplay":
        #     events = _process_parlayplay_data(raw_data, sport, markets_list, odds_format)
        else:
            # Generic processor for other bookmakers
            events = _process_generic_data(book_key, raw_data, sport, markets_list, odds_format)
            
    except Exception as e:
        logger.warning(f"Failed to process {book_key} data: {e}")
    
    return events

def _process_events_data(raw_data: Any, sport: str, days_from: int) -> List[Dict[str, Any]]:
    """Process raw events data into Odds API format."""
    events = []
    
    try:
        if isinstance(raw_data, dict) and "events" in raw_data:
            # Novig format
            for event in raw_data["events"]:
                if not isinstance(event, dict):
                    continue
                    
                # Extract basic event info
                event_id = event.get("id", f"event_{len(events)}")
                commence_time = event.get("scheduled_start") or event.get("start_time")
                
                # Extract teams/participants
                home_team = "Home Team"
                away_team = "Away Team"
                
                if "participants" in event:
                    participants = event["participants"]
                    if len(participants) >= 2:
                        home_team = participants[0].get("name", "Home Team")
                        away_team = participants[1].get("name", "Away Team")
                
                events.append({
                    "id": event_id,
                    "sport_key": sport,
                    "commence_time": format_to_12hour(commence_time or datetime.utcnow().isoformat()),
                    "home_team": home_team,
                    "away_team": away_team,
                    "status": "scheduled"
                })
                
    except Exception as e:
        logger.warning(f"Failed to process events data: {e}")
    
    return events

def _process_novig_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process Novig data into Odds API format."""
    events = []
    
    try:
        if isinstance(raw_data, dict) and "events" in raw_data:
            for event in raw_data["events"]:
                if not isinstance(event, dict):
                    continue
                
                # Skip non-Game events (Future, etc.)
                if event.get("type") != "Game":
                    continue
                
                # Extract event info
                event_id = event.get("id", f"novig_event_{len(events)}")
                commence_time = event.get("scheduled_start") or event.get("start_time")
                
                # Extract teams from description (e.g., "Detroit Lions @ Kansas City Chiefs")
                home_team = "Home Team"
                away_team = "Away Team"
                
                description = event.get("description", "")
                if " @ " in description:
                    parts = description.split(" @ ")
                    if len(parts) == 2:
                        away_team = parts[0].strip()
                        home_team = parts[1].strip()
                
                # Process markets
                processed_markets = []
                if "markets" in event:
                    for market in event["markets"]:
                        market_type = market.get("type", "")
                        
                        # Map Novig market types to Odds API format
                        mapped_type = _map_novig_market_type(market_type)
                        
                        # Check if this market type is requested
                        if mapped_type in markets_list or "h2h" in markets_list:
                            outcomes = _process_novig_market_outcomes(market, odds_format, home_team, away_team)
                            if outcomes:  # Only add markets with valid outcomes
                                processed_markets.append({
                                    "key": mapped_type,
                                    "last_update": format_to_12hour(datetime.utcnow().isoformat()),
                                    "outcomes": outcomes
                                })
                
                # Only add events with valid markets
                if processed_markets:
                    events.append({
                        "id": event_id,
                        "sport_key": sport,
                        "commence_time": format_to_12hour(commence_time or datetime.utcnow().isoformat()),
                        "home_team": home_team,
                        "away_team": away_team,
                        "bookmakers": [{
                            "key": "novig",
                            "title": "NoVig",
                            "last_update": format_to_12hour(datetime.utcnow().isoformat()),
                            "markets": processed_markets
                        }]
                    })
                
    except Exception as e:
        logger.warning(f"Failed to process Novig data: {e}")
    
    return events

def _process_prizepicks_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process PrizePicks data into Odds API format."""
    from datetime import datetime, timezone
    events = []
    
    try:
        logger.info(f"Processing PrizePicks data for {sport}")
        
        # PrizePicks returns projections in raw_response.combined
        raw_response = raw_data.get("raw_response", {})
        combined = raw_response.get("combined", [])
        included = raw_response.get("included", [])
        
        if not combined:
            logger.warning("No combined projections found in PrizePicks data")
            return events
        
        # Extract teams from included data
        teams_by_id = {}
        for item in included:
            if item.get("type") == "team":
                team_id = item.get("id")
                attrs = item.get("attributes", {})
                teams_by_id[team_id] = {
                    "abbreviation": attrs.get("abbreviation", ""),
                    "name": f"{attrs.get('market', '')} {attrs.get('name', '')}".strip(),
                }
        
        # Extract games from included data
        games_by_id = {}
        for item in included:
            if item.get("type") == "game":
                game_id = item.get("id")
                attrs = item.get("attributes", {})
                metadata = attrs.get("metadata", {})
                game_info = metadata.get("game_info", {})
                teams = game_info.get("teams", {})
                
                # Get team names from relationships or metadata
                home_team = teams.get("home", {}).get("abbreviation", "")
                away_team = teams.get("away", {}).get("abbreviation", "")
                
                # Try to find full team names
                relationships = item.get("relationships", {})
                if "home_team_data" in relationships:
                    home_team_id = relationships["home_team_data"].get("data", {}).get("id")
                    if home_team_id and home_team_id in teams_by_id:
                        home_team = teams_by_id[home_team_id]["name"]
                
                if "away_team_data" in relationships:
                    away_team_id = relationships["away_team_data"].get("data", {}).get("id")
                    if away_team_id and away_team_id in teams_by_id:
                        away_team = teams_by_id[away_team_id]["name"]
                
                games_by_id[game_id] = {
                    "id": game_id,
                    "home_team": home_team,
                    "away_team": away_team,
                    "start_time": attrs.get("start_time", ""),
                }
        
        # Group projections by game using relationships
        projections_by_game = {}
        for projection in combined:
            relationships = projection.get("relationships", {})
            game_rel = relationships.get("game", {})
            game_id = game_rel.get("data", {}).get("id")
            if not game_id:
                continue
                
            if game_id not in projections_by_game:
                projections_by_game[game_id] = []
            projections_by_game[game_id].append(projection)
        
        # Create events for each game
        for game_id, projections in projections_by_game.items():
            game_info = games_by_id.get(game_id, {})
            
            # Convert start time to 12-hour format
            start_time = game_info.get("start_time", "")
            if start_time:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    start_time = format_to_12hour(dt.isoformat())
                except:
                    from datetime import datetime, timezone
                    start_time = format_to_12hour(datetime.now(timezone.utc).isoformat())
            else:
                from datetime import datetime, timezone
                start_time = format_to_12hour(datetime.now(timezone.utc).isoformat())
            
            # Create event
            event = {
                "id": f"prizepicks_{game_id}",
                "sport_key": sport,
                "commence_time": start_time,
                "home_team": game_info.get("home_team", ""),
                "away_team": game_info.get("away_team", ""),
                "bookmakers": [{
                    "key": "prizepicks",
                    "title": "PrizePicks",
                    "last_update": format_to_12hour(raw_data.get("fetched_at", datetime.now(timezone.utc).isoformat())),
                    "markets": []
                }]
            }
            
            # Process player props
            if "player_props" in markets_list:
                # Group projections by player and stat
                player_props = {}
                for projection in projections:
                    player_name = projection.get("player_name", "")
                    attrs = projection.get("attributes", {})
                    stat_type = attrs.get("stat_type", "")
                    line_score = attrs.get("line_score", 0)
                    projection_type = attrs.get("projection_type", "")
                    
                    if not player_name or not stat_type:
                        continue
                    
                    prop_key = f"{player_name}_{stat_type}"
                    if prop_key not in player_props:
                        player_props[prop_key] = {
                            "player": player_name,
                            "stat": stat_type,
                            "line": line_score,
                            "outcomes": []
                        }
                    
                    # Add outcome (over/under) - PrizePicks typically has both over and under
                    player_props[prop_key]["outcomes"].append({
                        "name": "Over",
                        "price": 1.9  # PrizePicks typically offers 1.9x odds
                    })
                    player_props[prop_key]["outcomes"].append({
                        "name": "Under", 
                        "price": 1.9  # PrizePicks typically offers 1.9x odds
                    })
                
                # Create markets for each player prop
                for prop_key, prop_data in player_props.items():
                    if len(prop_data["outcomes"]) >= 2:  # Need both over and under
                        market = {
                            "key": "player_props",
                            "last_update": format_to_12hour(raw_data.get("fetched_at", datetime.now(timezone.utc).isoformat())),
                            "player": prop_data["player"],
                            "stat": prop_data["stat"],
                            "line": prop_data["line"],
                            "outcomes": prop_data["outcomes"][:2]  # Take only first 2 outcomes
                        }
                        event["bookmakers"][0]["markets"].append(market)
            
            # Only add event if it has markets
            if event["bookmakers"][0]["markets"]:
                events.append(event)
        
    except Exception as e:
        logger.warning(f"Failed to process PrizePicks data: {e}")
        import traceback
        traceback.print_exc()
    
    return events

def _process_dabble_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process Dabble data into Odds API format."""
    from datetime import datetime, timezone
    events = []
    
    try:
        logger.info(f"Processing Dabble data for {sport}")
        
        # Dabble returns props as a list directly
        if isinstance(raw_data, list):
            props = raw_data
        else:
            props = raw_data.get("props", [])
        
        if not props:
            logger.warning("No props found in Dabble data")
            return events
        
        # Group props by game/event
        events_by_game = {}
        for prop in props:
            # Extract game info from prop
            game_id = prop.get("fixtureId", "unknown")
            player_name = prop.get("playerName", "")
            team_name = prop.get("teamName", "")
            market_group = prop.get("marketGroupName", "")
            fixture_name = prop.get("fixtureName", "")
            
            # Extract line value from selection options
            line_value = 0
            selection_options = prop.get("selectionOptions", [])
            if selection_options:
                # Get the line from the first selection option name
                first_option = selection_options[0]
                option_name = first_option.get("name", "")
                # Extract number from option name (e.g., "A'ja Wilson points 26 over" -> 26)
                import re
                numbers = re.findall(r'\d+', option_name)
                if numbers:
                    line_value = float(numbers[0])
            
            if not player_name or not market_group:
                continue
            
            # Create or get event
            if game_id not in events_by_game:
                # Extract team names from fixture name
                home_team = ""
                away_team = ""
                if fixture_name:
                    # Format: "Phoenix Mercury @ Las Vegas Aces"
                    parts = fixture_name.split(" @ ")
                    if len(parts) == 2:
                        away_team = parts[0]
                        home_team = parts[1]
                
                events_by_game[game_id] = {
                    "id": f"dabble_{game_id}",
                    "sport_key": sport,
                    "commence_time": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                    "home_team": home_team,
                    "away_team": away_team,
                    "bookmakers": [{
                        "key": "dabble",
                        "title": "Dabble",
                        "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                        "markets": []
                    }]
                }
            
            # Add player prop market
            if "player_props" in markets_list:
                # Extract outcomes from selection options
                outcomes = []
                for option in selection_options:
                    option_name = option.get("name", "")
                    option_type = option.get("type", "")
                    option_price = option.get("price", "2")
                    
                    # Map option type to outcome name
                    if option_type == "more":
                        outcome_name = "Over"
                    elif option_type == "less":
                        outcome_name = "Under"
                    else:
                        continue
                    
                    # Convert price to decimal
                    try:
                        price = float(option_price)
                        # Convert to decimal odds (assuming it's fractional)
                        if price > 0:
                            decimal_price = (price / 100) + 1 if price > 1 else (100 / abs(price)) + 1
                        else:
                            decimal_price = 1.9  # Default
                    except:
                        decimal_price = 1.9
                    
                    outcomes.append({
                        "name": outcome_name,
                        "price": decimal_price
                    })
                
                if outcomes:
                    market = {
                        "key": "player_props",
                        "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                        "player": player_name,
                        "stat": market_group,
                        "line": line_value,
                        "outcomes": outcomes
                    }
                    
                    # Add team info if available
                    if team_name:
                        market["team"] = team_name
                    
                    events_by_game[game_id]["bookmakers"][0]["markets"].append(market)
        
        # Convert to list and filter events with markets
        for game_id, event in events_by_game.items():
            if event["bookmakers"][0]["markets"]:
                events.append(event)
        
    except Exception as e:
        logger.warning(f"Failed to process Dabble data: {e}")
        import traceback
        traceback.print_exc()
    
    return events

def _process_betr_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process Betr data into Odds API format."""
    from datetime import datetime, timezone
    events = []
    
    try:
        logger.info(f"Processing Betr data for {sport}")
        
        # Betr returns a list of events directly
        if isinstance(raw_data, list):
            raw_events = raw_data
        else:
            raw_events = raw_data.get("data", {}).get("getUpcomingEventsV2", [])
        
        if not raw_events:
            logger.warning("No events found in Betr data")
            return events
        
        for event in raw_events:
            event_id = event.get("id", "unknown")
            event_name = event.get("name", "")
            event_date = event.get("date", "")
            event_status = event.get("status", "")
            sport_name = event.get("sport", "")
            league_name = event.get("league", "")
            
            # Extract teams and players
            teams = []
            players = []
            
            # Handle different event types
            if "teams" in event:
                teams = event["teams"]
            elif "players" in event:
                players = event["players"]
            
            # Create event
            event_data = {
                "id": event_id,
                "sport_key": sport,
                "commence_time": format_to_12hour(event_date or datetime.now(timezone.utc).isoformat()),
                "home_team": "",
                "away_team": "",
                "bookmakers": [{
                    "key": "betr",
                    "title": "Betr",
                    "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                    "markets": []
                }]
            }
            
            # Extract team names for team events
            if teams and len(teams) >= 2:
                event_data["home_team"] = teams[0].get("name", "")
                event_data["away_team"] = teams[1].get("name", "")
                
                # Extract players from teams for player props
                all_players = []
                for team in teams:
                    team_players = team.get("players", [])
                    for player in team_players:
                        player["team_name"] = team.get("name", "")
                        all_players.append(player)
                players = all_players
            
            # Process player props if requested
            if "player_props" in markets_list and players:
                for player in players:
                    player_name = f"{player.get('firstName', '')} {player.get('lastName', '')}".strip()
                    player_position = player.get("position", "")
                    team_name = player.get("team_name", "")
                    projections = player.get("projections", [])
                    
                    for projection in projections:
                        stat_type = projection.get("name", "")
                        stat_label = projection.get("label", "")
                        stat_value = projection.get("value", 0.0)
                        current_value = projection.get("currentValue", 0.0)
                        
                        # Create player prop market
                        player_market = {
                            "key": "player_props",
                            "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                            "player": player_name,
                            "stat": stat_type,
                            "line": float(current_value or stat_value),
                            "outcomes": [
                                {
                                    "name": "Over",
                                    "price": 1.9  # Default odds since Betr doesn't provide odds
                                },
                                {
                                    "name": "Under", 
                                    "price": 1.9  # Default odds since Betr doesn't provide odds
                                }
                            ]
                        }
                        
                        # Add team info if available
                        if team_name:
                            player_market["team"] = team_name
                        
                        # Add position info
                        if player_position:
                            player_market["position"] = player_position
                        
                        event_data["bookmakers"][0]["markets"].append(player_market)
            
            # Only add events that have markets
            if event_data["bookmakers"][0]["markets"]:
                events.append(event_data)
        
    except Exception as e:
        logger.warning(f"Failed to process Betr data: {e}")
        import traceback
        traceback.print_exc()
    
    return events

# def _process_parlayplay_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
#     """Process ParlayPlay data into Odds API format."""
#     from datetime import datetime, timezone
#     events = []
#     
#     try:
#         logger.info(f"Processing ParlayPlay data for {sport}")
#         
#         # ParlayPlay returns results in raw_response.results
#         raw_response = raw_data.get("raw_response", {})
#         results = raw_response.get("results", [])
#         
#         if not results:
#             logger.warning("No results found in ParlayPlay data")
#             return events
#         
#         # Group results by game/event
#         events_by_game = {}
#         for result in results:
#             # Extract game info from result
#             match = result.get("match", {})
#             game_id = match.get("id", "unknown")
#             home_team = match.get("homeTeam", {}).get("teamAbbreviation", "")
#             away_team = match.get("awayTeam", {}).get("teamAbbreviation", "")
#             game_time = match.get("matchDate", "")
#             
#             # Extract player info
#             player = result.get("player", {})
#             player_name = player.get("fullName", "")
#             team = player.get("team", {})
#             team_name = team.get("teamnameAbbr", "")
#             
#             # Create or get event
#             if game_id not in events_by_game:
#                 events_by_game[game_id] = {
#                     "id": f"parlayplay_{game_id}",
#                     "sport_key": sport,
#                     "commence_time": format_to_12hour(game_time or datetime.now(timezone.utc).isoformat()),
#                     "home_team": home_team,
#                     "away_team": away_team,
#                     "bookmakers": [{
#                         "key": "parlayplay",
#                         "title": "ParlayPlay",
#                         "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
#                         "markets": []
#                     }]
#                 }
#             
#             # Extract player props from stats array
#             if "player_props" in markets_list and player_name:
#                 stats = result.get("stats", [])
#                 for stat in stats:
#                     stat_type = stat.get("challengeName", "")
#                     alt_lines = stat.get("altLines", {})
#                     values = alt_lines.get("values", [])
#                     
#                     if stat_type and values:
#                         # Process each line value
#                         for value in values:
#                             line_value = value.get("selectionPoints", 0)
#                             decimal_price_over = value.get("decimalPriceOver", 1.9)
#                             decimal_price_under = value.get("decimalPriceUnder", 1.9)
#                             
#                             # Skip if no valid prices
#                             if decimal_price_over == 0.0 and decimal_price_under == 0.0:
#                                 continue
#                             
#                             market = {
#                                 "key": "player_props",
#                                 "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
#                                 "player": player_name,
#                                 "stat": stat_type,
#                                 "line": line_value,
#                                 "outcomes": []
#                             }
#                             
#                             # Add team info if available
#                             if team_name:
#                                 market["team"] = team_name
#                             
#                             # Add over outcome if price > 0
#                             if decimal_price_over > 0.0:
#                                 market["outcomes"].append({
#                                     "name": "Over",
#                                     "price": decimal_price_over
#                                 })
#                             
#                             # Add under outcome if price > 0
#                             if decimal_price_under > 0.0:
#                                 market["outcomes"].append({
#                                     "name": "Under",
#                                     "price": decimal_price_under
#                                 })
#                             
#                             # Only add market if it has outcomes
#                             if market["outcomes"]:
#                                 events_by_game[game_id]["bookmakers"][0]["markets"].append(market)
#         
#         # Convert to list and filter events with markets
#         for game_id, event in events_by_game.items():
#             if event["bookmakers"][0]["markets"]:
#                 events.append(event)
#         
#     except Exception as e:
#         logger.warning(f"Failed to process ParlayPlay data: {e}")
#         import traceback
#         traceback.print_exc()
#     
#     return events

def _process_rebet_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process Rebet data into Odds API format."""
    from datetime import datetime, timezone
    events = []
    
    try:
        logger.info(f"Processing Rebet data for {sport}")
        
        # Rebet returns a list of events directly
        if isinstance(raw_data, list):
            raw_events = raw_data
        else:
            raw_events = raw_data.get("raw_events", [])
        
        if not raw_events:
            logger.warning("No events found in Rebet data")
            return events
        
        # Group events by game
        events_by_game = {}
        for event in raw_events:
            event_id = event.get("id", "unknown")
            sport_name = event.get("sport_name", "")
            league_name = event.get("league_name", "")
            start_time = event.get("start_time", "")
            
            # Extract competitors (teams)
            competitors_data = event.get("competitors", {})
            home_team = ""
            away_team = ""
            
            if "competitor" in competitors_data:
                competitors = competitors_data["competitor"]
                if len(competitors) >= 2:
                    # Find home and away teams by qualifier
                    for comp in competitors:
                        if comp.get("qualifier") == "home":
                            home_team = comp.get("name", "")
                        elif comp.get("qualifier") == "away":
                            away_team = comp.get("name", "")
            
            # Create event
            if event_id not in events_by_game:
                events_by_game[event_id] = {
                    "id": event_id,
                    "sport_key": sport,
                    "commence_time": format_to_12hour(start_time or datetime.now(timezone.utc).isoformat()),
                    "home_team": home_team,
                    "away_team": away_team,
                    "bookmakers": [{
                        "key": "rebet",
                        "title": "Rebet",
                        "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                        "markets": []
                    }]
                }
            
            # Process odds markets
            odds = event.get("odds", {})
            if odds and "market" in odds:
                # Rebet odds structure: odds.market is a list of markets
                markets = odds["market"]
                if isinstance(markets, list):
                    for market_item in markets:
                        market_name = market_item.get("name", "")
                        market_id = market_item.get("id", "")
                        outcomes = market_item.get("outcome", [])
                        
                        # Process different market types based on actual Rebet market names
                        if "winner" in market_name.lower() and "total" not in market_name.lower() and "h2h" in markets_list:
                            h2h_market = {
                                "key": "h2h",
                                "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                                "outcomes": []
                            }
                            
                            for outcome in outcomes:
                                if outcome.get("active") == "1":
                                    outcome_name = outcome.get("name", "")
                                    # Direct team name match
                                    if outcome_name == home_team:
                                        h2h_market["outcomes"].append({
                                            "name": home_team,
                                            "price": float(outcome.get("odds", 1.0))
                                        })
                                    elif outcome_name == away_team:
                                        h2h_market["outcomes"].append({
                                            "name": away_team,
                                            "price": float(outcome.get("odds", 1.0))
                                        })
                            
                            if h2h_market["outcomes"]:
                                events_by_game[event_id]["bookmakers"][0]["markets"].append(h2h_market)
                        
                        elif "handicap" in market_name.lower() and "total" not in market_name.lower() and "spreads" in markets_list:
                            spread_market = {
                                "key": "spreads",
                                "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                                "outcomes": []
                            }
                            
                            for outcome in outcomes:
                                if outcome.get("active") == "1":
                                    outcome_name = outcome.get("name", "")
                                    # Extract team name and point spread from outcome name (e.g., "Cleveland Browns (-0.5)")
                                    if home_team and home_team in outcome_name:
                                        # Extract point value from parentheses
                                        import re
                                        match = re.search(r'\(([+-]?\d+\.?\d*)\)', outcome_name)
                                        point = float(match.group(1)) if match else 0.0
                                        
                                        spread_market["outcomes"].append({
                                            "name": home_team,
                                            "price": float(outcome.get("odds", 1.0)),
                                            "point": point
                                        })
                                    elif away_team and away_team in outcome_name:
                                        match = re.search(r'\(([+-]?\d+\.?\d*)\)', outcome_name)
                                        point = float(match.group(1)) if match else 0.0
                                        
                                        spread_market["outcomes"].append({
                                            "name": away_team,
                                            "price": float(outcome.get("odds", 1.0)),
                                            "point": point
                                        })
                            
                            if spread_market["outcomes"]:
                                events_by_game[event_id]["bookmakers"][0]["markets"].append(spread_market)
                        
                        elif "total" in market_name.lower() and "handicap" not in market_name.lower() and "winner" not in market_name.lower() and "totals" in markets_list:
                            total_market = {
                                "key": "totals",
                                "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                                "outcomes": []
                            }
                            
                            for outcome in outcomes:
                                if outcome.get("active") == "1":
                                    outcome_name = outcome.get("name", "")
                                    # Extract over/under and point value from outcome name
                                    if "over" in outcome_name.lower():
                                        # Extract point value from outcome name (e.g., "Over 36.5")
                                        import re
                                        match = re.search(r'over\s+(\d+\.?\d*)', outcome_name.lower())
                                        point = float(match.group(1)) if match else 0.0
                                        
                                        total_market["outcomes"].append({
                                            "name": "Over",
                                            "price": float(outcome.get("odds", 1.0)),
                                            "point": point
                                        })
                                    elif "under" in outcome_name.lower():
                                        match = re.search(r'under\s+(\d+\.?\d*)', outcome_name.lower())
                                        point = float(match.group(1)) if match else 0.0
                                        
                                        total_market["outcomes"].append({
                                            "name": "Under",
                                            "price": float(outcome.get("odds", 1.0)),
                                            "point": point
                                        })
                            
                            if total_market["outcomes"]:
                                events_by_game[event_id]["bookmakers"][0]["markets"].append(total_market)
            
            # Process player props from odds markets
            if "player_props" in markets_list and odds and "market" in odds:
                markets = odds["market"]
                for market_item in markets:
                    market_name = market_item.get("name", "")
                    outcomes = market_item.get("outcome", [])
                    
                    # Look for player prop markets
                    if "player" in market_name.lower() and outcomes:
                        for outcome in outcomes:
                            if outcome.get("active") == "1":
                                outcome_name = outcome.get("name", "")
                                player_name = outcome.get("player_name", "")
                                
                                # Extract player name and stat/line from outcome name
                                # Format: "Player Name X+" or "Player Name X-"
                                if player_name and "+" in outcome_name:
                                    # Extract line value from outcome name
                                    import re
                                    match = re.search(r'(\d+(?:\.\d+)?)\+', outcome_name)
                                    line_value = float(match.group(1)) if match else 0.0
                                    
                                    # Extract stat type from market name
                                    stat_type = "Points"  # Default
                                    if "touchdown" in market_name.lower():
                                        stat_type = "Touchdowns"
                                    elif "rushing" in market_name.lower():
                                        stat_type = "Rushing Yards"
                                    elif "receiving" in market_name.lower():
                                        stat_type = "Receiving Yards"
                                    elif "passing" in market_name.lower():
                                        stat_type = "Passing Yards"
                                    elif "receptions" in market_name.lower():
                                        stat_type = "Receptions"
                                    elif "carries" in market_name.lower():
                                        stat_type = "Carries"
                                    
                                    # Clean player name (remove numbers and special chars)
                                    clean_player_name = re.sub(r'\s*\d+\+?$', '', player_name).strip()
                                    
                                    # Create player prop market
                                    player_market = {
                                        "key": "player_props",
                                        "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                                        "player": clean_player_name,
                                        "stat": stat_type,
                                        "line": line_value,
                                        "outcomes": [
                                            {
                                                "name": "Over",
                                                "price": float(outcome.get("odds", 1.9))
                                            }
                                        ]
                                    }
                                    
                                    # Add team info if available
                                    team = outcome.get("team", "")
                                    if team:
                                        # Map team number to team name
                                        if team == "1" and home_team:
                                            player_market["team"] = home_team
                                        elif team == "2" and away_team:
                                            player_market["team"] = away_team
                                    
                                    events_by_game[event_id]["bookmakers"][0]["markets"].append(player_market)
        
        # Convert to list and filter events with markets
        for event_id, event in events_by_game.items():
            if event["bookmakers"][0]["markets"]:
                events.append(event)
        
    except Exception as e:
        logger.warning(f"Failed to process Rebet data: {e}")
        import traceback
        traceback.print_exc()
    
    return events

def _process_fliff_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process Fliff data into Odds API format."""
    events = []
    
    try:
        raw_response = raw_data.get("raw_response", {})
        x_slots = raw_response.get("x_slots", {})
        updates = x_slots.get("prematch_subfeeds_updates", [])
        
        # Group updates by event_info to create events
        event_groups = {}
        for update in updates:
            market_updates = update.get("market_updates", [])
            for market_update in market_updates:
                groups = market_update.get("groups", [])
                for group in groups:
                    proposals = group.get("proposals", [])
                    for proposal in proposals:
                        event_info = proposal.get("t_121_event_info")
                        if event_info:
                            if event_info not in event_groups:
                                # Extract team names from event_info
                                if " vs " in event_info:
                                    teams = event_info.split(" vs ")
                                    if len(teams) == 2:
                                        event_groups[event_info] = {
                                            "away_team": teams[0].strip(),
                                            "home_team": teams[1].strip(),
                                            "markets": {}
                                        }
                            
                            # Extract market data
                            coeff = proposal.get("coeff")
                            selection_name = proposal.get("t_141_selection_name", "")
                            if coeff and selection_name and event_info in event_groups:
                                market_type = proposal.get("market_proposal_type")
                                
                                # Check for player props first (market types 7711/7712)
                                if market_type in [7711, 7712]:
                                    player_fkey = proposal.get("player_fkey")
                                    if player_fkey and player_fkey.startswith("extkey__dlt_player__"):
                                        # Extract player name from group_tag or visual_name
                                        group_tag = group.get("group_tag", "")
                                        visual_name = group.get("visual_name", "")
                                        
                                        # Get player name from group_tag (format: "player_id_Player Name#line")
                                        if "#" in group_tag:
                                            player_name = group_tag.split("#")[0].split("_", 1)[1] if "_" in group_tag else group_tag.split("#")[0]
                                        elif visual_name:
                                            player_name = visual_name
                                        else:
                                            player_name = "Unknown Player"
                                        
                                        # Map market types to standard prop names
                                        market_name = proposal.get("t_131_market_name", "")
                                        if "POINTS" in market_name:
                                            market_key = "player_points"
                                        elif "REBOUNDS" in market_name:
                                            market_key = "player_rebounds"
                                        elif "ASSISTS" in market_name:
                                            market_key = "player_assists"
                                        elif "THREE POINTERS" in market_name:
                                            market_key = "player_threes"
                                        elif "TRIPLE DOUBLE" in market_name:
                                            market_key = "player_triple_double"
                                        elif "POINTS AND REBOUNDS AND ASSISTS" in market_name:
                                            market_key = "player_pra"
                                        elif "HITS" in market_name:
                                            market_key = "player_hits"
                                        elif "RUNS" in market_name:
                                            market_key = "player_runs"
                                        elif "RBIS" in market_name or "RBI" in market_name:
                                            market_key = "player_rbis"
                                        elif "STRIKEOUTS" in market_name:
                                            market_key = "player_strikeouts"
                                        elif "WALKS" in market_name:
                                            market_key = "player_walks"
                                        elif "HOME RUNS" in market_name:
                                            market_key = "player_home_runs"
                                        else:
                                            # Map to standard market names if requested
                                            if "passing_yards" in markets_list:
                                                market_key = "passing_yards"
                                            elif "receiving_yards" in markets_list:
                                                market_key = "receiving_yards"
                                            elif "rushing_yards" in markets_list:
                                                market_key = "rushing_yards"
                                            elif "player_hits" in markets_list:
                                                market_key = "player_hits"
                                            elif "player_runs" in markets_list:
                                                market_key = "player_runs"
                                            elif "player_rbis" in markets_list:
                                                market_key = "player_rbis"
                                            else:
                                                market_key = f"player_prop_{market_type}"
                                        
                                        if market_key in markets_list:
                                            if market_key not in event_groups[event_info]["markets"]:
                                                event_groups[event_info]["markets"][market_key] = []
                                            
                                            outcome = {
                                                "name": selection_name,
                                                "price": coeff,
                                                "player": player_name
                                            }
                                            
                                            # Add point for player props (extract from group_tag or selection_name)
                                            if "#" in group_tag:
                                                try:
                                                    point_str = group_tag.split("#")[1].split(" /")[0]
                                                    outcome["point"] = float(point_str)
                                                except (ValueError, TypeError, IndexError):
                                                    pass
                                            elif selection_name and ("Over" in selection_name or "Under" in selection_name):
                                                # Try to extract number from selection name
                                                import re
                                                numbers = re.findall(r'\d+\.?\d*', selection_name)
                                                if numbers:
                                                    try:
                                                        outcome["point"] = float(numbers[0])
                                                    except (ValueError, TypeError):
                                                        pass
                                            
                                            event_groups[event_info]["markets"][market_key].append(outcome)
                                    continue
                                
                                # Handle main markets
                                elif market_type == 7791:  # Moneyline
                                    market_key = "h2h"
                                elif market_type == 7792:  # Spread
                                    market_key = "spreads"
                                elif market_type == 7793:  # Total
                                    market_key = "totals"
                                else:
                                    market_key = f"market_{market_type}"
                                
                                if market_key in markets_list:
                                    if market_key not in event_groups[event_info]["markets"]:
                                        event_groups[event_info]["markets"][market_key] = []
                                    
                                    outcome = {
                                        "name": selection_name,
                                        "price": coeff
                                    }
                                    
                                    # Add point for spreads and totals
                                    param_1 = proposal.get("t_142_selection_param_1")
                                    if param_1 and market_key in ["spreads", "totals"]:
                                        try:
                                            outcome["point"] = float(param_1)
                                        except (ValueError, TypeError):
                                            pass
                                    
                                    event_groups[event_info]["markets"][market_key].append(outcome)
                            
        
        # Convert to events format
        for event_info, event_data in event_groups.items():
            if event_data["home_team"] and event_data["away_team"]:
                # Generate a simple event ID from event_info
                event_id = event_info.replace(" ", "_").replace("vs", "").lower()
                
                event = {
                    "id": event_id,
                    "sport_key": sport,
                    "commence_time": "6:00 PM",  # Default time
                    "home_team": event_data["home_team"],
                    "away_team": event_data["away_team"],
                    "bookmakers": [{
                        "key": "fliff",
                        "title": "Fliff",
                        "last_update": "6:00 PM",
                        "markets": []
                    }]
                }
                
                # Add markets
                for market_key, outcomes in event_data["markets"].items():
                    if outcomes:
                        market = {
                            "key": market_key,
                            "last_update": "6:00 PM",
                            "outcomes": outcomes
                        }
                        event["bookmakers"][0]["markets"].append(market)
                
                if event["bookmakers"][0]["markets"]:
                    events.append(event)
        
        logger.info(f"Processed {len(events)} Fliff events for {sport}")
        
    except Exception as e:
        logger.warning(f"Failed to process Fliff data: {e}")
    
    return events

def _process_betonline_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process BetOnline data into Odds API format."""
    events = []
    
    try:
        raw_response = raw_data.get("raw_response", {})
        game_offering = raw_response.get("GameOffering", {})
        games_description = game_offering.get("GamesDescription", [])
        
        for game_date_group in games_description:
            games = game_date_group.get("Game", {})
            if not isinstance(games, dict):
                continue
                
            # Extract game info
            game_id = games.get("GameId")
            away_team = games.get("AwayTeam", "Unknown")
            home_team = games.get("HomeTeam", "Unknown")
            game_time = games.get("GameDateTime", "0001-01-01T00:00:00")
            
            # Convert game time to proper format
            if game_time == "0001-01-01T00:00:00":
                # Use current time if game time is not set
                from datetime import datetime, timezone
                game_time = datetime.now(timezone.utc).isoformat()
            
            # Create event
            event = {
                "id": str(game_id) if game_id else f"betonline-{away_team}-{home_team}",
                "sport_key": sport,
                "commence_time": format_to_12hour(game_time),
                "home_team": home_team,
                "away_team": away_team,
                "bookmakers": [{
                    "key": "betonline",
                    "title": "BetOnline",
                    "last_update": raw_data.get("fetched_at", ""),
                    "markets": []
                }]
            }
            
            # Process markets
            markets = []
            
            # Moneyline (h2h)
            if "h2h" in markets_list:
                away_line = games.get("AwayLine", {})
                home_line = games.get("HomeLine", {})
                
                outcomes = []
                if "MoneyLine" in away_line:
                    ml = away_line["MoneyLine"]
                    outcomes.append({
                        "name": away_team,
                        "price": ml.get("DecimalLine", 0)
                    })
                if "MoneyLine" in home_line:
                    ml = home_line["MoneyLine"]
                    outcomes.append({
                        "name": home_team,
                        "price": ml.get("DecimalLine", 0)
                    })
                
                if outcomes:
                    markets.append({
                        "key": "h2h",
                        "last_update": raw_data.get("fetched_at", ""),
                        "outcomes": outcomes
                    })
            
            # Spreads
            if "spreads" in markets_list:
                away_line = games.get("AwayLine", {})
                home_line = games.get("HomeLine", {})
                
                outcomes = []
                if "SpreadLine" in away_line:
                    spread = away_line["SpreadLine"]
                    outcomes.append({
                        "name": away_team,
                        "price": spread.get("DecimalLine", 0),
                        "point": spread.get("Point", 0)
                    })
                if "SpreadLine" in home_line:
                    spread = home_line["SpreadLine"]
                    outcomes.append({
                        "name": home_team,
                        "price": spread.get("DecimalLine", 0),
                        "point": spread.get("Point", 0)
                    })
                
                if outcomes:
                    markets.append({
                        "key": "spreads",
                        "last_update": raw_data.get("fetched_at", ""),
                        "outcomes": outcomes
                    })
            
            # Totals
            if "totals" in markets_list:
                total_line = games.get("TotalLine", {})
                total_data = total_line.get("TotalLine", {})
                
                outcomes = []
                if "Over" in total_data:
                    over = total_data["Over"]
                    outcomes.append({
                        "name": "Over",
                        "price": over.get("DecimalLine", 0),
                        "point": total_data.get("Point", 0)
                    })
                if "Under" in total_data:
                    under = total_data["Under"]
                    outcomes.append({
                        "name": "Under",
                        "price": under.get("DecimalLine", 0),
                        "point": total_data.get("Point", 0)
                    })
                
                if outcomes:
                    markets.append({
                        "key": "totals",
                        "last_update": raw_data.get("fetched_at", ""),
                        "outcomes": outcomes
                    })
            
            if markets:
                event["bookmakers"][0]["markets"] = markets
                events.append(event)
        
    except Exception as e:
        logger.warning(f"Failed to process BetOnline data: {e}")
    
    return events

def _process_bovada_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process Bovada data into Odds API format."""
    events = []
    
    try:
        responses = raw_data.get("responses", [])
        if not responses:
            return events
        
        for response in responses:
            payload = response.get("payload", [])
            if not payload:
                continue
                
            for item in payload:
                event_list = item.get("events", [])
                if not event_list:
                    continue
                    
                for event_data in event_list:
                    # Extract event info
                    event_id = event_data.get("id", "")
                    description = event_data.get("description", "")
                    start_time = event_data.get("startTime", 0)
                    link = event_data.get("link", "")
                    
                    # Convert timestamp to ISO format
                    from datetime import datetime, timezone
                    import re
                    
                    commence_time = None
                    
                    # Try to extract time from link first (more accurate)
                    if link:
                        time_match = re.search(r'(\d{12})$', link)
                        if time_match:
                            time_str = time_match.group(1)
                            try:
                                # Parse as YYYYMMDDHHMM
                                year = int(time_str[:4])
                                month = int(time_str[4:6])
                                day = int(time_str[6:8])
                                hour = int(time_str[8:10])
                                minute = int(time_str[10:12])
                                
                                dt = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
                                commence_time = dt.isoformat()
                            except (ValueError, IndexError):
                                pass
                    
                    # Fallback to startTime timestamp if link parsing failed
                    if not commence_time and start_time:
                        dt = datetime.fromtimestamp(start_time / 1000, tz=timezone.utc)
                        commence_time = dt.isoformat()
                    
                    # Final fallback to current time
                    if not commence_time:
                        commence_time = datetime.now(timezone.utc).isoformat()
                    
                    # Extract teams
                    competitors = event_data.get("competitors", [])
                    home_team = ""
                    away_team = ""
                    
                    for competitor in competitors:
                        if competitor.get("home"):
                            home_team = competitor.get("name", "")
                        else:
                            away_team = competitor.get("name", "")
                    
                    # Create event
                    event = {
                        "id": event_id,
                        "sport_key": sport,
                        "commence_time": format_to_12hour(commence_time),
                        "home_team": home_team,
                        "away_team": away_team,
                        "bookmakers": [{
                            "key": "bovada",
                            "title": "Bovada",
                            "last_update": format_to_12hour(raw_data.get("fetched_at", datetime.now(timezone.utc).isoformat())),
                            "markets": []
                        }]
                    }
                    
                    # Process markets
                    markets = []
                    display_groups = event_data.get("displayGroups", [])
                    
                    for group in display_groups:
                        group_markets = group.get("markets", [])
                        
                        for market in group_markets:
                            market_desc = market.get("description", "").lower()
                            market_key = ""
                            
                            # Map market types
                            if "head to head" in market_desc or "moneyline" in market_desc:
                                market_key = "h2h"
                            elif "spread" in market_desc:
                                market_key = "spreads"
                            elif "total" in market_desc or "over/under" in market_desc:
                                market_key = "totals"
                            elif "player" in market_desc or "prop" in market_desc or "passing" in market_desc or "rushing" in market_desc or "receiving" in market_desc:
                                market_key = "player_props"
                            else:
                                continue
                            
                            if market_key not in markets_list:
                                continue
                            
                            # Process outcomes
                            outcomes = []
                            market_outcomes = market.get("outcomes", [])
                            
                            for outcome in market_outcomes:
                                outcome_name = outcome.get("description", "")
                                price_data = outcome.get("price", {})
                                
                                if not outcome_name or not price_data:
                                    continue
                                
                                # Extract price based on format
                                if odds_format == "american":
                                    price = price_data.get("american", 0)
                                else:
                                    price = float(price_data.get("decimal", 0))
                                
                                # Convert American odds to decimal for consistency
                                if odds_format == "american" and price:
                                    try:
                                        price_int = int(price)
                                        if price_int > 0:
                                            price = (price_int / 100) + 1
                                        else:
                                            price = (100 / abs(price_int)) + 1
                                    except (ValueError, ZeroDivisionError):
                                        price = 0
                                
                                outcome_data = {
                                    "name": outcome_name,
                                    "price": price
                                }
                                
                                # Add point for spreads and totals
                                if market_key in ["spreads", "totals"]:
                                    # Extract point from outcome name or market
                                    import re
                                    point_match = re.search(r'([+-]?\d+\.?\d*)', outcome_name)
                                    if point_match:
                                        try:
                                            outcome_data["point"] = float(point_match.group(1))
                                        except ValueError:
                                            pass
                                
                                outcomes.append(outcome_data)
                            
                            if outcomes:
                                market_data = {
                                    "key": market_key,
                                    "last_update": format_to_12hour(raw_data.get("fetched_at", datetime.now(timezone.utc).isoformat())),
                                    "outcomes": outcomes
                                }
                                
                                # Add player info for player props
                                if market_key == "player_props":
                                    # Extract player name from market description or outcomes
                                    for outcome in outcomes:
                                        outcome_name = outcome.get("name", "")
                                        if outcome_name:
                                            # Simple player name extraction
                                            if " " in outcome_name and not any(word in outcome_name.lower() for word in ["over", "under", "yes", "no"]):
                                                market_data["player"] = outcome_name
                                                break
                                
                                markets.append(market_data)
                    
                    if markets:
                        event["bookmakers"][0]["markets"] = markets
                        events.append(event)
        
    except Exception as e:
        logger.warning(f"Failed to process Bovada data: {e}")
    
    return events

def _process_generic_data(book_key: str, raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process generic bookmaker data into Odds API format."""
    events = []
    
    try:
        # Generic processor for other bookmakers
        logger.info(f"Processing {book_key} data for {sport}")
        
    except Exception as e:
        logger.warning(f"Failed to process {book_key} data: {e}")
    
    return events

def _process_splashsports_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process SplashSports data into Odds API format."""
    from datetime import datetime, timezone
    events = []
    
    try:
        logger.info(f"Processing SplashSports data for {sport}")
        
        # SplashSports returns props directly in raw_data
        props = raw_data.get("props", [])
        
        if not props:
            logger.warning("No props found in SplashSports data")
            return events
        
        # Group props by game
        games = {}
        for prop in props:
            game_id = prop.get("game_id")
            if not game_id:
                continue
                
            if game_id not in games:
                game_info = prop.get("game", {})
                games[game_id] = {
                    "id": game_id,
                    "name": game_info.get("name", ""),
                    "start_date": game_info.get("start_date"),
                    "home_team": "",
                    "away_team": "",
                    "props": []
                }
                
                # Extract team names from game name
                game_name = game_info.get("name", "")
                if " vs " in game_name:
                    parts = game_name.split(" vs ")
                    games[game_id]["home_team"] = parts[1].strip() if len(parts) > 1 else ""
                    games[game_id]["away_team"] = parts[0].strip() if len(parts) > 0 else ""
            
            games[game_id]["props"].append(prop)
        
        # Convert games to events
        for game_id, game_data in games.items():
            # Only process if player_props is requested
            if "player_props" not in markets_list:
                continue
                
            event_data = {
                "id": game_id,
                "sport_key": sport,
                "commence_time": format_to_12hour(datetime.fromtimestamp(game_data["start_date"] / 1000, timezone.utc).isoformat()) if game_data["start_date"] else format_to_12hour(datetime.now(timezone.utc).isoformat()),
                "home_team": game_data["home_team"],
                "away_team": game_data["away_team"],
                "bookmakers": [{
                    "key": "splashsports",
                    "title": "SplashSports",
                    "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                    "markets": []
                }]
            }
            
            # Process player props
            for prop in game_data["props"]:
                player_name = prop.get("entity_name", "")
                stat_type = prop.get("type_display", prop.get("type", ""))
                line = prop.get("line", 0.0)
                
                # Create player prop market
                player_market = {
                    "key": "player_props",
                    "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                    "player": player_name,
                    "stat": stat_type,
                    "line": float(line),
                    "outcomes": [
                        {
                            "name": "Over",
                            "price": 1.9  # Default odds since SplashSports doesn't provide odds
                        },
                        {
                            "name": "Under", 
                            "price": 1.9  # Default odds since SplashSports doesn't provide odds
                        }
                    ]
                }
                
                event_data["bookmakers"][0]["markets"].append(player_market)
            
            # Only add events that have markets
            if event_data["bookmakers"][0]["markets"]:
                events.append(event_data)
        
    except Exception as e:
        logger.warning(f"Failed to process SplashSports data: {e}")
        import traceback
        traceback.print_exc()
    
    return events

def _process_underdog_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process Underdog data into Odds API format."""
    from datetime import datetime, timezone
    events = []
    
    try:
        logger.info(f"Processing Underdog data for {sport}")
        
        # Underdog returns responses array with different endpoints
        responses = raw_data.get("responses", [])
        
        if not responses:
            logger.warning("No responses found in Underdog data")
            return events
        
        # Find player_grouped_lines response which contains player props
        player_grouped_lines = None
        market_filters = None
        
        for response in responses:
            if response.get("endpoint") == "player_grouped_lines":
                player_grouped_lines = response.get("data", {})
            elif response.get("endpoint") == "market_filters":
                market_filters = response.get("data", {})
        
        if not player_grouped_lines:
            logger.warning("No player_grouped_lines found in Underdog data")
            return events
        
        # Extract data from player_grouped_lines
        lines = player_grouped_lines.get("lines", [])
        over_under_lines = player_grouped_lines.get("over_under_lines", {})
        appearances = player_grouped_lines.get("appearances", {})
        players = player_grouped_lines.get("players", {})
        games = player_grouped_lines.get("games", {})
        solo_games = player_grouped_lines.get("solo_games", {})
        
        if not over_under_lines:
            logger.warning("No over_under_lines found in Underdog player_grouped_lines data")
            return events
        
        # Data is already in dict format from player_grouped_lines
        appearances_dict = appearances
        players_dict = players
        games_dict = games
        
        # Combine games and solo_games for sports that use solo_games (tennis, mma)
        all_games = {**games, **solo_games}
        
        # First, create games dict from all_games data (includes both games and solo_games)
        games = {}
        for game in all_games.values():
            match_id = game.get("id")
            if not match_id:
                continue
                
            # Extract team names from game title
            full_title = game.get("full_team_names_title", "")
            title = game.get("title", "Unknown Teams")
            
            home_team = ""
            away_team = ""
            if full_title and " @ " in full_title:
                parts = full_title.split(" @ ")
                away_team = parts[0].strip() if len(parts) > 0 else ""
                home_team = parts[1].strip() if len(parts) > 1 else ""
            elif title:
                # For solo_games, use the title directly (e.g., "Sinner vs Altmaier")
                if " vs " in title:
                    parts = title.split(" vs ")
                    home_team = parts[0].strip() if len(parts) > 0 else ""
                    away_team = parts[1].strip() if len(parts) > 1 else ""
                else:
                    home_team = title
                    away_team = title
            
            # Get game start time from match_progress
            match_progress = game.get("match_progress", "")
            commence_time = datetime.now(timezone.utc).isoformat()
            if match_progress:
                # Parse time like "Sun 09:30am" - for now use current time
                commence_time = datetime.now(timezone.utc).isoformat()
            
            games[match_id] = {
                "id": str(match_id),
                "home_team": home_team,
                "away_team": away_team,
                "commence_time": commence_time,
                "props": []
            }
        
        # Now group lines by game/match
        for line_id, line in over_under_lines.items():
            if line.get("status") != "active":
                continue
            
            # Get appearance ID from over_under.appearance_stat
            over_under = line.get("over_under", {})
            appearance_stat = over_under.get("appearance_stat", {})
            appearance_id = appearance_stat.get("appearance_id")
            if not appearance_id:
                continue
                
            # Get appearance details
            appearance = appearances_dict.get(appearance_id)
            if not appearance:
                continue
                
            match_id = appearance.get("match_id")
            if not match_id or match_id not in games:
                continue
            
            # Extract player name from player data
            player_id = appearance.get("player_id")
            player_name = ""
            if player_id and player_id in players_dict:
                player_data = players_dict[player_id]
                first_name = player_data.get("first_name", "")
                last_name = player_data.get("last_name", "")
                player_name = f"{first_name} {last_name}".strip()
            
            # Extract stat info from appearance_stat
            stat_type = appearance_stat.get("display_stat", "")
            line_value = line.get("stat_value", 0.0)
            
            # Get over/under odds from options
            over_odds = 1.9  # Default
            under_odds = 1.9  # Default
            
            options = line.get("options", [])
            for option in options:
                if option.get("choice") == "higher":
                    over_odds = float(option.get("decimal_price", 1.9))
                elif option.get("choice") == "lower":
                    under_odds = float(option.get("decimal_price", 1.9))
            
            prop_data = {
                "player": player_name,
                "stat": stat_type,
                "line": float(line_value),
                "over_odds": over_odds,
                "under_odds": under_odds,
                "appearance_id": appearance_id
            }
            
            games[match_id]["props"].append(prop_data)
        
        # Convert games to events
        for match_id, game_data in games.items():
            # Only process if player_props is requested
            if "player_props" not in markets_list:
                continue
                
            event_data = {
                "id": str(match_id),
                "sport_key": sport,
                "commence_time": format_to_12hour(game_data["commence_time"]),
                "home_team": game_data["home_team"],
                "away_team": game_data["away_team"],
                "bookmakers": [{
                    "key": "underdog",
                    "title": "Underdog",
                    "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                    "markets": []
                }]
            }
            
            # Process player props
            for prop in game_data["props"]:
                player_market = {
                    "key": "player_props",
                    "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                    "player": prop["player"],
                    "stat": prop["stat"],
                    "line": prop["line"],
                    "outcomes": [
                        {
                            "name": "Over",
                            "price": float(prop["over_odds"])
                        },
                        {
                            "name": "Under", 
                            "price": float(prop["under_odds"])
                        }
                    ]
                }
                
                event_data["bookmakers"][0]["markets"].append(player_market)
            
            # Only add events that have markets
            if event_data["bookmakers"][0]["markets"]:
                events.append(event_data)
        
    except Exception as e:
        logger.warning(f"Failed to process Underdog data: {e}")
        import traceback
        traceback.print_exc()
    
    return events

def _process_propscash_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process PropsCash data into Odds API format."""
    from datetime import datetime, timezone
    events = []
    
    try:
        logger.info(f"Processing PropsCash data for {sport}")
        
        # PropsCash returns dict with raw_lines containing data array
        if not isinstance(raw_data, dict):
            logger.warning("PropsCash data is not a dict")
            return events
        
        # Extract player data from raw_lines
        raw_lines = raw_data.get("raw_lines", {})
        if not isinstance(raw_lines, dict):
            logger.warning("PropsCash raw_lines is not a dict")
            return events
            
        player_data = raw_lines.get("data", [])
        if not isinstance(player_data, list):
            logger.warning("PropsCash player data is not a list")
            return events
        
        if not player_data:
            logger.warning("No PropsCash player data found")
            return events
        
        # Group players by game
        games_dict = {}
        
        for player_data in player_data:
            if not isinstance(player_data, dict):
                continue
                
            player_name = player_data.get("name", "")
            game_start = player_data.get("gameStart", "")
            home_team = player_data.get("homeTeam", "")
            away_team = player_data.get("awayTeam", "")
            team = player_data.get("team", "")
            projection = player_data.get("projection", {})
            game_id = player_data.get("gameId", "")
            
            if not all([player_name, game_start, home_team, away_team, team, game_id]):
                continue
            
            # Create game key
            game_key = f"{game_id}_{home_team}_{away_team}"
            
            if game_key not in games_dict:
                # Parse game start time
                try:
                    if game_start.endswith('Z'):
                        game_start = game_start.replace('Z', '+00:00')
                    commence_time = datetime.fromisoformat(game_start)
                except:
                    commence_time = datetime.now(timezone.utc)
                
                games_dict[game_key] = {
                    "id": game_id,
                    "sport_title": sport.replace("_", " ").title(),
                    "commence_time": commence_time.isoformat(),
                    "home_team": home_team,
                    "away_team": away_team,
                    "players": []
                }
            
            # Process player markets
            player_markets = []
            
            for stat_type, stat_data in projection.items():
                if not isinstance(stat_data, dict):
                    continue
                    
                summary = stat_data.get("summary", {})
                if not summary or summary.get("manualOU") is None:
                    continue
                
                # Convert stat type to readable market name
                market_name = stat_type.replace("_", " ").title()
                
                # Create market outcomes
                outcomes = []
                
                # Over outcome
                over_price = summary.get("overPrice")
                if over_price is not None:
                    outcomes.append({
                        "name": f"{player_name} Over {summary['manualOU']}",
                        "price": over_price if odds_format == "american" else _convert_american_to_decimal(over_price)
                    })
                
                # Under outcome
                under_price = summary.get("underPrice")
                if under_price is not None:
                    outcomes.append({
                        "name": f"{player_name} Under {summary['manualOU']}",
                        "price": under_price if odds_format == "american" else _convert_american_to_decimal(under_price)
                    })
                
                if outcomes:
                    player_markets.append({
                        "key": f"player_{stat_type}",
                        "title": f"{market_name}",
                        "outcomes": outcomes
                    })
            
            # Add player data to game
            if player_markets:
                games_dict[game_key]["players"].append({
                    "name": player_name,
                    "team": team,
                    "markets": player_markets
                })
        
        # Convert games to events format
        for game_key, game_data in games_dict.items():
            if not game_data["players"]:
                continue
                
            # Create bookmaker data
            bookmaker_data = {
                "key": "propscash",
                "title": "PropsCash",
                "markets": []
            }
            
            # Add all player markets to the bookmaker
            for player in game_data["players"]:
                bookmaker_data["markets"].extend(player["markets"])
            
            if bookmaker_data["markets"]:
                event_data = {
                    "id": game_data["id"],
                    "sport_title": game_data["sport_title"],
                    "commence_time": game_data["commence_time"],
                    "home_team": game_data["home_team"],
                    "away_team": game_data["away_team"],
                    "bookmakers": [bookmaker_data]
                }
                events.append(event_data)
        
    except Exception as e:
        logger.warning(f"Failed to process PropsCash data: {e}")
        import traceback
        traceback.print_exc()
    
    return events

def _process_pick6_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process DraftKings Pick6 data into Odds API format."""
    from datetime import datetime, timezone
    events = []
    
    try:
        logger.info(f"Processing Pick6 data for {sport}")
        
        # Pick6 returns pickables in raw_response
        raw_response = raw_data.get("raw_response", {})
        pickables = raw_response.get("pickables", [])
        
        if not pickables:
            logger.warning("No pickables found in Pick6 data")
            return events
        
        # Group pickables by game/event
        events_by_game = {}
        
        for pickable in pickables:
            # Extract pickable entities (players)
            pickable_entities = pickable.get("pickableEntities", [])
            
            for entity in pickable_entities:
                # Extract game info from pickableCompetitions
                pickable_competitions = entity.get("pickableCompetitions", [])
                
                for competition in pickable_competitions:
                    competition_summary = competition.get("competitionSummary", {})
                    game_id = competition_summary.get("competitionId", "unknown")
                    home_team_info = competition_summary.get("homeTeam", {})
                    away_team_info = competition_summary.get("awayTeam", {})
                    start_time = competition_summary.get("startTime", "")
                    
                    home_team = home_team_info.get("name", "")
                    away_team = away_team_info.get("name", "")
                    
                    # Create or get event
                    if game_id not in events_by_game:
                        events_by_game[game_id] = {
                            "id": f"pick6_{game_id}",
                            "sport_key": sport,
                            "commence_time": format_to_12hour(start_time or datetime.now(timezone.utc).isoformat()),
                            "home_team": home_team,
                            "away_team": away_team,
                            "bookmakers": [{
                                "key": "pick6",
                                "title": "DraftKings Pick6",
                                "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                                "markets": []
                            }]
                        }
                    
                    # Process player props
                    if "player_props" in markets_list:
                        # Extract player info
                        player_name = entity.get("displayName", "")
                        team_info = competition.get("team", {})
                        team_name = team_info.get("name", "")
                        
                        # Extract market category info
                        market_category_id = pickable.get("marketCategoryId")
                        
                        # Map market category ID to stat type based on the actual API response
                        stat_type_map = {
                            2834: "Walks",  # BB
                            2909: "Hits",  # H
                            2068: "Runs",  # R
                            2043: "RBIs",  # RBI
                            2019: "Home Runs",  # HR
                            2871: "Strikeouts Thrown",  # SO
                            19: "Walks Allowed",  # Walks
                            21: "Hits Against",  # HA
                            405: "Outs",  # O
                            409: "Batter Fantasy Points",  # FPTS
                            965: "Singles",  # 1B
                            1832: "Hits + Runs + RBIs",  # H+R+RBI
                            20: "Total Bases",  # Bases
                            2354: "Doubles",  # 2B
                            2383: "Triples",  # 3B
                            2413: "Stolen Bases",  # SB
                            2978: "Batter Strikeouts",  # K
                        }
                        
                        stat_type = stat_type_map.get(market_category_id, f"Stat_{market_category_id}")
                        
                        if player_name and stat_type:
                            # Pick6 doesn't provide actual odds, so use default values
                            over_decimal = 1.9
                            under_decimal = 1.9
                            
                            # For now, use a default line value (this would need to be extracted from actual data)
                            line_value = 0.5
                            
                            market = {
                                "key": "player_props",
                                "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                                "player": player_name,
                                "stat": stat_type,
                                "line": line_value,
                                "outcomes": [
                                    {
                                        "name": "Over",
                                        "price": over_decimal
                                    },
                                    {
                                        "name": "Under",
                                        "price": under_decimal
                                    }
                                ]
                            }
                            
                            # Add team info if available
                            if team_name:
                                market["team"] = team_name
                            
                            events_by_game[game_id]["bookmakers"][0]["markets"].append(market)
        
        # Convert to list and filter events with markets
        for game_id, event in events_by_game.items():
            if event["bookmakers"][0]["markets"]:
                events.append(event)
        
    except Exception as e:
        logger.warning(f"Failed to process Pick6 data: {e}")
        import traceback
        traceback.print_exc()
    
    return events

def _process_pinnacle_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process Pinnacle data into Odds API format."""
    from datetime import datetime, timezone
    events = []
    
    try:
        logger.info(f"Processing Pinnacle data for {sport}")
        
        matched_games = raw_data.get("matched_games", [])
        raw_specials = raw_data.get("raw_markets_by_special", {})
        raw_related = raw_data.get("raw_related_by_matchup", {})
        raw_markets = raw_data.get("raw_markets", [])
        
        if not matched_games:
            logger.warning("No matched games found in Pinnacle data")
            # If no matched games but we have player props, create a generic event
            if "player_props" in markets_list and (raw_related or raw_markets):
                # Create a generic event for player props
                event = {
                    "id": f"pinnacle_player_props_{sport}",
                    "sport_key": sport,
                    "commence_time": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                    "home_team": "TBD",
                    "away_team": "TBD",
                    "bookmakers": [{
                        "key": "pinnacle",
                        "title": "Pinnacle",
                        "markets": []
                    }]
                }
                
                # Process player props from both related matchups and main markets
                player_props_added = 0
                if raw_related:
                    player_props_added += _process_pinnacle_player_props(raw_related, raw_specials, odds_format, event)
                if raw_markets:
                    player_props_added += _process_pinnacle_main_markets_player_props(raw_markets, raw_data.get('raw_matchups', []), odds_format, event)
                
                if player_props_added > 0:
                    events.append(event)
                    logger.info(f"Created generic event with {player_props_added} player props")
            
            return events
        
        for game in matched_games:
            teams = game.get("teams", [])
            if len(teams) != 2:
                continue
                
            home_team = teams[0]
            away_team = teams[1]
            start_time = game.get("start_time", "")
            game_id = game.get("game_id", "")
            
            # Create event structure
            event = {
                "id": f"pinnacle_{game_id}",
                "sport_key": sport,
                "commence_time": format_to_12hour(start_time or datetime.now(timezone.utc).isoformat()),
                "home_team": home_team,
                "away_team": away_team,
                "bookmakers": [{
                    "key": "pinnacle",
                    "title": "Pinnacle",
                    "markets": []
                }]
            }
            
            # Process main game markets (moneyline, spread, total)
            game_markets = game.get("markets", [])
            for market in game_markets:
                market_type = market.get("type", "")
                
                if market_type == "moneyline" and "h2h" in markets_list:
                    event["bookmakers"][0]["markets"].append({
                        "key": "h2h",
                        "outcomes": _process_pinnacle_market_outcomes(market, odds_format, home_team, away_team)
                    })
                elif market_type == "spread" and "spreads" in markets_list:
                    event["bookmakers"][0]["markets"].append({
                        "key": "spreads",
                        "outcomes": _process_pinnacle_market_outcomes(market, odds_format, home_team, away_team)
                    })
                elif market_type == "total" and "totals" in markets_list:
                    event["bookmakers"][0]["markets"].append({
                        "key": "totals",
                        "outcomes": _process_pinnacle_market_outcomes(market, odds_format, home_team, away_team)
                    })
            
                    # Process player props from related matchups if requested
                    if "player_props" in markets_list:
                        _process_pinnacle_player_props(raw_related, raw_specials, odds_format, event)
                        # Also process player props from main markets (for NFL)
                        _process_pinnacle_main_markets_player_props(raw_data.get('raw_markets', []), raw_data.get('raw_matchups', []), odds_format, event)
            
            # Only add events that have markets
            if event["bookmakers"][0]["markets"]:
                events.append(event)
        
        logger.info(f"Processed {len(events)} Pinnacle events for {sport}")
        
    except Exception as e:
        logger.warning(f"Failed to process Pinnacle data: {e}")
        import traceback
        traceback.print_exc()
    
    return events

def _process_pinnacle_player_props(raw_related: Dict[str, Any], raw_specials: Dict[str, Any], odds_format: str, event: Dict[str, Any]) -> int:
    """Process player props from Pinnacle related matchups data."""
    player_props_added = 0
    
    for matchup_id, related_data in raw_related.items():
        if isinstance(related_data, list):
            for special in related_data:
                if isinstance(special, dict) and special.get("type") == "special":
                    special_info = special.get("special", {})
                    if special_info and "Player Props" in special_info.get("category", ""):
                        description = special_info.get("description", "")
                        if description:
                            # Extract player name and stat from description
                            # Formats: "Player Name Total Stat Name" or "Player Name (Stat Name)"
                            parts = description.split()
                            if len(parts) >= 3:
                                # Find where the stat description starts
                                player_name_parts = []
                                stat_parts = []
                                
                                # Check for parentheses format: "Player Name (Stat Name)"
                                if "(" in description and ")" in description:
                                    # Extract content between parentheses
                                    start_paren = description.find("(")
                                    end_paren = description.find(")")
                                    if start_paren != -1 and end_paren != -1:
                                        player_name = description[:start_paren].strip()
                                        stat_type = description[start_paren+1:end_paren].strip()
                                    else:
                                        player_name = "Unknown Player"
                                        stat_type = "Unknown Stat"
                                # Look for "Total" to separate player from stat
                                elif "Total" in parts:
                                    total_index = parts.index("Total")
                                    player_name_parts = parts[:total_index]
                                    stat_parts = parts[total_index + 1:]
                                    player_name = " ".join(player_name_parts) if player_name_parts else "Unknown Player"
                                    stat_type = " ".join(stat_parts) if stat_parts else "Unknown Stat"
                                else:
                                    # If no "Total", try to separate by common patterns
                                    for i, part in enumerate(parts):
                                        if i == 0:  # First word is likely part of player name
                                            player_name_parts.append(part)
                                        elif part in ["Points", "Assists", "Rebounds", "Threes", "Made", "Steals", "Blocks", "Goals", "Shots"]:
                                            # Found stat-related word
                                            stat_parts = parts[i:]
                                            break
                                        else:
                                            player_name_parts.append(part)
                                    
                                    player_name = " ".join(player_name_parts) if player_name_parts else "Unknown Player"
                                    stat_type = " ".join(stat_parts) if stat_parts else "Unknown Stat"
                                
                                # Get the actual market data for this special
                                special_id = special.get("id")
                                if special_id and str(special_id) in raw_specials:
                                    special_markets = raw_specials[str(special_id)]
                                    if isinstance(special_markets, list):
                                        for market in special_markets:
                                            if isinstance(market, dict):
                                                market_outcomes = _process_pinnacle_market_outcomes(market, odds_format)
                                                if market_outcomes:
                                                    # Extract line value from market
                                                    line_value = None
                                                    for price in market.get("prices", []):
                                                        if price.get("points") is not None:
                                                            line_value = price.get("points")
                                                            break
                                                    
                                                    market_data = {
                                                        "key": "player_props",
                                                        "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                                                        "player": player_name,
                                                        "stat": stat_type,
                                                        "outcomes": market_outcomes
                                                    }
                                                    
                                                    if line_value is not None:
                                                        market_data["line"] = line_value
                                                    
                                                    event["bookmakers"][0]["markets"].append(market_data)
                                                    player_props_added += 1
    
    return player_props_added

def _process_pinnacle_main_markets_player_props(raw_markets: List[Dict[str, Any]], raw_matchups: List[Dict[str, Any]], odds_format: str, event: Dict[str, Any]) -> int:
    """Process player props from main markets (for NFL and other sports)."""
    player_props_added = 0
    
    try:
        # Create lookup for matchups to get player info
        matchups_by_id = {}
        for matchup in raw_matchups:
            if isinstance(matchup, dict) and 'id' in matchup:
                matchups_by_id[matchup['id']] = matchup
        
        for market in raw_markets:
            if not isinstance(market, dict):
                continue
                
            # Look for total markets with Over/Under participants (player props)
            if market.get("type") == "total":
                matchup_id = market.get("matchupId")
                
                prices = market.get("prices", [])
                if len(prices) == 2:
                    # Check if this looks like a player prop (has points/lines)
                    has_points = any(price.get("points") is not None for price in prices)
                    
                    if has_points:
                        # Extract line value
                        line_value = None
                        for price in prices:
                            if price.get("points") is not None:
                                line_value = price.get("points")
                                break
                        
                        # Process outcomes
                        outcomes = _process_pinnacle_market_outcomes(market, odds_format)
                        
                        if outcomes:
                            # Extract player name and stat from matchup data
                            player_name = f"Player {matchup_id}"  # Default fallback
                            stat_type = "Total"  # Default fallback
                            
                            if matchup_id in matchups_by_id:
                                matchup = matchups_by_id[matchup_id]
                                special = matchup.get('special', {})
                                if special:
                                    description = special.get('description', '')
                                    if description:
                                        # Parse description like "Devin Singletary Total Touchdowns"
                                        parts = description.split()
                                        if len(parts) >= 3:
                                            # Look for "Total" to separate player from stat
                                            if "Total" in parts:
                                                total_index = parts.index("Total")
                                                player_name = " ".join(parts[:total_index])
                                                stat_type = " ".join(parts[total_index + 1:])
                                            else:
                                                # Fallback: assume first part is player name
                                                player_name = parts[0]
                                                stat_type = " ".join(parts[1:])
                            
                            market_data = {
                                "key": "player_props",
                                "last_update": format_to_12hour(datetime.now(timezone.utc).isoformat()),
                                "player": player_name,
                                "stat": stat_type,
                                "outcomes": outcomes
                            }
                            
                            if line_value is not None:
                                market_data["line"] = line_value
                            
                            event["bookmakers"][0]["markets"].append(market_data)
                            player_props_added += 1
                            
                            # Limit to avoid too many props
                            if player_props_added >= 100:
                                break
    
    except Exception as e:
        logger.warning(f"Failed to process main markets player props: {e}")
    
    return player_props_added

def _process_pinnacle_market_outcomes(market: Dict[str, Any], odds_format: str, home_team: str = None, away_team: str = None) -> List[Dict[str, Any]]:
    """Process Pinnacle market outcomes into standard format."""
    outcomes = []
    
    try:
        prices = market.get("prices", [])
        for price in prices:
            if isinstance(price, dict):
                price_value = price.get("price", 0)
                
                if price_value != 0:
                    # Determine the outcome name
                    name = None
                    
                    # For main markets, use designation with actual team names
                    if "designation" in price:
                        designation = price.get("designation")
                        if designation == "home" and home_team:
                            name = home_team
                        elif designation == "away" and away_team:
                            name = away_team
                        elif designation in ["over", "under"]:
                            name = designation.capitalize()
                        else:
                            # Fallback to generic names if team names not available
                            name = designation.capitalize()
                    
                    # For player props, use participantId mapping
                    elif "participantId" in price:
                        participant_id = price.get("participantId")
                        name = "Over" if participant_id and participant_id % 2 == 1 else "Under"
                    
                    if name:
                        outcome_data = {
                            "name": name, 
                            "price": price_value if odds_format == "american" else _convert_american_to_decimal(price_value)
                        }
                        
                        # Add points for spreads and totals
                        if "points" in price:
                            outcome_data["point"] = price.get("points")
                        
                        outcomes.append(outcome_data)
                        
    except Exception as e:
        logger.warning(f"Failed to process Pinnacle market outcomes: {e}")
    
    return outcomes

def _convert_american_to_decimal(american_odds: int) -> float:
    """Convert American odds to decimal odds."""
    if american_odds > 0:
        return round((american_odds / 100) + 1, 2)
    else:
        return round((100 / abs(american_odds)) + 1, 2)

def _process_market_outcomes(market: Dict[str, Any], odds_format: str) -> List[Dict[str, Any]]:
    """Process market outcomes into Odds API format."""
    outcomes = []
    
    try:
        if "outcomes" in market:
            for outcome in market["outcomes"]:
                if isinstance(outcome, dict):
                    price = outcome.get("price", 0)
                    
                    outcomes.append({
                        "name": outcome.get("name", "Unknown"),
                        "price": price
                    })
                    
    except Exception as e:
        logger.warning(f"Failed to process market outcomes: {e}")
    
    return outcomes

def _map_novig_market_type(novig_type: str) -> str:
    """Map Novig market types to Odds API format."""
    mapping = {
        "MONEY": "h2h",
        "SPREAD": "spreads", 
        "TOTAL": "totals",
        "TEAM_TOTAL": "team_totals"
    }
    return mapping.get(novig_type, novig_type.lower())

def _process_novig_market_outcomes(market: Dict[str, Any], odds_format: str, home_team: str = None, away_team: str = None) -> List[Dict[str, Any]]:
    """Process Novig market outcomes into Odds API format."""
    outcomes = []
    
    try:
        if "outcomes" in market:
            # Get metadata from the market
            player_name = None
            if "player" in market and market["player"]:
                player_name = market["player"].get("full_name")
            
            strike = market.get("strike")
            description = market.get("description", "")
            
            for outcome in market["outcomes"]:
                if not isinstance(outcome, dict):
                    continue
                
                # Get the price - use 'available' first, then 'last'
                price = outcome.get("available") or outcome.get("last")
                
                # Skip outcomes without prices
                if price is None:
                    continue
                
                # Return raw price as-is (no conversion)
                american_price = price
                
                # Get team/outcome name
                name = "Unknown"
                if "competitor" in outcome and outcome["competitor"]:
                    name = outcome["competitor"].get("name", "Unknown")
                elif "description" in outcome:
                    name = outcome["description"]
                
                # Build outcome with additional metadata
                outcome_data = {
                    "name": name,
                    "price": american_price
                }
                
                # Add player name if available
                if player_name:
                    outcome_data["player"] = player_name
                
                # Add point/strike if available
                if strike is not None:
                    outcome_data["point"] = strike
                
                # Add full description for context
                if description:
                    outcome_data["description"] = description
                
                # Add team info for player props
                if player_name and (home_team or away_team):
                    # Try to determine which team the player belongs to
                    # This is a simple heuristic - in practice you might need more sophisticated matching
                    player_team = None
                    if home_team and player_name.lower() in home_team.lower():
                        player_team = home_team
                    elif away_team and player_name.lower() in away_team.lower():
                        player_team = away_team
                    else:
                        # Default to home team if we can't determine
                        player_team = home_team
                    
                    if player_team:
                        outcome_data["team"] = player_team
                
                outcomes.append(outcome_data)
                    
    except Exception as e:
        logger.warning(f"Failed to process Novig market outcomes: {e}")
    
    return outcomes

# Sport key mapping from Odds API format to internal streamer format
SPORT_KEY_MAPPING = {
    "americanfootball_nfl": "americanfootball_nfl",
    "americanfootball_ncaaf": "americanfootball_ncaaf", 
    "basketball_nba": "basketball_nba",
    "basketball_wnba": "basketball_wnba",
    "basketball_ncaa": "basketball_ncaa",
    "baseball_mlb": "baseball_mlb",
    "icehockey_nhl": "icehockey_nhl",
    "soccer_mls": "soccer_mls",
    "soccer_epl": "soccer_epl",
    "soccer_championship": "soccer_championship",
    "soccer_efl_cup": "soccer_efl_cup",
    "soccer_serie_a": "soccer_serie_a",
    "soccer_ligue_1": "soccer_ligue_1",
    "soccer_bundesliga": "soccer_bundesliga",
    "soccer_premiership": "soccer_premiership",
    "soccer_eredivisie": "soccer_eredivisie",
    "soccer_superliga": "soccer_superliga",
    "soccer_2_bundesliga": "soccer_2_bundesliga",
    "soccer_super_lig": "soccer_super_lig",
    "soccer_laliga_2": "soccer_laliga_2",
    "soccer_k_league_1": "soccer_k_league_1",
    "soccer_conmebol_sudamericana": "soccer_conmebol_sudamericana",
    "soccer_champions_league": "soccer_champions_league",
    "soccer_laliga": "soccer_laliga",
    "soccer_world_cup_qualification_uefa": "soccer_world_cup_qualification_uefa",
    "soccer_world_cup_qualification_caf": "soccer_world_cup_qualification_caf",
    "tennis_atp": "tennis",
    "tennis_wta": "tennis",
    "tennis": "tennis",
    "mma_ufc": "mma",
    "mma": "mma",
    "esports_lol": "esports_lol",
    "esports_cs2": "esports_counterstrike",
    "esports_counterstrike": "esports_counterstrike",
    "esports_valorant": "esports_valorant",
    "esports_dota2": "esports_dota2",
    "esports_fifa": "esports_fifa",
    "esports_r6": "esports_r6",
    "esports_cod": "esports_cod",
    "esports_halo": "esports_halo",
    "esports_rocketleague": "esports_rocketleague",
    "esports_apex": "esports_apex",
    "icehockey_nhl": "icehockey_nhl",
    "basketball_ncaa": "basketball_ncaa",
    "soccer_mls": "soccer_mls",
    "football_cfl": "football_cfl",
    "basketball_nbl": "basketball_nbl",
    "hockey_asia_league": "hockey_asia_league",
    "handball_ehf_european_league_women": "handball_ehf_european_league_women",
    "handball_hla_meisterliga": "handball_hla_meisterliga",
    "rugby_top_14": "rugby_top_14",
    "volleyball_super_cup_women": "volleyball_super_cup_women",
    "golf_pga": "golf_pga",
    "golf_lpga": "golf_lpga",
    "nascar": "nascar",
    "f1": "f1",
    "cricket": "cricket",
    "boxing": "boxing",
    "mma_powerslap": "mma_powerslap",
    "afl": "afl",
    "lacrosse": "lacrosse",
    "handball": "handball",
    "beachvolleyball": "beachvolleyball",
    "darts": "darts",
    "pwhl": "pwhl"
}

def _process_espn_scores_data(raw_data: Any, sport: str, player_stats: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Process ESPN scoreboard data into clean scores format - LIVE GAMES ONLY."""
    events = []
    
    try:
        if not raw_data or "events" not in raw_data:
            logger.warning("No events data found in ESPN response")
            return events
            
        evts = raw_data.get("events", [])
        
        for evt in evts:
            # Only include live/current games (status.type.state = "in")
            status = evt.get("status", {})
            status_obj = status.get("type", {})
            status_type = status_obj.get("state", "unknown")
            
            # Filter for live games only (status.type.state = "in")
            if status_type != "in":
                continue
            try:
                # Extract basic game info
                game_id = evt.get("id")
                game_date = evt.get("date")
                status = evt.get("status", {})
                
                # Extract teams and scores from competitions
                teams_data = []
                competitions = evt.get("competitions", [])
                if competitions:
                    for team in competitions[0].get("competitors", []):
                        team_info = team.get("team", {})
                        team_data = {
                            "id": team_info.get("id"),
                            "name": team_info.get("displayName"),
                            "abbreviation": team_info.get("abbreviation"),
                            "score": team.get("score"),
                            "is_home": team.get("homeAway") == "home",
                            "record": team_info.get("recordSummary", ""),
                            "logo": team_info.get("logo")
                        }
                        teams_data.append(team_data)
                
                # Determine home and away teams
                home_team = next((t for t in teams_data if t["is_home"]), None)
                away_team = next((t for t in teams_data if not t["is_home"]), None)
                
                if not home_team or not away_team:
                    continue
                
                # Build event data
                event_data = {
                    "id": game_id,
                    "sport_title": sport.replace("_", " ").title(),
                    "commence_time": game_date,
                    "home_team": home_team["name"],
                    "away_team": away_team["name"],
                    "home_score": home_team["score"],
                    "away_score": away_team["score"],
                    "completed": status_obj.get("completed", False),
                    "scores": {
                        "home": home_team["score"],
                        "away": away_team["score"]
                    },
                    "status": {
                        "type": status_obj.get("state", "unknown"),
                        "description": status_obj.get("description", ""),
                        "detail": status_obj.get("detail", ""),
                        "clock": status.get("clock", ""),
                        "period": status.get("period", 0)
                    },
                    "teams": {
                        "home": {
                            "id": home_team["id"],
                            "name": home_team["name"],
                            "abbreviation": home_team["abbreviation"],
                            "record": home_team["record"],
                            "logo": home_team["logo"]
                        },
                        "away": {
                            "id": away_team["id"],
                            "name": away_team["name"],
                            "abbreviation": away_team["abbreviation"],
                            "record": away_team["record"],
                            "logo": away_team["logo"]
                        }
                    }
                }
                
                # Add venue info if available
                venue = evt.get("vnue")
                if venue:
                    event_data["venue"] = {
                        "id": venue.get("id"),
                        "name": venue.get("fullName"),
                        "city": venue.get("address", {}).get("city"),
                        "state": venue.get("address", {}).get("state"),
                        "indoor": venue.get("indoor", False)
                    }
                
                # Add quarter-by-quarter scores if available
                line_scores = evt.get("lnescrs")
                if line_scores and "hme" in line_scores and "awy" in line_scores:
                    event_data["quarter_scores"] = {
                        "home": line_scores["hme"],
                        "away": line_scores["awy"],
                        "labels": line_scores.get("lbls", [])
                    }
                
                # Add player stats if available
                if player_stats and game_id in player_stats:
                    try:
                        boxscore = player_stats[game_id].get("boxscore", {})
                        if "players" in boxscore:
                            event_data["player_stats"] = _extract_player_stats(boxscore["players"])
                            logger.debug("Successfully added player stats", game_id=game_id)
                        # Note: No warning for missing player stats - this is normal for future games
                    except Exception as exc:
                        logger.warning("Failed to extract player stats", game_id=game_id, error=str(exc))
                else:
                    logger.debug("No player stats available", game_id=game_id, has_player_stats=bool(player_stats))
                
                events.append(event_data)
                
            except Exception as exc:
                logger.warning("Failed to process ESPN event", event_id=evt.get("id"), error=str(exc))
                continue
                
    except Exception as exc:
        logger.error("Failed to process ESPN scores data", error=str(exc))
    
    return events

def _extract_player_stats(players_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract player statistics from ESPN boxscore players data."""
    player_stats = {
        "home": [],
        "away": []
    }
    
    try:
        for team_data in players_data:
            team_stats = []
            team_id = team_data.get("team", {}).get("id", "unknown")
            
            # Get team's home/away status
            display_order = team_data.get("displayOrder", 0)
            team_side = "home" if display_order == 1 else "away"
            
            # Extract player statistics
            statistics = team_data.get("statistics", [])
            for stat_category in statistics:
                category_name = stat_category.get("name", "Unknown")
                labels = stat_category.get("labels", [])
                athletes = stat_category.get("athletes", [])
                
                for athlete_data in athletes:
                    athlete = athlete_data.get("athlete", {})
                    stats = athlete_data.get("stats", [])
                    
                    # Create player stat object
                    player_stat = {
                        "player_id": athlete.get("id"),
                        "name": athlete.get("displayName", ""),
                        "first_name": athlete.get("firstName", ""),
                        "last_name": athlete.get("lastName", ""),
                        "jersey": athlete.get("jersey", ""),
                        "headshot": athlete.get("headshot", ""),
                        "category": category_name,
                        "stats": {}
                    }
                    
                    # Map stats to labels
                    for i, stat_value in enumerate(stats):
                        if i < len(labels):
                            label = labels[i]
                            player_stat["stats"][label] = stat_value
                    
                    team_stats.append(player_stat)
            
            player_stats[team_side] = team_stats
            
    except Exception as exc:
        logger.warning("Failed to extract player stats", error=str(exc))
    
    return player_stats

def _process_espn_schedule_data(raw_data: Any, sport: str, player_stats: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Process ESPN scoreboard data into clean schedule format - ALL GAMES."""
    events = []
    
    try:
        if not raw_data or "events" not in raw_data:
            logger.warning("No events data found in ESPN response")
            return events
            
        evts = raw_data.get("events", [])
        
        for evt in evts:
            try:
                # Extract basic game info
                game_id = evt.get("id")
                game_date = evt.get("date")
                status = evt.get("status", {})
                status_obj = status.get("type", {})
                
                # Extract teams and scores from competitions
                teams_data = []
                competitions = evt.get("competitions", [])
                if competitions:
                    for team in competitions[0].get("competitors", []):
                        team_info = team.get("team", {})
                        team_data = {
                            "id": team_info.get("id"),
                            "name": team_info.get("displayName"),
                            "abbreviation": team_info.get("abbreviation"),
                            "score": team.get("score"),
                            "is_home": team.get("homeAway") == "home",
                            "record": team_info.get("recordSummary", ""),
                            "logo": team_info.get("logo")
                        }
                        teams_data.append(team_data)
                
                # Determine home and away teams
                home_team = next((t for t in teams_data if t["is_home"]), None)
                away_team = next((t for t in teams_data if not t["is_home"]), None)
                
                if not home_team or not away_team:
                    continue
                
                # Build event data
                event_data = {
                    "id": game_id,
                    "sport_title": sport.replace("_", " ").title(),
                    "commence_time": game_date,
                    "home_team": home_team["name"],
                    "away_team": away_team["name"],
                    "home_score": home_team["score"],
                    "away_score": away_team["score"],
                    "completed": status_obj.get("completed", False),
                    "scores": {
                        "home": home_team["score"],
                        "away": away_team["score"]
                    },
                    "status": {
                        "type": status_obj.get("state", "unknown"),
                        "description": status_obj.get("description", ""),
                        "detail": status_obj.get("detail", ""),
                        "clock": status.get("clock", ""),
                        "period": status.get("period", 0)
                    },
                    "teams": {
                        "home": {
                            "id": home_team["id"],
                            "name": home_team["name"],
                            "abbreviation": home_team["abbreviation"],
                            "record": home_team["record"],
                            "logo": home_team["logo"]
                        },
                        "away": {
                            "id": away_team["id"],
                            "name": away_team["name"],
                            "abbreviation": away_team["abbreviation"],
                            "record": away_team["record"],
                            "logo": away_team["logo"]
                        }
                    }
                }
                
                # Add venue info if available
                venue = evt.get("vnue")
                if venue:
                    event_data["venue"] = {
                        "id": venue.get("id"),
                        "name": venue.get("fullName"),
                        "city": venue.get("address", {}).get("city"),
                        "state": venue.get("address", {}).get("state"),
                        "indoor": venue.get("indoor", False)
                    }
                
                # Add quarter-by-quarter scores if available
                line_scores = evt.get("lnescrs")
                if line_scores and "hme" in line_scores and "awy" in line_scores:
                    event_data["quarter_scores"] = {
                        "home": line_scores["hme"],
                        "away": line_scores["awy"],
                        "labels": line_scores.get("lbls", [])
                    }
                
                # Add player stats if available
                if player_stats and game_id in player_stats:
                    try:
                        boxscore = player_stats[game_id].get("boxscore", {})
                        if "players" in boxscore:
                            event_data["player_stats"] = _extract_player_stats(boxscore["players"])
                            logger.debug("Successfully added player stats", game_id=game_id)
                        # Note: No warning for missing player stats - this is normal for future games
                    except Exception as exc:
                        logger.warning("Failed to extract player stats", game_id=game_id, error=str(exc))
                else:
                    logger.debug("No player stats available", game_id=game_id, has_player_stats=bool(player_stats))
                
                events.append(event_data)
                
            except Exception as exc:
                logger.warning("Failed to process ESPN event", event_id=evt.get("id"), error=str(exc))
                continue
                
    except Exception as exc:
        logger.error("Failed to process ESPN schedule data", error=str(exc))
    
    return events

def _process_espn_team_stats_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process ESPN team stats data into clean format."""
    processed_data = {
        "team": {},
        "players": [],
        "summary": {}
    }
    
    try:
        raw_response = raw_data.get("raw_response", {})
        
        # Extract team information
        team_info = raw_response.get("team", {})
        processed_data["team"] = {
            "id": team_info.get("id"),
            "name": team_info.get("displayName"),
            "abbreviation": team_info.get("abbreviation"),
            "logo": team_info.get("logo"),
            "color": team_info.get("color"),
            "alternate_color": team_info.get("alternateColor")
        }
        
        # Extract player statistics
        athletes_data = []
        
        # Check if athletes are in the direct 'athletes' key
        if "athletes" in raw_response:
            athletes_data = raw_response.get("athletes", [])
        # Check if athletes are in results[0]['leaders'] - this is the new ESPN format
        elif "results" in raw_response and raw_response["results"]:
            results = raw_response["results"]
            if isinstance(results, list) and len(results) > 0:
                first_result = results[0]
                leaders = first_result.get("leaders", [])
                
                # Process each leader which contains athlete and statistics
                for leader in leaders:
                    athlete = leader.get("athlete", {})
                    statistics = leader.get("statistics", [])
                    
                    if athlete:  # Only process if we have athlete data
                        athlete_with_stats = {
                            **athlete,
                            "statistics": statistics
                        }
                        athletes_data.append(athlete_with_stats)
        
        for athlete in athletes_data:
            player_data = {
                "id": athlete.get("id"),
                "name": athlete.get("displayName"),
                "position": athlete.get("position", {}).get("displayName") if athlete.get("position") else None,
                "jersey_number": athlete.get("jersey"),
                "headshot": athlete.get("headshot", {}).get("href") if athlete.get("headshot") else None,
                "age": athlete.get("age"),
                "height": athlete.get("height"),
                "weight": athlete.get("weight"),
                "stats": {}
            }
            
            # Extract statistics
            statistics = athlete.get("statistics", [])
            for stat_category in statistics:
                category_name = stat_category.get("displayName", "General")
                stats_in_category = stat_category.get("stats", [])
                
                for stat in stats_in_category:
                    stat_label = stat.get("displayName", "Unknown")
                    stat_value = stat.get("value")
                    stat_display = stat.get("displayValue")
                    
                    # Use display value if available, otherwise use raw value
                    final_value = stat_display if stat_display is not None else stat_value
                    player_data["stats"][stat_label] = final_value
            
            processed_data["players"].append(player_data)
        
        # Sort players by name for consistency
        processed_data["players"].sort(key=lambda x: x.get("name", ""))
        
        # Add summary information
        processed_data["summary"] = {
            "total_players": len(processed_data["players"]),
            "season": raw_data.get("season"),
            "season_type": raw_data.get("season_type"),
            "fetched_at": raw_data.get("fetched_at")
        }
        
    except Exception as exc:
        logger.error("Failed to process ESPN team stats data", error=str(exc))
        processed_data["error"] = str(exc)
    
    return processed_data

def _process_nba_player_stats_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process NBA player stats data into clean format."""
    processed_data = {
        "players": [],
        "headers": [],
        "summary": {}
    }
    
    try:
        raw_response = raw_data.get("raw_response", {})
        
        # Extract result sets
        result_sets = raw_response.get("resultSets", [])
        if not result_sets:
            logger.warning("No result sets found in NBA player stats response")
            return processed_data
        
        # Get the main player stats result set (usually the first one)
        main_result_set = result_sets[0]
        
        # Extract headers and row data
        headers = main_result_set.get("headers", [])
        rows = main_result_set.get("rowSet", [])
        
        processed_data["headers"] = headers
        
        # Process each player's stats
        for row in rows:
            if len(row) != len(headers):
                continue
                
            player_stats = {}
            for i, value in enumerate(row):
                if i < len(headers):
                    header = headers[i]
                    player_stats[header] = value
            
            processed_data["players"].append(player_stats)
        
        # Add summary information
        processed_data["summary"] = {
            "total_players": len(processed_data["players"]),
            "headers_count": len(headers),
            "data_type": raw_data.get("data_type", "unknown"),
            "season": raw_data.get("season", "unknown"),
            "season_type": raw_data.get("season_type", "unknown"),
            "measure_type": raw_data.get("measure_type", "unknown"),
            "per_mode": raw_data.get("per_mode", "unknown")
        }
        
        logger.info("Processed NBA player stats", 
                   players_count=len(processed_data["players"]),
                   headers_count=len(headers))
        
    except Exception as exc:
        logger.error("Failed to process NBA player stats data", error=str(exc))
        processed_data["error"] = str(exc)
    
    return processed_data

def _process_nba_team_stats_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process NBA team stats data into clean format."""
    processed_data = {
        "team": {},
        "players": [],
        "headers": [],
        "summary": {}
    }
    
    try:
        raw_response = raw_data.get("raw_response", {})
        
        # Extract result sets
        result_sets = raw_response.get("resultSets", [])
        if not result_sets:
            logger.warning("No result sets found in NBA team stats response")
            return processed_data
        
        # Process each result set
        for result_set in result_sets:
            result_set_name = result_set.get("name", "unknown")
            headers = result_set.get("headers", [])
            rows = result_set.get("rowSet", [])
            
            if result_set_name == "TeamInfo":
                # Team information
                if rows and len(rows[0]) == len(headers):
                    team_info = {}
                    for i, value in enumerate(rows[0]):
                        if i < len(headers):
                            header = headers[i]
                            team_info[header] = value
                    processed_data["team"] = team_info
                    
            elif result_set_name == "TeamDashboard":
                # Team dashboard stats
                if rows and len(rows[0]) == len(headers):
                    team_stats = {}
                    for i, value in enumerate(rows[0]):
                        if i < len(headers):
                            header = headers[i]
                            team_stats[header] = value
                    processed_data["team"]["dashboard"] = team_stats
                    
            elif result_set_name == "PlayersDashboard":
                # Player stats for the team
                processed_data["headers"] = headers
                
                for row in rows:
                    if len(row) != len(headers):
                        continue
                        
                    player_stats = {}
                    for i, value in enumerate(row):
                        if i < len(headers):
                            header = headers[i]
                            player_stats[header] = value
                    
                    processed_data["players"].append(player_stats)
        
        # Add summary information
        processed_data["summary"] = {
            "total_players": len(processed_data["players"]),
            "headers_count": len(processed_data["headers"]),
            "data_type": raw_data.get("data_type", "unknown"),
            "team_id": raw_data.get("team_id", "unknown"),
            "season": raw_data.get("season", "unknown"),
            "season_type": raw_data.get("season_type", "unknown"),
            "measure_type": raw_data.get("measure_type", "unknown"),
            "per_mode": raw_data.get("per_mode", "unknown")
        }
        
        logger.info("Processed NBA team stats", 
                   team_id=raw_data.get("team_id", "unknown"),
                   players_count=len(processed_data["players"]),
                   headers_count=len(processed_data["headers"]))
        
    except Exception as exc:
        logger.error("Failed to process NBA team stats data", error=str(exc))
        processed_data["error"] = str(exc)
    
    return processed_data

def _map_sport_key(sport_key: str) -> str:
    """Map Odds API sport key to internal streamer sport key."""
    return SPORT_KEY_MAPPING.get(sport_key, sport_key)

def _convert_american_to_decimal(american_odds: Union[int, str]) -> float:
    """Convert American odds to decimal odds."""
    try:
        odds = int(american_odds)
        if odds > 0:
            return round((odds / 100) + 1, 2)
        else:
            return round((100 / abs(odds)) + 1, 2)
    except (ValueError, TypeError):
        return 1.0

def _extract_api_key(authorization: Optional[str]) -> Optional[str]:
    """Extract API key from Authorization header."""
    if not authorization:
        return None
    
    # Handle "Bearer <token>" format
    if authorization.startswith("Bearer "):
        return authorization[7:]
    
    # Handle direct token format
    return authorization

def _validate_api_key(authorization: Optional[str]) -> bool:
    """Validate API key from Authorization header."""
    # TODO: Implement API key validation
    return True

def _process_fanduel_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process FanDuel API response data."""
    processed_events = []
    
    try:
        if not raw_data or "attachments" not in raw_data:
            logger.warning("No attachments found in FanDuel data")
            return processed_events
            
        attachments = raw_data["attachments"]
        markets_data = attachments.get("markets", {})
        events_data = attachments.get("events", {})
        
        if not markets_data:
            logger.warning("No markets found in FanDuel data")
            return processed_events
        
        # Group markets by event_id to create proper events
        events_by_id = {}
        
        # Process each market
        for market_id, market in markets_data.items():
            try:
                market_name = market.get("marketName", "")
                market_type = market.get("marketType", "")
                event_id = market.get("eventId")
                runners = market.get("runners", [])
                
                # Skip if no runners
                if not runners:
                    continue
                
                # Get event info
                event_info = events_data.get(str(event_id), {}) if event_id else {}
                event_name = event_info.get("name", "Unknown Event")
                
                # Map market type to our format
                mapped_market = _map_fanduel_market_type(market_name, market_type)
                
                # Skip if market not requested
                if markets_list and mapped_market not in markets_list:
                    continue
                
                # Initialize event if not exists
                if event_id not in events_by_id:
                    # Extract more detailed event information
                    start_time = event_info.get("openDate") or event_info.get("startTime")
                    if start_time:
                        # Convert to proper datetime format if it's a timestamp
                        if isinstance(start_time, str) and start_time.endswith('Z'):
                            start_time = start_time.replace('Z', '+00:00')
                        elif isinstance(start_time, (int, float)):
                            start_time = datetime.fromtimestamp(start_time / 1000, tz=timezone.utc).isoformat()
                    
                    events_by_id[event_id] = {
                        "id": event_id or f"fanduel_{market_id}",
                        "sport_key": sport,
                        "sport_title": _get_sport_title(sport),
                        "commence_time": start_time or datetime.now(timezone.utc).isoformat(),
                        "home_team": _extract_team_from_event_name(event_name, "home"),
                        "away_team": _extract_team_from_event_name(event_name, "away"),
                        "event_name": event_name,
                        "event_type": event_info.get("eventTypeId"),
                        "competition_id": event_info.get("competitionId"),
                        "video_available": event_info.get("videoAvailable", False),
                        "stats_available": event_info.get("statsAvailable", False),
                        "bookmakers": [{
                            "key": "fanduel",
                            "title": "FanDuel",
                            "last_update": datetime.now(timezone.utc).isoformat(),
                            "markets": []
                        }]
                    }
                
                # Process all runners for this market
                market_outcomes = []
                for runner in runners:
                    try:
                        runner_name = runner.get("runnerName", "")
                        runner_status = runner.get("runnerStatus", "")
                        handicap = runner.get("handicap", 0)
                        win_odds = runner.get("winRunnerOdds", {})
                        
                        # Skip inactive runners
                        if runner_status != "ACTIVE":
                            continue
                        
                        # Extract odds
                        american_odds = None
                        decimal_odds = None
                        
                        if win_odds:
                            american_display = win_odds.get("americanDisplayOdds", {})
                            true_odds = win_odds.get("trueOdds", {})
                            
                            if american_display:
                                american_odds = american_display.get("americanOddsInt")
                            elif true_odds:
                                decimal_data = true_odds.get("decimalOdds", {})
                                decimal_odds = decimal_data.get("decimalOdds")
                                if decimal_odds:
                                    american_odds = _convert_decimal_to_american(decimal_odds)
                        
                        # Skip if no odds
                        if american_odds is None:
                            continue
                        
                        # Format odds based on requested format
                        if odds_format == "decimal":
                            if decimal_odds is None:
                                decimal_odds = _convert_american_to_decimal(american_odds)
                            formatted_odds = decimal_odds
                        else:
                            formatted_odds = american_odds
                        
                        # Create outcome with additional fields
                        outcome = {
                            "name": runner_name,
                            "price": formatted_odds,
                            "point": handicap if handicap != 0 else None,
                            "description": runner_name,
                            "selection_id": runner.get("selectionId"),
                            "runner_status": runner_status,
                            "sort_priority": runner.get("sortPriority"),
                            "is_player_selection": runner.get("isPlayerSelection", False),
                            "logo": runner.get("logo"),
                            "secondary_logo": runner.get("secondaryLogo"),
                            "result": runner.get("result", {}),
                            "decimal_odds": decimal_odds,
                            "american_odds": american_odds,
                            "fractional_odds": win_odds.get("trueOdds", {}).get("fractionalOdds", {}) if win_odds else {}
                        }
                        
                        market_outcomes.append(outcome)
                        
                    except Exception as runner_exc:
                        logger.warning(f"Failed to process FanDuel runner: {runner_exc}")
                        continue
                
                # Add market to event if we have outcomes
                if market_outcomes:
                    market_data = {
                        "key": mapped_market,
                        "market_name": market_name,
                        "market_type": market_type,
                        "market_id": market_id,
                        "market_time": market.get("marketTime"),
                        "market_status": market.get("marketStatus", "OPEN"),
                        "number_of_runners": market.get("numberOfRunners", len(runners)),
                        "number_of_active_runners": market.get("numberOfActiveRunners", len([r for r in runners if r.get("runnerStatus") == "ACTIVE"])),
                        "number_of_winners": market.get("numberOfWinners", 1),
                        "sort_priority": market.get("sortPriority"),
                        "betting_type": market.get("bettingType", "ODDS"),
                        "bsp_market": market.get("bspMarket", False),
                        "sgm_market": market.get("sgmMarket", False),
                        "in_play": market.get("inPlay", False),
                        "last_update": datetime.now(timezone.utc).isoformat(),
                        "outcomes": market_outcomes
                    }
                    
                    # Add market to the first (and only) bookmaker
                    events_by_id[event_id]["bookmakers"][0]["markets"].append(market_data)
                        
            except Exception as market_exc:
                logger.warning(f"Failed to process FanDuel market {market_id}: {market_exc}")
                continue
        
        # Convert grouped events to list
        processed_events = list(events_by_id.values())
        
        logger.info(f"Processed {len(processed_events)} FanDuel events for sport {sport}")
        
    except Exception as exc:
        logger.error(f"Failed to process FanDuel data: {exc}")
    
    return processed_events

def _map_fanduel_market_type(market_name: str, market_type: str) -> str:
    """Map FanDuel market type to standard format."""
    market_name_lower = market_name.lower()
    
    # Player props
    if "touchdown" in market_name_lower:
        return "player_props"
    elif "reception" in market_name_lower:
        return "player_props"
    elif "sack" in market_name_lower:
        return "player_props"
    elif "yards" in market_name_lower:
        return "player_props"
    elif "points" in market_name_lower and "player" in market_name_lower:
        return "player_props"
    
    # Main markets
    elif "moneyline" in market_name_lower or market_type == "WINNER":
        return "h2h"
    elif "spread" in market_name_lower or "handicap" in market_name_lower or "run line" in market_name_lower:
        return "spreads"
    elif "total" in market_name_lower or "over" in market_name_lower or "under" in market_name_lower or "total runs" in market_name_lower:
        return "totals"
    
    # Futures markets - map to appropriate categories
    elif "regular season wins" in market_name_lower:
        return "h2h"  # Map futures to h2h for now
    elif "championship" in market_name_lower or "super bowl" in market_name_lower:
        return "h2h"
    elif "playoff" in market_name_lower:
        return "h2h"
    elif "mvp" in market_name_lower:
        return "player_props"
    
    # Default to h2h for unknown markets (futures)
    return "h2h"

def _extract_team_from_event_name(event_name: str, team_type: str) -> str:
    """Extract team name from event name."""
    if not event_name or event_name == "Unknown Event":
        return "TBD"
    
    # Handle different event name formats
    if " vs " in event_name:
        teams = event_name.split(" vs ")
        if team_type == "home" and len(teams) > 1:
            return teams[1].strip()
        elif team_type == "away" and len(teams) > 0:
            return teams[0].strip()
    elif " @ " in event_name:
        teams = event_name.split(" @ ")
        if team_type == "home" and len(teams) > 1:
            return teams[1].strip()
        elif team_type == "away" and len(teams) > 0:
            return teams[0].strip()
    
    return "TBD"

def _get_sport_title(sport_key: str) -> str:
    """Get sport title from sport key."""
    sport_titles = {
        "americanfootball_nfl": "NFL",
        "americanfootball_ncaaf": "College Football",
        "basketball_nba": "NBA",
        "basketball_wnba": "WNBA",
        "baseball_mlb": "MLB",
        "tennis": "Tennis",
        "mma": "UFC/MMA",
        "soccer_epl": "Premier League",
        "soccer_uefa_champs_league": "Champions League",
        "soccer_bundesliga": "Bundesliga",
        "soccer_serie_a": "Serie A",
        "soccer_la_liga": "La Liga",
        "soccer_mls": "MLS",
    }
    return sport_titles.get(sport_key, sport_key.title())

def _convert_decimal_to_american(decimal_odds: float) -> int:
    """Convert decimal odds to American odds."""
    try:
        if decimal_odds >= 2.0:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))
    except (ValueError, ZeroDivisionError):
        return 100

def _process_theesportslab_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process TheEsportsLab API response data."""
    processed_events = []
    
    try:
        if not raw_data or "endpoints" not in raw_data:
            logger.warning("No endpoints found in TheEsportsLab data")
            return processed_events
            
        endpoints = raw_data["endpoints"]
        
        # Process projections data (main PrizePicks insight)
        if "projections" in endpoints:
            projections_data = endpoints["projections"]
            if "projections" in projections_data:
                for proj in projections_data["projections"]:
                    try:
                        # Create event from projection
                        match = proj.get("match", {})
                        player = proj.get("player", {})
                        team = proj.get("team", {})
                        
                        # Create outcome
                        outcome = {
                            "name": f"{player.get('name', 'Unknown')} - {proj.get('stat_type', 'Unknown')}",
                            "price": proj.get("line_score", 0),
                            "point": proj.get("line_score"),
                            "description": f"{player.get('name', 'Unknown')} {proj.get('stat_type', 'stat')} over {proj.get('line_score', 0)}"
                        }
                        
                        # Create market
                        market_data = {
                            "key": "player_props",
                            "last_update": datetime.now(timezone.utc).isoformat(),
                            "outcomes": [outcome]
                        }
                        
                        # Create bookmaker
                        bookmaker = {
                            "key": "theesportslab",
                            "title": "TheEsportsLab",
                            "last_update": datetime.now(timezone.utc).isoformat(),
                            "markets": [market_data]
                        }
                        
                        # Create event
                        event_data = {
                            "id": f"theesportslab_{proj.get('id', 'unknown')}",
                            "sport_key": sport,
                            "sport_title": _get_sport_title(sport),
                            "commence_time": proj.get("start_time", datetime.now(timezone.utc).isoformat()),
                            "home_team": match.get("home_team", "TBD"),
                            "away_team": match.get("away_team", "TBD"),
                            "bookmakers": [bookmaker]
                        }
                        
                        processed_events.append(event_data)
                        
                    except Exception as proj_exc:
                        logger.warning(f"Failed to process TheEsportsLab projection: {proj_exc}")
                        continue
        
        # Process fixtures data
        if "fixtures" in endpoints:
            fixtures_data = endpoints["fixtures"]
            if "fixtures" in fixtures_data:
                for fixture in fixtures_data["fixtures"]:
                    try:
                        teams = fixture.get("teams", [])
                        home_team = "TBD"
                        away_team = "TBD"
                        
                        if len(teams) >= 2:
                            home_team = teams[1].get("name", "TBD")
                            away_team = teams[0].get("name", "TBD")
                        elif len(teams) == 1:
                            away_team = teams[0].get("name", "TBD")
                        
                        # Create basic moneyline market
                        outcome1 = {
                            "name": away_team,
                            "price": 100,
                            "point": None,
                            "description": away_team
                        }
                        
                        outcome2 = {
                            "name": home_team,
                            "price": -110,
                            "point": None,
                            "description": home_team
                        }
                        
                        market_data = {
                            "key": "h2h",
                            "last_update": datetime.now(timezone.utc).isoformat(),
                            "outcomes": [outcome1, outcome2]
                        }
                        
                        bookmaker = {
                            "key": "theesportslab",
                            "title": "TheEsportsLab",
                            "last_update": datetime.now(timezone.utc).isoformat(),
                            "markets": [market_data]
                        }
                        
                        event_data = {
                            "id": f"theesportslab_fixture_{fixture.get('id', 'unknown')}",
                            "sport_key": sport,
                            "sport_title": _get_sport_title(sport),
                            "commence_time": fixture.get("start_time", datetime.now(timezone.utc).isoformat()),
                            "home_team": home_team,
                            "away_team": away_team,
                            "bookmakers": [bookmaker]
                        }
                        
                        processed_events.append(event_data)
                        
                    except Exception as fixture_exc:
                        logger.warning(f"Failed to process TheEsportsLab fixture: {fixture_exc}")
                        continue
        
        logger.info(f"Processed {len(processed_events)} TheEsportsLab events for sport {sport}")
        
    except Exception as exc:
        logger.error(f"Failed to process TheEsportsLab data: {exc}")
    
    return processed_events


def _process_draftkings_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process DraftKings API response data."""
    processed_events = []
    
    try:
        if not raw_data or "data" not in raw_data:
            logger.warning("No data found in DraftKings response")
            return processed_events
            
        data = raw_data["data"]
        markets_data = data.get("markets", [])
        events_data = data.get("events", [])
        
        if not markets_data:
            logger.warning("No markets found in DraftKings data")
            return processed_events
        
        # Group markets by event
        events_by_id = {}
        
        # Process each market
        for market in markets_data:
            try:
                market_id = market.get("marketId", "")
                label = market.get("label", "")
                display_odds = market.get("displayOdds", {})
                true_odds = market.get("trueOdds")
                points = market.get("points")
                outcome_type = market.get("outcomeType", "")
                participants = market.get("participants", [])
                
                # Extract event info from market ID (format: "1_80918168")
                if "_" in market_id:
                    event_id = market_id.split("_")[1]
                else:
                    event_id = market_id
                
                # Map market type
                mapped_market = _map_draftkings_market_type(market_id, outcome_type)
                
                # Skip if market not requested
                if markets_list and mapped_market not in markets_list:
                    continue
                
                # Initialize event if not exists
                if event_id not in events_by_id:
                    # Find corresponding event data
                    event_info = next((e for e in events_data if str(e.get("eventId")) == event_id), {})
                    
                    events_by_id[event_id] = {
                        "id": event_id,
                        "sport_key": sport,
                        "sport_title": _get_sport_title(sport),
                        "commence_time": event_info.get("startTime", datetime.now(timezone.utc).isoformat()),
                        "home_team": _extract_team_from_participants(participants, "home"),
                        "away_team": _extract_team_from_participants(participants, "away"),
                        "event_name": event_info.get("name", "Unknown Event"),
                        "bookmakers": [{
                            "key": "draftkings",
                            "title": "DraftKings",
                            "last_update": datetime.now(timezone.utc).isoformat(),
                            "markets": []
                        }]
                    }
                
                # Create outcome
                outcome = {
                    "name": label,
                    "price": _format_draftkings_odds(display_odds, true_odds, odds_format),
                    "point": points if points is not None else None,
                    "description": label
                }
                
                # Add market to event if we have outcomes
                market_data = {
                    "key": mapped_market,
                    "market_name": _get_draftkings_market_name(market_id),
                    "market_id": market_id,
                    "outcome_type": outcome_type,
                    "last_update": datetime.now(timezone.utc).isoformat(),
                    "outcomes": [outcome]
                }
                
                # Add market to the first (and only) bookmaker
                events_by_id[event_id]["bookmakers"][0]["markets"].append(market_data)
                    
            except Exception as market_exc:
                logger.warning(f"Failed to process DraftKings market {market_id}: {market_exc}")
                continue
        
        # Convert grouped events to list
        processed_events = list(events_by_id.values())
        
        logger.info(f"Processed {len(processed_events)} DraftKings events for sport {sport}")
        
    except Exception as exc:
        logger.error(f"Failed to process DraftKings data: {exc}")
    
    return processed_events


def _map_draftkings_market_type(market_id: str, outcome_type: str) -> str:
    """Map DraftKings market type to standard format."""
    if market_id.startswith("1_"):
        return "h2h"
    elif market_id.startswith("2_"):
        return "spreads"
    elif market_id.startswith("3_"):
        return "totals"
    else:
        return "h2h"


def _get_draftkings_market_name(market_id: str) -> str:
    """Get market name from DraftKings market ID."""
    if market_id.startswith("1_"):
        return "Moneyline"
    elif market_id.startswith("2_"):
        return "Point Spread"
    elif market_id.startswith("3_"):
        return "Total Points"
    else:
        return "Unknown Market"


def _extract_team_from_participants(participants: List[Dict[str, Any]], team_type: str) -> str:
    """Extract team name from participants."""
    for participant in participants:
        venue_role = participant.get("venueRole", "")
        if team_type == "home" and venue_role == "Home":
            return participant.get("name", "Unknown Team")
        elif team_type == "away" and venue_role == "Away":
            return participant.get("name", "Unknown Team")
    return "Unknown Team"


def _format_draftkings_odds(display_odds: Dict[str, Any], true_odds: float, odds_format: str) -> Union[int, float]:
    """Format DraftKings odds based on requested format."""
    if odds_format == "decimal":
        return true_odds if true_odds else 1.0
    else:
        # Return American odds
        american_odds = display_odds.get("american", "0")
        try:
            return int(american_odds.replace("−", "-"))
        except (ValueError, AttributeError):
            return 0


def _process_bwin_data(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process Bwin data into standardized format."""
    try:
        if not raw_data or "fixtures" not in raw_data:
            logger.warning("No fixtures found in Bwin response")
            return []
        
        # Extract fixtures directly from the response
        fixtures = raw_data.get("fixtures", [])
        
        if not fixtures:
            logger.warning("No fixtures found in Bwin response")
            return []
        
        events = []
        
        for fixture in fixtures:
            try:
                # Extract basic event information
                event_id = fixture.get("id", "")
                event_name = fixture.get("name", {}).get("value", "Unknown Event")
                start_date = fixture.get("startDate", "")
                participants = fixture.get("participants", [])
                option_markets = fixture.get("optionMarkets", [])
                
                # Extract team information
                home_team = "Unknown"
                away_team = "Unknown"
                if len(participants) >= 2:
                    home_team = participants[0].get("name", {}).get("value", "Unknown")
                    away_team = participants[1].get("name", {}).get("value", "Unknown")
                
                # Process markets
                markets = []
                for market in option_markets:
                    market_name = market.get("name", {}).get("value", "")
                    market_type = _map_bwin_market_type(market_name)
                    
                    # Skip if market type not in requested markets
                    if market_type not in markets_list:
                        continue
                    
                    options = market.get("options", [])
                    outcomes = []
                    
                    for option in options:
                        option_name = option.get("name", {}).get("value", "")
                        price_data = option.get("price", {})
                        odds = price_data.get("odds", 0)
                        american_odds = price_data.get("americanOdds", 0)
                        
                        # Format odds based on requested format
                        if odds_format == "decimal":
                            formatted_odds = odds
                        else:
                            formatted_odds = american_odds
                        
                        # Extract point spread or total from option name
                        point = None
                        if "attr" in option:
                            point = option["attr"]
                        elif "totalsPrefix" in option:
                            # For totals, extract the number from the option name
                            import re
                            match = re.search(r'(\d+(?:,\d+)?)', option_name)
                            if match:
                                point = match.group(1).replace(',', '.')
                        
                        outcome = {
                            "name": option_name,
                            "price": formatted_odds
                        }
                        
                        if point:
                            outcome["point"] = point
                        
                        outcomes.append(outcome)
                    
                    if outcomes:
                        markets.append({
                            "key": market_type,
                            "outcomes": outcomes
                        })
                
                if markets:
                    event = {
                        "id": f"bwin_{event_id}",
                        "sport_key": sport,
                        "commence_time": format_to_12hour(start_date) if start_date else "",
                        "home_team": home_team,
                        "away_team": away_team,
                        "bookmakers": [{
                            "key": "bwin",
                            "title": "Bwin",
                            "markets": markets
                        }]
                    }
                    events.append(event)
                    
            except Exception as e:
                logger.warning(f"Failed to process Bwin fixture: {e}")
                continue
        
        logger.info(f"Processed {len(events)} Bwin events")
        return events
        
    except Exception as e:
        logger.error(f"Failed to process Bwin data: {e}")
        return []

def _process_bwin_fixture_details(raw_data: Any, sport: str, markets_list: List[str], odds_format: str) -> List[Dict[str, Any]]:
    """Process Bwin detailed fixture data including player props."""
    try:
        if not raw_data or "fixture" not in raw_data:
            logger.warning("No fixture data found in Bwin detailed response")
            return []
        
        fixture = raw_data.get("fixture", {})
        event_id = fixture.get("id", "")
        event_name = fixture.get("name", {}).get("value", "Unknown Event")
        start_date = fixture.get("startDate", "")
        participants = fixture.get("participants", [])
        option_markets = fixture.get("optionMarkets", [])
        
        # Extract team information
        home_team = "Unknown"
        away_team = "Unknown"
        if len(participants) >= 2:
            home_team = participants[0].get("name", {}).get("value", "Unknown")
            away_team = participants[1].get("name", {}).get("value", "Unknown")
        
        # Process all markets including player props
        markets = []
        for market in option_markets:
            market_name = market.get("name", {}).get("value", "")
            market_type = _map_bwin_market_type(market_name)
            
            # Skip if market type not in requested markets
            if market_type not in markets_list:
                continue
            
            options = market.get("options", [])
            outcomes = []
            
            for option in options:
                option_name = option.get("name", {}).get("value", "")
                price_data = option.get("price", {})
                odds = price_data.get("odds", 0)
                american_odds = price_data.get("americanOdds", 0)
                
                # Format odds based on requested format
                if odds_format == "decimal":
                    formatted_odds = odds
                else:
                    formatted_odds = american_odds
                
                # Extract point spread or total from option name
                point = None
                if "attr" in option:
                    point = option["attr"]
                elif "totalsPrefix" in option:
                    # For totals, extract the number from the option name
                    import re
                    match = re.search(r'(\d+(?:,\d+)?)', option_name)
                    if match:
                        point = match.group(1).replace(',', '.')
                
                outcome = {
                    "name": option_name,
                    "price": formatted_odds
                }
                
                if point:
                    outcome["point"] = point
                
                outcomes.append(outcome)
            
            if outcomes:
                markets.append({
                    "key": market_type,
                    "outcomes": outcomes
                })
        
        if markets:
            event = {
                "id": f"bwin_{event_id}",
                "sport_key": sport,
                "commence_time": format_to_12hour(start_date) if start_date else "",
                "home_team": home_team,
                "away_team": away_team,
                "bookmakers": [{
                    "key": "bwin",
                    "title": "Bwin",
                    "markets": markets
                }]
            }
            return [event]
        
        return []
        
    except Exception as e:
        logger.error(f"Failed to process Bwin fixture details: {e}")
        return []


def _map_bwin_market_type(market_name: str) -> str:
    """Map Bwin market names to standard market types."""
    market_mapping = {
        "Money Line": "h2h",
        "Spread": "spreads", 
        "Totals": "totals",
        "Over/Under": "totals",
        "Handicap": "spreads",
        "Total Points": "totals",
        "Match Winner": "h2h",
        "Draw": "h2h",
        # Player props
        "Passing touchdowns": "player_props",
        "Rushing attempts": "player_props",
        "Longest passing completion": "player_props",
        "Longest rush": "player_props",
        "Passing attempts": "player_props",
        "Interceptions thrown": "player_props",
        "Rushing yards": "player_props",
        "Passing yards": "player_props",
        "Total passing and rushing yards": "player_props",
        "Receiving yards": "player_props",
        "Receptions": "player_props",
        "Receiving touchdowns": "player_props",
        "Rushing touchdowns": "player_props",
        "Any time touchdown": "player_props",
        "First touchdown": "player_props",
        "Last touchdown": "player_props"
    }
    
    # Check for player props patterns
    if any(keyword in market_name.lower() for keyword in [
        "passing", "rushing", "receiving", "touchdown", "yards", "attempts", 
        "completion", "interception", "reception", "any time", "first", "last"
    ]):
        return "player_props"
    
    return market_mapping.get(market_name, "h2h")
