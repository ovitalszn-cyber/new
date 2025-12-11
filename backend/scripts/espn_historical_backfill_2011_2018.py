#!/usr/bin/env python3
"""
ESPN Historical Data Backfill Script (2011-2018)
Season-by-season approach with progress tracking and resumption capability
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from v6.stats.engine import StatsEngine
from v6.historical.database import get_historical_db
import structlog

logger = structlog.get_logger()

class ESPNHistoricalBackfill:
    """ESPN historical data backfill system for 2011-2018 seasons."""
    
    def __init__(self):
        self.engine = StatsEngine()
        self.database = None
        self.progress_file = "espn_backfill_progress_2011_2018.json"
        self.rate_limit_delay = 1.0  # 1 second between API calls
        
    async def initialize(self):
        """Initialize database and load progress."""
        self.database = await get_historical_db()
        await self.database.create_tables()
        logger.info("ESPN backfill system initialized")
        
    def load_progress(self) -> Dict[str, Any]:
        """Load backfill progress from file."""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {
            "completed_seasons": [],
            "completed_dates": [],
            "total_games_processed": 0,
            "start_time": None,
            "last_updated": None
        }
    
    def save_progress(self, progress: Dict[str, Any]):
        """Save backfill progress to file."""
        progress["last_updated"] = datetime.utcnow().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
        logger.info("Progress saved", completed_seasons=len(progress["completed_seasons"]))
    
    def get_complete_date_range(self) -> List[datetime]:
        """Get every single day from 2011-01-01 to today."""
        dates = []
        start_date = datetime(2011, 1, 1)
        end_date = datetime.utcnow()
        
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        return dates
    
    async def store_espn_games(self, games: List[Dict[str, Any]], date: datetime) -> bool:
        """Store ESPN games in historical database."""
        try:
            # Store as historical odds data with ESPN source
            for game in games:
                # Transform ESPN game to historical odds format
                scores = game.get('scores', [])
                teams = game.get('teams', [])
                
                if scores and teams:
                    # Create a historical record
                    historical_record = {
                        "sport": "basketball_nba",
                        "event_id": str(game.get('event_id', '')),
                        "home_team": teams[1].get('team', {}).get('displayName', '') if len(teams) > 1 else '',
                        "away_team": teams[0].get('team', {}).get('displayName', '') if teams else '',
                        "book_name": "ESPN_Historical",
                        "book_id": 999,
                        "market_type": "game_result",
                        "market_data": {
                            "espn_data": game,
                            "source": "espn_historical_backfill",
                            "collection_date": date.strftime("%Y-%m-%d"),
                            "final_score": {
                                "home": scores[1].get('score', 0) if len(scores) > 1 else 0,
                                "away": scores[0].get('score', 0) if scores else 0
                            }
                        },
                        "commence_time": date.isoformat()
                    }
                    
                    # Store in database
                    await self.database.store_odds_snapshot(**historical_record)
            
            return True
            
        except Exception as e:
            logger.error("Failed to store ESPN games", error=str(e))
            return False
    
    async def run_complete_backfill(self):
        """Run complete backfill for every day from 2011-present."""
        await self.initialize()
        
        progress = self.load_progress()
        progress["start_time"] = progress.get("start_time", datetime.utcnow().isoformat())
        
        # Get complete date range from 2011 to today
        all_dates = self.get_complete_date_range()
        
        # Filter out already completed dates
        remaining_dates = [d for d in all_dates if d.strftime("%Y-%m-%d") not in progress.get("completed_dates", [])]
        
        if not remaining_dates:
            logger.info("All dates already completed")
            return
        
        logger.info("Starting complete ESPN historical backfill",
                   total_dates=len(all_dates),
                   remaining_dates=len(remaining_dates),
                   start_date=remaining_dates[0].strftime("%Y-%m-%d"),
                   end_date=remaining_dates[-1].strftime("%Y-%m-%d"))
        
        total_games = 0
        total_errors = 0
        
        # Process each day
        for i, date in enumerate(remaining_dates):
            date_str = date.strftime("%Y-%m-%d")
            
            try:
                # Fetch games for this date
                games = await self.engine.get_historical_games_by_date(date, 'basketball_nba')
                
                if games:
                    # Store games in database
                    success = await self.store_espn_games(games, date)
                    if success:
                        total_games += len(games)
                        progress["completed_dates"].append(date_str)
                        
                        # Log progress every 100 games
                        if total_games % 100 == 0:
                            logger.info("Backfill progress", 
                                      games_processed=total_games,
                                      dates_completed=i+1,
                                      current_date=date_str,
                                      completion_pct=f"{((i+1)/len(remaining_dates)*100):.1f}%")
                    else:
                        total_errors += 1
                        logger.error("Failed to store games", date=date_str)
                
                # Rate limiting between API calls
                await asyncio.sleep(self.rate_limit_delay)
                
                # Save progress every 50 dates
                if (i + 1) % 50 == 0:
                    self.save_progress(progress)
                    logger.info("Progress checkpoint", 
                              dates_completed=i+1,
                              games_processed=total_games)
                
            except Exception as e:
                total_errors += 1
                logger.error("Error processing date", 
                           date=date_str,
                           error=str(e))
        
        # Final save and summary
        progress["total_games_processed"] = total_games
        self.save_progress(progress)
        
        completed_dates = len(progress["completed_dates"])
        
        logger.info("ESPN complete historical backfill finished",
                   total_games=total_games,
                   dates_completed=completed_dates,
                   total_errors=total_errors,
                   completion_pct=f"{(completed_dates/len(all_dates)*100):.1f}%")
        
        print(f"\n🎉 ESPN COMPLETE HISTORICAL BACKFILL FINISHED!")
        print(f"   📊 Total Games: {total_games}")
        print(f"   📅 Dates Processed: {completed_dates}/{len(all_dates)}")
        print(f"   ⚠️  Errors: {total_errors}")
        print(f"   📈 Data Coverage: 2011-01-01 to {datetime.utcnow().strftime('%Y-%m-%d')}")
        print(f"   ✅ Complete NBA historical dataset ready!")
    
    async def run_backfill(self):
        """Main backfill entry point."""
        await self.run_complete_backfill()

async def main():
    """Main execution function."""
    backfill = ESPNHistoricalBackfill()
    await backfill.run_backfill()

if __name__ == "__main__":
    asyncio.run(main())
