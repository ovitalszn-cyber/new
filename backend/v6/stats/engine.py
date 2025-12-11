"""
Main V6 Stats Engine - Unified endpoint for sports statistics.

This is the primary interface for the V6 stats engine, providing clean,
systematic access to all sports data through a unified API.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import asyncio
import structlog
import httpx

from ..clients.thescore import TheScoreClient
from ..models import Game, Team, Player, GameSchedule, LeagueStandings
from .resources import GamesResource, TeamsResource, PlayersResource
from . import StatsIngestor, StatsSnapshot

logger = structlog.get_logger(__name__)

# ESPN games cache (24 hour TTL)
from collections import OrderedDict
_espn_games_cache = OrderedDict()
ESPN_CACHE_TTL = timedelta(hours=24)
MAX_ESPN_CACHE_SIZE = 1000

class StatsEngine:
    """
    Unified V6 Stats Engine for sports data.
    
    Provides clean, systematic access to:
    - Games and schedules
    - Teams and standings  
    - Players and rosters
    - Box scores and statistics
    """
    
    def __init__(self):
        """Initialize the stats engine with API client and resources."""
        self.client = TheScoreClient()
        
        # ESPN client for historical data
        self.espn_client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'accept': '*/*',
                'sec-fetch-site': 'same-site',
                'priority': 'u=3, i',
                'sec-fetch-mode': 'cors',
                'accept-language': 'en-US,en;q=0.9',
                'origin': 'https://www.espn.com',
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
                'referer': 'https://www.espn.com/',
                'sec-fetch-dest': 'empty'
            }
        )
        
        # Resource handlers
        self.games = GamesResource(self.client)
        self.teams = TeamsResource(self.client)
        self.players = PlayersResource(self.client)
        
        logger.info("V6 Stats Engine initialized with ESPN historical data")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the stats engine and clean up resources."""
        await self.client.close()
        await self.espn_client.aclose()
        logger.info("V6 Stats Engine closed")
    
    # ============================================================================
    # GAMES API - Complete game information
    # ============================================================================
    
    async def get_games(
        self,
        sport: str = "nfl",
        league: str = "nfl",
        event_ids: Optional[List[int]] = None,
        betmode: bool = True
    ) -> List[Game]:
        """
        Get games with full information including scores, timing, and betting data.
        
        Args:
            sport: Sport name (nfl, nba, mlb, nhl, etc.)
            league: League name (nfl, nba, mlb, nhl, etc.)
            event_ids: Specific game IDs to fetch (optional)
            betmode: Include betting odds and lines
        
        Returns:
            List of Game objects with complete information
        """
        return await self.games.get_games(sport, league, event_ids, betmode)
    
    async def get_schedule(
        self,
        sport: str = "nfl",
        utc_offset: int = -18000
    ) -> GameSchedule:
        """
        Get complete schedule for a sport.
        
        Args:
            sport: Sport name
            utc_offset: UTC offset in seconds (default: EST)
        
        Returns:
            GameSchedule object with all scheduled games
        """
        return await self.games.get_schedule(sport, utc_offset)
    
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
        return await self.games.get_box_score(event_id, sport)
    
    async def get_game_by_id(self, game_id: int, sport: str = "nfl") -> Optional[Game]:
        """
        Get a specific game by ID.
        
        Args:
            game_id: Game ID
            sport: Sport name
        
        Returns:
            Game object or None if not found
        """
        games = await self.get_games(sport, sport, [game_id])
        return games[0] if games else None
    
    # ============================================================================
    # TEAMS API - Team information and standings
    # ============================================================================
    
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
        return await self.teams.get_teams(sport, league)
    
    async def get_standings(
        self,
        sport: str = "nfl",
        league: str = "nfl"
    ) -> LeagueStandings:
        """
        Get complete league standings.
        
        Args:
            sport: Sport name
            league: League name
        
        Returns:
            LeagueStandings object with rankings and records
        """
        return await self.teams.get_standings(sport, league)
    
    async def get_team_by_id(self, team_id: int, sport: str = "nfl") -> Optional[Team]:
        """
        Get a specific team by ID.
        
        Args:
            team_id: Team ID
            sport: Sport name
        
        Returns:
            Team object or None if not found
        """
        teams = await self.get_teams(sport, sport)
        for team in teams:
            if team.id == team_id:
                return team
        return None
    
    # ============================================================================
    # PLAYERS API - Player information and rosters
    # ============================================================================
    
    async def get_players(
        self,
        team_id: int,
        sport: str = "nfl",
        sideload_team: bool = True,
    ) -> List[Player]:
        """Get players for a specific team.

        Args:
            team_id: Team ID
            sport: Sport name (e.g., 'nfl', 'nba', 'mlb', 'nhl')
            sideload_team: Whether to include team information in the payload

        Returns:
            List of Player objects
        """
        return await self.players.get_players(team_id, sport, sideload_team)
    
    async def get_roster(self, team_id: int, sport: str = "nfl") -> List[Player]:
        """
        Get team roster (alias for get_players).
        
        Args:
            team_id: Team ID
            sport: Sport name (e.g., 'nfl', 'nba', 'mlb', 'nhl')
        
        Returns:
            List of Player objects
        """
        return await self.players.get_roster(team_id, sport)
    
    async def get_player_by_id(
        self,
        player_id: int,
        team_id: Optional[int] = None
    ) -> Optional[Player]:
        """
        Get a specific player by ID.
        
        Args:
            player_id: Player ID
            team_id: Team ID (optional, speeds up search)
        
        Returns:
            Player object or None if not found
        """
        if team_id:
            players = await self.get_players(team_id)
            for player in players:
                if player.id == player_id:
                    return player
        else:
            # Would need to search all teams - implement if needed
            logger.warning(
                "Player search without team_id not implemented",
                player_id=player_id
            )
        return None
    
    # ============================================================================
    # UNIFIED API METHODS - Convenience methods for common operations
    # ============================================================================
    
    async def get_today_games(self, sport: str = "nfl") -> List[Game]:
        """Get all games scheduled for today.

        TheScore returns `game_date` as an RFC 2822 string (e.g.
        "Thu, 02 Oct 2025 16:00:00 -0000"). The Game model exposes
        `scheduled_at` as an alias to that string, so we need to parse it
        into a real datetime before comparing dates.
        """
        schedule = await self.get_schedule(sport)
        today = datetime.utcnow().date()

        today_games: List[Game] = []
        for game in schedule.games:
            raw = getattr(game, "game_date", None) or getattr(game, "scheduled_at", None)
            game_date: Optional[datetime] = None

            if isinstance(raw, str):
                # Try RFC 2822 first, then ISO formats
                try:
                    game_date = datetime.strptime(raw, "%a, %d %b %Y %H:%M:%S %z")
                except Exception:
                    try:
                        game_date = datetime.fromisoformat(raw)
                    except Exception:
                        game_date = None
            elif isinstance(raw, datetime):
                game_date = raw

            if game_date and game_date.date() == today:
                today_games.append(game)

        logger.info(
            "Retrieved today's games",
            sport=sport,
            count=len(today_games)
        )

        return today_games
    
    async def get_live_games(self, sport: str = "nfl") -> List[Game]:
        """
        Get all games currently in progress.
        
        Args:
            sport: Sport name
        
        Returns:
            List of Game objects that are live
        """
        games = await self.get_games(sport, sport)
        
        live_games = [
            game for game in games 
            if game.status == "in_progress"
        ]
        
        logger.info(
            "Retrieved live games",
            sport=sport,
            count=len(live_games)
        )
        
        return live_games
    
    async def get_completed_games(
        self,
        sport: str = "nfl",
        days_back: int = 7
    ) -> List[Game]:
        """
        Get recently completed games.
        
        Args:
            sport: Sport name
            days_back: How many days back to look
        
        Returns:
            List of completed Game objects
        """
        games = await self.get_games(sport, sport)
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        completed_games = [
            game for game in games
            if (game.status in ["completed", "final"] and 
                game.scheduled_at)  # Remove completed_at requirement since it's None
        ]
        
        logger.info(
            "Retrieved completed games",
            sport=sport,
            days_back=days_back,
            count=len(completed_games)
        )
        
        return completed_games
    
    # ============================================================================
    # DATA INGESTION - Implements StatsIngestor protocol
    # ============================================================================
    
    async def run(self) -> None:
        """
        Run data ingestion for all supported sports.
        Implements the StatsIngestor protocol.
        """
        logger.info("Starting V6 Stats Engine data ingestion")
        
        # Get current data for all major sports
        sports = ["nfl", "nba", "mlb", "nhl"]
        
        tasks = []
        for sport in sports:
            try:
                # Get games, teams, and update caches
                task = asyncio.create_task(self._ingest_sport_data(sport))
                tasks.append(task)
            except Exception as e:
                logger.error(
                    "Failed to create ingestion task for sport",
                    sport=sport,
                    error=str(e)
                )
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("V6 Stats Engine data ingestion completed")
    
    async def _ingest_sport_data(self, sport: str) -> None:
        """Ingest data for a specific sport."""
        try:
            # Get current games
            games = await self.get_games(sport, sport)
            
            # Get teams and standings
            teams = await self.get_teams(sport, sport)
            
            logger.info(
                "Sport data ingestion completed",
                sport=sport,
                games=len(games),
                teams=len(teams)
            )
        except Exception as e:
            logger.error("Failed to ingest sport data", sport=sport, error=str(e))
    
    # ============================================================================
    # HISTORICAL DATA API - ESPN Integration
    # ============================================================================
    
    async def get_historical_game_summary(
        self,
        event_id: int,
        sport: str = "basketball_nba"
    ) -> Dict[str, Any]:
        """
        Get historical game summary from ESPN API.
        
        Args:
            event_id: ESPN event ID
            sport: Sport type (basketball_nba, americanfootball_nfl, etc.)
            
        Returns:
            Historical game data including teams, scores, and statistics
        """
        try:
            # Map sport to ESPN API path
            sport_mapping = {
                "basketball_nba": "basketball/nba",
                "americanfootball_nfl": "football/nfl",
                "baseball_mlb": "baseball/mlb",
                "icehockey_nhl": "hockey/nhl"
            }
            
            espn_sport = sport_mapping.get(sport, sport.replace("_", "/"))
            
            url = f"https://site.web.api.espn.com/apis/site/v2/sports/{espn_sport}/summary"
            params = {
                "region": "us",
                "lang": "en",
                "contentorigin": "espn",
                "event": str(event_id)
            }
            
            logger.info("Fetching historical game summary", event_id=event_id, sport=sport)
            
            response = await self.espn_client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract comprehensive information from correct ESPN API structure
            summary = {
                "event_id": event_id,
                "sport": sport,
                "header": data.get("header", {}),
                "teams": data.get("boxscore", {}).get("teams", []),  # Teams are in boxscore.teams
                "scores": data.get("header", {}).get("competitions", [{}])[0].get("competitors", []),  # Scores in header.competitors
                "boxscore": data.get("boxscore", {}),
                "game_info": data.get("gameInfo", {}),
                "plays": data.get("plays", []),
                "statistics": data.get("statistics", []),
                "competition": data.get("header", {}).get("competitions", [{}])[0] if data.get("header", {}).get("competitions") else {},
                "leaders": data.get("leaders", {}),
                "injuries": data.get("injuries", []),
                "broadcasts": data.get("broadcasts", []),
                "odds": data.get("odds", {}),
                "seasonseries": data.get("seasonseries", {}),
                "winprobability": data.get("winprobability", [])
            }
            
            logger.info("Retrieved historical game summary", event_id=event_id, sport=sport)
            return summary
            
        except httpx.HTTPStatusError as e:
            logger.error("ESPN API error", event_id=event_id, sport=sport, status_code=e.response.status_code)
            raise
        except Exception as e:
            logger.error("Failed to fetch historical game summary", event_id=event_id, sport=sport, error=str(e))
            raise
    
    def _get_espn_cache_key(self, sport: str, date_str: str) -> str:
        """Generate cache key for ESPN games data."""
        return f"espn:{sport}:{date_str}"
    
    def _is_espn_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if ESPN cache entry is still valid."""
        return datetime.utcnow() - cache_entry["timestamp"] < ESPN_CACHE_TTL
    
    def _evict_old_espn_cache(self):
        """Remove oldest entries if ESPN cache is full."""
        while len(_espn_games_cache) >= MAX_ESPN_CACHE_SIZE:
            _espn_games_cache.popitem(last=False)  # Remove oldest
    
    def _get_from_espn_cache(self, sport: str, date_str: str) -> Optional[List[Dict[str, Any]]]:
        """Get ESPN games data from cache if valid."""
        cache_key = self._get_espn_cache_key(sport, date_str)
        if cache_key in _espn_games_cache:
            cache_entry = _espn_games_cache[cache_key]
            if self._is_espn_cache_valid(cache_entry):
                # Move to end to mark as recently used
                _espn_games_cache.move_to_end(cache_key)
                return cache_entry["data"]
            else:
                # Remove expired entry
                del _espn_games_cache[cache_key]
        return None
    
    def _store_in_espn_cache(self, sport: str, date_str: str, data: List[Dict[str, Any]]):
        """Store ESPN games data in cache with timestamp."""
        self._evict_old_espn_cache()
        cache_key = self._get_espn_cache_key(sport, date_str)
        _espn_games_cache[cache_key] = {
            "data": data,
            "timestamp": datetime.utcnow()
        }
        _espn_games_cache.move_to_end(cache_key)
    
    async def get_historical_games_by_date(
        self,
        date: datetime,
        sport: str = "basketball_nba"
    ) -> List[Dict[str, Any]]:
        """
        Get historical games for a specific date from ESPN scoreboard API.
        
        Uses caching (24-hour TTL) and concurrent fetching for optimal performance.
        
        Args:
            date: Date to fetch games for
            sport: Sport type
            
        Returns:
            List of historical games for the specified date with full details
        """
        try:
            # Map sport to ESPN API path
            sport_mapping = {
                "basketball_nba": "basketball/nba",
                "americanfootball_nfl": "football/nfl",
                "baseball_mlb": "baseball/mlb",
                "icehockey_nhl": "hockey/nhl"
            }
            
            espn_sport = sport_mapping.get(sport, sport.replace("_", "/"))
            
            # Format date for ESPN API (YYYYMMDD)
            date_str = date.strftime("%Y%m%d")
            
            # Check cache first
            cached_data = self._get_from_espn_cache(sport, date_str)
            if cached_data is not None:
                logger.info("Returning cached ESPN games", sport=sport, date=date_str, games_count=len(cached_data))
                return cached_data
            
            url = f"https://site.web.api.espn.com/apis/site/v2/sports/{espn_sport}/scoreboard"
            params = {
                "region": "us",
                "lang": "en",
                "contentorigin": "espn",
                "dates": date_str
            }
            
            logger.info("Fetching ESPN games by date", sport=sport, date=date_str)
            
            response = await self.espn_client.get(url, params=params)
            response.raise_for_status()
            
            scoreboard_data = response.json()
            events = scoreboard_data.get("events", [])
            
            logger.info(f"Found {len(events)} games on scoreboard", sport=sport, date=date_str)
            
            # Fetch detailed summary for each game concurrently (max 8 concurrent)
            detailed_games = []
            semaphore = asyncio.Semaphore(8)  # Limit concurrent requests
            
            async def fetch_game_summary(event):
                async with semaphore:
                    try:
                        event_id = event.get("id")
                        if event_id:
                            # Get full game summary using existing method
                            game_summary = await self.get_historical_game_summary(event_id, sport)
                            
                            # Add basic scoreboard info to the summary
                            game_summary["scoreboard_info"] = {
                                "event_id": event.get("id"),
                                "event_name": event.get("name"),
                                "event_date": event.get("date"),
                                "short_name": event.get("shortName"),
                                "status": event.get("status", {})
                            }
                            
                            return game_summary
                    except Exception as e:
                        logger.warning("Failed to fetch details for game", event_id=event.get("id"), error=str(e))
                        return None
            
            # Execute concurrent requests
            tasks = [fetch_game_summary(event) for event in events]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results
            for result in results:
                if isinstance(result, dict) and result is not None:
                    detailed_games.append(result)
            
            # Store in cache
            self._store_in_espn_cache(sport, date_str, detailed_games)
            
            logger.info(f"Retrieved full details for {len(detailed_games)} games", sport=sport, date=date_str)
            return detailed_games
            
        except httpx.HTTPStatusError as e:
            logger.error("ESPN scoreboard API error", sport=sport, date=date_str, status_code=e.response.status_code)
            raise
        except Exception as e:
            logger.error("Failed to fetch historical games by date", sport=sport, date=date_str, error=str(e))
            raise
    
    async def search_historical_games(
        self,
        sport: str = "basketball_nba",
        team: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search historical games by team and/or date range.
        
        Args:
            sport: Sport type
            team: Team name to filter by (optional)
            start_date: Start date for search (optional)
            end_date: End date for search (optional)
            limit: Maximum number of results to return
            
        Returns:
            List of matching historical games with full details
        """
        try:
            logger.info("Searching ESPN historical games", sport=sport, team=team, 
                       start_date=start_date.isoformat() if start_date else None,
                       end_date=end_date.isoformat() if end_date else None)
            
            # Default to last 30 days if no date range specified
            if not start_date and not end_date:
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=30)
            
            # If only one date is specified, use that date for both
            if start_date and not end_date:
                end_date = start_date
            elif end_date and not start_date:
                start_date = end_date
            
            matching_games = []
            current_date = start_date
            
            # Iterate through dates and fetch games
            while current_date <= end_date and len(matching_games) < limit:
                try:
                    games_on_date = await self.get_historical_games_by_date(current_date, sport)
                    
                    for game in games_on_date:
                        if len(matching_games) >= limit:
                            break
                        
                        # Filter by team if specified
                        if team:
                            game_teams = []
                            
                            # Extract team names from game data
                            if "teams" in game:
                                for team_data in game["teams"]:
                                    if isinstance(team_data, dict):
                                        team_names = [
                                            team_data.get("displayName"),
                                            team_data.get("name"),
                                            team_data.get("abbreviation")
                                        ]
                                        game_teams.extend([name for name in team_names if name])
                            
                            # Also check scoreboard info for team names
                            if "scoreboard_info" in game:
                                scoreboard_info = game["scoreboard_info"]
                                event_name = scoreboard_info.get("event_name", "")
                                # Parse team names from event name (e.g., "Team A at Team B")
                                if " at " in event_name:
                                    away_team, home_team = event_name.split(" at ", 1)
                                    game_teams.extend([away_team.strip(), home_team.strip()])
                            
                            # Check if any team matches the search term (case-insensitive)
                            team_match = any(
                                team.lower() in game_team.lower() 
                                for game_team in game_teams 
                                if game_team
                            )
                            
                            if team_match:
                                matching_games.append(game)
                        else:
                            matching_games.append(game)
                    
                    # Move to next date
                    current_date += timedelta(days=1)
                    
                except Exception as e:
                    logger.warning("Failed to fetch games for date", date=current_date.isoformat(), error=str(e))
                    current_date += timedelta(days=1)
                    continue
            
            # Apply limit to final results
            matching_games = matching_games[:limit]
            
            logger.info(f"Search completed: found {len(matching_games)} matching games", 
                       sport=sport, team=team, limit=limit)
            
            return matching_games
            
        except Exception as e:
            logger.error("Failed to search historical games", sport=sport, team=team, error=str(e))
            raise


# Convenience function for quick usage
async def get_stats_engine() -> StatsEngine:
    """Get a configured StatsEngine instance."""
    return StatsEngine()
