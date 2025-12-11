"""
Pilot Test for Historical Odds Ingestion

Tests API behavior, data availability, and performance before scaling to full production.
"""

import sys
import os
# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
from datetime import datetime, timedelta
import structlog

from v6.historical.ingestion import HistoricalOddsIngestor
from v6.historical.database import get_historical_db

logger = structlog.get_logger(__name__)


async def test_historical_availability():
    """Test if historical data is available for different years and sports."""
    
    print("🧪 PILOT TEST: Historical Data Availability")
    print("=" * 60)
    
    # Initialize database and ingestor
    database = await get_historical_db()
    ingestor = HistoricalOddsIngestor(database)
    
    # Test parameters
    test_cases = [
        # (sport, year, book_id, book_name, test_date)
        ("basketball_nba", 2024, 83, "DraftKings", "2024-12-01"),
        ("basketball_nba", 2023, 83, "DraftKings", "2023-12-01"),
        ("basketball_nba", 2022, 83, "DraftKings", "2022-12-01"),
        ("basketball_nba", 2021, 83, "DraftKings", "2021-12-01"),
        ("basketball_nba", 2020, 83, "DraftKings", "2020-12-01"),
        ("basketball_nba", 2019, 83, "DraftKings", "2019-12-01"),
        
        ("americanfootball_nfl", 2024, 83, "DraftKings", "2024-12-01"),
        ("americanfootball_nfl", 2023, 83, "DraftKings", "2023-12-01"),
        ("americanfootball_nfl", 2019, 83, "DraftKings", "2019-12-01"),
    ]
    
    results = []
    
    for sport, year, book_id, book_name, date_str in test_cases:
        print(f"\n📅 Testing {sport} - {year} - {book_name} - {date_str}")
        
        try:
            # Create test job
            from v6.historical.ingestion import IngestionJob
            test_date = datetime.strptime(date_str, "%Y-%m-%d")
            job = IngestionJob(
                sport=sport,
                book_id=book_id,
                book_name=book_name,
                date=test_date
            )
            
            # Time the API call
            start_time = time.time()
            odds_data = await ingestor.fetch_historical_odds(job)
            end_time = time.time()
            
            # Record results
            result = {
                "sport": sport,
                "year": year,
                "book": book_name,
                "date": date_str,
                "success": True,
                "records": len(odds_data),
                "response_time": end_time - start_time,
                "data_available": len(odds_data) > 0
            }
            results.append(result)
            
            print(f"  ✅ SUCCESS: {len(odds_data)} records in {end_time - start_time:.2f}s")
            
            # Show sample data structure
            if odds_data:
                sample = odds_data[0]
                print(f"  📊 Sample keys: {list(sample.keys())}")
                if 'market_data' in sample:
                    market_data = sample['market_data']
                    if isinstance(market_data, dict) and 'game' in market_data:
                        game = market_data['game']
                        print(f"  🏀 Game info: {game.get('homeTeam', {}).get('name')} vs {game.get('awayTeam', {}).get('name')}")
            
        except Exception as e:
            result = {
                "sport": sport,
                "year": year,
                "book": book_name,
                "date": date_str,
                "success": False,
                "error": str(e),
                "data_available": False
            }
            results.append(result)
            print(f"  ❌ FAILED: {e}")
        
        # Rate limiting between tests
        await asyncio.sleep(2)
    
    # Analyze results
    print(f"\n📊 PILOT TEST RESULTS:")
    print("=" * 60)
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    data_available = [r for r in results if r.get('data_available', False)]
    
    print(f"Total tests: {len(results)}")
    print(f"Successful API calls: {len(successful_tests)}")
    print(f"Failed API calls: {len(failed_tests)}")
    print(f"Data available: {len(data_available)}")
    
    if successful_tests:
        avg_response_time = sum(r['response_time'] for r in successful_tests) / len(successful_tests)
        avg_records = sum(r['records'] for r in successful_tests) / len(successful_tests)
        print(f"Average response time: {avg_response_time:.2f}s")
        print(f"Average records per call: {avg_records:.1f}")
    
    # Show available years by sport
    print(f"\n📅 DATA AVAILABILITY BY SPORT:")
    for sport in set(r['sport'] for r in results):
        sport_results = [r for r in results if r['sport'] == sport and r.get('data_available', False)]
        years = sorted(set(r['year'] for r in sport_results))
        if years:
            print(f"  {sport}: {years}")
        else:
            print(f"  {sport}: No historical data available")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if len(data_available) == 0:
        print("  ❌ No historical data available - reconsider strategy")
    elif len(data_available) < len(results) * 0.5:
        print("  ⚠️  Limited historical data - start with available years only")
    else:
        print("  ✅ Good historical data availability - proceed with full ingestion")
    
    if successful_tests:
        print(f"  📈 Estimated full ingestion time: {avg_response_time * 332000 / 3600:.1f} hours")
        print(f"  📊 Estimated total records: {avg_records * 332000:.0f}")
    
    return results


async def test_rate_limiting():
    """Test optimal rate limiting to avoid API blocks."""
    
    print(f"\n🚦 RATE LIMITING TEST:")
    print("=" * 60)
    
    database = await get_historical_db()
    ingestor = HistoricalOddsIngestor(database)
    
    # Test different delays
    delays = [0.5, 1.0, 2.0, 3.0]
    test_date = datetime(2024, 12, 1)
    
    for delay in delays:
        print(f"\n⏱️  Testing {delay}s delay between requests...")
        
        start_time = time.time()
        success_count = 0
        error_count = 0
        
        # Test 5 consecutive requests
        for i in range(5):
            try:
                from v6.historical.ingestion import IngestionJob
                job = IngestionJob(
                    sport="basketball_nba",
                    book_id=83,
                    book_name="DraftKings",
                    date=test_date
                )
                
                await ingestor.fetch_historical_odds(job)
                success_count += 1
                print(f"    Request {i+1}: ✅")
                
            except Exception as e:
                error_count += 1
                print(f"    Request {i+1}: ❌ {e}")
            
            await asyncio.sleep(delay)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"  Results: {success_count}/5 successful in {total_time:.1f}s")
        print(f"  Success rate: {success_count/5*100:.0f}%")
        
        if success_count == 5:
            print(f"  ✅ {delay}s delay works well")
            break
        else:
            print(f"  ⚠️  {delay}s delay caused issues")
    
    print(f"\n💡 RATE LIMITING RECOMMENDATION:")
    print(f"  Use 2-3 second delays between requests for reliability")


async def main():
    """Run pilot tests to validate historical ingestion strategy."""
    
    print("🚀 HISTORICAL ODDS INGESTION - PILOT TEST SUITE")
    print("=" * 60)
    print("Testing API availability, data quality, and rate limiting")
    print("Before scaling to full production (2019-2024, multiple sports)")
    
    try:
        # Test 1: Historical data availability
        availability_results = await test_historical_availability()
        
        # Test 2: Rate limiting optimization
        await test_rate_limiting()
        
        print(f"\n🎯 PILOT TEST COMPLETE")
        print("=" * 60)
        print("Review results above before proceeding to full ingestion")
        
    except Exception as e:
        logger.error("Pilot test failed", error=str(e))
        print(f"❌ Pilot test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
