"""Test script to verify Lunosoft V6 client fetches both player props and traditional markets."""

import asyncio
import json
from streamers.lunosoft import LunosoftClient


async def test_lunosoft_client():
    """Test the enhanced Lunosoft client."""
    print("=" * 80)
    print("Testing Lunosoft V6 Client")
    print("=" * 80)
    
    # Create client
    client = LunosoftClient({"max_concurrency": 8})
    
    # Connect
    print("\n1. Connecting to Lunosoft API...")
    connected = await client.connect()
    if not connected:
        print("❌ Failed to connect")
        return
    print("✅ Connected successfully")
    
    # Test NBA (should have both props and traditional markets)
    print("\n2. Fetching NBA data...")
    nba_data = await client.fetch_sports("basketball_nba")
    
    if nba_data.get("sports"):
        sport_section = nba_data["sports"][0]
        print(f"✅ Sport: {sport_section.get('sport_name')}")
        print(f"   Sport ID: {sport_section.get('sport_id')}")
        print(f"   Games found: {len(sport_section.get('games', []))}")
        print(f"   Stat types: {len(sport_section.get('stat_types', []))}")
        print(f"   Player props: {len(sport_section.get('props', []))}")
        print(f"   Traditional markets: {len(sport_section.get('traditional_markets', []))}")
        
        # Show sample prop
        if sport_section.get('props'):
            sample_prop = sport_section['props'][0]
            print(f"\n   Sample Player Prop:")
            print(f"   - Player: {sample_prop.get('player_name')}")
            print(f"   - Stat: {sample_prop.get('stat_type_name')}")
            print(f"   - Line: {sample_prop.get('stat_value')}")
            print(f"   - Book: {sample_prop.get('sportsbook_name')} (ID: {sample_prop.get('sportsbook_id')})")
            print(f"   - Direction: {sample_prop.get('direction')}")
            print(f"   - Odds: {sample_prop.get('odds')}")
        
        # Show traditional market info
        if sport_section.get('traditional_markets'):
            print(f"\n   Traditional Markets Response Type: {type(sport_section['traditional_markets'])}")
            if isinstance(sport_section['traditional_markets'], list) and sport_section['traditional_markets']:
                print(f"   First item keys: {list(sport_section['traditional_markets'][0].keys())[:10]}")
            elif isinstance(sport_section['traditional_markets'], dict):
                print(f"   Response keys: {list(sport_section['traditional_markets'].keys())[:10]}")
    else:
        print("❌ No sports data returned")
    
    # Test filtering by book (DraftKings = 83)
    print("\n3. Testing book-specific filtering (DraftKings)...")
    dk_data = await client.fetch_book_props(83, "basketball_nba")
    
    if dk_data.get("sports"):
        dk_section = dk_data["sports"][0]
        print(f"✅ DraftKings NBA data:")
        print(f"   Player props: {len(dk_section.get('props', []))}")
        
        # Verify all props are from DraftKings
        if dk_section.get('props'):
            unique_books = set(p.get('sportsbook_id') for p in dk_section['props'])
            print(f"   Unique sportsbook IDs: {unique_books}")
            if unique_books == {83}:
                print("   ✅ All props correctly filtered to DraftKings")
            else:
                print(f"   ❌ Found props from other books: {unique_books}")
    else:
        print("❌ No DraftKings data returned")
    
    # Test NFL (uses week parameter)
    print("\n4. Testing NFL (week-based endpoint)...")
    nfl_data = await client.fetch_sports("americanfootball_nfl")
    
    if nfl_data.get("sports"):
        nfl_section = nfl_data["sports"][0]
        print(f"✅ NFL data:")
        print(f"   Games: {len(nfl_section.get('games', []))}")
        print(f"   Player props: {len(nfl_section.get('props', []))}")
        print(f"   Traditional markets: {len(nfl_section.get('traditional_markets', []))}")
    else:
        print("❌ No NFL data returned")
    
    # Test supported sports
    print("\n5. Supported sports:")
    for sport_key in client.get_supported_sports():
        sport_info = client.SPORT_MAP[sport_key]
        print(f"   - {sport_key}: {sport_info['name']} (ID: {sport_info['sport_id']})")
    
    # Disconnect
    print("\n6. Disconnecting...")
    await client.disconnect()
    print("✅ Disconnected")
    
    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_lunosoft_client())
