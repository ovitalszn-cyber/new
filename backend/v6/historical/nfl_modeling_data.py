"""
NFL Modeling Data Collection System

Focus: Building comprehensive datasets for ML model training, not odds.

Data Sources:
1. ESPN API: Team rosters, player information, team details
2. Historical game results: From existing databases or APIs
3. Team statistics: Performance metrics for feature engineering

Features:
- Team roster information (age, experience, position)
- Historical game results and scores
- Team performance trends
- Player statistics for predictions
- Feature engineering ready datasets
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import structlog
from sqlalchemy import text
from .database import HistoricalOddsDatabase

logger = structlog.get_logger(__name__)


class NFLModelingDataCollector:
    """
    Collects NFL data specifically for machine learning model building.
    
    Focus on features like:
    - Team performance metrics
    - Player demographics and experience
    - Historical game results
    - Season trends and patterns
    """
    
    def __init__(self, database: HistoricalOddsDatabase):
        self.database = database
        self.espn_base_url = "https://site.web.api.espn.com/apis/site/v2/sports/football/nfl"
        self.espn_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    
    async def ensure_modeling_tables(self):
        """Create tables specifically for NFL modeling data."""
        is_sqlite = "sqlite" in self.database.database_url.lower()
        
        # Teams table for modeling
        teams_sql = """
        CREATE TABLE IF NOT EXISTS nfl_teams (
            id INTEGER PRIMARY KEY,
            espn_team_id INTEGER UNIQUE NOT NULL,
            team_name VARCHAR(100) NOT NULL,
            location VARCHAR(100),
            abbreviation VARCHAR(10),
            division VARCHAR(50),
            conference VARCHAR(50),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """ if is_sqlite else """
        CREATE TABLE IF NOT EXISTS nfl_teams (
            id SERIAL PRIMARY KEY,
            espn_team_id INTEGER UNIQUE NOT NULL,
            team_name VARCHAR(100) NOT NULL,
            location VARCHAR(100),
            abbreviation VARCHAR(10),
            division VARCHAR(50),
            conference VARCHAR(50),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
        
        # Players table for modeling
        players_sql = """
        CREATE TABLE IF NOT EXISTS nfl_players (
            id INTEGER PRIMARY KEY,
            espn_player_id INTEGER UNIQUE NOT NULL,
            team_id INTEGER,
            name VARCHAR(100) NOT NULL,
            position VARCHAR(10),
            age INTEGER,
            experience_years INTEGER,
            height VARCHAR(10),
            weight INTEGER,
            college VARCHAR(100),
            draft_year INTEGER,
            draft_round INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES nfl_teams(espn_team_id)
        )
        """ if is_sqlite else """
        CREATE TABLE IF NOT EXISTS nfl_players (
            id SERIAL PRIMARY KEY,
            espn_player_id INTEGER UNIQUE NOT NULL,
            team_id INTEGER,
            name VARCHAR(100) NOT NULL,
            position VARCHAR(10),
            age INTEGER,
            experience_years INTEGER,
            height VARCHAR(10),
            weight INTEGER,
            college VARCHAR(100),
            draft_year INTEGER,
            draft_round INTEGER,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            FOREIGN KEY (team_id) REFERENCES nfl_teams(espn_team_id)
        )
        """
        
        # Games table for modeling
        games_sql = """
        CREATE TABLE IF NOT EXISTS nfl_games (
            id INTEGER PRIMARY KEY,
            espn_game_id VARCHAR(50) UNIQUE NOT NULL,
            season_year INTEGER NOT NULL,
            week INTEGER NOT NULL,
            home_team_id INTEGER,
            away_team_id INTEGER,
            home_score INTEGER,
            away_score INTEGER,
            game_date TIMESTAMP,
            venue VARCHAR(100),
            attendance INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (home_team_id) REFERENCES nfl_teams(espn_team_id),
            FOREIGN KEY (away_team_id) REFERENCES nfl_teams(espn_team_id)
        )
        """ if is_sqlite else """
        CREATE TABLE IF NOT EXISTS nfl_games (
            id SERIAL PRIMARY KEY,
            espn_game_id VARCHAR(50) UNIQUE NOT NULL,
            season_year INTEGER NOT NULL,
            week INTEGER NOT NULL,
            home_team_id INTEGER,
            away_team_id INTEGER,
            home_score INTEGER,
            away_score INTEGER,
            game_date TIMESTAMPTZ,
            venue VARCHAR(100),
            attendance INTEGER,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            FOREIGN KEY (home_team_id) REFERENCES nfl_teams(espn_team_id),
            FOREIGN KEY (away_team_id) REFERENCES nfl_teams(espn_team_id)
        )
        """
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_nfl_teams_espn_id ON nfl_teams(espn_team_id)",
            "CREATE INDEX IF NOT EXISTS idx_nfl_players_team_id ON nfl_players(team_id)",
            "CREATE INDEX IF NOT EXISTS idx_nfl_players_position ON nfl_players(position)",
            "CREATE INDEX IF NOT EXISTS idx_nfl_games_season_week ON nfl_games(season_year, week)",
            "CREATE INDEX IF NOT EXISTS idx_nfl_games_teams ON nfl_games(home_team_id, away_team_id)",
        ]
        
        try:
            async with self.database.engine.begin() as conn:
                for sql in [teams_sql, players_sql, games_sql]:
                    await conn.execute(text(sql))
                for index_sql in indexes:
                    await conn.execute(text(index_sql))
            logger.info("NFL modeling tables created/verified")
            return True
        except Exception as e:
            logger.error("Failed to create NFL modeling tables", error=str(e))
            return False
    
    async def collect_nfl_teams(self) -> List[Dict[str, Any]]:
        """Collect all NFL team information from ESPN."""
        try:
            url = f"{self.espn_base_url}/teams"
            
            logger.info("Collecting NFL teams from ESPN")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.espn_headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    teams = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])
                    
                    team_data = []
                    for team_info in teams:
                        team = team_info['team']
                        
                        # Extract division and conference from group info
                        group = team_info.get('group', {})
                        division = group.get('name', '')
                        parent_group = group.get('parent', {})
                        conference = parent_group.get('name', '') if parent_group else ''
                        
                        team_record = {
                            'espn_team_id': team.get('id'),
                            'team_name': team.get('displayName', ''),
                            'location': team.get('location', ''),
                            'abbreviation': team.get('abbreviation', ''),
                            'division': division,
                            'conference': conference
                        }
                        team_data.append(team_record)
                    
                    logger.info(f"Collected {len(team_data)} NFL teams")
                    return team_data
                    
        except Exception as e:
            logger.error("Failed to collect NFL teams", error=str(e))
            return []
    
    async def store_nfl_teams(self, teams: List[Dict[str, Any]]) -> bool:
        """Store NFL teams in database with bulk insert."""
        if not teams:
            return True
        
        try:
            is_sqlite = "sqlite" in self.database.database_url.lower()
            
            if is_sqlite:
                insert_sql = """
                INSERT OR REPLACE INTO nfl_teams (
                    espn_team_id, team_name, location, abbreviation, division, conference
                ) VALUES (
                    :espn_team_id, :team_name, :location, :abbreviation, :division, :conference
                )
                """
            else:
                insert_sql = """
                INSERT INTO nfl_teams (
                    espn_team_id, team_name, location, abbreviation, division, conference
                ) VALUES (
                    :espn_team_id, :team_name, :location, :abbreviation, :division, :conference
                )
                ON CONFLICT (espn_team_id) 
                DO UPDATE SET
                    team_name = EXCLUDED.team_name,
                    location = EXCLUDED.location,
                    abbreviation = EXCLUDED.abbreviation,
                    division = EXCLUDED.division,
                    conference = EXCLUDED.conference
                """
            
            async with self.database.session_maker() as session:
                await session.execute(text(insert_sql), teams)
                await session.commit()
                
            logger.info(f"Stored {len(teams)} NFL teams")
            return True
            
        except Exception as e:
            logger.error("Failed to store NFL teams", error=str(e))
            return False
    
    async def collect_team_rosters(self, team_id: int) -> List[Dict[str, Any]]:
        """Collect roster information for a specific team."""
        try:
            url = f"{self.espn_base_url}/teams/{team_id}/roster"
            
            logger.info(f"Collecting roster for team {team_id}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.espn_headers) as response:
                    if response.status != 200:
                        logger.warning(f"Roster data unavailable for team {team_id}: {response.status}")
                        return []
                    
                    data = await response.json()
                    athletes = data.get('athletes', [])
                    
                    roster_data = []
                    for athlete_info in athletes:
                        # Handle the athlete data structure properly
                        if isinstance(athlete_info, dict) and 'athlete' in athlete_info:
                            athlete = athlete_info['athlete']
                        elif isinstance(athlete_info, dict):
                            athlete = athlete_info
                        else:
                            continue
                        
                        # Extract player information
                        player_record = {
                            'espn_player_id': athlete.get('id'),
                            'team_id': team_id,
                            'name': athlete.get('displayName', ''),
                            'position': athlete.get('position', {}).get('abbreviation', ''),
                            'age': athlete.get('age'),
                            'experience_years': athlete.get('experience', {}).get('years') if athlete.get('experience') else None,
                            'height': athlete.get('height'),
                            'weight': athlete.get('weight'),
                            'college': athlete.get('college', {}).get('displayName') if athlete.get('college') else None,
                            'draft_year': athlete.get('draft', {}).get('year') if athlete.get('draft') else None,
                            'draft_round': athlete.get('draft', {}).get('round') if athlete.get('draft') else None,
                        }
                        roster_data.append(player_record)
                    
                    logger.info(f"Collected {len(roster_data)} players for team {team_id}")
                    return roster_data
                    
        except Exception as e:
            logger.error(f"Failed to collect roster for team {team_id}", error=str(e))
            return []
    
    async def store_nfl_players(self, players: List[Dict[str, Any]]) -> bool:
        """Store NFL players in database with bulk insert."""
        if not players:
            return True
        
        try:
            is_sqlite = "sqlite" in self.database.database_url.lower()
            
            if is_sqlite:
                insert_sql = """
                INSERT OR REPLACE INTO nfl_players (
                    espn_player_id, team_id, name, position, age, experience_years,
                    height, weight, college, draft_year, draft_round
                ) VALUES (
                    :espn_player_id, :team_id, :name, :position, :age, :experience_years,
                    :height, :weight, :college, :draft_year, :draft_round
                )
                """
            else:
                insert_sql = """
                INSERT INTO nfl_players (
                    espn_player_id, team_id, name, position, age, experience_years,
                    height, weight, college, draft_year, draft_round
                ) VALUES (
                    :espn_player_id, :team_id, :name, :position, :age, :experience_years,
                    :height, :weight, :college, :draft_year, :draft_round
                )
                ON CONFLICT (espn_player_id) 
                DO UPDATE SET
                    team_id = EXCLUDED.team_id,
                    name = EXCLUDED.name,
                    position = EXCLUDED.position,
                    age = EXCLUDED.age,
                    experience_years = EXCLUDED.experience_years,
                    height = EXCLUDED.height,
                    weight = EXCLUDED.weight,
                    college = EXCLUDED.college,
                    draft_year = EXCLUDED.draft_year,
                    draft_round = EXCLUDED.draft_round
                """
            
            async with self.database.session_maker() as session:
                await session.execute(text(insert_sql), players)
                await session.commit()
                
            logger.info(f"Stored {len(players)} NFL players")
            return True
            
        except Exception as e:
            logger.error("Failed to store NFL players", error=str(e))
            return False
    
    async def collect_all_modeling_data(self) -> Dict[str, Any]:
        """Collect all NFL modeling data in an optimized workflow."""
        logger.info("Starting comprehensive NFL modeling data collection")
        
        start_time = datetime.now()
        results = {
            'teams_collected': 0,
            'players_collected': 0,
            'teams_stored': False,
            'players_stored': False,
            'duration_minutes': 0
        }
        
        try:
            # Step 1: Collect and store teams
            teams = await self.collect_nfl_teams()
            if teams:
                results['teams_collected'] = len(teams)
                results['teams_stored'] = await self.store_nfl_teams(teams)
            
            # Step 2: Collect rosters for all teams (with rate limiting)
            all_players = []
            for i, team in enumerate(teams, 1):
                team_id = team['espn_team_id']
                players = await self.collect_team_rosters(team_id)
                all_players.extend(players)
                
                # Rate limiting to avoid overwhelming ESPN API
                if i < len(teams):
                    await asyncio.sleep(0.5)
                
                logger.info(f"Collected rosters for {i}/{len(teams)} teams")
            
            # Step 3: Store all players
            if all_players:
                results['players_collected'] = len(all_players)
                results['players_stored'] = await self.store_nfl_players(all_players)
            
            results['duration_minutes'] = (datetime.now() - start_time).total_seconds() / 60
            
            logger.info("NFL modeling data collection completed", **results)
            return results
            
        except Exception as e:
            logger.error("NFL modeling data collection failed", error=str(e))
            return results


# Utility function
async def build_nfl_modeling_dataset(database: HistoricalOddsDatabase) -> Dict[str, Any]:
    """Build comprehensive NFL dataset for machine learning."""
    collector = NFLModelingDataCollector(database)
    await collector.ensure_modeling_tables()
    return await collector.collect_all_modeling_data()


if __name__ == "__main__":
    print("🏈 NFL MODELING DATA COLLECTION")
    print("Building datasets for machine learning models")
