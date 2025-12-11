"""
Historical Odds Batch Ingestion System

Standalone batch system for filling historical odds database with entire seasons of data.
Features:
- Progress tracking with resume capability
- Rate limiting across 38+ sportsbooks
- Bulk insert optimization
- Error handling without data loss
- Multi-sport season coverage
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import structlog

from sqlalchemy import text
from .database import HistoricalOddsDatabase
from streamers.lunosoft_books import LUNOSOFT_BOOK_STREAMERS

logger = structlog.get_logger(__name__)


class IngestionStatus(Enum):
    """Ingestion job status tracking."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class IngestionJob:
    """Individual ingestion job definition."""
    sport: str
    book_id: int
    book_name: str
    date: datetime
    status: IngestionStatus = IngestionStatus.PENDING
    error_message: Optional[str] = None
    attempts: int = 0
    last_attempt: Optional[datetime] = None
    records_processed: int = 0


class HistoricalOddsIngestor:
    """
    Batch ingestion system for historical odds data.
    
    Designed for populating entire seasons of data across multiple sportsbooks
    with guaranteed persistence and progress tracking.
    """
    
    def __init__(self, database: HistoricalOddsDatabase):
        self.database = database
        self.rate_limit_delay = 2.0  # Base delay between requests
        self.max_retries = 3
        self.batch_size = 100  # Records per bulk insert
        self.max_concurrent_books = 5  # Max concurrent sportsbooks
        
    async def ensure_progress_table(self):
        """Create progress tracking table if it doesn't exist."""
        # Check if using SQLite for compatibility
        is_sqlite = "sqlite" in self.database.database_url.lower()
        
        if is_sqlite:
            sql = """
            CREATE TABLE IF NOT EXISTS ingestion_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sport VARCHAR(100) NOT NULL,
                book_id INTEGER NOT NULL,
                book_name VARCHAR(100) NOT NULL,
                date DATE NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                error_message TEXT,
                attempts INTEGER DEFAULT 0,
                last_attempt TIMESTAMP,
                records_processed INTEGER DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(sport, book_id, date)
            )
            """
        else:
            sql = """
            CREATE TABLE IF NOT EXISTS ingestion_progress (
                id BIGSERIAL PRIMARY KEY,
                sport VARCHAR(100) NOT NULL,
                book_id INTEGER NOT NULL,
                book_name VARCHAR(100) NOT NULL,
                date DATE NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                error_message TEXT,
                attempts INTEGER DEFAULT 0,
                last_attempt TIMESTAMPTZ,
                records_processed INTEGER DEFAULT 0,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE(sport, book_id, date)
            )
            """
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_ingestion_progress_status ON ingestion_progress(status, updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_ingestion_progress_sport_date ON ingestion_progress(sport, date)",
            "CREATE INDEX IF NOT EXISTS idx_ingestion_progress_book ON ingestion_progress(book_id, status)"
        ]
        
        try:
            async with self.database.engine.begin() as conn:
                await conn.execute(text(sql))
                for index_sql in indexes:
                    await conn.execute(text(index_sql))
            logger.info("Progress tracking table created/verified")
            return True
        except Exception as e:
            logger.error("Failed to create progress table", error=str(e))
            return False
    
    async def create_ingestion_plan(
        self,
        sports: List[str],
        start_date: datetime,
        end_date: datetime,
        book_ids: Optional[List[int]] = None
    ) -> List[IngestionJob]:
        """
        Create comprehensive ingestion plan for seasons of data.
        
        Args:
            sports: List of sports to ingest (e.g., ['basketball_nba', 'americanfootball_nfl'])
            start_date: Start date for historical data
            end_date: End date for historical data
            book_ids: Specific book IDs to process (None = all available)
        
        Returns:
            List of ingestion jobs
        """
        if book_ids is None:
            book_ids = list(LUNOSOFT_BOOK_STREAMERS.keys())
        
        jobs = []
        current_date = start_date
        
        while current_date <= end_date:
            for sport in sports:
                for book_id in book_ids:
                    book_name = LUNOSOFT_BOOK_STREAMERS.get(book_id, {}).get('name', f'Book_{book_id}')
                    job = IngestionJob(
                        sport=sport,
                        book_id=book_id,
                        book_name=book_name,
                        date=current_date
                    )
                    jobs.append(job)
            
            current_date += timedelta(days=1)
        
        logger.info(f"Created ingestion plan: {len(jobs)} total jobs", 
                   sports=len(sports), 
                   days=(end_date - start_date).days + 1,
                   books=len(book_ids))
        
        return jobs
    
    async def get_existing_progress(self) -> Set[Tuple[str, int, datetime.date]]:
        """Get existing progress to avoid reprocessing."""
        sql = """
        SELECT sport, book_id, date 
        FROM ingestion_progress 
        WHERE status = 'completed'
        """
        
        try:
            async with self.database.session_maker() as session:
                result = await session.execute(text(sql))
                completed = set()
                for row in result:
                    completed.add((row.sport, row.book_id, row.date))
                return completed
        except Exception as e:
            logger.error("Failed to get existing progress", error=str(e))
            return set()
    
    async def update_job_progress(self, job: IngestionJob):
        """Update job progress in database."""
        sql = """
        INSERT INTO ingestion_progress (
            sport, book_id, book_name, date, status, error_message, 
            attempts, last_attempt, records_processed, updated_at
        ) VALUES (
            :sport, :book_id, :book_name, :date, :status, :error_message,
            :attempts, :last_attempt, :records_processed, NOW()
        )
        ON CONFLICT (sport, book_id, date) 
        DO UPDATE SET 
            status = EXCLUDED.status,
            error_message = EXCLUDED.error_message,
            attempts = EXCLUDED.attempts,
            last_attempt = EXCLUDED.last_attempt,
            records_processed = EXCLUDED.records_processed,
            updated_at = NOW()
        """
        
        try:
            async with self.database.session_maker() as session:
                await session.execute(text(sql), {
                    "sport": job.sport,
                    "book_id": job.book_id,
                    "book_name": job.book_name,
                    "date": job.date,
                    "status": job.status.value,
                    "error_message": job.error_message,
                    "attempts": job.attempts,
                    "last_attempt": job.last_attempt,
                    "records_processed": job.records_processed
                })
                await session.commit()
        except Exception as e:
            logger.error("Failed to update job progress", error=str(e))
    
    async def fetch_historical_odds(self, job: IngestionJob) -> List[Dict[str, Any]]:
        """Fetch historical odds for a specific job using Lunosoft API."""
        try:
            # Get sport mapping for Lunosoft API
            from streamers.lunosoft import LunosoftClient
            
            sport_map = {
                "basketball_nba": 4,
                "americanfootball_nfl": 2,
                "baseball_mlb": 1,
                "icehockey_nhl": 6
            }
            
            sport_id = sport_map.get(job.sport)
            if not sport_id:
                raise ValueError(f"Unsupported sport: {job.sport}")
            
            # Initialize Lunosoft client
            client = LunosoftClient()
            await client.connect()
            
            try:
                # Build the historical odds URL with correct parameters
                base_url = "https://www.lunosoftware.com/sportsData/SportsDataService.svc"
                
                # Use week-based parameters for NFL (historical data available)
                if job.sport == "americanfootball_nfl":
                    # Convert date to week number (approximate)
                    # NFL season runs September to January
                    year = job.date.year
                    if job.date.month >= 9:  # September or later
                        season_start = datetime(year, 9, 1)
                    else:  # January games belong to previous season
                        season_start = datetime(year - 1, 9, 1)
                    
                    # Calculate week number (approximate)
                    days_diff = (job.date - season_start).days
                    week_num = max(1, min(18, (days_diff // 7) + 1))  # NFL has 18 weeks
                    
                    url = f"{base_url}/gamesOddsForDateWeek/{sport_id}?week={week_num}&sportsbookIDList={job.book_id}"
                    date_str = f"Week {week_num} ({job.date.year})"
                else:
                    # For other sports, try date format (may not have historical data)
                    date_str = job.date.strftime("%Y-%m-%d")
                    url = f"{base_url}/gamesOddsForDateWeek/{sport_id}?date={date_str}&sportsbookIDList={job.book_id}"
                
                logger.info("Fetching historical odds", 
                           sport=job.sport, 
                           book=job.book_name, 
                           date=date_str,
                           url=url)
                
                # Fetch odds data from Lunosoft API
                response = await client._get_json(url)
                
                if not response:
                    logger.info("No response from Lunosoft API", 
                               sport=job.sport, 
                               book=job.book_name, 
                               date=date_str)
                    return []
                
                # Transform data for database storage
                transformed_data = []
                games = response if isinstance(response, list) else response.get('games', [])
                
                for game in games:
                    # Extract game information
                    home_team = game.get('HomeTeamName', game.get('HomeTeamFullName', ''))
                    away_team = game.get('AwayTeamName', game.get('AwayTeamFullName', ''))
                    commence_time = game.get('StartTime')
                    game_id = game.get('GameID', '')
                    
                    # Extract odds data
                    odds_markets = game.get('Odds', [])
                    
                    if odds_markets:  # Only process if odds data exists
                        for market in odds_markets:
                            transformed = {
                                "sport": job.sport,
                                "event_id": str(game_id),
                                "home_team": home_team,
                                "away_team": away_team,
                                "book_name": job.book_name,
                                "book_id": job.book_id,
                                "market_type": "moneyline" if market.get('HomeLine') else "spreads",
                                "market_data": {
                                    "game": game,
                                    "market": market,
                                    "source": "lunosoft_historical",
                                    "week": week_num if job.sport == "americanfootball_nfl" else None,
                                    "date": date_str
                                },
                                "commence_time": commence_time
                            }
                            transformed_data.append(transformed)
                
                logger.info(f"Fetched {len(transformed_data)} odds records", 
                           book=job.book_name, 
                           date=date_str,
                           games=len(games))
                
                return transformed_data
                
            finally:
                await client.disconnect()
                
        except Exception as e:
            logger.error("Failed to fetch historical odds", 
                        sport=job.sport, 
                        book=job.book_name, 
                        date=job.date.strftime("%Y-%m-%d"),
                        error=str(e))
            raise
    
    async def process_job(self, job: IngestionJob) -> bool:
        """Process a single ingestion job with retry logic."""
        job.status = IngestionStatus.IN_PROGRESS
        job.attempts += 1
        job.last_attempt = datetime.utcnow()
        
        try:
            # Fetch historical odds
            odds_data = await self.fetch_historical_odds(job)
            
            if not odds_data:
                logger.info("No odds data found for job", 
                           sport=job.sport, 
                           book=job.book_name, 
                           date=job.date.strftime("%Y-%m-%d"))
                job.status = IngestionStatus.SKIPPED
                job.records_processed = 0
                await self.update_job_progress(job)
                return True
            
            # Store in database using bulk insert
            success = await self.database.bulk_store_odds(odds_data)
            
            if success:
                job.status = IngestionStatus.COMPLETED
                job.records_processed = len(odds_data)
                logger.info(f"Successfully processed job", 
                           sport=job.sport, 
                           book=job.book_name, 
                           date=job.date.strftime("%Y-%m-%d"),
                           records=len(odds_data))
            else:
                raise Exception("Failed to store odds data in database")
            
        except Exception as e:
            job.error_message = str(e)
            if job.attempts >= self.max_retries:
                job.status = IngestionStatus.FAILED
                logger.error(f"Job failed after {job.attempts} attempts", 
                           sport=job.sport, 
                           book=job.book_name, 
                           date=job.date.strftime("%Y-%m-%d"),
                           error=str(e))
            else:
                job.status = IngestionStatus.PENDING
                logger.warning(f"Job failed, will retry", 
                             sport=job.sport, 
                             book=job.book_name, 
                             date=job.date.strftime("%Y-%m-%d"),
                             attempt=job.attempts,
                             error=str(e))
        
        await self.update_job_progress(job)
        return job.status == IngestionStatus.COMPLETED
    
    async def execute_ingestion(
        self,
        jobs: List[IngestionJob],
        resume: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Execute the ingestion plan with progress tracking and resume capability.
        
        Args:
            jobs: List of ingestion jobs to process
            resume: Skip already completed jobs
            dry_run: Only estimate, don't actually process
        
        Returns:
            Execution summary
        """
        if dry_run:
            return await self.estimate_ingestion(jobs)
        
        # Filter out completed jobs if resuming
        if resume:
            completed = await self.get_existing_progress()
            pending_jobs = [
                job for job in jobs 
                if (job.sport, job.book_id, job.date.date()) not in completed
            ]
            logger.info(f"Resuming ingestion: {len(pending_jobs)} pending jobs out of {len(jobs)} total")
        else:
            pending_jobs = jobs
            logger.info(f"Starting fresh ingestion: {len(pending_jobs)} jobs")
        
        # Execute jobs with rate limiting
        completed_count = 0
        failed_count = 0
        skipped_count = 0
        total_records = 0
        
        # Process jobs in batches to manage rate limiting
        for i in range(0, len(pending_jobs), self.max_concurrent_books):
            batch = pending_jobs[i:i + self.max_concurrent_books]
            
            # Process batch concurrently
            tasks = [self.process_job(job) for job in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    failed_count += 1
                    logger.error(f"Job processing exception", error=str(result))
                elif result:
                    completed_count += 1
                else:
                    failed_count += 1
            
            # Rate limiting between batches
            if i + self.max_concurrent_books < len(pending_jobs):
                await asyncio.sleep(self.rate_limit_delay)
            
            # Progress logging
            processed = i + len(batch)
            progress = (processed / len(pending_jobs)) * 100
            logger.info(f"Ingestion progress: {processed}/{len(pending_jobs)} ({progress:.1f}%)")
        
        summary = {
            "total_jobs": len(jobs),
            "processed_jobs": len(pending_jobs),
            "completed": completed_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "total_records": total_records,
            "success_rate": (completed_count / len(pending_jobs)) * 100 if pending_jobs else 0
        }
        
        logger.info("Ingestion completed", **summary)
        return summary
    
    async def estimate_ingestion(self, jobs: List[IngestionJob]) -> Dict[str, Any]:
        """Estimate ingestion requirements without actually processing."""
        # Get existing progress
        completed = await self.get_existing_progress()
        pending_jobs = [
            job for job in jobs 
            if (job.sport, job.book_id, job.date.date()) not in completed
        ]
        
        # Estimate API calls and timing
        estimated_api_calls = len(pending_jobs)
        estimated_duration = (estimated_api_calls * self.rate_limit_delay) / 3600  # hours
        
        estimate = {
            "total_jobs": len(jobs),
            "pending_jobs": len(pending_jobs),
            "completed_jobs": len(jobs) - len(pending_jobs),
            "estimated_api_calls": estimated_api_calls,
            "estimated_duration_hours": estimated_duration,
            "estimated_records": estimated_api_calls * 50  # Rough estimate
        }
        
        logger.info("Ingestion estimate", **estimate)
        return estimate


# Utility functions for common ingestion scenarios
async def ingest_nba_season(
    database: HistoricalOddsDatabase,
    season_year: int,
    book_ids: Optional[List[int]] = None,
    resume: bool = True
) -> Dict[str, Any]:
    """Ingest entire NBA season data."""
    
    # NBA season typically runs from October to June
    start_date = datetime(season_year - 1, 10, 1)  # Previous year October
    end_date = datetime(season_year, 6, 30)        # Current year June
    
    ingestor = HistoricalOddsIngestor(database)
    await ingestor.ensure_progress_table()
    
    jobs = await ingestor.create_ingestion_plan(
        sports=["basketball_nba"],
        start_date=start_date,
        end_date=end_date,
        book_ids=book_ids
    )
    
    return await ingestor.execute_ingestion(jobs, resume=resume)


async def ingest_nfl_season(
    database: HistoricalOddsDatabase,
    season_year: int,
    book_ids: Optional[List[int]] = None,
    resume: bool = True
) -> Dict[str, Any]:
    """Ingest entire NFL season data."""
    
    # NFL season typically runs from September to January
    start_date = datetime(season_year - 1, 9, 1)   # Previous year September
    end_date = datetime(season_year, 2, 1)        # Current year February
    
    ingestor = HistoricalOddsIngestor(database)
    await ingestor.ensure_progress_table()
    
    jobs = await ingestor.create_ingestion_plan(
        sports=["americanfootball_nfl"],
        start_date=start_date,
        end_date=end_date,
        book_ids=book_ids
    )
    
    return await ingestor.execute_ingestion(jobs, resume=resume)


async def ingest_multi_sport_seasons(
    database: HistoricalOddsDatabase,
    season_year: int,
    sports: List[str],
    book_ids: Optional[List[int]] = None,
    resume: bool = True
) -> Dict[str, Any]:
    """Ingest multiple sports for a season year."""
    
    ingestor = HistoricalOddsIngestor(database)
    await ingestor.ensure_progress_table()
    
    # Create date ranges for each sport
    sport_dates = {
        "basketball_nba": (datetime(season_year - 1, 10, 1), datetime(season_year, 6, 30)),
        "americanfootball_nfl": (datetime(season_year - 1, 9, 1), datetime(season_year, 2, 1)),
        "baseball_mlb": (datetime(season_year, 3, 1), datetime(season_year, 10, 31)),
        "icehockey_nhl": (datetime(season_year - 1, 10, 1), datetime(season_year, 6, 30))
    }
    
    all_jobs = []
    for sport in sports:
        if sport in sport_dates:
            start_date, end_date = sport_dates[sport]
            jobs = await ingestor.create_ingestion_plan(
                sports=[sport],
                start_date=start_date,
                end_date=end_date,
                book_ids=book_ids
            )
            all_jobs.extend(jobs)
    
    return await ingestor.execute_ingestion(all_jobs, resume=resume)
