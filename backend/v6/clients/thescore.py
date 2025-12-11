"""
TheScore API client implementation.
"""

from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import structlog

from .base import BaseAPIClient

logger = structlog.get_logger(__name__)


class TheScoreClient(BaseAPIClient):
    """Client for theScore API with NFL and other sports data."""
    
    def __init__(self):
        # Default headers based on curl examples
        default_headers = {
            'accept': 'application/json',
            'x-country-code': 'US',
            'priority': 'u=3, i',
            'accept-language': 'en-US;q=1',
            'x-api-version': '1.8.2',
            'cache-control': 'max-age=0',
            'user-agent': 'theScore/25.19.0 iOS/26.2 (iPhone; Retina, 1284x2778)',
            'x-app-version': '25.19.0',
            'x-region-code': 'FL',
        }
        
        super().__init__(
            base_url="https://api.thescore.com",
            headers=default_headers,
            timeout=30,
            rate_limit_delay=0.1  # Be respectful to the API
        )
    
    async def get_games(
        self,
        sport: str = "nfl",
        utc_offset: int = -18000,
        rpp: int = -1,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Get current games for a sport using /events endpoint.
        
        Args:
            sport: Sport name (e.g., 'nfl', 'nba', 'mlb', 'nhl')
            utc_offset: UTC offset in seconds
            rpp: Results per page (-1 for all)
        """
        params = {"utc_offset": utc_offset}
        if rpp != -1:
            params["rpp"] = rpp
        else:
            params["rpp"] = "-1"
        
        endpoint = f"{sport}/events"
        
        try:
            data = await self.get(endpoint, params=params)
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(
                "Failed to fetch games",
                sport=sport,
                error=str(e)
            )
            return []
    
    async def get_schedule(
        self,
        sport: str = "nfl",
        utc_offset: int = -18000,
        rpp: int = -1
    ) -> List[Dict[str, Any]]:
        """
        Get game schedule (alias for get_games).
        
        Args:
            sport: Sport name
            utc_offset: UTC offset in seconds
            rpp: Results per page
        """
        return await self.get_games(sport, utc_offset, rpp)
    
    async def get_teams(self, sport: str = "nfl", league: str = "nfl", **kwargs) -> List[Dict[str, Any]]:
        """
        Get teams for a sport/league.
        Note: theScore doesn't have a direct teams endpoint, so we get from standings
        """
        return await self.get_standings(sport, league)
    
    async def get_standings(
        self,
        sport: str = "nfl",
        league: str = "nfl",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Get league standings.
        
        Args:
            sport: Sport name (e.g., 'nfl', 'nba')
            league: League name (e.g., 'nfl', 'nba')
        """
        params = {"rpp": "-1"}
        endpoint = f"{sport}/standings"
        
        try:
            data = await self.get(endpoint, params=params)
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(
                "Failed to fetch standings",
                sport=sport,
                league=league,
                error=str(e)
            )
            return []
    
    async def get_players(
        self,
        team_id: int,
        sport: str = "nfl",
        sideload_team: bool = True,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Get players for a team.
        
        Args:
            team_id: Team ID
            sport: Sport name for endpoint
            sideload_team: Whether to include team data
        """
        endpoint = f"{sport}/teams/{team_id}/players"
        
        # Build params dict like other working endpoints
        params = {"rpp": "-1"}  # Critical parameter that was missing!
        
        if sideload_team:
            params["sideload"] = "team"
        
        try:
            data = await self.get(endpoint, params=params)
            
            # Debug: Log raw response structure
            logger.info(
                "Raw API response structure",
                endpoint=endpoint,
                response_type=type(data).__name__,
                response_keys=list(data.keys()) if isinstance(data, dict) else None,
                response_length=len(data) if isinstance(data, list) else None
            )
            
            # If response is a dict, try to extract players list
            if isinstance(data, dict):
                logger.info("Response is dict, looking for players key")
                if "players" in data:
                    logger.info(f"Found {len(data['players'])} players in 'players' key")
                    return data["players"]
                elif "data" in data:
                    logger.info(f"Found {len(data['data'])} players in 'data' key")
                    return data["data"]
                else:
                    logger.warning(f"Dict response has no players key: {list(data.keys())}")
                    return []
            
            return data if isinstance(data, list) else []
            
        except Exception as e:
            logger.error(
                "Failed to fetch players",
                team_id=team_id,
                sport=sport,
                error=str(e)
            )
            return []
    
    async def get_player_stats(
        self,
        team_id: int,
        sideload_team: bool = True,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Get player statistics for a team.
        
        Args:
            team_id: Team ID
            sideload_team: Include team data in response
        """
        params = {"rpp": "-1"}
        
        if sideload_team:
            params["sideload"] = "team"
        
        endpoint = f"nfl/teams/{team_id}/players"
        
        try:
            data = await self.get(endpoint, params=params)
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(
                "Failed to fetch player stats",
                team_id=team_id,
                error=str(e)
            )
            return []
    
    async def get_team_stats(
        self,
        team_id: int,
        sport: str = "football",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get team statistics/profile.
        
        Args:
            team_id: Team ID
            sport: Sport name for endpoint
        """
        endpoint = f"{sport}/teams/{team_id}/profile"
        
        try:
            data = await self.get(endpoint)
            return data if isinstance(data, dict) else {}
        except Exception as e:
            logger.error(
                "Failed to fetch team stats",
                team_id=team_id,
                sport=sport,
                error=str(e)
            )
            return {}
    
    async def get_box_score(
        self,
        event_id: int,
        sport: str = "nfl",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get detailed box score for a specific game/event.
        
        Args:
            event_id: Game/event ID
            sport: Sport name for endpoint
        """
        endpoint = f"{sport}/events/{event_id}"
        
        try:
            data = await self.get(endpoint)
            return data if isinstance(data, dict) else {}
        except Exception as e:
            logger.error(
                "Failed to fetch box score",
                event_id=event_id,
                sport=sport,
                error=str(e)
            )
            return {}
    
    async def get_roster(
        self,
        team_id: int,
        sideload_team: bool = True,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Get team roster (alias for get_players).
        
        Args:
            team_id: Team ID
            sideload_team: Include team data in response
        """
        return await self.get_players(team_id, sideload_team, **kwargs)
