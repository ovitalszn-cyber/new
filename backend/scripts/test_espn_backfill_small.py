#!/usr/bin/env python3
"""
Small test of ESPN backfill system - 10 days from 2011
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.espn_historical_backfill_2011_2018 import ESPNHistoricalBackfill

async def test_small_backfill():
    """Test backfill with small date range."""
    print("🧪 TESTING ESPN BACKFILL - SMALL RANGE (10 DAYS)")
    print("=" * 60)
    
    backfill = ESPNHistoricalBackfill()
    
    # Override to test only 10 days from 2011
    original_method = backfill.get_complete_date_range
    
    def get_test_dates():
        dates = []
        start_date = datetime(2011, 1, 1)
        for i in range(10):
            dates.append(start_date + timedelta(days=i))
        return dates
    
    backfill.get_complete_date_range = get_test_dates
    
    try:
        await backfill.run_complete_backfill()
        print("✅ Small backfill test completed successfully!")
        
    except Exception as e:
        print(f"❌ Small backfill test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_small_backfill())
