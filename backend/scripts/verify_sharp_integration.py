"""
Final Verification Script for Sharp Integration (Odds + Props)
"""
import asyncio
import sys
import structlog
from datetime import datetime

# Configure structlog for readability
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.JSONRenderer(indent=2, sort_keys=True)
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)
logger = structlog.get_logger()

# Import our new components
from streamers.sharp_odds import SHARP_ODDS_STREAMERS
from streamers.ev_sources import EV_SOURCES

async def verify_odds():
    print("\n" + "="*50)
    print("TEST 1: Sharp Odds (Main Markets) - DraftKings")
    print("="*50)
    
    # Get Streamer Class
    dk_key = "sharp_draftkings"
    if dk_key not in SHARP_ODDS_STREAMERS:
        print(f"❌ Error: {dk_key} not found in SHARP_ODDS_STREAMERS")
        return False
        
    streamer_cls = SHARP_ODDS_STREAMERS[dk_key]
    streamer = streamer_cls("test_dk", {})
    
    print("Connecting...")
    await streamer.connect()
    
    try:
        print("Fetching NBA Odds...")
        data = await streamer.fetch_data("basketball_nba")
        processed = await streamer.process_data(data)
        
        games = processed.get("games", [])
        print(f"✅ Fetched {len(games)} games.")
        
        if not games:
            print("⚠️ No games returned. Is it off-season or API issue?")
            return False
            
        game = games[0]
        print(f"\nSample Game: {game.get('away_team')} @ {game.get('home_team')} ({game.get('start_time')})")
        
        markets = game.get("normalized_markets", [])
        print(f"Markets Found: {len(markets)}")
        
        types = set(m.get("market_key") for m in markets)
        print(f"Market Types: {types}")
        
        required = {"h2h", "spreads", "totals"}
        if required.issubset(types):
            print("✅ All required market types (h2h, spreads, totals) present.")
        else:
            print(f"⚠️ Missing market types: {required - types}")
            
        # Inspect a random market
        if markets:
            print(f"Sample Market: {markets[0]}")
            
        return True
        
    except Exception as e:
        print(f"❌ Exception verifying odds: {e}")
        return False
    finally:
        await streamer.disconnect()


async def verify_props():
    print("\n" + "="*50)
    print("TEST 2: Sharp Props/EV (Player Props) - PrizePicks")
    print("="*50)
    
    # Get Streamer (SharpPropsStreamer is registered as 'sharp_props' in EV_SOURCES)
    # Check if 'sharp_props' is in EV_SOURCES?
    # In 'streamers/ev_sources.py', it is added.
    
    if "sharp_props" not in EV_SOURCES:
        print("❌ Error: sharp_props not found in EV_SOURCES")
        return False
        
    streamer_cls = EV_SOURCES["sharp_props"]
    # Config needs to specific books maybe? Or defaults to all? 
    # SharpPropsStreamer defaults to filtering relevant DFS books.
    streamer = streamer_cls("test_props", {})
    
    print("Connecting...")
    await streamer.connect()
    
    try:
        print("Fetching NBA Props...")
        # EV Streamers return raw data that needs processing
        raw_data = await streamer.fetch_data("basketball_nba")
        processed = await streamer.process_data(raw_data)
        
        props = processed.get("player_props", [])
        projections = processed.get("game_projections", [])
        
        print(f"✅ Fetched {len(props)} player props.")
        
        if not props:
             # Try NFL if NBA empty?
            print("⚠️ No NBA props. Trying NFL...")
            raw_data = await streamer.fetch_data("americanfootball_nfl")
            processed = await streamer.process_data(raw_data)
            props = processed.get("player_props", [])
            print(f"✅ Fetched {len(props)} NFL props.")

        if not props:
             print("⚠️ No props found for NBA or NFL.")
             # Check raw structure
             # raw_data for SharpPropsStreamer is dict of book_key -> result
             print(f"Raw Keys: {list(raw_data.keys())}")
             return False

        sample = props[0]
        print("\nSample Prop:")
        print(f"  Player: {sample.get('player_name')}")
        print(f"  Team: {sample.get('player_team')}")
        print(f"  Market: {sample.get('stat_type')} ({sample.get('line')})")
        print(f"  Book: {sample.get('book_id')} (Source: {sample.get('source')})")
        
        # Check EV specific fields
        ev_fields = ["ev_edge", "consensus_price", "sportsbook_projection"]
        found_ev = {k: sample.get(k) for k in ev_fields if sample.get(k) is not None}
        print(f"  EV Fields Found: {list(found_ev.keys())}")
        
        if found_ev:
             print("✅ EV Data present.")
        else:
             print("⚠️ EV Data MISSING from prop.")

        return True

    except Exception as e:
        print(f"❌ Exception verifying props: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await streamer.disconnect()

async def main():
    print("Starting Comprehensive Verification...")
    
    odds_ok = await verify_odds()
    props_ok = await verify_props()
    
    print("\n" + "="*50)
    print("VERIFICATION SUMMARY")
    print("="*50)
    print(f"Sharp Odds (Main Markets): {'✅ PASS' if odds_ok else '❌ FAIL'}")
    print(f"Sharp Props (EV/DFS):      {'✅ PASS' if props_ok else '❌ FAIL'}")
    
    if odds_ok and props_ok:
        print("\n🚀 READY FOR LAUNCH 🚀")
    else:
        print("\n⚠️  ISSUES DETECTED - CHECK LOGS ⚠️")

if __name__ == "__main__":
    asyncio.run(main())
