"""
Kashrock V6 Odds API - Core betting odds infrastructure

Provides unified access to aggregated odds from multiple sportsbooks:
- Moneyline odds (win/loss betting)
- Point spreads (handicap betting)  
- Totals/over-under (combined score betting)
- Real-time odds delivery
- Historical odds with timestamps
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Query, Path, Depends, BackgroundTasks
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
import structlog
import asyncio
from decimal import Decimal

from ..stats.engine import StatsEngine
from ..models import Game, Team
from ..historical.database import get_historical_db

logger = structlog.get_logger(__name__)

from v6.common.redis_cache import get_cache_manager
from v6.common.market_normalizer import normalize_market_key

# Sportsbook name mapping for Lunosoft IDs (from booklist.txt - source of truth)
SPORTSBOOK_MAPPING = {
    2: "Bodog",
    3: "BetCRIS", 
    5: "BookMaker",
    7: "Bovada",
    13: "William Hill",
    17: "bwin",
    20: "Sportsbet",
    28: "Caesars",
    83: "DraftKings",
    85: "BetRivers",
    86: "PointsBet",
    87: "BetMGM",
    88: "Unibet",
    89: "FanDuel",
    91: "888sport",
    93: "Bally Bet",
    94: "Hard Rock",
    97: "Sporttrade",
    98: "BET99",
    101: "Betano",
    106: "BetOpenly",
    107: "betPARX",
    110: "Betsafe",
    113: "Borgata",
    118: "ESPN BET",
    119: "Fanatics",
    122: "Ladbrokes",
    125: "partypoker",
    130: "Prophet X",
    135: "SugarHouse",
    139: "theScore",
    141: "TwinSpires",
    147: "Novig"
}

# Simple in-memory cache for historical data (24 hour TTL)
from collections import OrderedDict
_historical_cache = OrderedDict()
CACHE_TTL = timedelta(hours=24)
MAX_CACHE_SIZE = 1000

# Create router for odds endpoints
router = APIRouter(tags=["v6-odds"])

# ============================================================================
# ODDS DATA MODELS
# ============================================================================

class OddsResponse(BaseModel):
    """Standard odds response for a single game."""
    game_id: int
    sport: str
    league: str
    home_team: str
    away_team: str
    scheduled_at: datetime
    status: str
    
    # Moneyline odds
    home_moneyline: Optional[int] = None
    away_moneyline: Optional[int] = None
    
    # Point spreads
    home_spread: Optional[float] = None
    home_spread_odds: Optional[int] = None
    away_spread: Optional[float] = None  
    away_spread_odds: Optional[int] = None
    
    # Totals (over/under)
    total_line: Optional[float] = None
    over_odds: Optional[int] = None
    under_odds: Optional[int] = None
    
    # Metadata
    updated_at: datetime
    source: str = "kashrock"
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)


class OddsHistoryResponse(BaseModel):
    """Historical odds data for analysis and backtesting."""
    game_id: int
    sport: str
    timestamp: datetime
    odds_snapshot: OddsResponse
    movement_indicators: Dict[str, str] = Field(default_factory=dict)


class UnifiedOddsResponse(BaseModel):
    """Unified odds response following props API pattern."""
    source: str = "kashrock"
    team: str  # Team name without home/away distinction
    market: str  # Market type: "moneyline", "spread", "total"
    line: Optional[float] = None  # Spread value or total line, null for moneyline
    odds: int  # American odds
    direction: str  # "over" or "under" for totals, team name for moneyline/spreads
    book: str  # Actual sportsbook name
    event_time: datetime
    timestamp: str
    is_live: bool = False


class LiveOddsResponse(BaseModel):
    """Live odds response for in-progress games."""
    game_id: int
    sport: str
    league: str
    home_team: str
    away_team: str
    scheduled_at: datetime
    status: str  # "in_progress", "halftime", "final", etc.
    
    # Game state (live-specific)
    current_period: Optional[str] = None  # "Q1", "Q2", "Q3", "Q4", "OT"
    clock: Optional[str] = None  # "12:34", "2:15", etc.
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    
    # Moneyline odds (live)
    home_moneyline: Optional[int] = None
    away_moneyline: Optional[int] = None
    
    # Point spreads (live)
    home_spread: Optional[float] = None
    home_spread_odds: Optional[int] = None
    away_spread: Optional[float] = None  
    away_spread_odds: Optional[int] = None
    
    # Totals (live)
    total_line: Optional[float] = None
    over_odds: Optional[int] = None
    under_odds: Optional[int] = None
    
    # Metadata
    updated_at: datetime
    source: str = "kashrock"
    is_live: bool = True


# ============================================================================
# REAL ODDS AGGREGATION ENGINE
# ============================================================================

class OddsAggregator:
    """
    Production odds aggregation engine using real sportsbook data.
    
    Integrates with existing Kashrock streamers to provide real-time odds
    from multiple sportsbooks without mock data.
    """
    
    def __init__(self):
        self.active_streamers = {}
        self.cache_ttl = timedelta(seconds=30)  # Cache odds for 30 seconds
        self.live_cache_ttl = timedelta(seconds=10)  # Cache live odds for 10 seconds
        # Default set of sportsbooks we ingest from Lunosoft (spreads, totals, moneylines)
        # Default sportsbooks pulled from booklist.txt so we ingest every main book
        self.default_sportsbooks: List[int] = [
            2,    # Bodog
            3,    # BetCRIS
            5,    # BookMaker
            7,    # Bovada
            13,   # William Hill
            17,   # bwin
            20,   # Sportsbet
            28,   # Caesars
            83,   # DraftKings
            85,   # BetRivers
            86,   # PointsBet
            87,   # BetMGM
            88,   # Unibet
            89,   # FanDuel
            91,   # 888sport
            93,   # Bally Bet
            94,   # Hard Rock
            97,   # Sporttrade
            98,   # BET99
            101,  # Betano
            106,  # BetOpenly
            107,  # betPARX
            110,  # Betsafe
            113,  # Borgata
            118,  # ESPN BET
            119,  # Fanatics
            122,  # Ladbrokes
        ]
    
    async def initialize_streamers(self):
        """Initialize real odds streamers using lunosoft books."""
        try:
            # Import lunosoft book streamers
            from streamers.lunosoft_books import LUNOSOFT_BOOK_STREAMERS
            
            # Initialize all lunosoft book streamers with production configs
            self.active_streamers = {}
            for book_key, streamer_class in LUNOSOFT_BOOK_STREAMERS.items():
                try:
                    self.active_streamers[book_key] = streamer_class(
                        book_key, 
                        {"sport": "americanfootball_nfl"}
                    )
                except Exception as e:
                    logger.warning(f"Failed to initialize {book_key} streamer", error=str(e))
                    continue
            
            logger.info("Initialized lunosoft odds streamers", 
                       streamers=list(self.active_streamers.keys()),
                       total_count=len(self.active_streamers))
            
        except Exception as e:
            logger.error("Failed to initialize lunosoft streamers", error=str(e))
            # Fallback to empty streamers if initialization fails
            self.active_streamers = {}
    
    async def get_game_odds(self, game_id: int, sport: str) -> List[UnifiedOddsResponse]:
        """
        Get unified odds for a specific game using direct Lunosoft API.
        
        Args:
            game_id: Game identifier
            sport: Sport type (basketball_nba, americanfootball_nfl, etc.)
            
        Returns:
            List of unified odds entries without home/away distinction
        """
        logger.info("Getting unified odds", game_id=game_id, sport=sport)
        
        # Map sport to Lunosoft sport_id
        sport_mapping = {
            "basketball_nba": 4,
            "nba": 4,
            "americanfootball_nfl": 2,
            "nfl": 2,
            "baseball_mlb": 1,
            "mlb": 1,
            "icehockey_nhl": 6,
            "nhl": 6
        }
        
        sport_id = sport_mapping.get(sport)
        if not sport_id:
            raise HTTPException(status_code=400, detail=f"Unsupported sport: {sport}")
        
        try:
            # Create dedicated LunosoftClient for odds
            from streamers.lunosoft import LunosoftClient
            client = LunosoftClient()
            await client.connect()
            
            # Fetch current odds from Lunosoft for all default sportsbooks
            url = f"https://www.lunosoftware.com/sportsData/SportsDataService.svc/gamesOddsForDateWeek/{sport_id}"
            sportsbook_param = ",".join(str(sid) for sid in self.default_sportsbooks)
            params = {
                "sportsbookIDList": sportsbook_param
            }
            
            response = await client._get_json(f"{url}?{'&'.join(f'{k}={v}' for k, v in params.items())}")
            
            await client.disconnect()
            
            if not response:
                raise HTTPException(status_code=404, detail="No odds data available")
            
            # Find the specific game in the response
            target_game = None
            for game in response:
                if str(game.get("EventID", "")) == str(game_id):
                    target_game = game
                    break
            
            if not target_game:
                raise HTTPException(status_code=404, detail=f"Game {game_id} not found in odds data")
            
            # Convert to unified odds format
            unified_odds = self._convert_lunosoft_game_to_unified_odds(target_game, sport, datetime.utcnow())
            return unified_odds
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to fetch odds from Lunosoft", game_id=game_id, sport=sport, error=str(e))
            raise HTTPException(status_code=500, detail="Failed to fetch odds data")
    
    def _convert_to_unified_odds(self, odds_data: OddsResponse, sport: str, sportsbook_name: str) -> List[UnifiedOddsResponse]:
        """Convert traditional odds to unified props-like format."""
        unified_odds = []
        current_time = datetime.now(timezone.utc)
        
        # Moneyline odds - one entry per team with line: null
        if odds_data.home_moneyline and odds_data.away_moneyline:
            unified_odds.append(UnifiedOddsResponse(
                source="kashrock",
                team=odds_data.home_team,
                prop="moneyline",
                line=None,  # Moneyline has no line value
                odds=odds_data.home_moneyline,
                direction=odds_data.home_team,
                book=sportsbook_name,  # Use actual sportsbook name
                event_time=odds_data.scheduled_at,
                timestamp=current_time.isoformat(),
                is_live=False
            ))
            
            unified_odds.append(UnifiedOddsResponse(
                source="kashrock",
                team=odds_data.away_team,
                prop="moneyline",
                line=None,  # Moneyline has no line value
                odds=odds_data.away_moneyline,
                direction=odds_data.away_team,
                book=sportsbook_name,  # Use actual sportsbook name
                event_time=odds_data.scheduled_at,
                timestamp=current_time.isoformat(),
                is_live=False
            ))
        
        # Spread odds - one entry per team with opposite lines
        if odds_data.home_spread is not None and odds_data.away_spread is not None:
            unified_odds.append(UnifiedOddsResponse(
                source="kashrock",
                team=odds_data.home_team,
                prop="spread",
                line=odds_data.home_spread,
                odds=odds_data.home_spread_odds or -110,
                direction=odds_data.home_team,
                book=sportsbook_name,  # Use actual sportsbook name
                event_time=odds_data.scheduled_at,
                timestamp=current_time.isoformat(),
                is_live=False
            ))
            
            unified_odds.append(UnifiedOddsResponse(
                source="kashrock",
                team=odds_data.away_team,
                prop="spread",
                line=odds_data.away_spread,
                odds=odds_data.away_spread_odds or -110,
                direction=odds_data.away_team,
                book=sportsbook_name,  # Use actual sportsbook name
                event_time=odds_data.scheduled_at,
                timestamp=current_time.isoformat(),
                is_live=False
            ))
        
        # Total odds - over/under entries
        if odds_data.total_line is not None:
            unified_odds.append(UnifiedOddsResponse(
                source="kashrock",
                team=f"{odds_data.home_team} vs {odds_data.away_team}",
                prop="total",
                line=odds_data.total_line,
                odds=odds_data.over_odds or -110,
                direction="over",
                book=sportsbook_name,  # Use actual sportsbook name
                event_time=odds_data.scheduled_at,
                timestamp=current_time.isoformat(),
                is_live=False
            ))
            
            unified_odds.append(UnifiedOddsResponse(
                source="kashrock",
                team=f"{odds_data.home_team} vs {odds_data.away_team}",
                prop="total",
                line=odds_data.total_line,
                odds=odds_data.under_odds or -110,
                direction="under",
                book=sportsbook_name,  # Use actual sportsbook name
                event_time=odds_data.scheduled_at,
                timestamp=current_time.isoformat(),
                is_live=False
            ))
        
        return unified_odds
    
    async def get_historical_odds_by_date(
        self, 
        sport: str, 
        date: datetime,
        sportsbook_ids: List[int] = None
    ) -> List[UnifiedOddsResponse]:
        """
        Get historical odds for a specific date using Lunosoft API.
        
        Args:
            sport: Sport type (basketball_nba, americanfootball_nfl, etc.)
            date: Date to fetch odds for (datetime object)
            sportsbook_ids: List of sportsbook IDs to filter by (optional)
            
        Returns:
            List of unified historical odds entries
        """
        logger.info("Getting historical odds by date", sport=sport, date=date.isoformat())
        
        # Convert datetime to string for caching and API calls
        date_str = date.strftime("%Y-%m-%d")
        
        # Check cache first with sportsbook-aware key
        cached_data = self._get_from_cache(sport, date_str, sportsbook_ids)
        if cached_data is not None:
            logger.info("Returning cached historical odds", sport=sport, date=date_str, entries=len(cached_data))
            return cached_data
        
        # Skip streamer initialization for historical odds to avoid rate limiting
        # We use dedicated LunosoftClient for historical data, not streamers
        logger.info("Using dedicated LunosoftClient for historical odds, skipping streamer initialization")
        
        # Create dedicated LunosoftClient for historical odds
        from streamers.lunosoft import LunosoftClient
        lunosoft_client = LunosoftClient()
        await lunosoft_client.connect()
        
        # Get sport ID from LunosoftClient mapping
        sport_mapping = lunosoft_client.SPORT_MAP.get(sport, {})
        sport_id = sport_mapping.get("sport_id")
        
        if not sport_id:
            raise HTTPException(status_code=400, detail=f"Unsupported sport: {sport}")
        
        # Use configured sportsbook list by default
        if sportsbook_ids is None:
            sportsbook_ids = list(self.default_sportsbooks)
        
        sportsbook_str = ",".join(str(sid) for sid in sportsbook_ids)
        
        # Fetch historical odds from Lunosoft
        url = f"https://www.lunosoftware.com/sportsData/SportsDataService.svc/gamesOddsForDateWeek/{sport_id}"
        params = {
            "date": date_str,
            "sportsbookIDList": sportsbook_str
        }
        
        # Debug logging to verify parameters
        logger.info("Making Lunosoft API call", 
                   url=url,
                   params=params,
                   requested_sportsbooks=sportsbook_ids,
                   sportsbook_str=sportsbook_str)
        
        try:
            response = await lunosoft_client.session.get(url, params=params)
            response.raise_for_status()
            
            games_data = response.json()
            logger.info(f"Retrieved {len(games_data)} historical games", sport=sport, date=date_str)
            
            # Convert all games to unified odds format
            all_historical_odds = []
            for game in games_data:
                # Convert each game's odds to unified format
                game_odds = self._convert_lunosoft_game_to_unified_odds(game, sport, date)
                all_historical_odds.extend(game_odds)
            
            # Store in cache with sportsbook-aware key
            self._store_in_cache(sport, date_str, all_historical_odds, sportsbook_ids)
            
            # Filter by requested sportsbooks if specified
            if sportsbook_ids:
                sportsbook_names = {SPORTSBOOK_MAPPING.get(sid, f"Sportsbook_{sid}") for sid in sportsbook_ids}
                all_historical_odds = [odds for odds in all_historical_odds if odds.book in sportsbook_names]
            
            await lunosoft_client.disconnect()
            return all_historical_odds
            
        except Exception as e:
            await lunosoft_client.disconnect()
            logger.error("Failed to fetch historical odds from Lunosoft", sport=sport, date=date_str, error=str(e))
            raise HTTPException(status_code=500, detail="Failed to fetch historical odds")
    
    def _convert_lunosoft_game_to_unified_odds(
        self, 
        game: Dict[str, Any], 
        sport: str, 
        date: datetime
    ) -> List[UnifiedOddsResponse]:
        """Convert Lunosoft historical game data to unified odds format."""
        unified_odds = []
        current_time = datetime.now(timezone.utc)
        
        # Get game info
        home_team = game.get("HomeTeamFullName", "")
        away_team = game.get("AwayTeamFullName", "")
        game_id = game.get("GameID", 0)
        
        if not home_team or not away_team:
            return unified_odds
        
        # Parse game time
        start_time = game.get("StartTime", "")
        if start_time:
            try:
                # Lunosoft returns time in various formats, attempt to parse
                game_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except:
                game_datetime = date
        else:
            game_datetime = date
        
        # Process odds from each sportsbook
        odds_list = game.get("Odds", [])
        for odds_data in odds_list:
            sportsbook_id = odds_data.get("SportsbookID", 0)
            # Use sportsbook name mapping, fallback to generic format
            sportsbook_name = SPORTSBOOK_MAPPING.get(sportsbook_id, f"Sportsbook_{sportsbook_id}")
            
            # Moneyline odds
            home_ml = odds_data.get("HomeLine")
            away_ml = odds_data.get("AwayLine")
            
            if home_ml is not None and away_ml is not None:
                unified_odds.append(UnifiedOddsResponse(
                    source="kashrock",
                    team=home_team,
                    prop="moneyline",
                    line=None,
                    odds=int(home_ml),
                    direction=home_team,
                    book=sportsbook_name,
                    event_time=game_datetime,
                    timestamp=current_time.isoformat(),
                    is_live=False
                ))
                
                unified_odds.append(UnifiedOddsResponse(
                    source="kashrock",
                    team=away_team,
                    prop="moneyline",
                    line=None,
                    odds=int(away_ml),
                    direction=away_team,
                    book=sportsbook_name,
                    event_time=game_datetime,
                    timestamp=current_time.isoformat(),
                    is_live=False
                ))
            
            # Spread odds (if available)
            home_spread = odds_data.get("HomePoints")
            away_spread = odds_data.get("AwayPoints")
            
            if home_spread is not None and away_spread is not None:
                unified_odds.append(UnifiedOddsResponse(
                    source="kashrock",
                    team=home_team,
                    prop="spread",
                    line=float(home_spread),
                    odds=odds_data.get("HomePointsLine", -110),
                    direction=home_team,
                    book=sportsbook_name,
                    event_time=game_datetime,
                    timestamp=current_time.isoformat(),
                    is_live=False
                ))
                
                unified_odds.append(UnifiedOddsResponse(
                    source="kashrock",
                    team=away_team,
                    prop="spread",
                    line=float(away_spread),
                    odds=odds_data.get("AwayPointsLine", -110),
                    direction=away_team,
                    book=sportsbook_name,
                    event_time=game_datetime,
                    timestamp=current_time.isoformat(),
                    is_live=False
                ))
            
            # Total odds (over/under)
            total_line = odds_data.get("OverUnder")
            if total_line is not None:
                unified_odds.append(UnifiedOddsResponse(
                    source="kashrock",
                    team=f"{home_team} vs {away_team}",
                    prop="total",
                    line=float(total_line),
                    odds=odds_data.get("OverLine", -110),
                    direction="over",
                    book=sportsbook_name,
                    event_time=game_datetime,
                    timestamp=current_time.isoformat(),
                    is_live=False
                ))
                
                unified_odds.append(UnifiedOddsResponse(
                    source="kashrock",
                    team=f"{home_team} vs {away_team}",
                    prop="total",
                    line=float(total_line),
                    odds=odds_data.get("UnderLine", -110),
                    direction="under",
                    book=sportsbook_name,
                    event_time=game_datetime,
                    timestamp=current_time.isoformat(),
                    is_live=False
                ))
        
        return unified_odds
    
    def _get_cache_key(self, sport: str, date_str: str, sportsbook_ids: Optional[List[int]] = None) -> str:
        """Generate cache key for historical data including sportsbook IDs."""
        if sportsbook_ids:
            # Sort sportsbook IDs to ensure consistent cache keys
            sorted_ids = sorted(sportsbook_ids)
            sportsbook_key = "_".join(str(sid) for sid in sorted_ids)
            return f"{sport}:{date_str}:books_{sportsbook_key}"
        return f"{sport}:{date_str}:default"
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid."""
        return datetime.utcnow() - cache_entry["timestamp"] < CACHE_TTL
    
    def _evict_old_cache(self):
        """Remove oldest entries if cache is full."""
        while len(_historical_cache) >= MAX_CACHE_SIZE:
            _historical_cache.popitem(last=False)  # Remove oldest
    
    def _get_from_cache(self, sport: str, date_str: str, sportsbook_ids: Optional[List[int]] = None) -> Optional[List[UnifiedOddsResponse]]:
        """Get data from cache if valid with sportsbook awareness."""
        cache_key = self._get_cache_key(sport, date_str, sportsbook_ids)
        if cache_key in _historical_cache:
            cache_entry = _historical_cache[cache_key]
            if self._is_cache_valid(cache_entry):
                # Move to end to mark as recently used
                _historical_cache.move_to_end(cache_key)
                return cache_entry["data"]
            else:
                # Remove expired entry
                del _historical_cache[cache_key]
        return None
    
    def _store_in_cache(self, sport: str, date_str: str, data: List[UnifiedOddsResponse], sportsbook_ids: Optional[List[int]] = None):
        """Store data in cache with timestamp and sportsbook awareness."""
        self._evict_old_cache()
        cache_key = self._get_cache_key(sport, date_str, sportsbook_ids)
        _historical_cache[cache_key] = {
            "data": data,
            "timestamp": datetime.utcnow()
        }
        _historical_cache.move_to_end(cache_key)
    
    async def aggregate_live_odds(self, sport: str) -> List[LiveOddsResponse]:
        """
        Aggregate live odds from Redis cache (populated by background worker).
        Includes both Lunosoft and Sharp data.
        """
        logger.info("Aggregating live odds from cache", sport=sport)
        
        try:
            cache_manager = await get_cache_manager()
            
            # Get all event IDs for the sport
            event_ids = await cache_manager.get_sport_events(sport)
            
            if not event_ids:
                logger.info(f"No events found in cache for {sport}")
                return []
                
            live_odds_responses = []
            
            # Fetch specific events (limit to prevent overload, though Redis is fast)
            # In V6, 'live' usually means 'in progress' or 'upcoming'?
            # The method name implies 'live', but description says 'live odds'.
            # We'll fetch all active events.
            
            for event_id in event_ids:
                cached_event = await cache_manager.get_event(event_id)
                if not cached_event:
                    continue
                
                # Convert cached event to LiveOddsResponse
                response = self._convert_cached_event_to_live_resp(cached_event, sport)
                if response:
                    live_odds_responses.append(response)
                    
            return live_odds_responses

        except Exception as e:
            logger.error(f"Error aggregating live odds from cache for {sport}", error=str(e))
            return []

    def _convert_cached_event_to_live_resp(self, event: Dict[str, Any], sport: str) -> Optional[LiveOddsResponse]:
        """Convert cached V6 event dictionary to LiveOddsResponse model."""
        try:
            # Extract main markets
            markets = event.get('markets', {})
            h2h = markets.get('h2h', [])
            spreads = markets.get('spreads', [])
            totals = markets.get('totals', [])
            
            # Helper to find best odds (or consensus)
            # For now, just take the first available or a specific book if preferred
            # Simulating "Consensus" or "Best" by taking valid entries
            
            home_ml = None
            away_ml = None
            if h2h:
                # Find home/away
                for m in h2h:
                     # Attempt to match by team name or selection
                     # V6 market structure has 'selection' normalized?
                     # We'll look for simple mapping if available, or just take first pair if structured
                     # Actually h2h list often separates home vs away entries in flat list
                     if m.get('selection') == event.get('home_team'):
                         home_ml = m.get('odds')
                     elif m.get('selection') == event.get('away_team'):
                         away_ml = m.get('odds')
            
            home_spread_val = None
            home_spread_odds = None
            away_spread_val = None
            away_spread_odds = None
            if spreads:
                # Similar logic
                for m in spreads:
                     if m.get('selection') == event.get('home_team'):
                         home_spread_val = m.get('line')
                         home_spread_odds = m.get('odds')
                     elif m.get('selection') == event.get('away_team'):
                         away_spread_val = m.get('line')
                         away_spread_odds = m.get('odds')

            total_line_val = None
            over_odds_val = None
            under_odds_val = None
            if totals:
                for m in totals:
                    if m.get('selection') == 'over':
                         total_line_val = m.get('line')
                         over_odds_val = m.get('odds')
                    elif m.get('selection') == 'under':
                         # If lines differ, this might be imprecise, but grabbing first valid
                         if total_line_val is None: total_line_val = m.get('line')
                         under_odds_val = m.get('odds')

            # Parse scheduled_at
            sch = event.get('start_time') or event.get('commence_time')
            if isinstance(sch, str):
                try:
                    scheduled_at = datetime.fromisoformat(sch.replace('Z', '+00:00'))
                except:
                    scheduled_at = datetime.now(timezone.utc)
            else:
                scheduled_at = datetime.now(timezone.utc)

            # Map status
            status_raw = event.get('status', 'scheduled')
            
            return LiveOddsResponse(
                game_id=0, # mapping canonical ID to int is hard, use 0 or hash? The API expects int...
                # Ideally change model to str/int, but if client expects int, we might break it.
                # However, if we return hash(id) it might overflow. 
                # Let's try to extract numeric ID if present in canonical string (e.g. nba-123456 -> 123456)
                # But canonical ID format is sport-date-teams usually.
                # Using 0 for now as placeholder unless we find 'lunosoft_id' in metadata.
                sport=sport,
                league=sport.upper(),
                home_team=event.get('home_team', ''),
                away_team=event.get('away_team', ''),
                scheduled_at=scheduled_at,
                status=status_raw,
                home_moneyline=home_ml,
                away_moneyline=away_ml,
                home_spread=home_spread_val,
                home_spread_odds=home_spread_odds,
                away_spread=away_spread_val,
                away_spread_odds=away_spread_odds,
                total_line=total_line_val,
                over_odds=over_odds_val,
                under_odds=under_odds_val,
                updated_at=datetime.now(timezone.utc),
                source="kashrock_v6_cache",
                is_live=status_raw == 'in_progress'
            )
        except Exception as e:
            logger.warning(f"Failed to convert cached event: {e}")
            return None
    
    async def _get_live_games(self, sport: str) -> List[Dict[str, Any]]:
        """Get list of in-progress games for the sport."""
        try:
            # Import Lunosoft client to fetch live games
            from streamers.lunosoft import LunosoftClient
            
            client = LunosoftClient()
            await client.connect()
            
            # Use correct sport mapping from LunosoftClient
            sport_id = LunosoftClient.SPORT_MAP.get(sport, {}).get("sport_id", 4)  # Default to NBA
            
            # Fetch live games with inGameOdds=1
            live_games_url = f"https://www.lunosoftware.com/sportsData/SportsDataService.svc/gamesOddsForDateWeek/{sport_id}?lineTypes=1&inGameOdds=1&sportsbookIDList=1,2,5,13,83,89,94,3,6,85"
            
            response = await client.session.get(live_games_url, headers=LunosoftClient.DEFAULT_HEADERS)
            if response.status_code == 200:
                games_data = response.json()
                # Filter for in-progress games only (Lunosoft uses integer status codes)
                live_games = [game for game in games_data if game.get('Status') == 2]  # 2 = in_progress
                await client.disconnect()
                logger.info(f"Found {len(live_games)} live games for {sport}")
                return live_games
            else:
                await client.disconnect()
                return []
                    
        except Exception as e:
            logger.error(f"Error fetching live games for {sport}", error=str(e))
            return []
    
    async def _get_live_odds_for_game(self, game: Dict[str, Any], sport: str) -> Optional[LiveOddsResponse]:
        """Convert live game data to LiveOddsResponse."""
        try:
            # Extract odds from first sportsbook (or aggregate from all)
            odds_data = game.get('Odds', [])
            first_odds = odds_data[0] if odds_data else {}
            
            # Parse StartTime from Lunosoft format /Date(timestamp)/
            start_time_str = game.get('StartTimeStr', '')
            if start_time_str:
                try:
                    # Parse "12/07/2025 00:30" format
                    scheduled_at = datetime.strptime(start_time_str, "%m/%d/%Y %H:%M")
                    scheduled_at = scheduled_at.replace(tzinfo=timezone.utc)
                except Exception as e:
                    logger.warning(f"Failed to parse datetime: {start_time_str}, error: {e}")
                    scheduled_at = datetime.now(timezone.utc)
            else:
                scheduled_at = datetime.now(timezone.utc)
            
            # Debug logging to see what we're passing to the model
            debug_data = {
                'game_id': game.get('GameID', 0),
                'sport': sport,
                'league': sport.upper(),
                'home_team': game.get('HomeTeamFullName', 'Home Team'),
                'away_team': game.get('AwayTeamFullName', 'Away Team'),
                'scheduled_at': scheduled_at,
                'status': self._convert_status(game.get('Status', 2)),
                'current_period': game.get('Period'),
                'clock': f"{game.get('GameTime', 0)}:{game.get('GameTimeFrac', 0):02d}" if game.get('GameTime') else None,
                'home_score': game.get('HomeScore'),
                'away_score': game.get('AwayScore'),
                'home_moneyline': first_odds.get('HomeLine'),
                'away_moneyline': first_odds.get('AwayLine'),
                'home_spread': first_odds.get('HomePoints'),
                'home_spread_odds': first_odds.get('HomePointsLine'),
                'away_spread': -first_odds.get('HomePoints', 0) if first_odds.get('HomePoints') else None,
                'away_spread_odds': first_odds.get('AwayPointsLine'),
                'total_line': first_odds.get('OverUnder'),
                'over_odds': first_odds.get('OverLine'),
                'under_odds': first_odds.get('UnderLine'),
                'updated_at': datetime.now(timezone.utc),
                'source': "kashrock",
                'is_live': True
            }
            
            logger.info(f"Creating LiveOddsResponse with data: {debug_data}")
            
            try:
                live_odds = LiveOddsResponse(**debug_data)
                logger.info(f"Successfully created LiveOddsResponse for game {debug_data['game_id']}")
                return live_odds
            except Exception as validation_error:
                logger.error(f"Pydantic validation failed: {validation_error}")
                logger.error(f"Data that failed validation: {debug_data}")
                return None
            
        except Exception as e:
            logger.error(f"Error converting live odds data", error=str(e))
            return None
    
    def _convert_status(self, status_code: int) -> str:
        """Convert Lunosoft status code to readable status."""
        status_map = {
            1: "scheduled",
            2: "in_progress", 
            3: "final",
            4: "halftime",
            5: "postponed"
        }
        return status_map.get(status_code, "unknown")
    
    async def _get_odds_from_streamer(self, streamer, game_id: int, sport: str) -> Optional[OddsResponse]:
        """Get real odds data from a specific streamer."""
        try:
            # Connect to streamer if not already connected
            if not hasattr(streamer, 'connected') or not streamer.connected:
                await streamer.connect()
            
            # Get real odds data
            odds_data = await streamer.get_odds_for_game(game_id)
            
            if odds_data:
                return self._convert_to_odds_response(odds_data, game_id, sport, streamer.name)
            
        except Exception as e:
            logger.error(f"Error getting odds from {streamer.name}", error=str(e))
        
        return None
    
    def _convert_to_odds_response(self, raw_odds: Dict[str, Any], game_id: int, sport: str, source: str) -> OddsResponse:
        """Convert raw streamer odds to standardized OddsResponse."""
        # This would be customized based on each streamer's data format
        return OddsResponse(
            game_id=game_id,
            sport=sport,
            league=sport.upper(),
            home_team=raw_odds.get("home_team", "Home Team"),
            away_team=raw_odds.get("away_team", "Away Team"),
            scheduled_at=raw_odds.get("scheduled_at", datetime.utcnow()),
            status=raw_odds.get("status", "scheduled"),
            home_moneyline=raw_odds.get("home_moneyline"),
            away_moneyline=raw_odds.get("away_moneyline"),
            home_spread=raw_odds.get("home_spread"),
            home_spread_odds=raw_odds.get("home_spread_odds"),
            away_spread=raw_odds.get("away_spread"),
            away_spread_odds=raw_odds.get("away_spread_odds"),
            total_line=raw_odds.get("total_line"),
            over_odds=raw_odds.get("over_odds"),
            under_odds=raw_odds.get("under_odds"),
            updated_at=datetime.utcnow(),
            source=source,
        )
    
    

# Global odds aggregator instance
odds_aggregator = OddsAggregator()


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

async def get_odds_aggregator():
    """Get odds aggregator instance."""
    return odds_aggregator


async def get_stats_engine():
    """Get stats engine for game data."""
    engine = StatsEngine()
    try:
        yield engine
    finally:
        await engine.close()


# ============================================================================
# CORE ODDS ENDPOINTS
# ============================================================================

@router.get("/odds/live", response_model=List[LiveOddsResponse])
async def get_live_odds(
    sport: str = Query(default="basketball_nba", description="Sport type for live odds"),
    aggregator: OddsAggregator = Depends(get_odds_aggregator)
):
    """
    Get live odds for all in-progress games.
    
    Returns real-time odds and game state for all currently active games.
    Includes live moneyline, spreads, totals, and game status information.
    
    Features:
    - Real-time odds updates (10-second cache)
    - In-progress games only
    - Live game state (score, clock, period)
    - Multiple sportsbook aggregation
    - KashRock-branded unified format
    
    Supported sports:
    - basketball_nba (NBA games)
    - americanfootball_nfl (NFL games)
    - icehockey_nhl (NHL games)
    - baseball_mlb (MLB games)
    """
    try:
        logger.info("Fetching live odds", sport=sport)
        
        # Get live odds for all in-progress games
        live_odds = await aggregator.aggregate_live_odds(sport)
        
        if not live_odds:
            return []
        
        logger.info(f"Retrieved {len(live_odds)} live games", sport=sport)
        return live_odds
        
    except Exception as e:
        logger.error("Failed to fetch live odds", sport=sport, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch live odds")


@router.get("/odds/{game_id}", response_model=List[UnifiedOddsResponse])
async def get_game_odds(
    game_id: int = Path(..., description="Game ID"),
    sport: str = Query(default="nfl", description="Sport type"),
    aggregator: OddsAggregator = Depends(get_odds_aggregator)
):
    """
    Get unified odds for a specific game following props API pattern.
    
    Returns odds in unified format without home/away distinction:
    - Moneyline: One entry per team
    - Spreads: One entry per team with opposite lines
    - Totals: Over/under entries
    
    Unified format matches EV props structure.
    """
    try:
        logger.info("Fetching unified game odds", game_id=game_id, sport=sport)
        
        # Get unified odds for the game
        odds_data = await aggregator.get_game_odds(game_id, sport)
        
        logger.info(f"Retrieved {len(odds_data)} unified odds entries", 
                   game_id=game_id, sport=sport)
        return odds_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch unified game odds", game_id=game_id, sport=sport, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch unified game odds")


@router.get("/odds/history/{sport}/{date}", response_model=List[UnifiedOddsResponse])
async def get_historical_odds_by_date(
    sport: str = Path(..., description="Sport type"),
    date: str = Path(..., description="Date in YYYY-MM-DD format"),
    sportsbook_ids: Optional[str] = Query(default=None, description="Comma-separated sportsbook IDs (optional)"),
    aggregator: OddsAggregator = Depends(get_odds_aggregator)
):
    """
    Get historical odds for a specific date using Lunosoft API.
    
    Returns unified odds format for all games on the specified date:
    - Moneyline odds for each team
    - Spread odds (when available)
    - Total over/under odds (when available)
    
    Follows the same unified format as live odds for consistency.
    
    Supported sports:
    - americanfootball_nfl (NFL games)
    - basketball_nba (NBA games)
    - icehockey_nhl (NHL games)
    - baseball_mlb (MLB games)
    
    Args:
        sport: Sport type
        date: Date in YYYY-MM-DD format
        sportsbook_ids: Comma-separated sportsbook IDs (optional, uses default if not provided)
        
    Returns:
        List of unified historical odds entries
    """
    try:
        # Parse date string
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
        
        # Parse sportsbook IDs if provided
        sportsbook_list = None
        if sportsbook_ids:
            try:
                sportsbook_list = [int(sid.strip()) for sid in sportsbook_ids.split(",")]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid sportsbook IDs format. Use comma-separated integers")
        
        logger.info("Fetching historical odds by date", sport=sport, date=date, sportsbook_ids=sportsbook_ids)
        
        # Get historical odds for the date
        historical_odds = await aggregator.get_historical_odds_by_date(sport, parsed_date, sportsbook_list)
        
        logger.info(f"Retrieved {len(historical_odds)} historical odds entries", sport=sport, date=date)
        return historical_odds
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch historical odds", sport=sport, date=date, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch historical odds")


@router.get("/odds/live/{sport}", response_model=List[UnifiedOddsResponse])
async def get_live_odds_unified(
    sport: str = Path(..., description="Sport type (nfl, nba, mlb, nhl)"),
    aggregator: OddsAggregator = Depends(get_odds_aggregator)
):
    """
    Get live odds for all current/upcoming games in a sport.
    
    Returns live odds data from Lunosoft's live game feed in the
    unified odds format used by the rest of the API.
    """
    try:
        logger.info("Fetching live odds (unified)", sport=sport)

        # Get live odds snapshots from Lunosoft
        live_odds = await aggregator.aggregate_live_odds(sport)

        unified_odds: List[UnifiedOddsResponse] = []

        for game_odds in live_odds:
            # Moneyline odds
            if game_odds.home_moneyline is not None and game_odds.away_moneyline is not None:
                unified_odds.append(
                    UnifiedOddsResponse(
                        source="kashrock",
                        team=game_odds.home_team,
                        market="moneyline",
                        line=None,
                        odds=game_odds.home_moneyline,
                        direction=game_odds.home_team,
                        book="consensus",
                        event_time=game_odds.scheduled_at,
                        timestamp=datetime.utcnow().isoformat(),
                        is_live=game_odds.is_live,
                    )
                )
                unified_odds.append(
                    UnifiedOddsResponse(
                        source="kashrock",
                        team=game_odds.away_team,
                        market="moneyline",
                        line=None,
                        odds=game_odds.away_moneyline,
                        direction=game_odds.away_team,
                        book="consensus",
                        event_time=game_odds.scheduled_at,
                        timestamp=datetime.utcnow().isoformat(),
                        is_live=game_odds.is_live,
                    )
                )

            # Spread odds
            if game_odds.home_spread is not None and game_odds.away_spread is not None:
                unified_odds.append(
                    UnifiedOddsResponse(
                        source="kashrock",
                        team=game_odds.home_team,
                        market="spread",
                        line=game_odds.home_spread,
                        odds=game_odds.home_spread_odds or -110,
                        direction=game_odds.home_team,
                        book="consensus",
                        event_time=game_odds.scheduled_at,
                        timestamp=datetime.utcnow().isoformat(),
                        is_live=game_odds.is_live,
                    )
                )
                unified_odds.append(
                    UnifiedOddsResponse(
                        source="kashrock",
                        team=game_odds.away_team,
                        market="spread",
                        line=game_odds.away_spread,
                        odds=game_odds.away_spread_odds or -110,
                        direction=game_odds.away_team,
                        book="consensus",
                        event_time=game_odds.scheduled_at,
                        timestamp=datetime.utcnow().isoformat(),
                        is_live=game_odds.is_live,
                    )
                )

            # Total odds
            if game_odds.total_line is not None:
                matchup = f"{game_odds.home_team} vs {game_odds.away_team}"
                unified_odds.append(
                    UnifiedOddsResponse(
                        source="kashrock",
                        team=matchup,
                        market="total",
                        line=game_odds.total_line,
                        odds=game_odds.over_odds or -110,
                        direction="over",
                        book="consensus",
                        event_time=game_odds.scheduled_at,
                        timestamp=datetime.utcnow().isoformat(),
                        is_live=game_odds.is_live,
                    )
                )
                unified_odds.append(
                    UnifiedOddsResponse(
                        source="kashrock",
                        team=matchup,
                        market="total",
                        line=game_odds.total_line,
                        odds=game_odds.under_odds or -110,
                        direction="under",
                        book="consensus",
                        event_time=game_odds.scheduled_at,
                        timestamp=datetime.utcnow().isoformat(),
                        is_live=game_odds.is_live,
                    )
                )

        logger.info("Unified live odds built", sport=sport, entries=len(unified_odds))
        return unified_odds

    except Exception as e:
        logger.error("Failed to fetch live odds", sport=sport, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch live odds")


@router.get("/odds/history/{game_id}", response_model=List[OddsHistoryResponse])
async def get_odds_history(
    game_id: int = Path(..., description="Game ID to fetch history for"),
    sport: str = Query(..., description="Sport type (nfl, nba, mlb, nhl)"),
    hours_back: int = Query(24, ge=1, le=168, description="Hours of history to fetch"),
    aggregator: OddsAggregator = Depends(get_odds_aggregator)
):
    """
    Get historical odds movement for a specific game (DB-backed).
    
    Essential for backtesting, model training, and odds analysis.
    Each snapshot includes timestamp and movement indicators.
    """
    try:
        logger.info("Fetching odds history", game_id=game_id, sport=sport, hours_back=hours_back)
        
        db = await get_historical_db()
        base_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Fetch from historical DB
        rows = await db.fetch_odds(
            sport=sport,
            event_id=str(game_id),
            date_from=base_time,
            limit=1000
        )
        
        if not rows:
            return []
            
        # Group by capture time
        history_map = {}
        for row in rows:
            ts_str = row["captured_at"]
            # Ensure we have a datetime object or string key
            if isinstance(ts_str, datetime):
                ts = ts_str
            else:
                try:
                    ts = datetime.fromisoformat(str(ts_str))
                except:
                    continue
                    
            ts_key = ts.isoformat()
            
            if ts_key not in history_map:
                history_map[ts_key] = {
                    "timestamp": ts,
                    "game_id": game_id,
                    "sport": sport,
                    "league": "",
                    "home_team": row["home_team"],
                    "away_team": row["away_team"],
                    "scheduled_at": row["commence_time"] if isinstance(row["commence_time"], datetime) else datetime.utcnow(), # Fallback
                    "status": "scheduled",
                    "updated_at": ts,
                    "source": "kashrock",
                    "home_moneyline": None,
                    "away_moneyline": None,
                    "home_spread": None,
                    "home_spread_odds": None,
                    "away_spread": None,
                    "away_spread_odds": None,
                    "total_line": None,
                    "over_odds": None,
                    "under_odds": None
                }
            
            # Merge market data
            data = row["market_data"]
            if not isinstance(data, dict):
                 continue
                 
            mtype = row["market_type"] or "unknown"
            entry = history_map[ts_key]
            
            if mtype == "moneyline":
                entry["home_moneyline"] = data.get("home_moneyline") or data.get("h_odds")
                entry["away_moneyline"] = data.get("away_moneyline") or data.get("a_odds")
            elif mtype == "spread":
                entry["home_spread"] = data.get("home_spread") or data.get("home_point")
                entry["home_spread_odds"] = data.get("home_spread_odds") or data.get("home_price")
                entry["away_spread"] = data.get("away_spread") or data.get("away_point")
                entry["away_spread_odds"] = data.get("away_spread_odds") or data.get("away_price")
            elif mtype == "total":
                entry["total_line"] = data.get("total_line") or data.get("total")
                entry["over_odds"] = data.get("over_odds") or data.get("over_price")
                entry["under_odds"] = data.get("under_odds") or data.get("under_price")
        
        # Convert to response format
        history = []
        sorted_timestamps = sorted(history_map.keys())
        
        for i, ts_key in enumerate(sorted_timestamps):
            data = history_map[ts_key]
            odds_snapshot = OddsResponse(**data)
            
            # Calculate movement (simple)
            movement = {}
            if i > 0:
                prev_data = history_map[sorted_timestamps[i-1]]
                
                # Moneyline movement
                if data["home_moneyline"] and prev_data["home_moneyline"]:
                    if data["home_moneyline"] > prev_data["home_moneyline"]:
                        movement["home_moneyline"] = "↑"
                    elif data["home_moneyline"] < prev_data["home_moneyline"]:
                         movement["home_moneyline"] = "↓"
                
                # Spread movement
                if data["home_spread"] and prev_data["home_spread"]:
                     if data["home_spread"] > prev_data["home_spread"]:
                         movement["home_spread"] = "↑"
                     elif data["home_spread"] < prev_data["home_spread"]:
                         movement["home_spread"] = "↓"
                         
                # Total movement
                if data["total_line"] and prev_data["total_line"]:
                     if data["total_line"] > prev_data["total_line"]:
                         movement["total_line"] = "↑"
                     elif data["total_line"] < prev_data["total_line"]:
                         movement["total_line"] = "↓"
            
            history.append(OddsHistoryResponse(
                game_id=game_id,
                sport=sport,
                timestamp=data["timestamp"],
                odds_snapshot=odds_snapshot,
                movement_indicators=movement
            ))
            
        return history
        
    except Exception as e:
        logger.error("Failed to fetch odds history", game_id=game_id, sport=sport, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch odds history")


@router.get("/odds/export/{sport}")
async def export_odds(
    sport: str = Path(..., description="Sport type"),
    date_from: datetime = Query(..., description="Start date for export"),
    date_to: datetime = Query(..., description="End date for export"),
    format: str = Query(default="json", description="Export format (json, csv)"),
):
    """
    Export odds data with timestamps for analysis.
    
    Redirects to the unified streaming export endpoint [/v6/export].
    """
    # Redirect to the actual export service
    # We format dates as ISO strings for the query params
    url = f"/v6/export?sport={sport}&datasets=historical_odds&format={format}&date_from={date_from.isoformat()}&date_to={date_to.isoformat()}"
    return RedirectResponse(url=url)
        

