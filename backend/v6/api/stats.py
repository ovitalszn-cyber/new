"""
V6 Stats Engine API endpoints - unified interface for sports data.

Provides clean, systematic access to:
- Games, schedules, and live scores
- Teams, standings, and statistics  
- Players, rosters, and performance data
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from pydantic import BaseModel, Field
import structlog

from ..stats.engine import StatsEngine
from ..models import Game, Team, Player, GameSchedule, LeagueStandings

logger = structlog.get_logger(__name__)

# Create router
router = APIRouter(tags=["v6-stats"])

# Dependency to get stats engine instance with proper lifecycle management
async def get_stats_engine() -> StatsEngine:
    """Get a StatsEngine instance for dependency injection."""
    return StatsEngine()


# ============================================================================
# RESPONSE MODELS - Clean API responses
# ============================================================================

class GameResponse(BaseModel):
    """Standard game response."""
    id: int
    sport: str
    league: str
    scheduled_at: datetime
    status: str
    home_team_id: int
    away_team_id: int
    home_team: Optional[Dict[str, Any]] = None
    away_team: Optional[Dict[str, Any]] = None
    venue: Optional[str] = None
    score: Optional[Dict[str, Any]] = None
    spread: Optional[float] = None
    over_under: Optional[float] = None


class TeamResponse(BaseModel):
    """Standard team response."""
    id: int
    name: str
    abbreviation: str
    full_name: Optional[str] = None
    sport: str
    league: str
    location: Optional[Dict[str, Any]] = None
    record: Optional[Dict[str, Any]] = None
    standing: Optional[Dict[str, Any]] = None


class PlayerResponse(BaseModel):
    """Standard player response."""
    id: int
    first_name: str
    last_name: str
    full_name: Optional[str] = None
    sport: str
    league: str
    team_id: Optional[int] = None
    team: Optional[Dict[str, Any]] = None
    position: Optional[str] = None
    jersey_number: Optional[int] = None
    status: str


class ScheduleResponse(BaseModel):
    """Schedule response with games and metadata."""
    games: List[GameResponse]
    total_count: int
    sport: str
    updated_at: datetime


class StandingsResponse(BaseModel):
    """Standings response."""
    league: str
    sport: str
    standings: List[Dict[str, Any]]
    updated_at: datetime


class PlayerStatsResponse(BaseModel):
    """Comprehensive player statistics response."""
    id: int
    first_name: str
    last_name: str
    full_name: Optional[str] = None
    sport: str
    league: str
    team_id: Optional[int] = None
    team: Optional[Dict[str, Any]] = None
    position: Optional[str] = None
    jersey_number: Optional[int] = None
    status: str
    stats_summary: Optional[str] = None
    all_stats_categories: Dict[str, Dict[str, Any]]
    season_stats: Dict[str, Any]


class TeamStatsResponse(BaseModel):
    """Team statistics summary response."""
    team_id: int
    team_name: str
    sport: str
    league: str
    total_players: int
    players: List[PlayerStatsResponse]
    updated_at: datetime
    date_filter: Optional[Dict[str, Any]] = None


# ============================================================================
# GAMES HELPERS
# ============================================================================

def _to_game_response(game: Game, sport_hint: str, league_hint: str) -> GameResponse:
    """Map internal Game model to public GameResponse schema."""
    # Derive sport string
    raw_sport = getattr(game, "sport", None)
    if isinstance(raw_sport, str):
        sport_str = raw_sport
    else:
        sport_str = sport_hint

    # Derive league string from nested dict if present
    league_value = getattr(game, "league", None)
    if isinstance(league_value, dict):
        league_str = (
            league_value.get("alias")
            or league_value.get("slug")
            or league_value.get("name")
            or league_hint
        )
    else:
        league_str = league_hint

    # Parse scheduled_at from game_date (RFC 2822) if possible
    scheduled_raw = getattr(game, "game_date", None)
    scheduled_at: datetime
    if isinstance(scheduled_raw, str):
        try:
            scheduled_at = datetime.strptime(scheduled_raw, "%a, %d %b %Y %H:%M:%S %z")
        except Exception:
            try:
                scheduled_at = datetime.fromisoformat(scheduled_raw)
            except Exception:
                scheduled_at = datetime.utcnow()
    else:
        scheduled_at = datetime.utcnow()

    home_team = getattr(game, "home_team", None) or {}
    away_team = getattr(game, "away_team", None) or {}

    venue = getattr(game, "location", None) or getattr(game, "stadium", None)
    score = getattr(game, "score", None)

    return GameResponse(
        id=game.id,
        sport=str(sport_str),
        league=str(league_str),
        scheduled_at=scheduled_at,
        status=getattr(game, "status", "unknown"),
        home_team_id=home_team.get("id"),
        away_team_id=away_team.get("id"),
        home_team=home_team,
        away_team=away_team,
        venue=venue,
        score=score,
        spread=None,
        over_under=None,
    )


@router.get("/games", response_model=List[GameResponse])
async def get_games(
    sport: str = Query(default="nfl", description="Sport name (nfl, nba, mlb, nhl)"),
    league: str = Query(default="nfl", description="League name"),
    event_ids: Optional[str] = Query(default=None, description="Comma-separated game IDs"),
    betmode: bool = Query(default=True, description="Include betting data"),
    engine: StatsEngine = Depends(get_stats_engine),
):
    """Get games with full information including scores and betting data."""
    try:
        ids = None
        if event_ids:
            try:
                ids = [int(id.strip()) for id in event_ids.split(",")]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid event_ids format")

        games = await engine.get_games(sport, league, ids, betmode)
        response_games = [_to_game_response(game, sport, league) for game in games]
        return response_games

    except Exception as e:
        logger.error(
            "Failed to get games",
            sport=sport,
            league=league,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to fetch games")


@router.get("/games/today", response_model=List[GameResponse])
async def get_today_games(
    sport: str = Query(default="nfl", description="Sport name"),
    engine: StatsEngine = Depends(get_stats_engine),
):
    """Get all games scheduled for today."""
    try:
        games = await engine.get_today_games(sport)
        response_games = [_to_game_response(game, sport, sport) for game in games]
        return response_games

    except Exception as e:
        logger.error(
            "Failed to get today's games",
            sport=sport,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to fetch today's games")


@router.get("/games/live", response_model=List[GameResponse])
async def get_live_games(
    sport: str = Query(default="nfl", description="Sport name"),
    engine: StatsEngine = Depends(get_stats_engine),
):
    """Get all games currently in progress."""
    try:
        games = await engine.get_live_games(sport)
        response_games = [_to_game_response(game, sport, sport) for game in games]
        return response_games

    except Exception as e:
        logger.error(
            "Failed to get live games",
            sport=sport,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to fetch live games")


@router.get("/games/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: int = Path(..., description="Game ID"),
    sport: str = Query(default="nfl", description="Sport name"),
    engine: StatsEngine = Depends(get_stats_engine)
):
    """Get a specific game by ID."""
    try:
        game = await engine.get_game_by_id(game_id, sport)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")

        return GameResponse(**game.dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get game",
            game_id=game_id,
            sport=sport,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Failed to fetch game")


@router.get("/schedule", response_model=ScheduleResponse)
async def get_schedule(
    sport: str = Query(default="nfl", description="Sport name"),
    utc_offset: int = Query(default=-18000, description="UTC offset in seconds"),
    engine: StatsEngine = Depends(get_stats_engine),
):
    """Get complete schedule for a sport."""
    try:
        schedule = await engine.get_schedule(sport, utc_offset)

        response_games = [_to_game_response(game, sport, sport) for game in schedule.games]

        return ScheduleResponse(
            games=response_games,
            total_count=schedule.total_count,
            sport=sport,
            updated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(
            "Failed to get schedule",
            sport=sport,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to fetch schedule")


# ============================================================================
# TEAMS ENDPOINTS
# ============================================================================

@router.get("/teams", response_model=List[TeamResponse])
async def get_teams(
    sport: str = Query(default="nfl", description="Sport name"),
    league: str = Query(default="nfl", description="League name"),
    engine: StatsEngine = Depends(get_stats_engine)
):
    """Get all teams for a sport/league with current records."""
    try:
        teams = await engine.get_teams(sport, league)
        
        # Convert to response models
        response_teams = []
        for team in teams:
            team_dict = team.dict()
            response_teams.append(TeamResponse(**team_dict))
        
        return response_teams
        
    except Exception as e:
        logger.error(
            "Failed to get teams",
            sport=sport,
            league=league,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Failed to fetch teams")


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int = Path(..., description="Team ID"),
    sport: str = Query(default="nfl", description="Sport name"),
    engine: StatsEngine = Depends(get_stats_engine)
):
    """Get a specific team by ID."""
    try:
        team = await engine.get_team_by_id(team_id, sport)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return TeamResponse(**team.dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get team",
            team_id=team_id,
            sport=sport,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Failed to fetch team")


@router.get("/standings", response_model=StandingsResponse)
async def get_standings(
    sport: str = Query(default="nfl", description="Sport name"),
    league: str = Query(default="nfl", description="League name"),
    engine: StatsEngine = Depends(get_stats_engine)
):
    """Get complete league standings."""
    try:
        standings = await engine.get_standings(sport, league)
        
        return StandingsResponse(
            league=standings.league,
            sport=sport,
            standings=[standing.dict() for standing in standings.overall],
            updated_at=standings.updated_at
        )
        
    except Exception as e:
        logger.error(
            "Failed to get standings",
            sport=sport,
            league=league,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Failed to fetch standings")


# ============================================================================
# PLAYERS ENDPOINTS
# ============================================================================

@router.get("/players", response_model=List[PlayerResponse])
async def get_players(
    team_id: int = Query(..., description="Team ID"),
    sideload_team: bool = Query(default=True, description="Include team data"),
    engine: StatsEngine = Depends(get_stats_engine)
):
    """Get all players for a team with current statistics."""
    try:
        players = await engine.get_players(team_id, sideload_team)
        
        # Convert to response models
        response_players = []
        for player in players:
            player_dict = player.dict()
            response_players.append(PlayerResponse(**player_dict))
        
        return response_players
        
    except Exception as e:
        logger.error(
            "Failed to get players",
            team_id=team_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Failed to fetch players")


@router.get("/roster", response_model=List[PlayerResponse])
async def get_roster(
    team_id: int = Query(..., description="Team ID"),
    sideload_team: bool = Query(default=True, description="Include team data"),
    engine: StatsEngine = Depends(get_stats_engine)
):
    """Get team roster (alias for players endpoint)."""
    return await get_players(team_id, sideload_team, engine)


@router.get("/players/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: int = Path(..., description="Player ID"),
    team_id: Optional[int] = Query(None, description="Team ID (recommended for performance)"),
    engine: StatsEngine = Depends(get_stats_engine)
):
    """Get a specific player by ID."""
    try:
        player = await engine.get_player_by_id(player_id, team_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        return PlayerResponse(**player.dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get player",
            player_id=player_id,
            team_id=team_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Failed to fetch player")


# ============================================================================
# BOX SCORE ENDPOINTS
# ============================================================================

def _normalize_box_score(box_score: Dict[str, Any], sport: str) -> Dict[str, Any]:
    """
    Normalize box score data structure across sports for consistent API responses.
    
    Args:
        box_score: Raw box score data from the API
        sport: Sport type (nfl, nba, etc.)
    
    Returns:
        Normalized box score with consistent structure
    """
    if not box_score:
        return box_score
    
    normalized = box_score.copy()
    
    # Normalize attendance data - NBA has it nested, NFL has it at root
    if sport.lower() == 'nba':
        # For NBA, move attendance from nested box_score to root level
        nested_box_score = box_score.get('box_score', {})
        if 'attendance' in nested_box_score:
            normalized['attendance'] = nested_box_score['attendance']
    
    # For NBA, replace duplicate game_description with useful team statistics
    if sport.lower() == 'nba':
        team_records = box_score.get('box_score', {}).get('team_records', {})
        if team_records:
            team_stats = {}
            
            # Extract key team statistics for both teams
            for team_key in ['away', 'home']:
                if team_key in team_records:
                    stats = team_records[team_key]
                    team_stats[team_key] = {
                        'field_goals_percentage': stats.get('field_goals_percentage', '0.000'),
                        'rebounds_total': stats.get('rebounds_total', 0),
                        'assists': stats.get('assists', 0),
                        'points_in_paint': stats.get('points_in_paint', 0),
                        'fast_break_points': stats.get('fast_break_points', 0),
                        'turnovers': stats.get('turnovers', 0)
                    }
            
            # Replace game_description with team statistics
            normalized['team_statistics'] = team_stats
            # Remove the duplicate game_description
            if 'game_description' in normalized:
                del normalized['game_description']
    
    return normalized


@router.get("/boxscore/{game_id}")
async def get_box_score(
    game_id: int = Path(..., description="Game ID"),
    sport: str = Query(default="nfl", description="Sport name"),
    engine: StatsEngine = Depends(get_stats_engine)
):
    """
    Get detailed box score for a specific game.
    
    Args:
        game_id: Game/event ID
        sport: Sport name
    
    Returns:
        Complete box score data with player and team statistics
    """
    try:
        box_score = await engine.get_box_score(game_id, sport)
        
        if not box_score:
            raise HTTPException(status_code=404, detail="Box score not found")
        
        # Normalize the box score data for consistent API responses
        normalized_box_score = _normalize_box_score(box_score, sport)
        
        return {
            "game_id": game_id,
            "sport": sport,
            "box_score": normalized_box_score,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get box score",
            game_id=game_id,
            sport=sport,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Failed to fetch box score")


# ============================================================================
# COMPREHENSIVE PLAYER STATISTICS ENDPOINTS
# ============================================================================

@router.get("/stats", response_model=TeamStatsResponse)
async def get_team_player_stats(
    team_id: int = Query(..., description="Team ID"),
    sport: str = Query(..., description="Sport name (nfl, nba, mlb, nhl, epl, mls)"),
    start_date: Optional[str] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for filtering (YYYY-MM-DD)"),
    categories: Optional[str] = Query(None, description="Stat categories to include (comma-separated: offensive,defensive,efficiency,per_game,situational,discipline,achievements,sport_specific)"),
    position: Optional[str] = Query(None, description="Filter by player position"),
    min_games: Optional[int] = Query(0, description="Minimum games played filter"),
    engine: StatsEngine = Depends(get_stats_engine)
):
    """
    Get comprehensive player statistics for a team with categorized data.
    
    Args:
        team_id: Team ID to fetch players for
        sport: Sport name (nfl, nba, mlb, nhl, epl, mls)
        start_date: Start date for filtering (YYYY-MM-DD)
        end_date: End date for filtering (YYYY-MM-DD)
        categories: Specific stat categories to return (all if not specified)
        position: Filter players by position
        min_games: Only include players with minimum games played
    
    Returns:
        Team statistics with all player data categorized by stat type
        Note: Date filtering applies to current season data only
    """
    try:
        # Get players for the team (current season)
        players = await engine.get_players(team_id, sport)
        
        # Parse categories filter
        category_filter = None
        if categories:
            category_filter = [cat.strip().lower() for cat in categories.split(",")]
        
        # Filter and process players
        processed_players = []
        for player in players:
            # Skip players without season stats
            if not player.season_stats:
                continue
                
            # Apply filters
            if position and player.position_display != position:
                continue
                
            games_played = player.season_stats.get("games", player.season_stats.get("games_played", 0))
            if games_played and games_played < min_games:
                continue
            
            # Manually construct player response data
            player_data = {
                "id": player.id,
                "first_name": player.first_name,
                "last_name": player.last_name,
                "full_name": player.full_name,
                "sport": sport,
                "league": sport.upper(),
                "team_id": player.team_id,
                "team": player.team.dict() if hasattr(player.team, 'dict') else None,
                "position": player.position_display or "Unknown",
                "jersey_number": player.jersey_number or 0,
                "status": "active",  # Default status
                "stats_summary": player.stats_summary or "No stats available",
                "all_stats_categories": player.all_stats_categories or {},
                "season_stats": player.season_stats or {},
                "season_id": player.season_stats.get("season_id", 64) if player.season_stats else 64
            }
            
            # Apply category filter if specified
            if category_filter:
                filtered_categories = {}
                for category in category_filter:
                    if category in player.all_stats_categories:
                        filtered_categories[category] = player.all_stats_categories[category]
                player_data["all_stats_categories"] = filtered_categories
            
            processed_players.append(PlayerStatsResponse(**player_data))
        
        # Get team info for response
        team_name = f"Team {team_id}"
        if processed_players and processed_players[0].team:
            team_name = processed_players[0].team.get("name", team_name)
        
        # Create response with date filter info
        date_filter_info = None
        if start_date or end_date:
            date_filter_info = {
                "start_date": start_date,
                "end_date": end_date,
                "note": "Date filtering applies to current season cumulative data."
            }
        
        return TeamStatsResponse(
            team_id=team_id,
            team_name=team_name,
            sport=sport,
            league=sport.upper(),
            total_players=len(processed_players),
            players=processed_players,
            updated_at=datetime.utcnow(),
            date_filter=date_filter_info
        )
        
    except Exception as e:
        logger.error(
            "Failed to get team player statistics",
            team_id=team_id,
            sport=sport,
            start_date=start_date,
            end_date=end_date,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Failed to fetch team player statistics")


@router.get("/stats/{player_id}", response_model=PlayerStatsResponse)
async def get_player_comprehensive_stats(
    player_id: int = Path(..., description="Player ID"),
    team_id: Optional[int] = Query(None, description="Team ID (recommended for performance)"),
    sport: str = Query(..., description="Sport name (nfl, nba, mlb, nhl, epl, mls)"),
    categories: Optional[str] = Query(None, description="Stat categories to include (comma-separated)"),
    engine: StatsEngine = Depends(get_stats_engine)
):
    """
    Get comprehensive statistics for a specific player with categorized data.
    
    Args:
        player_id: Player ID
        team_id: Team ID (recommended for performance)
        sport: Sport name
        categories: Specific stat categories to return (all if not specified)
    
    Returns:
        Complete player statistics with all categories
    """
    try:
        # Get player by ID
        player = await engine.get_player_by_id(player_id, team_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Manually construct player response data
        player_data = {
            "id": player.id,
            "first_name": player.first_name,
            "last_name": player.last_name,
            "full_name": player.full_name,
            "sport": sport,
            "league": sport.upper(),
            "team_id": player.team_id,
            "team": player.team.dict() if hasattr(player.team, 'dict') else None,
            "position": player.position_display,
            "jersey_number": player.jersey_number,
            "status": "active",  # Default status
            "stats_summary": player.stats_summary,
            "all_stats_categories": player.all_stats_categories,
            "season_stats": player.season_stats or {}
        }
        
        # Apply category filter if specified
        if categories:
            category_filter = [cat.strip().lower() for cat in categories.split(",")]
            filtered_categories = {}
            for category in category_filter:
                if category in player.all_stats_categories:
                    filtered_categories[category] = player.all_stats_categories[category]
            player_data["all_stats_categories"] = filtered_categories
        
        return PlayerStatsResponse(**player_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get player comprehensive statistics",
            player_id=player_id,
            team_id=team_id,
            sport=sport,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Failed to fetch player statistics")


@router.get("/stats/categories")
async def get_stats_categories_info():
    """
    Get information about available statistics categories.
    
    Returns:
        Information about all available stat categories and what they contain
    """
    return {
        "categories": {
            "per_game": {
                "description": "Per-game average statistics",
                "examples": ["points_average", "rebounds_average", "goals_average", "receiving_yards_per_game"]
            },
            "offensive": {
                "description": "Offensive production statistics",
                "examples": ["points", "goals", "receptions", "assists", "batting_average"]
            },
            "defensive": {
                "description": "Defensive and stopping statistics", 
                "examples": ["rebounds", "tackles", "blocked_shots", "interceptions", "clean_sheets"]
            },
            "efficiency": {
                "description": "Efficiency and advanced metrics",
                "examples": ["player_efficiency_rating", "field_goals_percentage", "catch_rate", "save_percentage"]
            },
            "situational": {
                "description": "Situational and context-specific statistics",
                "examples": ["clutch_stats", "power_play_points", "game_winning_goals", "redzone_targets"]
            },
            "discipline": {
                "description": "Fouls, penalties and disciplinary statistics",
                "examples": ["personal_fouls", "yellow_cards", "penalty_minutes", "ejections"]
            },
            "achievements": {
                "description": "Achievement-based statistics",
                "examples": ["double_doubles", "hat_tricks", "shutouts", "high_game_points"]
            },
            "sport_specific": {
                "description": "Sport-specific statistics that don't fit other categories",
                "examples": ["games_started", "minutes", "innings_pitched", "touches_total"]
            }
        },
        "supported_sports": ["nfl", "nba", "mlb", "nhl", "epl", "mls"],
        "usage": "Use categories parameter to filter: ?categories=offensive,defensive,efficiency"
    }


@router.get("/stats/compare")
async def compare_players(
    player_ids: str = Query(..., description="Comma-separated player IDs to compare"),
    sport: str = Query(..., description="Sport name"),
    categories: Optional[str] = Query(None, description="Stat categories to include"),
    engine: StatsEngine = Depends(get_stats_engine)
):
    """
    Compare statistics between multiple players.
    
    Args:
        player_ids: Comma-separated player IDs
        sport: Sport name
        categories: Specific stat categories to compare
    
    Returns:
        Side-by-side comparison of player statistics
    """
    try:
        # Parse player IDs
        ids = [int(id.strip()) for id in player_ids.split(",")]
        
        # Get players
        players_data = []
        for player_id in ids:
            player = await engine.get_player_by_id(player_id)
            if player:
                player_dict = player.dict()
                
                # Apply category filter if specified
                if categories:
                    category_filter = [cat.strip().lower() for cat in categories.split(",")]
                    filtered_categories = {}
                    for category in category_filter:
                        if category in player.all_stats_categories:
                            filtered_categories[category] = player.all_stats_categories[category]
                    player_dict["all_stats_categories"] = filtered_categories
                
                players_data.append(player_dict)
        
        if not players_data:
            raise HTTPException(status_code=404, detail="No players found")
        
        return {
            "sport": sport,
            "players_compared": len(players_data),
            "players": players_data,
            "comparison_timestamp": datetime.utcnow().isoformat()
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid player_ids format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to compare players",
            player_ids=player_ids,
            sport=sport,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Failed to compare players")


# ============================================================================
# HEALTH AND STATUS ENDPOINTS
# ============================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint for stats engine."""
    return {
        "status": "healthy",
        "engine": "v6",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/status")
async def get_status():
    """Get detailed status of the stats engine."""
    return {
        "engine": "v6-stats",
        "status": "operational",
        "supported_sports": ["nfl", "nba", "mlb", "nhl", "epl", "mls"],
        "features": [
            "games",
            "schedule", 
            "teams",
            "standings",
            "players",
            "rosters",
            "box_scores",
            "comprehensive_player_stats",
            "categorized_statistics",
            "player_comparison",
            "multi_sport_coverage"
        ],
        "stat_categories": [
            "per_game",
            "offensive", 
            "defensive",
            "efficiency",
            "situational",
            "discipline",
            "achievements",
            "sport_specific"
        ],
        "total_sports_supported": 6,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# HISTORICAL DATA API - ESPN Integration
# ============================================================================

class ESPNGameHeader(BaseModel):
    """ESPN game header information."""
    id: str
    uid: str
    season: Dict[str, Any]
    timeValid: bool
    competitions: List[Dict[str, Any]]
    league: Dict[str, Any]

class ESPNGameInfo(BaseModel):
    """ESPN game venue and metadata."""
    venue: Dict[str, Any]
    attendance: Optional[int] = None
    officials: List[Dict[str, Any]] = Field(default_factory=list)

class ESPNBoxscore(BaseModel):
    """ESPN box score data."""
    teams: List[Dict[str, Any]] = Field(default_factory=list)
    players: List[Dict[str, Any]] = Field(default_factory=list)

class HistoricalGameSummary(BaseModel):
    """Complete historical game summary from ESPN."""
    event_id: int
    sport: str
    header: ESPNGameHeader
    teams: List[Dict[str, Any]] = Field(default_factory=list)
    boxscore: ESPNBoxscore
    game_info: ESPNGameInfo
    plays: List[Dict[str, Any]] = Field(default_factory=list)
    statistics: List[Dict[str, Any]] = Field(default_factory=list)
    cached_at: datetime = Field(default_factory=datetime.utcnow)

class HistoricalGameList(BaseModel):
    """List of historical games for a date."""
    date: datetime
    sport: str
    games: List[Dict[str, Any]] = Field(default_factory=list)
    cached_at: datetime = Field(default_factory=datetime.utcnow)


@router.get("/history/{sport}/{date}", response_model=HistoricalGameList)
async def get_historical_games_by_date(
    sport: str = Path(..., description="Sport type"),
    date: str = Path(..., description="Date in YYYY-MM-DD format"),
    stats_engine: StatsEngine = Depends(get_stats_engine)
):
    """
    Get historical games for a specific date from ESPN.
    
    Returns comprehensive game data for all games played on the specified date:
    - Game header and metadata
    - Team rosters and statistics  
    - Box scores and player performance
    - Play-by-play data (when available)
    - Game venue and officials
    
    Fetches games from ESPN scoreboard API, then retrieves full details for each game.
    
    Supported sports:
    - basketball_nba (NBA games)
    - americanfootball_nfl (NFL games) 
    - baseball_mlb (MLB games)
    - icehockey_nhl (NHL games)
    
    Args:
        sport: Sport type (basketball_nba, americanfootball_nfl, etc.)
        date: Date in YYYY-MM-DD format
        
    Returns:
        List of games with full ESPN data for the specified date
    """
    try:
        # Parse date string
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
        
        logger.info("Fetching ESPN historical games by date", sport=sport, date=date)
        
        # Get historical games with full details
        games = await stats_engine.get_historical_games_by_date(parsed_date, sport)
        
        # Convert to response model (simplified for list view)
        game_summaries = []
        for game in games:
            summary = {
                "event_id": game.get("event_id"),
                "sport": game.get("sport"),
                "event_name": game.get("scoreboard_info", {}).get("event_name"),
                "event_date": game.get("scoreboard_info", {}).get("event_date"),
                "status": game.get("scoreboard_info", {}).get("status", {}),
                "header": game.get("header", {}),
                "teams": game.get("teams", []),
                "game_info": game.get("game_info", {})
            }
            game_summaries.append(summary)
        
        response = HistoricalGameList(
            date=parsed_date,
            sport=sport,
            games=game_summaries
        )
        
        logger.info("Retrieved ESPN historical games by date", sport=sport, date=date, games_count=len(games))
        return response
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error("Failed to fetch ESPN historical games by date", sport=sport, date=date, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch historical games")


@router.get("/history/{event_id}", response_model=HistoricalGameSummary)
async def get_historical_game_summary(
    event_id: int = Path(..., description="ESPN event ID"),
    sport: str = Query(default="basketball_nba", description="Sport type"),
    stats_engine: StatsEngine = Depends(get_stats_engine)
):
    """
    Get complete historical game summary from ESPN.
    
    Returns comprehensive game data including:
    - Game header and metadata
    - Team rosters and statistics  
    - Box scores and player performance
    - Play-by-play data (when available)
    - Game venue and officials
    
    Data is cached aggressively since historical information never changes.
    
    Supported sports:
    - basketball_nba (NBA games)
    - americanfootball_nfl (NFL games) 
    - baseball_mlb (MLB games)
    - icehockey_nhl (NHL games)
    """
    try:
        logger.info("Fetching historical game summary", event_id=event_id, sport=sport)
        
        # Get historical data from ESPN
        raw_data = await stats_engine.get_historical_game_summary(event_id, sport)
        
        # Convert to response model
        summary = HistoricalGameSummary(
            event_id=raw_data["event_id"],
            sport=raw_data["sport"],
            header=ESPNGameHeader(**raw_data["header"]),
            teams=raw_data["teams"],
            boxscore=ESPNBoxscore(**raw_data["boxscore"]),
            game_info=ESPNGameInfo(**raw_data["game_info"]),
            plays=raw_data["plays"],
            statistics=raw_data["statistics"]
        )
        
        logger.info("Retrieved historical game summary", event_id=event_id, sport=sport)
        return summary
        
    except Exception as e:
        logger.error("Failed to fetch historical game summary", event_id=event_id, sport=sport, error=str(e))
        raise HTTPException(status_code=404, detail=f"Historical game summary not found for event {event_id}")


@router.get("/history/{sport}/{date}", response_model=HistoricalGameList)
async def get_historical_games_by_date(
    sport: str = Path(..., description="Sport type"),
    date: str = Path(..., description="Date in YYYY-MM-DD format"),
    stats_engine: StatsEngine = Depends(get_stats_engine)
):
    """
    Get historical games for a specific date from ESPN.
    
    Returns comprehensive game data for all games played on the specified date:
    - Game header and metadata
    - Team rosters and statistics  
    - Box scores and player performance
    - Play-by-play data (when available)
    - Game venue and officials
    
    Fetches games from ESPN scoreboard API, then retrieves full details for each game.
    
    Supported sports:
    - basketball_nba (NBA games)
    - americanfootball_nfl (NFL games) 
    - baseball_mlb (MLB games)
    - icehockey_nhl (NHL games)
    
    Args:
        sport: Sport type (basketball_nba, americanfootball_nfl, etc.)
        date: Date in YYYY-MM-DD format
        
    Returns:
        List of games with full ESPN data for the specified date
    """
    try:
        # Parse date string
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
        
        logger.info("Fetching ESPN historical games by date", sport=sport, date=date)
        
        # Get historical games with full details
        games = await stats_engine.get_historical_games_by_date(parsed_date, sport)
        
        # Convert to response model (simplified for list view)
        game_summaries = []
        for game in games:
            summary = {
                "event_id": game.get("event_id"),
                "sport": game.get("sport"),
                "event_name": game.get("scoreboard_info", {}).get("event_name"),
                "event_date": game.get("scoreboard_info", {}).get("event_date"),
                "status": game.get("scoreboard_info", {}).get("status", {}),
                "header": game.get("header", {}),
                "teams": game.get("teams", []),
                "game_info": game.get("game_info", {})
            }
            game_summaries.append(summary)
        
        response = HistoricalGameList(
            date=parsed_date,
            sport=sport,
            games=game_summaries
        )
        
        logger.info("Retrieved ESPN historical games by date", sport=sport, date=date, games_count=len(games))
        return response
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error("Failed to fetch ESPN historical games by date", sport=sport, date=date, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch historical games")


@router.get("/history/{sport}/search")
async def search_historical_games(
    sport: str = Path(..., description="Sport type"),
    team: Optional[str] = Query(default=None, description="Team name to search for"),
    start_date: Optional[str] = Query(default=None, description="Start date in YYYY-MM-DD"),
    end_date: Optional[str] = Query(default=None, description="End date in YYYY-MM-DD"),
    limit: int = Query(default=50, description="Maximum results to return"),
    stats_engine: StatsEngine = Depends(get_stats_engine)
):
    """
    Search historical games by team and/or date range.
    
    Returns comprehensive game data matching the search criteria:
    - Game header and metadata
    - Team rosters and statistics  
    - Box scores and player performance
    - Play-by-play data (when available)
    - Game venue and officials
    
    Searches ESPN games by iterating through dates and filtering by team name.
    Supports partial team name matching (case-insensitive).
    
    Supported sports:
    - basketball_nba (NBA games)
    - americanfootball_nfl (NFL games) 
    - baseball_mlb (MLB games)
    - icehockey_nhl (NHL games)
    
    Args:
        sport: Sport type
        team: Team name to filter by (optional, partial matching supported)
        start_date: Start date for search in YYYY-MM-DD format (optional)
        end_date: End date for search in YYYY-MM-DD format (optional)
        limit: Maximum number of results to return (default: 50)
        
    Returns:
        List of matching games with full ESPN data and search metadata
    """
    try:
        # Parse date strings if provided
        parsed_start_date = None
        parsed_end_date = None
        
        if start_date:
            parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        logger.info("Searching ESPN historical games", sport=sport, team=team, 
                   start_date=start_date, end_date=end_date, limit=limit)
        
        # Search for matching games
        games = await stats_engine.search_historical_games(
            sport=sport,
            team=team,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            limit=limit
        )
        
        # Convert to response format
        game_summaries = []
        for game in games:
            summary = {
                "event_id": game.get("event_id"),
                "sport": game.get("sport"),
                "event_name": game.get("scoreboard_info", {}).get("event_name"),
                "event_date": game.get("scoreboard_info", {}).get("event_date"),
                "status": game.get("scoreboard_info", {}).get("status", {}),
                "header": game.get("header", {}),
                "teams": game.get("teams", []),
                "game_info": game.get("game_info", {})
            }
            game_summaries.append(summary)
        
        response = {
            "sport": sport,
            "search_criteria": {
                "team": team,
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit
            },
            "results": game_summaries,
            "total_found": len(game_summaries),
            "search_metadata": {
                "searched_date_range": {
                    "start": start_date,
                    "end": end_date
                },
                "team_filter_applied": team is not None,
                "date_filter_applied": start_date is not None or end_date is not None
            }
        }
        
        logger.info("ESPN historical games search completed", sport=sport, team=team, 
                   results_count=len(game_summaries), limit=limit)
        
        return response
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error("Failed to search ESPN historical games", sport=sport, team=team, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to search historical games")
