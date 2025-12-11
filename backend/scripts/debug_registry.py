
import sys
import os

# Ensure path is correct
sys.path.append(os.getcwd())

try:
    from v6.odds.optimized_engine import ALL_BOOK_STREAMERS, SHARP_ODDS_STREAMERS
    print(f"SHARP_ODDS_STREAMERS count: {len(SHARP_ODDS_STREAMERS)}")
    print(f"ALL_BOOK_STREAMERS count: {len(ALL_BOOK_STREAMERS)}")
    
    if "sharp_draftkings" in SHARP_ODDS_STREAMERS:
        print("✅ sharp_draftkings found in SHARP_ODDS_STREAMERS")
    else:
        print("❌ sharp_draftkings NOT found in SHARP_ODDS_STREAMERS")
        
    if "sharp_draftkings" in ALL_BOOK_STREAMERS:
        print("✅ sharp_draftkings found in ALL_BOOK_STREAMERS")
    else:
        print("❌ sharp_draftkings NOT found in ALL_BOOK_STREAMERS")
        
except Exception as e:
    print(f"Error importing: {e}")
