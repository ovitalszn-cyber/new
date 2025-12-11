#!/usr/bin/env python3
"""
Gradual Sportsbook Expansion for V6 Odds System
Strategically adds sportsbooks to populate database without rate limiting
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from v6.api.odds import OddsAggregator
from v6.historical.database import get_historical_db
import structlog

logger = structlog.get_logger()

class SportsbookExpansion:
    """Gradual sportsbook expansion system for odds data collection."""
    
    def __init__(self):
        self.aggregator = OddsAggregator()
        self.database = None
        self.expansion_config = "sportsbook_expansion_config.json"
        self.expansion_delay = 2.0  # 2 seconds between API calls
        
        # Priority sportsbooks by volume/popularity
        self.priority_sportsbooks = [
            {"id": 83, "name": "Barstool", "status": "tested"},  # Already working
            {"id": 89, "name": "DraftKings", "status": "pending"},
            {"id": 94, "name": "FanDuel", "status": "pending"},
            {"id": 3, "name": "BetMGM", "status": "pending"},
            {"id": 6, "name": "Caesars", "status": "pending"},
            {"id": 85, "name": "BetRivers", "status": "pending"},
            {"id": 90, "name": "PointsBet", "status": "pending"},
            {"id": 91, "name": "Unibet", "status": "pending"},
            {"id": 92, "name": "Bet365", "status": "pending"},
            {"id": 93, "name": "WynnBet", "status": "pending"}
        ]
        
    async def initialize(self):
        """Initialize database and load expansion config."""
        self.database = await get_historical_db()
        await self.database.create_tables()
        logger.info("Sportsbook expansion system initialized")
        
    def load_expansion_config(self) -> Dict[str, Any]:
        """Load expansion progress from config file."""
        if os.path.exists(self.expansion_config):
            with open(self.expansion_config, 'r') as f:
                return json.load(f)
        return {
            "tested_sportsbooks": [],
            "successful_sportsbooks": [83],  # Barstool already working
            "failed_sportsbooks": [],
            "last_test_time": None,
            "current_batch_size": 2,
            "total_odds_collected": 0
        }
    
    def save_expansion_config(self, config: Dict[str, Any]):
        """Save expansion progress to config file."""
        config["last_test_time"] = datetime.utcnow().isoformat()
        with open(self.expansion_config, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info("Expansion config saved", 
                   successful=len(config["successful_sportsbooks"]),
                   failed=len(config["failed_sportsbooks"]))
    
    async def test_sportsbook_batch(self, sportsbook_ids: List[int]) -> Dict[str, Any]:
        """Test a batch of sportsbooks for rate limiting and data quality."""
        logger.info("Testing sportsbook batch", 
                   sportsbooks=sportsbook_ids,
                   batch_size=len(sportsbook_ids))
        
        batch_results = {
            "sportsbook_ids": sportsbook_ids,
            "success": False,
            "total_odds": 0,
            "errors": [],
            "test_time": datetime.utcnow().isoformat()
        }
        
        try:
            # Test with historical odds for a recent date
            test_date = datetime(2024, 12, 1)
            
            # Make API call with this batch
            odds_data = await self.aggregator.get_historical_odds_by_date(
                sport='basketball_nba',
                date=test_date,
                sportsbook_ids=sportsbook_ids
            )
            
            if odds_data:
                batch_results["success"] = True
                batch_results["total_odds"] = len(odds_data)
                
                # Analyze data quality
                unique_books = set(odd.book for odd in odds_data)
                logger.info("Batch test successful",
                           sportsbooks=sportsbook_ids,
                           total_odds=len(odds_data),
                           unique_books=len(unique_books))
                
                # Store the data in database
                await self.store_odds_batch(odds_data, test_date)
                
            else:
                batch_results["errors"].append("No odds data returned")
                
        except Exception as e:
            batch_results["errors"].append(str(e))
            logger.error("Batch test failed", 
                        sportsbooks=sportsbook_ids,
                        error=str(e))
        
        return batch_results
    
    async def store_odds_batch(self, odds_data: List[Any], date: datetime):
        """Store odds batch in historical database."""
        try:
            for odds in odds_data:
                # Convert to historical record format
                historical_record = {
                    "sport": "basketball_nba",
                    "event_id": f"odds_{odds.team}_{date.strftime('%Y%m%d')}",
                    "home_team": odds.team if odds.direction == odds.team else odds.direction,
                    "away_team": odds.direction if odds.direction != odds.team else "Unknown",
                    "book_name": odds.book,
                    "book_id": next((sb["id"] for sb in self.priority_sportsbooks if sb["name"] == odds.book), 0),
                    "market_type": odds.prop,
                    "market_data": {
                        "odds": odds.odds,
                        "line": odds.line,
                        "direction": odds.direction,
                        "source": "gradual_expansion",
                        "collection_date": date.strftime("%Y-%m-%d")
                    },
                    "commence_time": odds.event_time.isoformat()
                }
                
                # Store in database
                await self.database.store_odds_snapshot(**historical_record)
                
        except Exception as e:
            logger.error("Failed to store odds batch", error=str(e))
    
    async def run_gradual_expansion(self):
        """Run gradual sportsbook expansion process."""
        await self.initialize()
        
        config = self.load_expansion_config()
        current_batch_size = config["current_batch_size"]
        
        logger.info("Starting gradual sportsbook expansion",
                   current_batch_size=current_batch_size,
                   successful_books=len(config["successful_sportsbooks"]))
        
        # Get pending sportsbooks
        successful_ids = set(config["successful_sportsbooks"])
        failed_ids = set(config["failed_sportsbooks"])
        
        pending_sportsbooks = [
            sb for sb in self.priority_sportsbooks 
            if sb["id"] not in successful_ids and sb["id"] not in failed_ids
        ]
        
        if not pending_sportsbooks:
            logger.info("All sportsbooks already tested")
            return
        
        # Test in batches
        for i in range(0, len(pending_sportsbooks), current_batch_size):
            batch = pending_sportsbooks[i:i + current_batch_size]
            batch_ids = [sb["id"] for sb in batch]
            
            print(f"\\n🧪 TESTING BATCH {i//current_batch_size + 1}:")
            for sb in batch:
                print(f"   📚 {sb['name']} (ID: {sb['id']})")
            
            # Test the batch
            result = await self.test_sportsbook_batch(batch_ids)
            
            if result["success"]:
                print(f"   ✅ SUCCESS: {result['total_odds']} odds collected")
                config["successful_sportsbooks"].extend(batch_ids)
                config["total_odds_collected"] += result["total_odds"]
                
                # If successful, we can try increasing batch size next time
                if current_batch_size < 5:
                    config["current_batch_size"] = min(current_batch_size + 1, 5)
                    
            else:
                print(f"   ❌ FAILED: {result['errors']}")
                config["failed_sportsbooks"].extend(batch_ids)
                
                # If failed, reduce batch size for next attempt
                config["current_batch_size"] = max(1, current_batch_size - 1)
            
            # Save progress
            self.save_expansion_config(config)
            
            # Delay between batches to avoid rate limiting
            if i + current_batch_size < len(pending_sportsbooks):
                print(f"   ⏱️  Waiting {self.expansion_delay} seconds before next batch...")
                await asyncio.sleep(self.expansion_delay)
        
        # Final summary
        print(f"\\n🎉 SPORTSBOOK EXPANSION COMPLETE!")
        print(f"   ✅ Successful books: {len(config['successful_sportsbooks'])}")
        print(f"   ❌ Failed books: {len(config['failed_sportsbooks'])}")
        print(f"   📊 Total odds collected: {config['total_odds_collected']}")
        print(f"   📈 Final batch size: {config['current_batch_size']}")

async def main():
    """Main execution function."""
    expansion = SportsbookExpansion()
    await expansion.run_gradual_expansion()

if __name__ == "__main__":
    asyncio.run(main())
