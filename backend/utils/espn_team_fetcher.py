"""
ESPN Team Name Fetcher
Fetches team names from ESPN Fastcast API and updates team name mappings.
"""

import asyncio
import httpx
import json
from typing import Dict, List, Set
from collections import defaultdict
import structlog

logger = structlog.get_logger()

# ESPN sport mappings - comprehensive list
ESPN_SPORT_MAP = {
    # Basketball
    "basketball_nba": "basketball-nba",
    "basketball_wnba": "basketball-wnba",
    "basketball_ncaa": "basketball-mens-college-basketball",
    "basketball_ncaa_women": "basketball-womens-college-basketball",
    
    # American Football
    "americanfootball_nfl": "football-nfl",
    "americanfootball_ncaaf": "football-college-football",
    "football_nfl": "football-nfl",
    "football_ncaaf": "football-college-football",
    
    # Baseball
    "baseball_mlb": "baseball-mlb",
    
    # Ice Hockey
    "icehockey_nhl": "hockey-nhl",
    "hockey_nhl": "hockey-nhl",
    
    # Soccer - Major Leagues
    "soccer_epl": "soccer-eng.1",
    "soccer_championship": "soccer-eng.2",
    "soccer_serie_a": "soccer-ita.1",
    "soccer_ligue_1": "soccer-fra.1",
    "soccer_bundesliga": "soccer-ger.1",
    "soccer_laliga": "soccer-esp.1",
    "soccer_mls": "soccer-usa.1",
    "soccer_champions_league": "soccer-uefa.champions",
    "soccer_uefa_europa_league": "soccer-uefa.europa",
    "soccer_brasileiro_serie_a": "soccer-bra.1",
    "soccer_j_league": "soccer-jpn.1",
    "soccer_a_league": "soccer-aus.1",
    "soccer_eredivisie": "soccer-ned.1",
    "soccer_primera_liga": "soccer-por.1",
    "soccer_super_lig": "soccer-tur.1",
    "soccer_ekstraklasa": "soccer-pol.1",
    "soccer_eliteserien": "soccer-nor.1",
}

# ESPN Fastcast base URL
ESPN_FASTCAST_BASE = "https://fcast.espncdn.com/FastcastService/pubsub/profiles/12000/topic/event-{sport}/message/{message_id}/checkpoint"

# Headers for ESPN requests
ESPN_HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "origin": "https://www.espn.com",
    "referer": "https://www.espn.com/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
}


async def fetch_espn_teams_from_event(sport: str, message_id: str) -> List[Dict[str, str]]:
    """
    Fetch team data from a specific ESPN event.
    
    Args:
        sport: Sport key (e.g., "hockey-nhl")
        message_id: Event message ID
        
    Returns:
        List of team dictionaries with displayName, name, abbreviation, location
    """
    url = ESPN_FASTCAST_BASE.format(sport=sport, message_id=message_id)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=ESPN_HEADERS)
            response.raise_for_status()
            data = response.json()
            
            teams = []
            # Navigate through the nested JSON structure to find competitors
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        # Check for events array
                        events = item.get("events", [])
                        for event in events:
                            competitors = event.get("competitors", [])
                            for competitor in competitors:
                                if competitor.get("type") == "team":
                                    teams.append({
                                        "displayName": competitor.get("displayName", ""),
                                        "name": competitor.get("name", ""),
                                        "abbreviation": competitor.get("abbreviation", ""),
                                        "location": competitor.get("location", ""),
                                    })
            
            return teams
            
    except Exception as e:
        logger.warning("Failed to fetch ESPN teams", sport=sport, message_id=message_id, error=str(e))
        return []


async def fetch_espn_teams_direct(sport: str) -> List[Dict[str, str]]:
    """
    Fetch teams directly from ESPN teams API.
    
    Args:
        sport: Sport key (e.g., "hockey-nhl")
        
    Returns:
        List of team dictionaries
    """
    # ESPN API uses different format - convert sport key to API format
    # Most sports use format: sport/league (e.g., "basketball/nba")
    # Soccer uses: soccer/league (e.g., "soccer/eng.1")
    espn_sport_map = {
        "hockey-nhl": "hockey/nhl",
        "basketball-nba": "basketball/nba",
        "basketball-wnba": "basketball/wnba",
        "basketball-mens-college-basketball": "basketball/mens-college-basketball",
        "basketball-womens-college-basketball": "basketball/womens-college-basketball",
        "football-nfl": "football/nfl",
        "football-college-football": "football/college-football",
        "baseball-mlb": "baseball/mlb",
        "soccer-eng.1": "soccer/eng.1",
        "soccer-eng.2": "soccer/eng.2",
        "soccer-ita.1": "soccer/ita.1",
        "soccer-fra.1": "soccer/fra.1",
        "soccer-ger.1": "soccer/ger.1",
        "soccer-esp.1": "soccer/esp.1",
        "soccer-usa.1": "soccer/usa.1",
        "soccer-uefa.champions": "soccer/uefa.champions",
        "soccer-uefa.europa": "soccer/uefa.europa",
        "soccer-bra.1": "soccer/bra.1",
        "soccer-jpn.1": "soccer/jpn.1",
        "soccer-aus.1": "soccer/aus.1",
        "soccer-ned.1": "soccer/ned.1",
        "soccer-por.1": "soccer/por.1",
        "soccer-tur.1": "soccer/tur.1",
        "soccer-pol.1": "soccer/pol.1",
        "soccer-nor.1": "soccer/nor.1",
    }
    
    espn_sport = espn_sport_map.get(sport, sport.replace("-", "/"))
    url = f"https://site.api.espn.com/apis/site/v2/sports/{espn_sport}/teams"
    
    teams = []
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=ESPN_HEADERS)
            response.raise_for_status()
            data = response.json()
            
            # Extract teams from sports array
            sports = data.get("sports", [])
            for sport_data in sports:
                leagues = sport_data.get("leagues", [])
                for league in leagues:
                    teams_data = league.get("teams", [])
                    for team_item in teams_data:
                        team = team_item.get("team", {})
                        if team:
                            teams.append({
                                "displayName": team.get("displayName", "").strip(),
                                "name": team.get("name", "").strip(),
                                "abbreviation": team.get("abbreviation", "").strip(),
                                "location": team.get("location", "").strip(),
                            })
            
            logger.info("Fetched teams from ESPN teams API", sport=sport, count=len(teams))
            return teams
            
    except Exception as e:
        logger.warning("Failed to fetch ESPN teams directly", sport=sport, error=str(e))
        return []


async def fetch_espn_teams_from_schedule(sport: str, limit: int = 20) -> List[Dict[str, str]]:
    """
    Fetch teams from ESPN schedule/scoreboard for a sport.
    Uses ESPN's scoreboard API to get recent events and extract teams.
    
    Args:
        sport: Sport key (e.g., "hockey-nhl")
        limit: Number of recent events to check
        
    Returns:
        List of unique team dictionaries
    """
    # ESPN scoreboard API endpoint
    # Format: https://site.api.espn.com/apis/site/v2/sports/{sport}/scoreboard
    # ESPN API uses different format - convert sport key to API format
    # Most sports use format: sport/league (e.g., "basketball/nba")
    # Soccer uses: soccer/league (e.g., "soccer/eng.1")
    espn_sport_map = {
        "hockey-nhl": "hockey/nhl",
        "basketball-nba": "basketball/nba",
        "basketball-wnba": "basketball/wnba",
        "basketball-mens-college-basketball": "basketball/mens-college-basketball",
        "basketball-womens-college-basketball": "basketball/womens-college-basketball",
        "football-nfl": "football/nfl",
        "football-college-football": "football/college-football",
        "baseball-mlb": "baseball/mlb",
        "soccer-eng.1": "soccer/eng.1",
        "soccer-eng.2": "soccer/eng.2",
        "soccer-ita.1": "soccer/ita.1",
        "soccer-fra.1": "soccer/fra.1",
        "soccer-ger.1": "soccer/ger.1",
        "soccer-esp.1": "soccer/esp.1",
        "soccer-usa.1": "soccer/usa.1",
        "soccer-uefa.champions": "soccer/uefa.champions",
        "soccer-uefa.europa": "soccer/uefa.europa",
        "soccer-bra.1": "soccer/bra.1",
        "soccer-jpn.1": "soccer/jpn.1",
        "soccer-aus.1": "soccer/aus.1",
        "soccer-ned.1": "soccer/ned.1",
        "soccer-por.1": "soccer/por.1",
        "soccer-tur.1": "soccer/tur.1",
        "soccer-pol.1": "soccer/pol.1",
        "soccer-nor.1": "soccer/nor.1",
    }
    
    espn_sport = espn_sport_map.get(sport, sport.replace("-", "/"))
    url = f"https://site.api.espn.com/apis/site/v2/sports/{espn_sport}/scoreboard"
    
    teams_dict = {}  # Use dict to deduplicate by displayName
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=ESPN_HEADERS)
            response.raise_for_status()
            data = response.json()
            
            # Extract teams from events
            events = data.get("events", [])
            for event in events[:limit]:
                competitors = event.get("competitors", [])
                for competitor in competitors:
                    if competitor.get("type") == "team":
                        display_name = competitor.get("displayName", "").strip()
                        if display_name:
                            teams_dict[display_name] = {
                                "displayName": display_name,
                                "name": competitor.get("name", "").strip(),
                                "abbreviation": competitor.get("abbreviation", "").strip(),
                                "location": competitor.get("location", "").strip(),
                            }
            
            teams = list(teams_dict.values())
            logger.info("Fetched teams from ESPN", sport=sport, count=len(teams))
            return teams
            
    except Exception as e:
        logger.warning("Failed to fetch ESPN teams from schedule", sport=sport, error=str(e))
        return []


def build_team_mappings(teams: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Build team name mappings from ESPN team data.
    
    Args:
        teams: List of team dictionaries from ESPN
        
    Returns:
        Dictionary mapping normalized names to canonical names
    """
    mappings = {}
    
    for team in teams:
        display_name = team.get("displayName", "").strip()
        name = team.get("name", "").strip()
        abbreviation = team.get("abbreviation", "").strip()
        location = team.get("location", "").strip()
        
        if not display_name:
            continue
        
        canonical = display_name
        
        # Map various forms to canonical name
        # Full display name
        if display_name:
            normalized = display_name.lower().strip()
            mappings[normalized] = canonical
            # Remove periods and apostrophes
            mappings[normalized.replace(".", "").replace("'", "")] = canonical
        
        # Location + Name (e.g., "Dallas Stars")
        if location and name:
            full_name = f"{location} {name}"
            normalized = full_name.lower().strip()
            mappings[normalized] = canonical
            mappings[normalized.replace(".", "").replace("'", "")] = canonical
        
        # Just the name/mascot
        if name:
            normalized = name.lower().strip()
            mappings[normalized] = canonical
        
        # Abbreviation variations
        if abbreviation:
            abbrev_lower = abbreviation.lower().strip()
            # Map abbreviation + location
            if location:
                abbrev_location = f"{location} {abbreviation}"
                mappings[abbrev_location.lower()] = canonical
            # Map just abbreviation (less reliable, but included)
            mappings[abbrev_lower] = canonical
    
    return mappings


async def fetch_and_update_teams(sport: str) -> Dict[str, str]:
    """
    Fetch teams from ESPN and return mappings.
    
    Args:
        sport: Sport key (e.g., "icehockey_nhl")
        
    Returns:
        Dictionary of team name mappings
    """
    espn_sport = ESPN_SPORT_MAP.get(sport, sport.replace("_", "-"))
    
    # Try teams API first (most reliable)
    teams = await fetch_espn_teams_direct(espn_sport)
    
    # Fallback to schedule if teams API fails
    if not teams:
        logger.info("Teams API returned no results, trying schedule API", sport=sport)
        teams = await fetch_espn_teams_from_schedule(espn_sport, limit=50)
    
    if teams:
        mappings = build_team_mappings(teams)
        logger.info("Built team mappings", sport=sport, count=len(mappings))
        return mappings
    
    return {}


async def update_team_name_map(sport: str) -> int:
    """
    Fetch teams from ESPN and update the team name map.
    
    Args:
        sport: Sport key (e.g., "icehockey_nhl")
        
    Returns:
        Number of mappings added
    """
    from utils.team_names import add_team_mapping, TEAM_NAME_MAP
    
    mappings = await fetch_and_update_teams(sport)
    
    added_count = 0
    for normalized, canonical in mappings.items():
        if normalized not in TEAM_NAME_MAP:
            add_team_mapping(normalized, canonical)
            added_count += 1
    
    logger.info("Updated team name map", sport=sport, added=added_count, total=len(mappings))
    return added_count


if __name__ == "__main__":
    # Test the fetcher
    async def test():
        # Test NHL
        print("Testing NHL teams fetch...")
        teams = await fetch_espn_teams_direct("hockey-nhl")
        if not teams:
            teams = await fetch_espn_teams_from_schedule("hockey-nhl", limit=50)
        
        print(f"\nNHL teams fetched: {len(teams)}")
        for team in teams[:15]:
            print(f"  {team['displayName']} ({team['abbreviation']}) - {team['location']} {team['name']}")
        
        mappings = build_team_mappings(teams)
        print(f"\nMappings created: {len(mappings)}")
        for norm, canon in list(mappings.items())[:15]:
            print(f"  '{norm}' -> '{canon}'")
    
    asyncio.run(test())

