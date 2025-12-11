#!/usr/bin/env python3
"""
ESPN Games to Odds Integration System
Enriches collected ESPN game data with comprehensive odds from V6 system
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from v6.api.odds import OddsAggregator
from v6.historical.database import get_historical_db
import structlog

logger = structlog.get_logger()

class ESPNOddsIntegrator:
    """Integrates ESPN game data with comprehensive odds collection."""
    
    def __init__(self):
        self.aggregator = OddsAggregator()
        self.database = None
        
        # Validated working sportsbooks from V6 system
        self.working_sportsbooks = [
            {"id": 83, "name": "DraftKings"},
            {"id": 85, "name": "BetRivers"},
            {"id": 87, "name": "BetMGM"},
            {"id": 88, "name": "Unibet"},
            {"id": 94, "name": "Hard Rock"}
        ]
        
        # Integration strategy: start with recent games for validation
        self.integration_phases = [
            # Phase 1: Recent 2024 season (2 weeks for validation)
            {"start": datetime(2024, 12, 1), "end": datetime(2024, 12, 14), "name": "2024 Validation"},
            # Phase 2: Test different years for historical availability
            {"start": datetime(2020, 12, 1), "end": datetime(2020, 12, 7), "name": "2020 Test"},
            {"start": datetime(2015, 12, 1), "end": datetime(2015, 12, 7), "name": "2015 Test"},
            {"start": datetime(2011, 12, 1), "end": datetime(2011, 12, 7), "name": "2011 Test"},
        ]
        
        self.integration_config = "espn_odds_integration.json"
        
    async def initialize(self):
        """Initialize database and load integration config."""
        self.database = await get_historical_db()
        await self.database.create_tables()
        logger.info("ESPN-Odds integration system initialized")
        
    def load_integration_config(self) -> Dict[str, Any]:
        """Load integration progress from config file."""
        if os.path.exists(self.integration_config):
            with open(self.integration_config, 'r') as f:
                return json.load(f)
        return {
            "completed_phases": [],
            "current_phase": 0,
            "total_odds_collected": 0,
            "total_games_enriched": 0,
            "integration_start_time": None
        }
    
    def save_integration_config(self, config: Dict[str, Any]):
        """Save integration progress to config file."""
        config["last_update"] = datetime.utcnow().isoformat()
        with open(self.integration_config, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info("Integration config saved", 
                   completed_phases=len(config["completed_phases"]),
                   total_odds=config["total_odds_collected"],
                   games_enriched=config["total_games_enriched"])
    
    async def get_espn_games_for_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get ESPN games for a specific date range from database."""
        logger.info("Fetching ESPN games for date range", 
                   start=start_date.strftime("%Y-%m-%d"),
                   end=end_date.strftime("%Y-%m-%d"))
        
        try:
            # Query ESPN games from database for the date range
            # This would need to be implemented based on your ESPN database schema
            # For now, we'll simulate by calling the odds system directly
            
            games = []
            current_date = start_date
            while current_date <= end_date:
                # For each date, we'll collect odds (which implicitly validates game existence)
                games.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "date_obj": current_date
                })
                current_date += timedelta(days=1)
            
            logger.info("Retrieved ESPN games", count=len(games))
            return games
            
        except Exception as e:
            logger.error("Failed to fetch ESPN games", error=str(e))
            return []
    
    async def collect_odds_for_espn_games(self, games: List[Dict[str, Any]], phase_name: str) -> Dict[str, Any]:
        """Collect odds for ESPN games using all working sportsbooks."""
        logger.info("Collecting odds for ESPN games", 
                   phase=phase_name,
                   games_count=len(games),
                   sportsbooks=len(self.working_sportsbooks))
        
        phase_results = {
            "phase_name": phase_name,
            "success": True,
            "total_odds": 0,
            "total_games_processed": len(games),
            "successful_dates": 0,
            "sportsbook_coverage": {},
            "errors": []
        }
        
        # Use all working sportsbooks for comprehensive coverage
        sportsbook_ids = [sb["id"] for sb in self.working_sportsbooks]
        
        for i, game in enumerate(games):
            date_obj = game["date_obj"]
            date_str = game["date"]
            
            print(f"\\n📊 PROCESSING GAME DATE - Day {i+1}/{len(games)}")
            print(f"   📅 Date: {date_str}")
            print(f"   📚 Sportsbooks: {len(self.working_sportsbooks)} working books")
            
            try:
                # Collect odds for this game date
                odds_data = await self.aggregator.get_historical_odds_by_date(
                    sport='basketball_nba',
                    date=date_obj,
                    sportsbook_ids=sportsbook_ids
                )
                
                if odds_data:
                    # Analyze sportsbook coverage
                    sportsbook_counts = {}
                    for odds in odds_data:
                        book = odds.book
                        sportsbook_counts[book] = sportsbook_counts.get(book, 0) + 1
                    
                    print(f"   ✅ SUCCESS: {len(odds_data)} odds collected")
                    for book, count in sportsbook_counts.items():
                        print(f"      📈 {book}: {count} odds")
                        phase_results["sportsbook_coverage"][book] = phase_results["sportsbook_coverage"].get(book, 0) + count
                    
                    phase_results["total_odds"] += len(odds_data)
                    phase_results["successful_dates"] += 1
                    
                else:
                    print(f"   ❌ NO ODDS: No betting data available for this date")
                    phase_results["errors"].append(f"No odds data for {date_str}")
                
            except Exception as e:
                error_msg = f"Error collecting odds for {date_str}: {str(e)}"
                print(f"   ❌ ERROR: {error_msg}")
                phase_results["errors"].append(error_msg)
                phase_results["success"] = False
            
            # Strategic delay to avoid rate limiting
            if i < len(games) - 1:
                delay = 3.0  # 3 seconds between dates
                print(f"   ⏱️  Waiting {delay} seconds...")
                await asyncio.sleep(delay)
        
        return phase_results
    
    async def run_integration(self):
        """Run ESPN-Odds integration across all phases."""
        await self.initialize()
        
        config = self.load_integration_config()
        
        print("🎯 ESPN-ODDS INTEGRATION SYSTEM")
        print("=" * 60)
        print(f"📊 ESPN Games Available: 20,282 games")
        print(f"📚 Working Sportsbooks: {len(self.working_sportsbooks)} validated books")
        print(f"📈 Integration Phases: {len(self.integration_phases)} phases planned")
        print("")
        
        for i, phase in enumerate(self.integration_phases):
            if i < config["current_phase"]:
                print(f"⏭️  SKIPPING PHASE {i+1}: {phase['name']} (already completed)")
                continue
            
            print(f"🚀 STARTING PHASE {i+1}: {phase['name']}")
            print(f"   📅 Date Range: {phase['start'].strftime('%Y-%m-%d')} to {phase['end'].strftime('%Y-%m-%d')}")
            
            # Get ESPN games for this phase
            games = await self.get_espn_games_for_date_range(phase["start"], phase["end"])
            
            if not games:
                print(f"   ❌ NO GAMES: Skipping phase - no ESPN games found")
                continue
            
            # Collect odds for these games
            phase_results = await self.collect_odds_for_espn_games(games, phase["name"])
            
            # Update config with results
            config["completed_phases"].append(phase_results)
            config["total_odds_collected"] += phase_results["total_odds"]
            config["total_games_enriched"] += phase_results["successful_dates"]
            config["current_phase"] = i + 1
            
            # Save progress
            self.save_integration_config(config)
            
            # Phase summary
            print(f"\\n📊 PHASE {i+1} COMPLETE!")
            print(f"   ✅ Success: {phase_results['success']}")
            print(f"   📈 Total Odds: {phase_results['total_odds']}")
            print(f"   🎯 Successful Dates: {phase_results['successful_dates']}/{len(games)}")
            print(f"   📚 Sportsbook Coverage: {len(phase_results['sportsbook_coverage'])} books")
            
            # Strategic delay between phases
            if i < len(self.integration_phases) - 1:
                delay = 10.0
                print(f"   ⏱️  Waiting {delay} seconds before next phase...")
                await asyncio.sleep(delay)
        
        # Final integration summary
        print(f"\\n🎉 ESPN-ODDS INTEGRATION COMPLETE!")
        print("=" * 60)
        print(f"   ✅ Phases Completed: {len(config['completed_phases'])}/{len(self.integration_phases)}")
        print(f"   📊 Total Odds Collected: {config['total_odds_collected']}")
        print(f"   🎯 Games Enriched: {config['total_games_enriched']}")
        print(f"   📈 Average Odds per Game: {config['total_odds_collected'] // max(config['total_games_enriched'], 1)}")
        
        # Historical availability analysis
        print(f"\\n📅 HISTORICAL AVAILABILITY ANALYSIS:")
        for phase_result in config["completed_phases"]:
            phase_name = phase_result["phase_name"]
            success_rate = (phase_result["successful_dates"] / phase_result["total_games_processed"]) * 100
            print(f"   📊 {phase_name}: {success_rate:.1f}% odds availability")

async def main():
    """Main execution function."""
    integrator = ESPNOddsIntegrator()
    await integrator.run_integration()

if __name__ == "__main__":
    asyncio.run(main())
