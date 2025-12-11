"""
Action Network API client for EV projections and player props.
"""

import asyncio
from typing import Optional, Dict, Any, List
import structlog

from .base import BaseAPIClient

logger = structlog.get_logger(__name__)


class ActionNetworkClient(BaseAPIClient):
    """Client for Action Network API with EV projections and player props."""
    
    def __init__(self):
        # Action Network specific headers from curl examples
        default_headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'user-agent': 'Action-AppStore/57060 CFNetwork/901.1 Darwin/17.6.0',
            'priority': 'u=3, i',
            'accept-language': 'en-US,en;q=0.9',
        }
        
        super().__init__(
            base_url="https://api.actionnetwork.com/mobile/v2",
            headers=default_headers,
            timeout=30,
            rate_limit_delay=0.2  # Be respectful to Action Network API
        )
    
    async def get_player_props(
        self,
        league_id: int = 1,  # NFL = 1, NBA = 4, MLB = 7
        week: Optional[int] = None,
        state_code: str = "NJ",
        is_live: bool = False,
        limit: int = 500000 # Increased from 50 to 500
    ) -> List[Dict[str, Any]]:
        """
        Get player props projections from Action Network.
        
        Args:
            league_id: League ID (1 for NFL)
            week: Week number (optional)
            state_code: State code for jurisdiction
            is_live: Whether to include live props
            limit: Maximum number of props to return
        
        Returns:
            List of player prop projections
        """
        params = {
            "stateCode": state_code,
            "isLive": str(is_live).lower(),
            "limit": limit
        }
        
        if week:
            params["week"] = week
        
        endpoint = f"/leagues/{league_id}/projections/available"
        
        try:
            data = await self.get(endpoint, params=params)
            
            # Extract player props from response
            player_props = data.get("playerProps", [])
            
            logger.info(
                "Fetched Action Network player props",
                league_id=league_id,
                week=week,
                props_count=len(player_props)
            )
            
            return player_props
            
        except Exception as e:
            logger.error(
                "Failed to fetch Action Network player props",
                league_id=league_id,
                week=week,
                error=str(e)
            )
            return []
    
    async def get_multi_league_props(
        self,
        week: Optional[int] = None,
        state_code: str = "NJ",
        is_live: bool = False,
        limit: int = 500000
    ) -> List[Dict[str, Any]]:
        """
        Get player props from multiple leagues in parallel for expanded coverage.
        
        Args:
            week: Week number (optional)
            state_code: State code for jurisdiction
            is_live: Whether to include live props
            limit: Maximum number of props per league
            
        Returns:
            Combined list of player props from all leagues
        """
        # Define major leagues with their IDs (matching existing mapping)
        leagues = [
            {"id": 1, "name": "NFL"},  # Football
            {"id": 2, "name": "NBA"},  # Basketball (corrected from 4)
            {"id": 3, "name": "MLB"},  # Baseball (corrected from 7)
        ]
        
        # Fetch props from all leagues in parallel
        tasks = []
        for league in leagues:
            task = self.get_player_props(
                league_id=league["id"],
                week=week,
                state_code=state_code,
                is_live=is_live,
                limit=limit
            )
            tasks.append(task)
        
        try:
            # Execute all requests in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_props = []
            for i, result in enumerate(results):
                league_name = leagues[i]["name"]
                if isinstance(result, Exception):
                    logger.error(f"Failed to fetch {league_name} props", error=str(result))
                elif isinstance(result, list):
                    # Add league identifier to each prop
                    for prop in result:
                        prop["league_name"] = league_name
                        prop["league_id"] = leagues[i]["id"]
                    all_props.extend(result)
                    logger.info(f"Fetched {len(result)} {league_name} props")
            
            logger.info(
                "Total Action Network props fetched",
                total_props=len(all_props),
                leagues_count=len(leagues)
            )
            
            return all_props
            
        except Exception as e:
            logger.error("Failed to fetch multi-league props", error=str(e))
            return []
    
    async def get_game_projections(
        self,
        sport: str = "nfl",
        book_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Get game projections from Action Network.
        
        Args:
            sport: Sport name (nfl, nba, etc.)
            book_ids: List of book IDs to include
        
        Returns:
            Game projections data
        """
        params = {}
        
        if book_ids:
            params["bookIds"] = ",".join(str(book_id) for book_id in book_ids)
        
        endpoint = f"/scoreboard/gameprojections/{sport}"
        
        try:
            data = await self.get(endpoint, params=params)
            
            logger.info(
                "Fetched Action Network game projections",
                sport=sport,
                book_ids=book_ids
            )
            
            return data
            
        except Exception as e:
            logger.error(
                "Failed to fetch Action Network game projections",
                sport=sport,
                book_ids=book_ids,
                error=str(e)
            )
            return {}
    
    def normalize_player_props(self, raw_props: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert Action Network player props to standard EV format.
        
        Args:
            raw_props: Raw player props from Action Network API
        
        Returns:
            Normalized player props compatible with EV calculations
        """
        normalized_props = []
        
        for prop in raw_props:
            try:
                # Extract base player information
                player_id = prop.get("player_id")
                player_abbr = prop.get("player_abbr", "")
                team_id = prop.get("team_id")
                
                # Extract prop details
                pick_type = prop.get("custom_pick_type", "")
                pick_display = prop.get("custom_pick_type_display_name", "")
                period_type = prop.get("period_type", "game")
                line_type = prop.get("line_type", "total")
                
                # Process lines/odds
                lines = prop.get("lines", [])
                for line in lines:
                    try:
                        normalized_prop = {
                            "source": "actionnetwork",
                            "player_id": player_id,
                            "player_name": player_abbr,
                            "team_id": team_id,
                            "prop_type": pick_display,
                            "prop_category": pick_type,
                            "period": period_type,
                            "line_type": line_type,
                            
                            # Line details
                            "line_value": line.get("value"),
                            "odds": line.get("odds"),
                            "side": line.get("side", "over"),
                            
                            # Event information
                            "event_id": line.get("event_id"),
                            "league_id": line.get("league_id"),
                            "book_id": line.get("book_id"),
                            "book_parent_id": line.get("book_parent_id"),
                            
                            # Market details
                            "market_id": line.get("market_id"),
                            "outcome_id": line.get("outcome_id"),
                            "option_type_id": line.get("option_type_id"),
                            
                            # Status
                            "is_live": line.get("is_live", False),
                            
                            # Raw data for debugging
                            "raw_data": prop
                        }
                        
                        normalized_props.append(normalized_prop)
                        
                    except Exception as e:
                        logger.warning(
                            "Failed to normalize Action Network line",
                            player_id=player_id,
                            line_id=line.get("outcome_id"),
                            error=str(e)
                        )
                        continue
                        
            except Exception as e:
                logger.warning(
                    "Failed to normalize Action Network prop",
                    prop_id=prop.get("player_id"),
                    error=str(e)
                )
                continue
        
        logger.info(
            "Normalized Action Network player props",
            raw_count=len(raw_props),
            normalized_count=len(normalized_props)
        )
        
        return normalized_props
    
    def normalize_game_projections(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert Action Network game projections to standard EV format.
        
        Args:
            raw_data: Raw game projections from Action Network API
        
        Returns:
            Normalized game projections compatible with EV calculations
        """
        normalized_projections = []
        
        try:
            # Extract games from the response
            games = raw_data.get("games", [])
            
            for game in games:
                try:
                    # Extract basic game info
                    game_id = game.get("id")
                    home_team = game.get("home_team", {})
                    away_team = game.get("away_team", {})
                    
                    # Extract projections if available
                    projections = game.get("projections", {})
                    
                    normalized_projection = {
                        "source": "actionnetwork",
                        "event_id": game_id,
                        "sport": raw_data.get("league", {}).get("sport", "football"),
                        "league": raw_data.get("league", {}).get("name", "nfl"),
                        
                        # Teams
                        "home_team_id": home_team.get("id"),
                        "home_team_name": home_team.get("name"),
                        "away_team_id": away_team.get("id"), 
                        "away_team_name": away_team.get("name"),
                        
                        # Game projections
                        "projections": projections,
                        
                        # Raw data for debugging
                        "raw_data": game
                    }
                    
                    normalized_projections.append(normalized_projection)
                    
                except Exception as e:
                    logger.warning(
                        "Failed to normalize Action Network game projection",
                        game_id=game.get("id"),
                        error=str(e)
                    )
                    continue
                    
        except Exception as e:
            logger.error(
                "Failed to normalize Action Network game projections",
                error=str(e)
            )
        
        logger.info(
            "Normalized Action Network game projections",
            raw_games=len(raw_data.get("games", [])),
            normalized_count=len(normalized_projections)
        )
        
        return normalized_projections
    
    async def get_ev_data(
        self,
        sport: str = "nfl",
        week: Optional[int] = None,
        book_ids: Optional[List[int]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get comprehensive EV data from Action Network.
        
        Args:
            sport: Sport name (or "all" for multi-league)
            week: Week number for player props
            book_ids: Book IDs for game projections
        
        Returns:
            Dictionary with player_props and game_projections
        """
        try:
            if sport == "all":
                # Fetch all leagues for maximum coverage
                raw_player_props = await self.get_multi_league_props(
                    week=week,
                    limit=500000
                )
            else:
                # Map sport to league_id and fetch specific league
                sport_to_league = {
                    "nfl": 1,
                    "nba": 2,
                    "mlb": 3,
                    "nhl": 4
                }
                
                league_id = sport_to_league.get(sport, 1)
                
                # Fetch player props for specific sport
                raw_player_props = await self.get_player_props(
                    league_id=league_id,
                    week=week,
                    limit=500000
                )
            
            # Fetch game projections
            raw_game_projections = await self.get_game_projections(
                sport=sport,
                book_ids=book_ids
            )
            
            logger.info(
                "Fetched Action Network EV data",
                sport=sport,
                player_props=len(raw_player_props),
                game_projections=len(raw_game_projections)
            )
            
            return {
                "player_props": raw_player_props,
                "game_projections": raw_game_projections
            }
            
        except Exception as e:
            logger.error(
                "Failed to fetch Action Network EV data",
                sport=sport,
                error=str(e)
            )
            return {
                "player_props": [],
                "game_projections": []
            }
    
    async def get_games(self, sport: str, league: str, **kwargs) -> List[Dict[str, Any]]:
        """Get games for a sport/league - Action Network implementation."""
        # Action Network specific implementation
        return []
    
    async def get_teams(self, sport: str, league: str, **kwargs) -> List[Dict[str, Any]]:
        """Get teams for a sport/league - Action Network implementation."""
        # Action Network specific implementation
        return []
    
    async def get_players(self, team_id: int, **kwargs) -> List[Dict[str, Any]]:
        """Get players for a team - Action Network implementation."""
        # Action Network specific implementation
        return []
