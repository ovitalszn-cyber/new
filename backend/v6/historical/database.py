"""
Historical odds database for persistent storage.

This module handles writing odds data to PostgreSQL/TimescaleDB for historical analysis.
Separate from Redis cache which is ephemeral and gets cleared regularly.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import structlog
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

logger = structlog.get_logger()


class HistoricalOddsDatabase:
    """
    Persistent storage for historical odds data.
    
    Architecture:
    - Redis: Real-time cache (cleared regularly)
    - PostgreSQL: Historical data (never cleared, append-only)
    """
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.session_maker = None
        self._connected = False
    
    async def connect(self):
        """Initialize database connection."""
        try:
            # For SQLite/aiosqlite we must not pass pool_size/max_overflow
            is_sqlite = "sqlite" in self.database_url.lower()

            if is_sqlite:
                self.engine = create_async_engine(
                    self.database_url,
                    pool_pre_ping=True,
                    echo=False,
                )
            else:
                self.engine = create_async_engine(
                    self.database_url,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    echo=False,
                )
            
            self.session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            self._connected = True
            logger.info("Connected to historical odds database")
            return True
            
        except Exception as e:
            logger.error("Failed to connect to historical database", error=str(e))
            self._connected = False
            return False
    
    async def disconnect(self):
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()
            self._connected = False
            logger.info("Disconnected from historical odds database")
    
    async def create_tables(self):
        """Create historical odds tables if they don't exist."""
        # Check if using SQLite for compatibility
        is_sqlite = "sqlite" in self.database_url.lower()
        
        if is_sqlite:
            sql_statements = [
                """
                CREATE TABLE IF NOT EXISTS historical_odds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    captured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    sport VARCHAR(100) NOT NULL,
                    event_id VARCHAR(255) NOT NULL,
                    home_team VARCHAR(255) NOT NULL,
                    away_team VARCHAR(255) NOT NULL,
                    commence_time TIMESTAMP,
                    book_name VARCHAR(100) NOT NULL,
                    book_id INTEGER,
                    market_type VARCHAR(50) NOT NULL,
                    market_data TEXT NOT NULL,
                    source VARCHAR(50) NOT NULL DEFAULT 'kashrock'
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS historical_player_props (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    captured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    sport VARCHAR(100) NOT NULL,
                    event_id VARCHAR(255) NOT NULL,
                    game_id INTEGER,
                    player_name VARCHAR(255) NOT NULL,
                    player_team VARCHAR(100),
                    stat_type VARCHAR(100) NOT NULL,
                    stat_value DECIMAL(10, 2),
                    direction VARCHAR(20),
                    odds INTEGER,
                    book_name VARCHAR(100) NOT NULL,
                    book_id INTEGER,
                    sportsbook_id INTEGER,
                    prop_data TEXT NOT NULL,
                    source VARCHAR(50) NOT NULL DEFAULT 'kashrock'
                )
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_historical_odds_sport_time 
                    ON historical_odds(sport, captured_at DESC)
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_historical_odds_event 
                    ON historical_odds(event_id, captured_at DESC)
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_historical_odds_book 
                    ON historical_odds(book_name, captured_at DESC)
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_historical_player_props_sport_time 
                    ON historical_player_props(sport, captured_at DESC)
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_historical_player_props_player 
                    ON historical_player_props(player_name, captured_at DESC)
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_historical_player_props_stat 
                    ON historical_player_props(stat_type, captured_at DESC)
                """
                ,
                """
                CREATE TABLE IF NOT EXISTS nba_player_boxscores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sport TEXT NOT NULL,
                    game_id INTEGER NOT NULL,
                    game_date TIMESTAMP,
                    season_year INTEGER,
                    season_type TEXT,
                    team_id INTEGER,
                    team_name TEXT,
                    team_key TEXT,
                    alignment TEXT,
                    player_id INTEGER,
                    player_name TEXT,
                    position TEXT,
                    minutes REAL,
                    total_seconds INTEGER,
                    points REAL,
                    rebounds_offensive REAL,
                    rebounds_defensive REAL,
                    rebounds_total REAL,
                    assists REAL,
                    steals REAL,
                    blocked_shots REAL,
                    turnovers REAL,
                    personal_fouls REAL,
                    flagrant_fouls REAL,
                    technical_fouls_player REAL,
                    field_goals_attempted REAL,
                    field_goals_made REAL,
                    field_goals_percentage TEXT,
                    three_point_field_goals_attempted REAL,
                    three_point_field_goals_made REAL,
                    three_point_field_goals_percentage TEXT,
                    free_throws_attempted REAL,
                    free_throws_made REAL,
                    free_throws_percentage TEXT,
                    plus_minus REAL,
                    started_game BOOLEAN,
                    games_started INTEGER,
                    on_court BOOLEAN,
                    fouled_out BOOLEAN,
                    ejected BOOLEAN,
                    raw_player_json TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS esports_matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sport TEXT NOT NULL,
                    discipline TEXT NOT NULL,
                    match_id INTEGER NOT NULL,
                    slug TEXT,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    team1_id INTEGER,
                    team1_name TEXT,
                    team2_id INTEGER,
                    team2_name TEXT,
                    winner_team_id INTEGER,
                    loser_team_id INTEGER,
                    team1_score INTEGER,
                    team2_score INTEGER,
                    bo_type INTEGER,
                    status TEXT,
                    tournament_id INTEGER,
                    tier TEXT,
                    raw_stats_json TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(sport, match_id)
                )
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_nba_player_boxscores_game 
                    ON nba_player_boxscores(game_id, team_id, player_id)
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_nba_player_boxscores_date 
                    ON nba_player_boxscores(game_date)
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_esports_matches_discipline_date 
                    ON esports_matches(discipline, start_date)
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_esports_matches_tournament 
                    ON esports_matches(tournament_id)
                """
            ]
        else:
            # Original PostgreSQL schema
            sql_statements = [
                """
                CREATE TABLE IF NOT EXISTS historical_odds (
                    id BIGSERIAL PRIMARY KEY,
                    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    sport VARCHAR(100) NOT NULL,
                    event_id VARCHAR(255) NOT NULL,
                    home_team VARCHAR(255) NOT NULL,
                    away_team VARCHAR(255) NOT NULL,
                    commence_time TIMESTAMPTZ,
                    book_name VARCHAR(100) NOT NULL,
                    book_id INTEGER,
                    market_type VARCHAR(50) NOT NULL,
                    market_data JSONB NOT NULL,
                    source VARCHAR(50) NOT NULL DEFAULT 'kashrock'
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS historical_player_props (
                    id BIGSERIAL PRIMARY KEY,
                    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    sport VARCHAR(100) NOT NULL,
                    event_id VARCHAR(255) NOT NULL,
                    game_id INTEGER,
                    player_name VARCHAR(255) NOT NULL,
                    player_team VARCHAR(100),
                    stat_type VARCHAR(100) NOT NULL,
                    stat_value DECIMAL(10, 2),
                    direction VARCHAR(20),
                    odds INTEGER,
                    book_name VARCHAR(100) NOT NULL,
                    book_id INTEGER,
                    sportsbook_id INTEGER,
                    prop_data JSONB NOT NULL,
                    source VARCHAR(50) NOT NULL DEFAULT 'kashrock'
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS esports_matches (
                    id BIGSERIAL PRIMARY KEY,
                    sport TEXT NOT NULL,
                    discipline TEXT NOT NULL,
                    match_id INTEGER NOT NULL,
                    slug TEXT,
                    start_date TIMESTAMPTZ NOT NULL,
                    end_date TIMESTAMPTZ,
                    team1_id INTEGER,
                    team1_name TEXT,
                    team2_id INTEGER,
                    team2_name TEXT,
                    winner_team_id INTEGER,
                    loser_team_id INTEGER,
                    team1_score INTEGER,
                    team2_score INTEGER,
                    bo_type INTEGER,
                    status TEXT,
                    tournament_id INTEGER,
                    tier TEXT,
                    raw_stats_json JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE(sport, match_id)
                )
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_historical_odds_sport_time 
                    ON historical_odds(sport, captured_at DESC)
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_historical_odds_event 
                    ON historical_odds(event_id, captured_at DESC)
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_historical_odds_book 
                    ON historical_odds(book_name, captured_at DESC)
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_historical_player_props_sport_time 
                    ON historical_player_props(sport, captured_at DESC)
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_historical_player_props_player 
                    ON historical_player_props(player_name, captured_at DESC)
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_historical_player_props_stat 
                    ON historical_player_props(stat_type, captured_at DESC)
                """
            ]
        
        try:
            async with self.engine.begin() as conn:
                for sql in sql_statements:
                    await conn.execute(text(sql))
            logger.info("Historical odds tables created/verified")
            return True
        except Exception as e:
            logger.error("Failed to create historical tables", error=str(e))
            return False
    
    async def store_odds_snapshot(
        self,
        sport: str,
        event_id: str,
        home_team: str,
        away_team: str,
        book_name: str,
        market_type: str,
        market_data: Dict[str, Any],
        commence_time: Optional[str] = None,
        book_id: Optional[int] = None
    ):
        """Store a single odds snapshot."""
        if not self._connected:
            logger.warning("Not connected to historical database")
            return False
        
        is_sqlite = "sqlite" in self.database_url.lower()
        
        if is_sqlite:
            # Convert JSON data to string for SQLite
            market_data_str = json.dumps(market_data)
            insert_sql = """
            INSERT INTO historical_odds (
                sport, event_id, home_team, away_team, book_name, book_id,
                market_type, market_data, commence_time
            ) VALUES (
                :sport, :event_id, :home_team, :away_team, :book_name, :book_id,
                :market_type, :market_data, :commence_time
            )
            """
        else:
            # PostgreSQL with JSONB
            insert_sql = """
            INSERT INTO historical_odds (
                sport, event_id, home_team, away_team, book_name, book_id,
                market_type, market_data, commence_time
            ) VALUES (
                :sport, :event_id, :home_team, :away_team, :book_name, :book_id,
                :market_type, :market_data::jsonb, :commence_time::timestamptz
            )
            """
            market_data_str = market_data
        
        try:
            async with self.session_maker() as session:
                await session.execute(
                    text(insert_sql),
                    {
                        "sport": sport,
                        "event_id": event_id,
                        "home_team": home_team,
                        "away_team": away_team,
                        "book_name": book_name,
                        "book_id": book_id,
                        "market_type": market_type,
                        "market_data": market_data_str,
                        "commence_time": commence_time
                    }
                )
                await session.commit()
            return True
        except Exception as e:
            logger.error("Failed to store odds snapshot", error=str(e))
            return False
    
    async def store_player_prop_snapshot(
        self,
        sport: str,
        event_id: str,
        player_name: str,
        stat_type: str,
        book_name: str,
        prop_data: Dict[str, Any],
        game_id: Optional[int] = None,
        player_team: Optional[str] = None,
        stat_value: Optional[float] = None,
        direction: Optional[str] = None,
        odds: Optional[int] = None,
        book_id: Optional[int] = None,
        sportsbook_id: Optional[int] = None
    ):
        """Store a single player prop snapshot."""
        if not self._connected:
            logger.warning("Not connected to historical database")
            return False
        
        insert_sql = """
        INSERT INTO historical_player_props (
            sport, event_id, game_id, player_name, player_team, stat_type,
            stat_value, direction, odds, book_name, book_id, sportsbook_id, prop_data
        ) VALUES (
            :sport, :event_id, :game_id, :player_name, :player_team, :stat_type,
            :stat_value, :direction, :odds, :book_name, :book_id, :sportsbook_id, :prop_data::jsonb
        )
        """
        
        try:
            async with self.session_maker() as session:
                await session.execute(
                    text(insert_sql),
                    {
                        "sport": sport,
                        "event_id": event_id,
                        "game_id": game_id,
                        "player_name": player_name,
                        "player_team": player_team,
                        "stat_type": stat_type,
                        "stat_value": stat_value,
                        "direction": direction,
                        "odds": odds,
                        "book_name": book_name,
                        "book_id": book_id,
                        "sportsbook_id": sportsbook_id,
                        "prop_data": prop_data
                    }
                )
                await session.commit()
            return True
        except Exception as e:
            logger.error("Failed to store player prop snapshot", error=str(e))
            return False
    
    async def bulk_store_odds(self, odds_list: List[Dict[str, Any]]):
        """Bulk insert odds snapshots for efficiency."""
        if not self._connected or not odds_list:
            return False
        
        insert_sql = """
        INSERT INTO historical_odds (
            sport, event_id, home_team, away_team, book_name, book_id,
            market_type, market_data, commence_time
        ) VALUES (
            :sport, :event_id, :home_team, :away_team, :book_name, :book_id,
            :market_type, :market_data::jsonb, :commence_time::timestamptz
        )
        """
        
        try:
            async with self.session_maker() as session:
                await session.execute(text(insert_sql), odds_list)
                await session.commit()
            logger.info(f"Bulk stored {len(odds_list)} odds snapshots")
            return True
        except Exception as e:
            logger.error("Failed to bulk store odds", error=str(e), count=len(odds_list))
            return False
    
    async def bulk_store_player_props(self, props_list: List[Dict[str, Any]]):
        """Bulk insert player prop snapshots for efficiency."""
        if not self._connected or not props_list:
            return False
        
        insert_sql = """
        INSERT INTO historical_player_props (
            sport, event_id, game_id, player_name, player_team, stat_type,
            stat_value, direction, odds, book_name, book_id, sportsbook_id, prop_data
        ) VALUES (
            :sport, :event_id, :game_id, :player_name, :player_team, :stat_type,
            :stat_value, :direction, :odds, :book_name, :book_id, :sportsbook_id, :prop_data::jsonb
        )
        """
        
        try:
            async with self.session_maker() as session:
                await session.execute(text(insert_sql), props_list)
                await session.commit()
            logger.info(f"Bulk stored {len(props_list)} player prop snapshots")
            return True
        except Exception as e:
            logger.error("Failed to bulk store player props", error=str(e), count=len(props_list))
            return False

    async def fetch_odds(
        self,
        sport: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        book_name: Optional[str] = None,
        event_id: Optional[str] = None,
        limit: int = 5000,
    ) -> List[Dict[str, Any]]:
        """Fetch historical odds rows with optional filters."""
        if not self._connected or not self.session_maker:
            logger.warning("Historical database not connected for fetch_odds")
            return []

        conditions = []
        params: Dict[str, Any] = {"limit": limit}
        if sport:
            conditions.append("sport = :sport")
            params["sport"] = sport
        if date_from:
            conditions.append("captured_at >= :date_from")
            params["date_from"] = date_from
        if date_to:
            conditions.append("captured_at <= :date_to")
            params["date_to"] = date_to
        if book_name:
            conditions.append("book_name = :book_name")
            params["book_name"] = book_name
        if event_id:
            conditions.append("event_id = :event_id")
            params["event_id"] = str(event_id)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = text(
            f"""
            SELECT captured_at, sport, event_id, home_team, away_team, commence_time,
                   book_name, book_id, market_type, market_data
            FROM historical_odds
            {where_clause}
            ORDER BY captured_at DESC
            LIMIT :limit
            """
        )

        async with self.session_maker() as session:
            result = await session.execute(query, params)
            rows = result.mappings().all()

        parsed_rows: List[Dict[str, Any]] = []
        for row in rows:
            record = dict(row)
            market_data = record.get("market_data")
            if isinstance(market_data, str):
                try:
                    record["market_data"] = json.loads(market_data)
                except json.JSONDecodeError:
                    pass
            parsed_rows.append(record)
        return parsed_rows

    async def fetch_player_props(
        self,
        sport: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        book_name: Optional[str] = None,
        limit: int = 5000,
    ) -> List[Dict[str, Any]]:
        """Fetch historical player props rows with optional filters."""
        if not self._connected or not self.session_maker:
            logger.warning("Historical database not connected for fetch_player_props")
            return []

        conditions = []
        params: Dict[str, Any] = {"limit": limit}
        if sport:
            conditions.append("sport = :sport")
            params["sport"] = sport
        if date_from:
            conditions.append("captured_at >= :date_from")
            params["date_from"] = date_from
        if date_to:
            conditions.append("captured_at <= :date_to")
            params["date_to"] = date_to
        if book_name:
            conditions.append("book_name = :book_name")
            params["book_name"] = book_name

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = text(
            f"""
            SELECT captured_at, sport, event_id, player_name, player_team, stat_type,
                   stat_value, direction, odds, book_name, book_id, sportsbook_id, prop_data
            FROM historical_player_props
            {where_clause}
            ORDER BY captured_at DESC
            LIMIT :limit
            """
        )

        async with self.session_maker() as session:
            result = await session.execute(query, params)
            rows = result.mappings().all()

        parsed_rows: List[Dict[str, Any]] = []
        for row in rows:
            record = dict(row)
            prop_data = record.get("prop_data")
            if isinstance(prop_data, str):
                try:
                    record["prop_data"] = json.loads(prop_data)
                except json.JSONDecodeError:
                    pass
            parsed_rows.append(record)
        return parsed_rows

    async def fetch_thescore_games(
        self,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch game rows from thescore_games table."""
        if not self._connected or not self.session_maker:
            logger.warning("Historical database not connected for fetch_thescore_games")
            return []

        sql = """
            SELECT *
            FROM thescore_games
            WHERE game_date <= datetime('now')
            ORDER BY game_date DESC
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            sql += " LIMIT :limit"
            params["limit"] = limit

        query = text(sql)

        async with self.session_maker() as session:
            result = await session.execute(query, params)
            return [dict(row) for row in result.mappings().all()]

    async def fetch_nba_player_boxscores(
        self,
        sport: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        team_id: Optional[int] = None,
        player_id: Optional[int] = None,
        game_id: Optional[int] = None,
        limit: int = 5000,
    ) -> List[Dict[str, Any]]:
        if not self._connected or not self.session_maker:
            logger.warning("Historical database not connected for fetch_nba_player_boxscores")
            return []

        conditions = []
        params: Dict[str, Any] = {"limit": limit}
        if sport:
            conditions.append("sport = :sport")
            params["sport"] = sport
        if date_from:
            conditions.append("game_date >= :date_from")
            params["date_from"] = date_from
        if date_to:
            conditions.append("game_date <= :date_to")
            params["date_to"] = date_to
        if team_id is not None:
            conditions.append("team_id = :team_id")
            params["team_id"] = team_id
        if player_id is not None:
            conditions.append("player_id = :player_id")
            params["player_id"] = player_id
        if game_id is not None:
            conditions.append("game_id = :game_id")
            params["game_id"] = game_id

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = text(
            f"""
            SELECT *
            FROM nba_player_boxscores
            {where_clause}
            ORDER BY game_date DESC, game_id, team_id, player_id
            LIMIT :limit
            """
        )

        async with self.session_maker() as session:
            result = await session.execute(query, params)
            return [dict(row) for row in result.mappings().all()]

    async def fetch_nfl_team_statistics(
        self,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch rows from nfl_team_stats_summary table (canonical team season stats)."""
        if not self._connected or not self.session_maker:
            logger.warning("Historical database not connected for fetch_nfl_team_statistics")
            return []

        sql = """
            SELECT * FROM nfl_team_stats_summary
            ORDER BY season_year DESC, team_id
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            sql += " LIMIT :limit"
            params["limit"] = limit

        query = text(sql)

        async with self.session_maker() as session:
            result = await session.execute(query, params)
            return [dict(row) for row in result.mappings().all()]

    async def fetch_realvg_team_stat_leaders(
        self,
        sport: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch rows from realvg_team_stat_leaders table with optional sport filter."""
        if not self._connected or not self.session_maker:
            logger.warning("Historical database not connected for fetch_realvg_team_stat_leaders")
            return []

        conditions = []
        params: Dict[str, Any] = {}
        if sport:
            conditions.append("sport = :sport")
            params["sport"] = sport

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        sql = f"""
            SELECT * FROM realvg_team_stat_leaders
            {where_clause}
            ORDER BY season_year DESC, sport, stat_id
        """

        if limit is not None:
            sql += " LIMIT :limit"
            params["limit"] = limit

        query = text(sql)

        async with self.session_maker() as session:
            result = await session.execute(query, params)
            return [dict(row) for row in result.mappings().all()]

    async def fetch_nfl_modeling_players(
        self,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch rows from nfl_modeling_players table."""
        if not self._connected or not self.session_maker:
            logger.warning("Historical database not connected for fetch_nfl_modeling_players")
            return []

        sql = """
            SELECT * FROM nfl_modeling_players
            ORDER BY team_id, name
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            sql += " LIMIT :limit"
            params["limit"] = limit

        query = text(sql)

        async with self.session_maker() as session:
            result = await session.execute(query, params)
            return [dict(row) for row in result.mappings().all()]
    async def fetch_esports_matches(
        self,
        discipline: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        match_id: Optional[int] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Fetch esports matches with optional filters."""
        if not self._connected or not self.session_maker:
            logger.warning("Historical database not connected for fetch_esports_matches")
            return []

        conditions = []
        params: Dict[str, Any] = {"limit": limit}

        if discipline:
            conditions.append("discipline = :discipline")
            params["discipline"] = discipline
        
        if date_from:
            # Note: start_date is stored as TEXT/string in SQLite, TIMESTAMPTZ in Postgres
            # We pass ISO format string which works for SQLite comparisons
            conditions.append("start_date >= :date_from")
            params["date_from"] = date_from.isoformat() if isinstance(date_from, datetime) else date_from
            
        if date_to:
            conditions.append("start_date <= :date_to")
            params["date_to"] = date_to.isoformat() if isinstance(date_to, datetime) else date_to

        if match_id is not None:
            conditions.append("match_id = :match_id")
            params["match_id"] = match_id

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        query = text(
            f"""
            SELECT *
            FROM esports_matches
            {where_clause}
            ORDER BY start_date DESC
            LIMIT :limit
            """
        )

        async with self.session_maker() as session:
            result = await session.execute(query, params)
            return [dict(row) for row in result.mappings().all()]

# Global instance
_historical_db: Optional[HistoricalOddsDatabase] = None


async def get_historical_db() -> HistoricalOddsDatabase:
    """Get or create the global historical database instance.
    
    Supports Railway deployment with volume-mounted database:
    - If HISTORICAL_DB_PATH env var is set, uses that path for SQLite
    - Otherwise falls back to config database_url
    """
    global _historical_db
    if _historical_db is None:
        import os
        from config import get_settings
        settings = get_settings()
        
        # Check for Railway volume-mounted database path
        historical_db_path = os.getenv("HISTORICAL_DB_PATH")
        if historical_db_path:
            # Use volume-mounted SQLite database (Railway deployment)
            database_url = f"sqlite+aiosqlite:///{historical_db_path}"
            logger.info(
                "Using volume-mounted historical database",
                path=historical_db_path,
                url=database_url
            )
        else:
            # Use configured database URL (local development or PostgreSQL)
            database_url = settings.database_url
            logger.info(
                "Using configured historical database",
                url=database_url
            )
        
        _historical_db = HistoricalOddsDatabase(database_url)
        await _historical_db.connect()
        await _historical_db.create_tables()
    return _historical_db


async def shutdown_historical_db():
    """Shutdown the historical database connection."""
    global _historical_db
    if _historical_db is not None:
        await _historical_db.disconnect()
        _historical_db = None
