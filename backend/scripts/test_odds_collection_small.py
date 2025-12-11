#!/usr/bin/env python3
"""
Small Test Run for Comprehensive Odds Collection
Tests 1 week of data with conservative delays to validate approach
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from v6.api.odds import OddsAggregator
from v6.historical.database import get_historical_db
import structlog

logger = structlog.get_logger()

class TestOddsCollector:
    """Test run for odds collection with conservative parameters."""
    
    def __init__(self):
        self.aggregator = OddsAggregator()
        self.database = None
        
        # Use smaller subset of working sportsbooks for test
        self.test_sportsbooks = [
            {"id": 89, "name": "DraftKings"}, 
            {"id": 94, "name": "FanDuel"},
            {"id": 85, "name": "BetRivers"},
            {"id": 91, "name": "Unibet"}
        ]
        
        # Test only 1 week of data (Dec 1-7, 2024)
        self.test_dates = []
        current_date = datetime(2024, 12, 1)
        for i in range(7):
            self.test_dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Conservative delays to avoid rate limiting
        self.api_delay = 5.0  # 5 seconds between API calls
        self.date_delay = 10.0  # 10 seconds between dates
        
    async def initialize(self):
        """Initialize database."""
        self.database = await get_historical_db()
        await self.database.create_tables()
        logger.info("Test odds collector initialized")
        
    async def collect_odds_for_date(self, date: datetime) -> Dict[str, Any]:
        """Collect odds for a specific date using test sportsbooks."""
        logger.info("Collecting odds for test date", date=date.strftime("%Y-%m-%d"))
        
        try:
            # Use conservative 4-sportsbook batch
            sportsbook_ids = [sb["id"] for sb in self.test_sportsbooks]
            
            odds_data = await self.aggregator.get_historical_odds_by_date(
                sport='basketball_nba',
                date=date,
                sportsbook_ids=sportsbook_ids
            )
            
            if odds_data:
                # Analyze data by sportsbook
                sportsbook_counts = {}
                for odds in odds_data:
                    book = odds.book
                    sportsbook_counts[book] = sportsbook_counts.get(book, 0) + 1
                
                logger.info("Test collection successful",
                           date=date.strftime("%Y-%m-%d"),
                           total_odds=len(odds_data),
                           sportsbooks=len(sportsbook_counts),
                           breakdown=sportsbook_counts)
                
                return {
                    "success": True,
                    "total_odds": len(odds_data),
                    "sportsbook_breakdown": sportsbook_counts
                }
            else:
                return {"success": False, "error": "No odds data returned"}
                
        except Exception as e:
            logger.error("Test collection failed", 
                        date=date.strftime("%Y-%m-%d"),
                        error=str(e))
            return {"success": False, "error": str(e)}
    
    async def run_test_collection(self):
        """Run conservative test collection."""
        await self.initialize()
        
        print("🧪 STARTING CONSERVATIVE TEST RUN")
        print("=" * 50)
        print(f"📅 Test Dates: {len(self.test_dates)} days (Dec 1-7, 2024)")
        print(f"📚 Test Sportsbooks: {len(self.test_sportsbooks)} books")
        print(f"⏱️  Delays: {self.api_delay}s between calls, {self.date_delay}s between dates")
        print("")
        
        total_odds = 0
        successful_dates = 0
        
        for i, date in enumerate(self.test_dates):
            date_str = date.strftime("%Y-%m-%d")
            
            print(f"📊 TEST DAY {i+1}/{len(self.test_dates)}: {date_str}")
            print(f"   📚 Sportsbooks: {[sb['name'] for sb in self.test_sportsbooks]}")
            
            # Collect odds for this date
            result = await self.collect_odds_for_date(date)
            
            if result["success"]:
                print(f"   ✅ SUCCESS: {result['total_odds']} odds collected")
                for book, count in result["sportsbook_breakdown"].items():
                    print(f"      📈 {book}: {count} odds")
                
                total_odds += result["total_odds"]
                successful_dates += 1
                
            else:
                print(f"   ❌ FAILED: {result['error']}")
            
            # Conservative delay between dates
            if i < len(self.test_dates) - 1:
                print(f"   ⏱️  Waiting {self.date_delay} seconds...")
                await asyncio.sleep(self.date_delay)
        
        # Test summary
        print("")
        print("🎉 TEST RUN COMPLETE!")
        print("=" * 50)
        print(f"   ✅ Successful dates: {successful_dates}/{len(self.test_dates)}")
        print(f"   📊 Total odds collected: {total_odds}")
        print(f"   📈 Average odds per date: {total_odds // max(successful_dates, 1)}")
        
        if successful_dates == len(self.test_dates):
            print("   🎯 RESULT: All tests passed - ready for full collection!")
        else:
            print("   ⚠️  RESULT: Some tests failed - adjust parameters before full run")

async def main():
    """Main execution function."""
    collector = TestOddsCollector()
    await collector.run_test_collection()

if __name__ == "__main__":
    asyncio.run(main())
