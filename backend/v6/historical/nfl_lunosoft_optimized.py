"""
Optimized NFL Historical Data Ingestion using Lunosoft API

Switching from ESPN to Lunosoft API because:
- ESPN API returns 500 errors for historical NFL data
- ESPN doesn't provide odds data (only game metadata)
- Lunosoft API is proven working with actual odds data
- Database already configured for Lunosoft data structure

Features:
- Lunosoft API integration for NFL odds
- Enhanced bulk inserts (300 records per query)
- Transaction support
- Parallel batch processing
- Index optimization
- SQLite compatibility
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import structlog
import json

from sqlalchemy import text
from .database import HistoricalOddsDatabase

logger = structlog.get_logger(__name__)


class IngestionStatus(Enum):
    """Ingestion job status tracking."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class NFLIngestionJob:
    """NFL ingestion job definition."""
    season_year: int
    week: int
    book_id: int
    book_name: str
    status: IngestionStatus = IngestionStatus.PENDING
    error_message: Optional[str] = None
    attempts: int = 0
    last_attempt: Optional[datetime] = None
    records_processed: int = 0


class NFLLunosoftOptimizedIngestor:
    """
    Optimized NFL data ingestion using Lunosoft API with bulk operations.
    
    Using proven Lunosoft API instead of ESPN for actual odds data.
    """
    
    def __init__(self, database: HistoricalOddsDatabase):
        self.database = database
        self.batch_size = 300  # Optimal for SQLite/PostgreSQL
        self.max_workers = 4   # Parallel batch processing
        self.max_retries = 3
        self.api_delay = 1.0   # Rate limiting for Lunosoft API
        
        # Lunosoft API configuration
        self.lunosoft_base_url = "https://www.lunosoftware.com/sportsData/SportsDataService.svc"
        
        # Sport mapping for Lunosoft
        self.sport_mapping = {
            "americanfootball_nfl": 2,  # NFL sport ID
        }
        
        # Sportsbook names mapping
        self.book_names = {
            83: "DraftKings", 85: "BetRivers", 87: "BetMGM",
            88: "Unibet", 89: "FanDuel", 94: "Hard Rock"
        }
    
    async def ensure_progress_table(self):
        """Create NFL-specific progress tracking table."""
        is_sqlite = "sqlite" in self.database.database_url.lower()
        
        if is_sqlite:
            sql = """
            CREATE TABLE IF NOT EXISTS nfl_lunosoft_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                season_year INTEGER NOT NULL,
                week INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                book_name VARCHAR(100) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                error_message TEXT,
                attempts INTEGER DEFAULT 0,
                last_attempt TIMESTAMP,
                records_processed INTEGER DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(season_year, week, book_id)
            )
            """
        else:
            sql = """
            CREATE TABLE IF NOT EXISTS nfl_lunosoft_progress (
                id BIGSERIAL PRIMARY KEY,
                season_year INTEGER NOT NULL,
                week INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                book_name VARCHAR(100) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                error_message TEXT,
                attempts INTEGER DEFAULT 0,
                last_attempt TIMESTAMPTZ,
                records_processed INTEGER DEFAULT 0,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE(season_year, week, book_id)
            )
            """
        
        # Performance indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_nfl_lunosoft_progress_status ON nfl_lunosoft_progress(status, updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_nfl_lunosoft_progress_season_week ON nfl_lunosoft_progress(season_year, week)",
        ]
        
        try:
            async with self.database.engine.begin() as conn:
                await conn.execute(text(sql))
                for index_sql in indexes:
                    await conn.execute(text(index_sql))
            logger.info("NFL Lunosoft progress table created/verified")
            return True
        except Exception as e:
            logger.error("Failed to create NFL Lunosoft progress table", error=str(e))
            return False
    
    async def create_nfl_season_plan(
        self,
        season_year: int,
        book_ids: Optional[List[int]] = None
    ) -> List[NFLIngestionJob]:
        """Create comprehensive NFL season ingestion plan."""
        
        # Default sportsbooks for NFL
        if book_ids is None:
            book_ids = [83, 85, 87, 88, 89, 94]  # DraftKings, BetRivers, BetMGM, Unibet, FanDuel, Hard Rock
        
        jobs = []
        
        # NFL regular season: 18 weeks
        for week in range(1, 19):  # Weeks 1-18
            for book_id in book_ids:
                book_name = self.book_names.get(book_id, f"Book_{book_id}")
                
                job = NFLIngestionJob(
                    season_year=season_year,
                    week=week,
                    book_id=book_id,
                    book_name=book_name
                )
                jobs.append(job)
        
        logger.info(f"Created NFL Lunosoft season plan: {len(jobs)} total jobs",
                   season=season_year, weeks=18, books=len(book_ids))
        
        return jobs
    
    async def get_existing_progress(self) -> Set[Tuple[int, int, int]]:
        """Get existing progress to avoid reprocessing."""
        sql = """
        SELECT season_year, week, book_id 
        FROM nfl_lunosoft_progress 
        WHERE status = 'completed'
        """
        
        try:
            async with self.database.session_maker() as session:
                result = await session.execute(text(sql))
                completed = set()
                for row in result:
                    completed.add((row.season_year, row.week, row.book_id))
                return completed
        except Exception as e:
            logger.error("Failed to get existing NFL Lunosoft progress", error=str(e))
            return set()
    
    async def update_job_progress(self, job: NFLIngestionJob):
        """Update NFL job progress in database."""
        is_sqlite = "sqlite" in self.database.database_url.lower()
        now_func = "CURRENT_TIMESTAMP" if is_sqlite else "NOW()"
        
        sql = f"""
        INSERT INTO nfl_lunosoft_progress (
            season_year, week, book_id, book_name, status, error_message, 
            attempts, last_attempt, records_processed, updated_at
        ) VALUES (
            :season_year, :week, :book_id, :book_name, :status, :error_message,
            :attempts, :last_attempt, :records_processed, {now_func}
        )
        ON CONFLICT (season_year, week, book_id) 
        DO UPDATE SET 
            status = EXCLUDED.status,
            error_message = EXCLUDED.error_message,
            attempts = EXCLUDED.attempts,
            last_attempt = EXCLUDED.last_attempt,
            records_processed = EXCLUDED.records_processed,
            updated_at = {now_func}
        """
        
        try:
            async with self.database.session_maker() as session:
                await session.execute(text(sql), {
                    "season_year": job.season_year,
                    "week": job.week,
                    "book_id": job.book_id,
                    "book_name": job.book_name,
                    "status": job.status.value,
                    "error_message": job.error_message,
                    "attempts": job.attempts,
                    "last_attempt": job.last_attempt,
                    "records_processed": job.records_processed
                })
                await session.commit()
        except Exception as e:
            logger.error("Failed to update NFL job progress", error=str(e))
    
    async def fetch_lunosoft_nfl_week(self, season_year: int, week: int, book_id: int) -> List[Dict[str, Any]]:
        """Fetch NFL week odds data from Lunosoft API."""
        try:
            sport_id = self.sport_mapping["americanfootball_nfl"]
            
            # Build Lunosoft URL with week parameter
            url = f"{self.lunosoft_base_url}/gamesOddsForDateWeek/{sport_id}?week={week}&sportsbookIDList={book_id}"
            
            logger.info(f"Fetching Lunosoft NFL odds", season=season_year, week=week, book_id=book_id, url=url)
            
            # Use LunosoftClient for API calls
            from streamers.lunosoft import LunosoftClient
            
            client = LunosoftClient()
            await client.connect()
            
            try:
                response = await client._get_json(url)
                
                if not response:
                    logger.info(f"No response from Lunosoft API", season=season_year, week=week, book_id=book_id)
                    return []
                
                # Extract games from Lunosoft response
                games = response if isinstance(response, list) else response.get('games', [])
                
                logger.info(f"Fetched {len(games)} games from Lunosoft", 
                           season=season_year, week=week, book_id=book_id)
                
                return games
                
            finally:
                await client.disconnect()
                
        except Exception as e:
            logger.error("Failed to fetch Lunosoft NFL data", 
                        season=season_year, week=week, book_id=book_id, error=str(e))
            raise
    
    async def transform_lunosoft_to_odds_format(
        self, 
        games: List[Dict[str, Any]], 
        job: NFLIngestionJob
    ) -> List[Dict[str, Any]]:
        """Transform Lunosoft data to odds format for bulk insertion."""
        transformed_data = []
        
        for game in games:
            try:
                # Extract game information from Lunosoft response
                home_team = game.get('HomeTeamName', game.get('HomeTeamFullName', ''))
                away_team = game.get('AwayTeamName', game.get('AwayTeamFullName', ''))
                commence_time = game.get('StartTime')
                game_id = game.get('GameID', '')
                
                if not home_team or not away_team:
                    continue
                
                # Extract odds data
                odds_markets = game.get('Odds', [])
                
                if odds_markets:  # Only process if odds data exists
                    for market in odds_markets:
                        # Determine market type based on odds structure
                        market_type = "moneyline"
                        if market.get('HomeLine') is not None or market.get('AwayLine') is not None:
                            market_type = "spreads"
                        elif market.get('HomeTotal') is not None or market.get('AwayTotal') is not None:
                            market_type = "totals"
                        
                        transformed = {
                            "sport": "americanfootball_nfl",
                            "event_id": str(game_id),
                            "home_team": home_team,
                            "away_team": away_team,
                            "book_name": job.book_name,
                            "book_id": job.book_id,
                            "market_type": market_type,
                            "commence_time": commence_time,
                            "market_data": {
                                "lunosoft_data": game,
                                "market": market,
                                "source": "lunosoft_nfl_historical",
                                "season_year": job.season_year,
                                "week": job.week,
                                "collection_timestamp": datetime.utcnow().isoformat()
                            }
                        }
                        transformed_data.append(transformed)
                
            except Exception as e:
                logger.warning("Failed to transform Lunosoft game", 
                             game_id=game.get('GameID', 'unknown'), error=str(e))
                continue
        
        return transformed_data
    
    async def bulk_insert_with_transaction(self, odds_data: List[Dict[str, Any]]) -> bool:
        """Enhanced bulk insert with transaction and SQLite compatibility."""
        if not odds_data:
            return True
        
        try:
            async with self.database.session_maker() as session:
                # Start transaction
                await session.begin()
                
                try:
                    # Process in batches for memory efficiency
                    total_inserted = 0
                    is_sqlite = "sqlite" in self.database.database_url.lower()
                    
                    for i in range(0, len(odds_data), self.batch_size):
                        batch = odds_data[i:i + self.batch_size]
                        
                        # Enhanced bulk insert with conflict handling
                        if is_sqlite:
                            # SQLite version with JSON text
                            insert_sql = """
                            INSERT OR REPLACE INTO historical_odds (
                                sport, event_id, home_team, away_team, book_name, book_id,
                                market_type, market_data, commence_time
                            ) VALUES (
                                :sport, :event_id, :home_team, :away_team, :book_name, :book_id,
                                :market_type, :market_data, :commence_time
                            )
                            """
                            # Convert market_data to JSON string for SQLite
                            for record in batch:
                                record['market_data'] = json.dumps(record['market_data'])
                        else:
                            # PostgreSQL version with JSONB
                            insert_sql = """
                            INSERT INTO historical_odds (
                                sport, event_id, home_team, away_team, book_name, book_id,
                                market_type, market_data, commence_time
                            ) VALUES (
                                :sport, :event_id, :home_team, :away_team, :book_name, :book_id,
                                :market_type, :market_data::jsonb, :commence_time::timestamptz
                            )
                            ON CONFLICT (sport, event_id, book_name, market_type) 
                            DO UPDATE SET
                                market_data = EXCLUDED.market_data,
                                updated_at = NOW()
                            """
                        
                        await session.execute(text(insert_sql), batch)
                        total_inserted += len(batch)
                        
                        logger.debug(f"Bulk inserted batch of {len(batch)} records")
                    
                    # Commit transaction
                    await session.commit()
                    
                    logger.info(f"Successfully bulk inserted {total_inserted} NFL odds records")
                    return True
                    
                except Exception as e:
                    await session.rollback()
                    logger.error("Bulk insert transaction failed", error=str(e))
                    raise
                    
        except Exception as e:
            logger.error("Failed to bulk insert NFL odds data", error=str(e))
            return False
    
    async def process_nfl_job(self, job: NFLIngestionJob) -> bool:
        """Process a single NFL ingestion job with Lunosoft API."""
        job.status = IngestionStatus.IN_PROGRESS
        job.attempts += 1
        job.last_attempt = datetime.utcnow()
        
        try:
            # Fetch Lunosoft odds data
            games = await self.fetch_lunosoft_nfl_week(job.season_year, job.week, job.book_id)
            
            if not games:
                logger.info(f"No Lunosoft games found for NFL week", 
                           season=job.season_year, week=job.week, book=job.book_name)
                job.status = IngestionStatus.SKIPPED
                job.records_processed = 0
                await self.update_job_progress(job)
                return True
            
            # Transform to odds format
            odds_data = await self.transform_lunosoft_to_odds_format(games, job)
            
            if not odds_data:
                logger.info(f"No odds data generated for NFL week", 
                           season=job.season_year, week=job.week, book=job.book_name)
                job.status = IngestionStatus.SKIPPED
                job.records_processed = 0
                await self.update_job_progress(job)
                return True
            
            # Bulk insert with transaction optimization
            success = await self.bulk_insert_with_transaction(odds_data)
            
            if success:
                job.status = IngestionStatus.COMPLETED
                job.records_processed = len(odds_data)
                logger.info(f"Successfully processed NFL job", 
                           season=job.season_year, week=job.week, 
                           book=job.book_name, records=len(odds_data))
            else:
                raise Exception("Failed to bulk insert NFL odds data")
            
        except Exception as e:
            job.error_message = str(e)
            if job.attempts >= self.max_retries:
                job.status = IngestionStatus.FAILED
                logger.error(f"NFL job failed after {job.attempts} attempts", 
                           season=job.season_year, week=job.week,
                           book=job.book_name, error=str(e))
            else:
                job.status = IngestionStatus.PENDING
                logger.warning(f"NFL job failed, will retry", 
                             season=job.season_year, week=job.week,
                             book=job.book_name, attempt=job.attempts, error=str(e))
        
        await self.update_job_progress(job)
        return job.status == IngestionStatus.COMPLETED
    
    async def execute_parallel_ingestion(
        self,
        jobs: List[NFLIngestionJob],
        resume: bool = True
    ) -> Dict[str, Any]:
        """Execute NFL ingestion with parallel batch processing."""
        
        # Filter completed jobs if resuming
        if resume:
            completed = await self.get_existing_progress()
            pending_jobs = [
                job for job in jobs 
                if (job.season_year, job.week, job.book_id) not in completed
            ]
            logger.info(f"Resuming NFL Lunosoft ingestion: {len(pending_jobs)} pending jobs out of {len(jobs)} total")
        else:
            pending_jobs = jobs
            logger.info(f"Starting fresh NFL Lunosoft ingestion: {len(pending_jobs)} jobs")
        
        # Execute with parallel batch processing
        completed_count = 0
        failed_count = 0
        skipped_count = 0
        total_records = 0
        start_time = time.time()
        
        # Process jobs in parallel batches
        for i in range(0, len(pending_jobs), self.max_workers):
            batch = pending_jobs[i:i + self.max_workers]
            
            # Process batch concurrently
            tasks = [self.process_nfl_job(job) for job in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    failed_count += 1
                    logger.error(f"NFL job processing exception", error=str(result))
                elif result:
                    completed_count += 1
                else:
                    failed_count += 1
            
            # Rate limiting between batches
            if i + self.max_workers < len(pending_jobs):
                await asyncio.sleep(self.api_delay)
            
            # Progress logging
            processed = i + len(batch)
            progress = (processed / len(pending_jobs)) * 100
            elapsed = time.time() - start_time
            eta = (elapsed / processed) * (len(pending_jobs) - processed) if processed > 0 else 0
            
            logger.info(f"NFL Lunosoft ingestion progress: {processed}/{len(pending_jobs)} ({progress:.1f}%) - ETA: {eta/60:.1f}min")
        
        duration = time.time() - start_time
        summary = {
            "total_jobs": len(jobs),
            "processed_jobs": len(pending_jobs),
            "completed": completed_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "total_records": total_records,
            "duration_minutes": duration / 60,
            "records_per_minute": total_records / (duration / 60) if duration > 0 else 0,
            "success_rate": (completed_count / len(pending_jobs)) * 100 if pending_jobs else 0
        }
        
        logger.info("NFL Lunosoft ingestion completed", **summary)
        return summary


# Utility function for NFL ingestion
async def ingest_nfl_season_lunosoft_optimized(
    database: HistoricalOddsDatabase,
    season_year: int,
    book_ids: Optional[List[int]] = None,
    resume: bool = True
) -> Dict[str, Any]:
    """Ingest entire NFL season with optimized Lunosoft bulk operations."""
    
    ingestor = NFLLunosoftOptimizedIngestor(database)
    await ingestor.ensure_progress_table()
    
    jobs = await ingestor.create_nfl_season_plan(
        season_year=season_year,
        book_ids=book_ids
    )
    
    return await ingestor.execute_parallel_ingestion(jobs, resume=resume)


if __name__ == "__main__":
    print("🏈 NFL LUNOSOFT OPTIMIZED INGESTION")
    print("Using proven Lunosoft API for actual NFL odds data")
