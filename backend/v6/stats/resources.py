"""
Resource classes for V6 Stats Engine - clean separation of data types.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog

from ..clients.thescore import TheScoreClient
from ..models import Game, Team, Player, GameSchedule, LeagueStandings, Standing

logger = structlog.get_logger(__name__)


class BaseResource:
    """Base class for all resource handlers."""
    
    def __init__(self, client: TheScoreClient):
        self.client = client
    
    async def _normalize_response(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Common response normalization."""
        return data


class GamesResource(BaseResource):
    """Resource for game data and schedules."""
    
    async def get_games(
        self,
        sport: str = "football",
        league: str = "nfl",
        event_ids: Optional[List[int]] = None,
        betmode: bool = True
    ) -> List[Game]:
        """
        Get games for a specific sport/league.
        
        Args:
            sport: Sport name (nfl, nba, etc.)
            league: League name (nfl, nba, etc.)
            event_ids: Specific game IDs to fetch
            betmode: Include betting odds data
        
        Returns:
            List of Game objects
        """
        try:
            # TheScoreClient.get_games() only accepts sport, utc_offset, rpp
            # We need to work with its actual signature
            raw_data = await self.client.get_games(sport, -18000, -1)
            
            games = []
            for game_data in raw_data:
                try:
                    game = Game(**game_data)
                    games.append(game)
                except Exception as e:
                    logger.warning(
                        "Failed to parse game data",
                        game_id=game_data.get('id'),
                        error=str(e)
                    )
                    continue
            
            logger.info(
                "Retrieved games successfully",
                sport=sport,
                league=league,
                count=len(games)
            )
            
            return games
            
        except Exception as e:
            logger.error(
                "Failed to get games",
                sport=sport,
                league=league,
                error=str(e)
            )
            return []
    
    async def get_box_score(
        self,
        event_id: int,
        sport: str = "nfl"
    ) -> Dict[str, Any]:
        """
        Get detailed box score for a specific game.
        
        Args:
            event_id: Game/event ID
            sport: Sport name
        
        Returns:
            Box score data as dictionary
        """
        try:
            raw_data = await self.client.get_box_score(event_id, sport)
            
            logger.info(
                "Retrieved box score successfully",
                event_id=event_id,
                sport=sport
            )
            
            return raw_data
            
        except Exception as e:
            logger.error(
                "Failed to get box score",
                event_id=event_id,
                sport=sport,
                error=str(e)
            )
            return {}
    
    async def get_schedule(
        self,
        sport: str = "nfl",
        utc_offset: int = -18000
    ) -> GameSchedule:
        """
        Get complete schedule for a sport.
        
        Args:
            sport: Sport name
            utc_offset: UTC offset in seconds
        
        Returns:
            GameSchedule object with all games
        """
        try:
            raw_data = await self.client.get_schedule(sport, utc_offset)
            
            games = []
            for game_data in raw_data:
                try:
                    game = Game(**game_data)
                    games.append(game)
                except Exception as e:
                    logger.warning(
                        "Failed to parse schedule game data",
                        game_id=game_data.get('id'),
                        error=str(e)
                    )
                    continue
            
            schedule = GameSchedule(
                games=games,
                total_count=len(games),
                per_page=-1
            )
            
            logger.info(
                "Retrieved schedule successfully",
                sport=sport,
                game_count=len(games)
            )
            
            return schedule
            
        except Exception as e:
            logger.error(
                "Failed to get schedule",
                sport=sport,
                error=str(e)
            )
            return GameSchedule(games=[], total_count=0)


class TeamsResource(BaseResource):
    """Resource for team data and statistics."""
    
    async def get_teams(
        self,
        sport: str = "nfl",
        league: str = "nfl"
    ) -> List[Team]:
        """
        Get all teams for a sport/league with current records and standings.
        
        Args:
            sport: Sport name
            league: League name
        
        Returns:
            List of Team objects with full information
        """
        try:
            # Get teams from standings data
            raw_data = await self.client.get_teams(sport, league)
            
            teams = []
            for standing_data in raw_data:
                try:
                    # Extract team info from standing data - theScore API structure
                    if 'team' in standing_data:
                        team_info = standing_data['team'].copy()  # Start with team object
                        
                        # Add standing information
                        team_info.update({
                            'record': {
                                'wins': standing_data.get('wins', 0),
                                'losses': standing_data.get('losses', 0),
                                'ties': standing_data.get('ties', 0),
                                'winning_percentage': standing_data.get('winning_percentage'),
                                'streak': standing_data.get('streak'),
                                'short_record': standing_data.get('short_record')
                            },
                            'standing': standing_data,
                            'sport': sport,
                            'league': league
                        })
                        
                        team = Team(**team_info)
                        teams.append(team)
                except Exception as e:
                    logger.warning(
                        "Failed to parse team data",
                        standing_id=standing_data.get('id'),
                        error=str(e)
                    )
                    continue
            
            logger.info(
                "Retrieved teams successfully",
                sport=sport,
                league=league,
                count=len(teams)
            )
            
            return teams
            
        except Exception as e:
            logger.error(
                "Failed to get teams",
                sport=sport,
                league=league,
                error=str(e)
            )
            return []
    
    async def get_standings(
        self,
        sport: str = "nfl",
        league: str = "nfl"
    ) -> LeagueStandings:
        """
        Get league standings.
        
        Args:
            sport: Sport name (e.g., 'nfl', 'nba')
            league: League name (e.g., 'nfl', 'nba')
        """
        try:
            raw_data = await self.client.get_standings(sport, league)
            
            # Parse standings using the actual API structure
            standings_list = []
            for standing_data in raw_data:
                try:
                    standing = Standing(**standing_data)
                    standings_list.append(standing)
                except Exception as e:
                    logger.warning(
                        "Failed to parse standing data",
                        standing_id=standing_data.get('id'),
                        error=str(e)
                    )
                    continue
            
            standings = LeagueStandings(
                league=league,
                season=None,  # Will be extracted from first standing if needed
                updated_at=raw_data[0].get('updated_at', '') if raw_data else '',
                overall=standings_list
            )
            
            logger.info(
                "Retrieved standings successfully",
                sport=sport,
                league=league,
                team_count=len(standings_list)
            )
            
            return standings
            
        except Exception as e:
            logger.error(
                "Failed to get standings",
                sport=sport,
                league=league,
                error=str(e)
            )
            return LeagueStandings(league=league, updated_at='', overall=[])


class PlayersResource(BaseResource):
    """Resource for player data and statistics."""
    
    async def get_players(
        self,
        team_id: int,
        sport: str = "nfl",
        sideload_team: bool = True
    ) -> List[Player]:
        """
        Get players for a specific team.
        
        Args:
            team_id: Team ID
            sport: Sport name (nfl, nba, mlb, nhl)
            sideload_team: Whether to include team information
        
        Returns:
            List of Player objects
        """
        try:
            raw_data = await self.client.get_players(team_id, sport, sideload_team)
            
            # Debug logging
            logger.info(
                "Raw player API response received",
                team_id=team_id,
                sport=sport,
                response_type=type(raw_data).__name__,
                response_length=len(raw_data) if isinstance(raw_data, (list, dict)) else 0
            )
            
            # Log first player structure for debugging
            if raw_data and isinstance(raw_data, list) and len(raw_data) > 0:
                logger.debug(
                    "First player raw data structure",
                    sample_player_keys=list(raw_data[0].keys()) if isinstance(raw_data[0], dict) else "Not a dict",
                    sample_player_id=raw_data[0].get('id') if isinstance(raw_data[0], dict) else None
                )
            
            players = []
            for i, player_data in enumerate(raw_data):
                try:
                    player = Player(**player_data)
                    players.append(player)
                    logger.debug(
                        "Successfully parsed player",
                        player_index=i,
                        player_id=player.id,
                        player_name=player.primary_name
                    )
                except Exception as e:
                    logger.warning(
                        "Failed to parse player data",
                        player_index=i,
                        player_id=player_data.get('id') if isinstance(player_data, dict) else None,
                        player_name=player_data.get('primary_name') if isinstance(player_data, dict) else None,
                        error=str(e),
                        error_type=type(e).__name__
                    )
                    # Log the actual player data that failed
                    logger.debug(
                        "Failed player raw data",
                        player_index=i,
                        raw_data=player_data
                    )
                    continue
            
            logger.info(
                "Retrieved players successfully",
                team_id=team_id,
                sport=sport,
                raw_count=len(raw_data) if isinstance(raw_data, list) else 0,
                parsed_count=len(players)
            )
            
            return players
            
        except Exception as e:
            logger.error(
                "Failed to get players",
                team_id=team_id,
                sport=sport,
                error=str(e),
                error_type=type(e).__name__
            )
            return []
    
    async def get_roster(
        self,
        team_id: int,
        sport: str = "nfl",
        sideload_team: bool = True
    ) -> List[Player]:
        """Alias for get_players - returns team roster."""
        return await self.get_players(team_id, sport, sideload_team)


class ScheduleResource(BaseResource):
    """Resource specifically for schedule data."""
    
    async def get_schedule(
        self,
        sport: str = "nfl",
        utc_offset: int = -18000
    ) -> GameSchedule:
        """Get schedule - delegates to GamesResource."""
        games_resource = GamesResource(self.client)
        return await games_resource.get_schedule(sport, utc_offset)


class StandingsResource(BaseResource):
    """Resource specifically for standings data."""
    
    async def get_standings(
        self,
        sport: str = "nfl",
        league: str = "nfl"
    ) -> LeagueStandings:
        """Get standings - delegates to TeamsResource."""
        teams_resource = TeamsResource(self.client)
        return await teams_resource.get_standings(sport, league)
