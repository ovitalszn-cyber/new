#!/usr/bin/env python3
"""
Test script for Dabble slips endpoint
Run this after restarting the server to verify the endpoint works
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
AUTH_HEADER = {"Authorization": "Bearer test"}

def test_dabble_slips(sport: str, num_legs: int, min_ev: float = 2.0, max_results: int = 3):
    """Test the Dabble slips endpoint"""
    url = f"{BASE_URL}/v4/sports/{sport}/dabble_slips"
    params = {
        "num_legs": num_legs,
        "min_ev_percentage": min_ev,
        "max_results": max_results
    }
    
    print(f"\n{'='*60}")
    print(f"Testing: {num_legs}-leg Dabble slips for {sport}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, params=params, headers=AUTH_HEADER, timeout=30)
        
        if response.status_code == 404:
            print("❌ Endpoint not found - server may need restart")
            return
        
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, dict) and "detail" in data:
            print(f"❌ Error: {data['detail']}")
            return
        
        print(f"✅ Found {len(data)} Dabble slips\n")
        
        for i, slip in enumerate(data[:max_results], 1):
            print(f"Slip {i}:")
            print(f"  Legs: {slip.get('num_legs')}")
            print(f"  Multiplier: {slip.get('payout_multiplier')}x")
            print(f"  Combined Payout: {slip.get('soft_parlay_payout', 0):.2f}x")
            print(f"  Sharp Probability: {slip.get('sharp_parlay_probability', 0):.4f}")
            print(f"  Total EV: {slip.get('total_expected_value_percent', 0):.2f}%")
            print(f"  Individual Legs:")
            
            games = {}
            for leg in slip.get('legs', []):
                match = leg.get('match_title', 'Unknown')
                player_desc = leg.get('outcome_description', 'Unknown')[:50]
                team = leg.get('player_info', {}).get('team', 'Unknown') if leg.get('player_info') else 'Unknown'
                odds = leg.get('soft_book_odds', 0)
                
                if match not in games:
                    games[match] = []
                games[match].append((player_desc, team, odds))
            
            for match, legs in games.items():
                print(f"    Game: {match}")
                for player, team, odds in legs:
                    print(f"      - {player} ({team}) - {odds:.2f}x")
            print()
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Testing Dabble Slips Endpoint")
    print("=" * 60)
    
    # Test 1: Single leg
    test_dabble_slips("basketball_nba", num_legs=1, min_ev=5.0, max_results=3)
    
    # Test 2: 2 legs
    test_dabble_slips("basketball_nba", num_legs=2, min_ev=2.0, max_results=3)
    
    # Test 3: 3 legs
    test_dabble_slips("basketball_nba", num_legs=3, min_ev=2.0, max_results=2)
    
    print("\n" + "="*60)
    print("✅ Testing complete!")
    print("="*60)



