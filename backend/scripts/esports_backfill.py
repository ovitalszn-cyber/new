#!/usr/bin/env python3
"""
Esports Historical Data Backfill Script
Backfills esports match data from BO3.gg for LoL, CS2, Dota2, and Valorant
from specific start dates to the present.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from v6.historical.esports_bo3_matches_ingestion import Bo3EsportsMatchesIngestor
from v6.historical.database import get_historical_db
import structlog

logger = structlog.get_logger()

class EsportsBackfill:
    """Esports historical data backfill system using BO3.gg."""

    def __init__(self):
        self.db = None
        self.ingestor = None
        self.progress_file = "esports_backfill_progress.json"

        # Define start dates for each discipline (last 180 days)
        days_back = 180
        base_date = datetime.utcnow() - timedelta(days=days_back)
        self.start_dates = {
            "lol": base_date.strftime("%Y-%m-%d"),
            "cs2": base_date.strftime("%Y-%m-%d"),
            "dota2": base_date.strftime("%Y-%m-%d"),
            "val": base_date.strftime("%Y-%m-%d")
        }

    async def initialize(self):
        """Initialize database and ingestor."""
        self.db = await get_historical_db()
        self.ingestor = Bo3EsportsMatchesIngestor(self.db)
        logger.info("Esports backfill system initialized")

    def load_progress(self) -> Dict[str, Any]:
        """Load backfill progress from file."""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {
            "disciplines_completed": [],
            "start_time": None,
            "last_updated": None
        }

    def save_progress(self, progress: Dict[str, Any]):
        """Save backfill progress to file."""
        progress["last_updated"] = datetime.utcnow().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
        logger.info("Progress saved", completed_disciplines=len(progress["disciplines_completed"]))

    async def backfill_discipline(self, discipline: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Backfill data for a single discipline."""
        logger.info("Starting backfill for discipline", discipline=discipline,
                   start_date=start_date, end_date=end_date)

        try:
            # Use the ingestor to fetch and store data
            summary = await self.ingestor.ingest(
                disciplines=[discipline],
                start_date=start_date,
                end_date=end_date,
                page_limit=50  # Use reasonable page size
            )

            result = summary["disciplines"].get(discipline, {})
            logger.info("Completed backfill for discipline",
                       discipline=discipline,
                       matches_stored=result.get("matches_stored", 0),
                       total_reported=result.get("total_reported", 0))

            return result

        except Exception as e:
            logger.error("Failed to backfill discipline", discipline=discipline, error=str(e))
            return {"error": str(e)}

    async def run_complete_backfill(self):
        """Run complete backfill for all esports disciplines."""
        await self.initialize()

        progress = self.load_progress()
        progress["start_time"] = progress.get("start_time", datetime.utcnow().isoformat())

        end_date = datetime.utcnow().strftime("%Y-%m-%d")

        # Get remaining disciplines
        all_disciplines = list(self.start_dates.keys())
        completed_disciplines = progress.get("disciplines_completed", [])
        remaining_disciplines = [d for d in all_disciplines if d not in completed_disciplines]

        if not remaining_disciplines:
            logger.info("All disciplines already completed")
            return

        logger.info("Starting esports complete backfill",
                   total_disciplines=len(all_disciplines),
                   remaining_disciplines=len(remaining_disciplines))

        total_matches = 0
        total_errors = 0

        # Process each discipline
        for discipline in remaining_disciplines:
            start_date = self.start_dates[discipline]

            try:
                result = await self.backfill_discipline(discipline, start_date, end_date)

                if "error" not in result:
                    total_matches += result.get("matches_stored", 0)
                    progress["disciplines_completed"].append(discipline)
                    logger.info("Discipline completed",
                               discipline=discipline,
                               matches_stored=result.get("matches_stored", 0))
                else:
                    total_errors += 1
                    logger.error("Failed to complete discipline", discipline=discipline,
                               error=result["error"])

                # Save progress after each discipline
                self.save_progress(progress)

            except Exception as e:
                total_errors += 1
                logger.error("Exception during discipline backfill",
                           discipline=discipline, error=str(e))

        # Final summary
        completed_count = len(progress["disciplines_completed"])

        logger.info("Esports complete historical backfill finished",
                   disciplines_completed=completed_count,
                   total_matches=total_matches,
                   total_errors=total_errors)

        print("\n🎮 ESPORTS HISTORICAL BACKFILL FINISHED!")
        print(f"   🎯 Disciplines: {completed_count}/{len(all_disciplines)}")
        print(f"   📊 Total Matches: {total_matches}")
        print(f"   ⚠️  Errors: {total_errors}")
        print(f"   📅 Date Range: {min(self.start_dates.values())} to {end_date}")
        print(f"   ✅ Esports historical dataset ready!")

    async def run_backfill(self):
        """Main backfill entry point."""
        await self.run_complete_backfill()

async def main():
    """Main execution function."""
    backfill = EsportsBackfill()
    await backfill.run_backfill()

if __name__ == "__main__":
    asyncio.run(main())
