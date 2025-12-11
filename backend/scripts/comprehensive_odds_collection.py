#!/usr/bin/env python3
"""
Comprehensive Odds Collection System
Builds deep historical odds dataset using validated sportsbooks
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

class ComprehensiveOddsCollector:
    """Builds comprehensive odds dataset using validated sportsbooks."""
    
    def __init__(self):
        self.aggregator = OddsAggregator()
        self.database = None
        
        # Validated working sportsbooks from expansion testing
        self.working_sportsbooks = [
            {"id": 83, "name": "Barstool"},
            {"id": 89, "name": "DraftKings"}, 
            {"id": 94, "name": "FanDuel"},
            {"id": 85, "name": "BetRivers"},
            {"id": 90, "name": "PointsBet"},
            {"id": 91, "name": "Unibet"},
            {"id": 92, "name": "Bet365"},
            {"id": 93, "name": "WynnBet"}
        ]
        
        # Date ranges for comprehensive collection
        self.date_ranges = [
            # NBA 2024 season dates
            (datetime(2024, 10, 24), datetime(2024, 11, 30)),  # Start of season
            (datetime(2024, 12, 1), datetime(2024, 12, 31)),   # December 2024
            (datetime(2025, 1, 1), datetime(2025, 1, 31)),     # January 2025
        ]
        
        self.collection_config = "comprehensive_odds_collection.json"
        
    async def initialize(self):
        """Initialize database and load collection config."""
        self.database = await get_historical_db()
        await self.database.create_tables()
        logger.info("Comprehensive odds collector initialized")
        
    def load_collection_config(self) -> Dict[str, Any]:
        """Load collection progress from config file."""
        if os.path.exists(self.collection_config):
            with open(self.collection_config, 'r') as f:
                return json.load(f)
        return {
            "completed_dates": [],
            "current_date_index": 0,
            "total_odds_collected": 0,
            "collection_start_time": None
        }
    
    def save_collection_config(self, config: Dict[str, Any]):
        """Save collection progress to config file."""
        config["last_update"] = datetime.utcnow().isoformat()
        with open(self.collection_config, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info("Collection config saved", 
                   completed_dates=len(config["completed_dates"]),
                   total_odds=config["total_odds_collected"])
    
    async def collect_odds_for_date(self, date: datetime) -> Dict[str, Any]:
        """Collect odds for a specific date using all working sportsbooks."""
        logger.info("Collecting odds for date", date=date.strftime("%Y-%m-%d"))
        
        date_results = {
            "date": date.strftime("%Y-%m-%d"),
            "success": False,
            "total_odds": 0,
            "sportsbooks_tested": len(self.working_sportsbooks),
            "errors": []
        }
        
        try:
            # Collect odds using all working sportsbooks
            sportsbook_ids = [sb["id"] for sb in self.working_sportsbooks]
            
            odds_data = await self.aggregator.get_historical_odds_by_date(
                sport='basketball_nba',
                date=date,
                sportsbook_ids=sportsbook_ids
            )
            
            if odds_data:
                date_results["success"] = True
                date_results["total_odds"] = len(odds_data)
                
                # Analyze data by sportsbook
                sportsbook_counts = {}
                for odds in odds_data:
                    book = odds.book
                    sportsbook_counts[book] = sportsbook_counts.get(book, 0) + 1
                
                logger.info("Successfully collected odds for date",
                           date=date.strftime("%Y-%m-%d"),
                           total_odds=len(odds_data),
                           sportsbooks=len(sportsbook_counts),
                           breakdown=sportsbook_counts)
                
            else:
                date_results["errors"].append("No odds data returned")
                
        except Exception as e:
            date_results["errors"].append(str(e))
            logger.error("Failed to collect odds for date", 
                        date=date.strftime("%Y-%m-%d"),
                        error=str(e))
        
        return date_results
    
    async def run_comprehensive_collection(self):
        """Run comprehensive odds collection across all date ranges."""
        await self.initialize()
        
        config = self.load_collection_config()
        
        logger.info("Starting comprehensive odds collection",
                   working_sportsbooks=len(self.working_sportsbooks),
                   date_ranges=len(self.date_ranges))
        
        # Generate all dates to process
        all_dates = []
        for start_date, end_date in self.date_ranges:
            current_date = start_date
            while current_date <= end_date:
                all_dates.append(current_date)
                current_date += timedelta(days=1)
        
        logger.info("Generated date list", total_dates=len(all_dates))
        
        # Process dates
        for i, date in enumerate(all_dates):
            date_str = date.strftime("%Y-%m-%d")
            
            # Skip if already completed
            if date_str in config["completed_dates"]:
                logger.info("Skipping already completed date", date=date_str)
                continue
            
            print(f"\\n📊 COLLECTING ODDS - Day {i+1}/{len(all_dates)}")
            print(f"   📅 Date: {date_str}")
            print(f"   📚 Sportsbooks: {len(self.working_sportsbooks)} working books")
            
            # Collect odds for this date
            result = await self.collect_odds_for_date(date)
            
            if result["success"]:
                print(f"   ✅ SUCCESS: {result['total_odds']} odds collected")
                config["completed_dates"].append(date_str)
                config["total_odds_collected"] += result["total_odds"]
                
            else:
                print(f"   ❌ FAILED: {result['errors']}")
            
            # Save progress
            self.save_collection_config(config)
            
            # Delay between dates to avoid rate limiting
            if i < len(all_dates) - 1:
                delay = 3.0  # 3 seconds between dates
                print(f"   ⏱️  Waiting {delay} seconds before next date...")
                await asyncio.sleep(delay)
        
        # Final summary
        print(f"\\n🎉 COMPREHENSIVE ODDS COLLECTION COMPLETE!")
        print(f"   ✅ Dates processed: {len(config['completed_dates'])}")
        print(f"   📊 Total odds collected: {config['total_odds_collected']}")
        print(f"   📚 Sportsbooks used: {len(self.working_sportsbooks)}")
        print(f"   📈 Average odds per date: {config['total_odds_collected'] // max(len(config['completed_dates']), 1)}")

async def main():
    """Main execution function."""
    collector = ComprehensiveOddsCollector()
    await collector.run_comprehensive_collection()

if __name__ == "__main__":
    asyncio.run(main())
