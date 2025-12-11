"""
Team Name Normalization
Canonicalizes team names across different bookmakers.
"""

from typing import Dict, Optional, List
import re
import structlog
import asyncio
import json
from pathlib import Path

logger = structlog.get_logger()

# Import sport-aware data
try:
    from data.team_canonical_map import CANONICAL_TEAM_SPORT_MAP
    from data.team_aliases import GLOBAL_ABBREVIATIONS, SPORT_SPECIFIC_ALIASES
except ImportError:
    CANONICAL_TEAM_SPORT_MAP = {}
    GLOBAL_ABBREVIATIONS = {}
    SPORT_SPECIFIC_ALIASES = {}

# Load dynamic mappings from JSON file if it exists
def _load_dynamic_mappings() -> Dict[str, str]:
    """Load additional team name mappings from JSON file."""
    dynamic_mappings_file = Path(__file__).parent.parent.parent / "team_name_mappings.json"
    if dynamic_mappings_file.exists():
        try:
            with open(dynamic_mappings_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Failed to load dynamic team mappings", error=str(e))
    return {}

# Canonical team name mappings
TEAM_NAME_MAP: Dict[str, str] = {
    # NBA
    "atlanta hawks": "Atlanta Hawks",
    "boston celtics": "Boston Celtics",
    "brooklyn nets": "Brooklyn Nets",
    "charlotte hornets": "Charlotte Hornets",
    "chicago bulls": "Chicago Bulls",
    "cleveland cavaliers": "Cleveland Cavaliers",
    "dallas mavericks": "Dallas Mavericks",
    "mavericks": "Dallas Mavericks",
    "denver nuggets": "Denver Nuggets",
    "detroit pistons": "Detroit Pistons",
    "golden state warriors": "Golden State Warriors",
    "houston rockets": "Houston Rockets",
    "indiana pacers": "Indiana Pacers",
    "la clippers": "LA Clippers",
    "los angeles clippers": "LA Clippers",
    "l.a. clippers": "LA Clippers",
    "los angeles lakers": "Los Angeles Lakers",
    "la lakers": "Los Angeles Lakers",
    "l.a. lakers": "Los Angeles Lakers",
    "memphis grizzlies": "Memphis Grizzlies",
    "miami heat": "Miami Heat",
    "milwaukee bucks": "Milwaukee Bucks",
    "minnesota timberwolves": "Minnesota Timberwolves",
    "new orleans pelicans": "New Orleans Pelicans",
    "new york knicks": "New York Knicks",
    "oklahoma city thunder": "Oklahoma City Thunder",
    "orlando magic": "Orlando Magic",
    "philadelphia 76ers": "Philadelphia 76ers",
    "phoenix suns": "Phoenix Suns",
    "portland trail blazers": "Portland Trail Blazers",
    "sacramento kings": "Sacramento Kings",
    "san antonio spurs": "San Antonio Spurs",
    "toronto raptors": "Toronto Raptors",
    "utah jazz": "Utah Jazz",
    "washington wizards": "Washington Wizards",

    # NFL
    "arizona cardinals": "Arizona Cardinals",
    "atlanta falcons": "Atlanta Falcons",
    "baltimore ravens": "Baltimore Ravens",
    "buffalo bills": "Buffalo Bills",
    "carolina panthers": "Carolina Panthers",
    "chicago bears": "Chicago Bears",
    "cincinnati bengals": "Cincinnati Bengals",
    "cleveland browns": "Cleveland Browns",
    "dallas cowboys": "Dallas Cowboys",
    "denver broncos": "Denver Broncos",
    "detroit lions": "Detroit Lions",
    "green bay packers": "Green Bay Packers",
    "houston texans": "Houston Texans",
    "indianapolis colts": "Indianapolis Colts",
    "jacksonville jaguars": "Jacksonville Jaguars",
    "kansas city chiefs": "Kansas City Chiefs",
    "las vegas raiders": "Las Vegas Raiders",
    "los angeles chargers": "Los Angeles Chargers",
    "los angeles rams": "Los Angeles Rams",
    "miami dolphins": "Miami Dolphins",
    "minnesota vikings": "Minnesota Vikings",
    "new england patriots": "New England Patriots",
    "new orleans saints": "New Orleans Saints",
    "new york giants": "New York Giants",
    "new york jets": "New York Jets",
    "philadelphia eagles": "Philadelphia Eagles",
    "pittsburgh steelers": "Pittsburgh Steelers",
    "san francisco 49ers": "San Francisco 49ers",
    "seattle seahawks": "Seattle Seahawks",
    "tampa bay buccaneers": "Tampa Bay Buccaneers",
    "tennessee titans": "Tennessee Titans",
    "washington commanders": "Washington Commanders",

    # MLB
    "arizona diamondbacks": "Arizona Diamondbacks",
    "atlanta braves": "Atlanta Braves",
    "baltimore orioles": "Baltimore Orioles",
    "boston red sox": "Boston Red Sox",
    "chicago cubs": "Chicago Cubs",
    "chicago white sox": "Chicago White Sox",
    "cincinnati reds": "Cincinnati Reds",
    "cleveland guardians": "Cleveland Guardians",
    "colorado rockies": "Colorado Rockies",
    "detroit tigers": "Detroit Tigers",
    "houston astros": "Houston Astros",
    "kansas city royals": "Kansas City Royals",
    "los angeles angels": "Los Angeles Angels",
    "los angeles dodgers": "Los Angeles Dodgers",
    "miami marlins": "Miami Marlins",
    "milwaukee brewers": "Milwaukee Brewers",
    "minnesota twins": "Minnesota Twins",
    "new york mets": "New York Mets",
    "new york yankees": "New York Yankees",
    "oakland athletics": "Oakland Athletics",
    "philadelphia phillies": "Philadelphia Phillies",
    "pittsburgh pirates": "Pittsburgh Pirates",
    "san diego padres": "San Diego Padres",
    "san francisco giants": "San Francisco Giants",
    "seattle mariners": "Seattle Mariners",
    "st. louis cardinals": "St. Louis Cardinals",
    "tampa bay rays": "Tampa Bay Rays",
    "texas rangers": "Texas Rangers",
    "toronto blue jays": "Toronto Blue Jays",
    "washington nationals": "Washington Nationals",

    # NHL
    "anaheim ducks": "Anaheim Ducks",
    "arizona coyotes": "Arizona Coyotes",
    "boston bruins": "Boston Bruins",
    "buffalo sabres": "Buffalo Sabres",
    "calgary flames": "Calgary Flames",
    "carolina hurricanes": "Carolina Hurricanes",
    "chicago blackhawks": "Chicago Blackhawks",
    "colorado avalanche": "Colorado Avalanche",
    "columbus blue jackets": "Columbus Blue Jackets",
    "dallas stars": "Dallas Stars",
    "detroit red wings": "Detroit Red Wings",
    "edmonton oilers": "Edmonton Oilers",
    "florida panthers": "Florida Panthers",
    "los angeles kings": "Los Angeles Kings",
    "minnesota wild": "Minnesota Wild",
    "montreal canadiens": "Montreal Canadiens",
    "nashville predators": "Nashville Predators",
    "new jersey devils": "New Jersey Devils",
    "new york islanders": "New York Islanders",
    "new york rangers": "New York Rangers",
    "ottawa senators": "Ottawa Senators",
    "philadelphia flyers": "Philadelphia Flyers",
    "pittsburgh penguins": "Pittsburgh Penguins",
    "san jose sharks": "San Jose Sharks",
    "seattle kraken": "Seattle Kraken",
    "st. louis blues": "St. Louis Blues",
    "tampa bay lightning": "Tampa Bay Lightning",
    "toronto maple leafs": "Toronto Maple Leafs",
    "vancouver canucks": "Vancouver Canucks",
    "vegas golden knights": "Vegas Golden Knights",
    "washington capitals": "Washington Capitals",
    "winnipeg jets": "Winnipeg Jets",
}

# Common team abbreviations (primarily NBA) to canonical names
TEAM_ABBREVIATION_MAP: Dict[str, str] = {
    # NBA abbreviations
    "atl": "Atlanta Hawks",
    "bos": "Boston Celtics",
    "bkn": "Brooklyn Nets",
    "cha": "Charlotte Hornets",
    "chi": "Chicago Bulls",
    "cle": "Cleveland Cavaliers",
    "dal": "Dallas Mavericks",
    "den": "Denver Nuggets",
    "det": "Detroit Pistons",
    "gsw": "Golden State Warriors",
    "hou": "Houston Rockets",
    "ind": "Indiana Pacers",
    "lac": "LA Clippers",
    "lal": "Los Angeles Lakers",
    "mem": "Memphis Grizzlies",
    "mia": "Miami Heat",
    "mil": "Milwaukee Bucks",
    "min": "Minnesota Timberwolves",
    "nop": "New Orleans Pelicans",
    "nor": "New Orleans Pelicans",
    "nyk": "New York Knicks",
    "okc": "Oklahoma City Thunder",
    "orl": "Orlando Magic",
    "phi": "Philadelphia 76ers",
    "phx": "Phoenix Suns",
    "por": "Portland Trail Blazers",
    "sac": "Sacramento Kings",
    "sas": "San Antonio Spurs",
    "sa": "San Antonio Spurs",
    "tor": "Toronto Raptors",
    "uta": "Utah Jazz",
    "uth": "Utah Jazz",
    "was": "Washington Wizards",
    "wsh": "Washington Wizards",
}

# Map sport aliases to canonical sport keys
SPORT_ALIASES: Dict[str, str] = {
    "nba": "basketball_nba",
    "basketball": "basketball_nba",
    "basketball_nba": "basketball_nba",
    "wnba": "basketball_wnba",
    "basketball_wnba": "basketball_wnba",
    "nfl": "americanfootball_nfl",
    "football": "americanfootball_nfl",
    "football_nfl": "americanfootball_nfl",
    "americanfootball_nfl": "americanfootball_nfl",
    "mlb": "baseball_mlb",
    "baseball": "baseball_mlb",
    "baseball_mlb": "baseball_mlb",
    "nhl": "icehockey_nhl",
    "hockey": "icehockey_nhl",
    "icehockey_nhl": "icehockey_nhl",
    "soccer": "soccer_mls",
    "mls": "soccer_mls",
    "soccer_mls": "soccer_mls",
    "golf": "golf",
    "pga": "golf",
    "mma": "mma_ufc",
    "ufc": "mma_ufc",
    "mma_ufc": "mma_ufc",
}

# Sport-specific overrides for ambiguous city/abbreviation mappings
SPORT_CITY_OVERRIDES: Dict[str, Dict[str, str]] = {
    "basketball_nba": {
        "atl": "Atlanta Hawks",
        "atlanta": "Atlanta Hawks",
        "bos": "Boston Celtics",
        "boston": "Boston Celtics",
        "bkn": "Brooklyn Nets",
        "brooklyn": "Brooklyn Nets",
        "cha": "Charlotte Hornets",
        "charlotte": "Charlotte Hornets",
        "chi": "Chicago Bulls",
        "chicago": "Chicago Bulls",
        "cle": "Cleveland Cavaliers",
        "cleveland": "Cleveland Cavaliers",
        "dal": "Dallas Mavericks",
        "dallas": "Dallas Mavericks",
        "den": "Denver Nuggets",
        "denver": "Denver Nuggets",
        "det": "Detroit Pistons",
        "detroit": "Detroit Pistons",
        "gsw": "Golden State Warriors",
        "golden state": "Golden State Warriors",
        "hou": "Houston Rockets",
        "houston": "Houston Rockets",
        "ind": "Indiana Pacers",
        "indiana": "Indiana Pacers",
        "lac": "LA Clippers",
        "la clippers": "LA Clippers",
        "lal": "Los Angeles Lakers",
        "la lakers": "Los Angeles Lakers",
        "los angeles lakers": "Los Angeles Lakers",
        "los angeles clippers": "LA Clippers",
        "mem": "Memphis Grizzlies",
        "memphis": "Memphis Grizzlies",
        "mia": "Miami Heat",
        "miami": "Miami Heat",
        "mil": "Milwaukee Bucks",
        "milwaukee": "Milwaukee Bucks",
        "min": "Minnesota Timberwolves",
        "minnesota": "Minnesota Timberwolves",
        "nop": "New Orleans Pelicans",
        "nor": "New Orleans Pelicans",
        "new orleans": "New Orleans Pelicans",
        "ny": "New York Knicks",
        "nyk": "New York Knicks",
        "new york": "New York Knicks",
        "okc": "Oklahoma City Thunder",
        "oklahoma city": "Oklahoma City Thunder",
        "orl": "Orlando Magic",
        "orlando": "Orlando Magic",
        "phi": "Philadelphia 76ers",
        "philadelphia": "Philadelphia 76ers",
        "phx": "Phoenix Suns",
        "phoenix": "Phoenix Suns",
        "por": "Portland Trail Blazers",
        "portland": "Portland Trail Blazers",
        "sac": "Sacramento Kings",
        "sacramento": "Sacramento Kings",
        "sas": "San Antonio Spurs",
        "san antonio": "San Antonio Spurs",
        "tor": "Toronto Raptors",
        "toronto": "Toronto Raptors",
        "uta": "Utah Jazz",
        "utah": "Utah Jazz",
        "was": "Washington Wizards",
        "washington": "Washington Wizards",
    },
    "americanfootball_nfl": {
        "ari": "Arizona Cardinals",
        "arizona": "Arizona Cardinals",
        "atl": "Atlanta Falcons",
        "atlanta": "Atlanta Falcons",
        "bal": "Baltimore Ravens",
        "baltimore": "Baltimore Ravens",
        "buf": "Buffalo Bills",
        "buffalo": "Buffalo Bills",
        "car": "Carolina Panthers",
        "carolina": "Carolina Panthers",
        "chi": "Chicago Bears",
        "chicago": "Chicago Bears",
        "cin": "Cincinnati Bengals",
        "cincinnati": "Cincinnati Bengals",
        "cle": "Cleveland Browns",
        "cleveland": "Cleveland Browns",
        "dal": "Dallas Cowboys",
        "dallas": "Dallas Cowboys",
        "den": "Denver Broncos",
        "denver": "Denver Broncos",
        "det": "Detroit Lions",
        "detroit": "Detroit Lions",
        "gb": "Green Bay Packers",
        "green bay": "Green Bay Packers",
        "hou": "Houston Texans",
        "houston": "Houston Texans",
        "ind": "Indianapolis Colts",
        "indianapolis": "Indianapolis Colts",
        "jac": "Jacksonville Jaguars",
        "jacksonville": "Jacksonville Jaguars",
        "kc": "Kansas City Chiefs",
        "kansas city": "Kansas City Chiefs",
        "la": "Los Angeles Rams",  # Default LA to Rams
        "lar": "Los Angeles Rams",
        "lac": "Los Angeles Chargers",
        "los angeles": "Los Angeles Rams",
        "lv": "Las Vegas Raiders",
        "las vegas": "Las Vegas Raiders",
        "mia": "Miami Dolphins",
        "miami": "Miami Dolphins",
        "min": "Minnesota Vikings",
        "minnesota": "Minnesota Vikings",
        "ne": "New England Patriots",
        "new england": "New England Patriots",
        "no": "New Orleans Saints",
        "new orleans": "New Orleans Saints",
        "ny": "New York Giants",
        "nyg": "New York Giants",
        "nyj": "New York Jets",
        "new york": "New York Giants",
        "phi": "Philadelphia Eagles",
        "philadelphia": "Philadelphia Eagles",
        "pit": "Pittsburgh Steelers",
        "pittsburgh": "Pittsburgh Steelers",
        "sea": "Seattle Seahawks",
        "seattle": "Seattle Seahawks",
        "sf": "San Francisco 49ers",
        "san francisco": "San Francisco 49ers",
        "tb": "Tampa Bay Buccaneers",
        "tampa bay": "Tampa Bay Buccaneers",
        "ten": "Tennessee Titans",
        "tennessee": "Tennessee Titans",
        "was": "Washington Commanders",
        "washington": "Washington Commanders",
    },
    "baseball_mlb": {
        "mia": "Miami Marlins",
        "miami": "Miami Marlins",
        "det": "Detroit Tigers",
        "detroit": "Detroit Tigers",
        "atl": "Atlanta Braves",
        "atlanta": "Atlanta Braves",
        "chi": "Chicago Cubs",
        "chicago": "Chicago Cubs",
        "phi": "Philadelphia Phillies",
        "philadelphia": "Philadelphia Phillies",
        "ny": "New York Mets",
        "new york": "New York Mets",
    },
    "icehockey_nhl": {
        "ana": "Anaheim Ducks",
        "anaheim": "Anaheim Ducks",
        "ari": "Arizona Coyotes",
        "arizona": "Arizona Coyotes",
        "bos": "Boston Bruins",
        "boston": "Boston Bruins",
        "buf": "Buffalo Sabres",
        "buffalo": "Buffalo Sabres",
        "cgy": "Calgary Flames",
        "calgary": "Calgary Flames",
        "car": "Carolina Hurricanes",
        "carolina": "Carolina Hurricanes",
        "chi": "Chicago Blackhawks",
        "chicago": "Chicago Blackhawks",
        "col": "Colorado Avalanche",
        "colorado": "Colorado Avalanche",
        "cbj": "Columbus Blue Jackets",
        "columbus": "Columbus Blue Jackets",
        "dal": "Dallas Stars",
        "dallas": "Dallas Stars",
        "det": "Detroit Red Wings",
        "detroit": "Detroit Red Wings",
        "edm": "Edmonton Oilers",
        "edmonton": "Edmonton Oilers",
        "fla": "Florida Panthers",
        "florida": "Florida Panthers",
        "mia": "Florida Panthers",
        "la": "Los Angeles Kings",
        "lak": "Los Angeles Kings",
        "los angeles": "Los Angeles Kings",
        "min": "Minnesota Wild",
        "minnesota": "Minnesota Wild",
        "mtl": "Montreal Canadiens",
        "montreal": "Montreal Canadiens",
        "nsh": "Nashville Predators",
        "nashville": "Nashville Predators",
        "nj": "New Jersey Devils",
        "njd": "New Jersey Devils",
        "new jersey": "New Jersey Devils",
        "nyi": "New York Islanders",
        "nyr": "New York Rangers",
        "ny": "New York Rangers",
        "new york": "New York Rangers",
        "ott": "Ottawa Senators",
        "ottawa": "Ottawa Senators",
        "phi": "Philadelphia Flyers",
        "philadelphia": "Philadelphia Flyers",
        "pit": "Pittsburgh Penguins",
        "pittsburgh": "Pittsburgh Penguins",
        "sj": "San Jose Sharks",
        "san jose": "San Jose Sharks",
        "sea": "Seattle Kraken",
        "seattle": "Seattle Kraken",
        "stl": "St. Louis Blues",
        "st louis": "St. Louis Blues",
        "tb": "Tampa Bay Lightning",
        "tbl": "Tampa Bay Lightning",
        "tampa bay": "Tampa Bay Lightning",
        "tor": "Toronto Maple Leafs",
        "toronto": "Toronto Maple Leafs",
        "uta": "Utah Hockey Club",
        "utah": "Utah Hockey Club",
        "van": "Vancouver Canucks",
        "vancouver": "Vancouver Canucks",
        "vgk": "Vegas Golden Knights",
        "vegas": "Vegas Golden Knights",
        "las vegas": "Vegas Golden Knights",
        "wsh": "Washington Capitals",
        "was": "Washington Capitals",
        "washington": "Washington Capitals",
        "wpg": "Winnipeg Jets",
        "winnipeg": "Winnipeg Jets",
    },
    "soccer_mls": {
        "mia": "Inter Miami CF",
        "miami": "Inter Miami CF",
        "atl": "Atlanta United",
        "atlanta": "Atlanta United",
        "chi": "Chicago Fire",
        "chicago": "Chicago Fire",
        "phi": "Philadelphia Union",
        "philadelphia": "Philadelphia Union",
        "por": "Portland Timbers",
        "portland": "Portland Timbers",
        "min": "Minnesota United",
        "minnesota": "Minnesota United",
        "ny": "New York Red Bulls",
        "new york": "New York Red Bulls",
    },
}

# Load and merge dynamic mappings from JSON file
_dynamic_mappings = _load_dynamic_mappings()
TEAM_NAME_MAP.update(_dynamic_mappings)


INDIVIDUAL_SPORTS = {
    "golf", "tennis", "mma", "ufc", "boxing", "wrestling",
    "esports", "esports_lol", "esports_cs2", "esports_valorant",
    "esports_dota2", "esports_cod"
}

SPORT_ALIASES = {
    "nba": "basketball_nba",
    "basketball": "basketball_nba",
    "basketball_nba": "basketball_nba",
    "wnba": "basketball_wnba",
    "basketball_wnba": "basketball_wnba",
    "nfl": "americanfootball_nfl",
    "football": "americanfootball_nfl",
    "football_nfl": "americanfootball_nfl",
    "americanfootball_nfl": "americanfootball_nfl",
    "mlb": "baseball_mlb",
    "baseball": "baseball_mlb",
    "baseball_mlb": "baseball_mlb",
    "nhl": "icehockey_nhl",
    "hockey": "icehockey_nhl",
    "icehockey_nhl": "icehockey_nhl",
    "soccer": "soccer_mls",
    "mls": "soccer_mls",
    "soccer_mls": "soccer_mls",
}


def _normalize_raw_team(name: str) -> str:
    if not name:
        return ""
    cleaned = name.strip()
    cleaned = re.sub(r"\s+fc$", "", cleaned, flags=re.IGNORECASE)
    # Remove incomplete parenthetical suffixes and complete ones
    cleaned = re.sub(r"\s*\([^)]*$", "", cleaned).strip()  # Incomplete: "(ARCHITEC"
    cleaned = re.sub(r"\s*\([^)]*\)", "", cleaned).strip()  # Complete: "(ARCHITECT)"
    cleaned = re.sub(r"[\.']", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _resolve_sport_key(sport: Optional[str]) -> Optional[str]:
    if not sport:
        return None
    key = sport.lower().strip()
    return SPORT_ALIASES.get(key, key)


def _sport_specific_lookup(normalized: str, sport_key: str) -> Optional[str]:
    if not sport_key:
        return None
    aliases = SPORT_SPECIFIC_ALIASES.get(sport_key, {})
    # Exact match on alias key
    canonical = aliases.get(normalized.upper()) or aliases.get(normalized.lower())
    if canonical:
        return canonical
    # Match on cleaned alias names
    for alias, team in aliases.items():
        if normalized.lower() == alias.lower() or normalized.lower() == team.lower():
            return team
    return None


def _global_abbreviation_lookup(normalized: str, sport_key: Optional[str]) -> Optional[str]:
    if normalized.upper() not in GLOBAL_ABBREVIATIONS:
        return None
    candidates = GLOBAL_ABBREVIATIONS[normalized.upper()]
    if sport_key:
        for team in candidates:
            if CANONICAL_TEAM_SPORT_MAP.get(team) == sport_key:
                return team
    return candidates[0] if candidates else None


def _direct_canonical_lookup(normalized: str, sport_key: Optional[str]) -> Optional[str]:
    for team, team_sport in CANONICAL_TEAM_SPORT_MAP.items():
        if normalized.lower() == team.lower():
            if not sport_key or sport_key == team_sport:
                return team
    return None


def _match_by_suffix(suffix: str, sport_key: Optional[str]) -> Optional[str]:
    """Match canonical team when only nickname/suffix is provided."""
    suffix_lower = suffix.lower().strip()
    if not suffix_lower:
        return None

    candidates = []
    for team, team_sport in CANONICAL_TEAM_SPORT_MAP.items():
        if sport_key and team_sport != sport_key:
            continue
        if team.lower().endswith(suffix_lower):
            candidates.append(team)

    if len(candidates) == 1:
        return candidates[0]
    return None


def canonicalize_team(team_name: str, sport: Optional[str] = None) -> Optional[str]:
    """Canonicalize a team name using sport-aware logic."""
    if not team_name:
        return None

    normalized_raw = _normalize_raw_team(team_name)
    if not normalized_raw:
        return None

    sport_key = _resolve_sport_key(sport)
    if sport_key and sport_key in INDIVIDUAL_SPORTS:
        return None

    # 1. Sport-specific alias lookup
    if sport_key:
        sport_canonical = _sport_specific_lookup(normalized_raw, sport_key)
        if sport_canonical:
            return sport_canonical

        parts = normalized_raw.split(" ", 1)
        if parts:
            prefix = parts[0].strip()
            if prefix:
                prefix_match = _sport_specific_lookup(prefix, sport_key)
                if prefix_match:
                    return prefix_match

    # 2. Direct canonical name match (validate sport)
    direct = _direct_canonical_lookup(normalized_raw, sport_key)
    if direct:
        return direct

    # 3. Global abbreviations with sport validation
    global_match = _global_abbreviation_lookup(normalized_raw, sport_key)
    if global_match:
        if not sport_key or CANONICAL_TEAM_SPORT_MAP.get(global_match) == sport_key:
            return global_match

    # 4. Legacy TEAM_NAME_MAP
    legacy_key = normalized_raw.lower()
    legacy_match = TEAM_NAME_MAP.get(legacy_key)
    if legacy_match and (not sport_key or CANONICAL_TEAM_SPORT_MAP.get(legacy_match) == sport_key):
        return legacy_match

    # 5. Abbreviation map
    abbrev_match = TEAM_ABBREVIATION_MAP.get(legacy_key)
    if abbrev_match and (not sport_key or CANONICAL_TEAM_SPORT_MAP.get(abbrev_match) == sport_key):
        return abbrev_match

    # 6. Handle alias-prefix formats (e.g., "WSH Wizards", "TB Lightning")
    parts = normalized_raw.split(" ", 1)
    if len(parts) == 2:
        _, remainder = parts
        remainder = remainder.strip()
        if remainder:
            remainder_match = _match_by_suffix(remainder, sport_key)
            if remainder_match:
                return remainder_match

    logger.warning(
        "No canonical name found for team",
        raw_team_name=team_name,
        normalized=normalized_raw,
        sport=sport_key,
    )
    return None


def add_team_mapping(raw_name: str, canonical_name: str):
    """
    Add a new team name mapping (for dynamic updates).

    Args:
        raw_name: Raw team name from bookmaker
        canonical_name: Canonical team name
    """
    TEAM_NAME_MAP[raw_name.lower().strip()] = canonical_name
    logger.info("Added team name mapping", raw=raw_name, canonical=canonical_name)


async def sync_teams_from_espn(sport: str) -> int:
    """
    Sync team names from ESPN API for a given sport.
    
    Args:
        sport: Sport key (e.g., "icehockey_nhl", "basketball_nba")
        
    Returns:
        Number of mappings added
    """
    try:
        from utils.espn_team_fetcher import update_team_name_map
        return await update_team_name_map(sport)
    except Exception as e:
        logger.error("Failed to sync teams from ESPN", sport=sport, error=str(e))
        return 0


def get_all_teams(sport: str = "nba") -> list:
    """
    Get all canonical team names for a sport.

    Args:
        sport: Sport key ("nba", "nfl", "mlb", "nhl")

    Returns:
        List of canonical team names
    """
    sport_prefixes = {
        "nba": ["hawks", "celtics", "nets", "hornets", "bulls", "cavaliers", "mavericks",
                "nuggets", "pistons", "warriors", "rockets", "pacers", "clippers", "lakers",
                "grizzlies", "heat", "bucks", "timberwolves", "pelicans", "knicks", "thunder",
                "magic", "76ers", "suns", "blazers", "kings", "spurs", "raptors", "jazz", "wizards"],
        "nfl": ["cardinals", "falcons", "ravens", "bills", "panthers", "bears", "bengals",
                "browns", "cowboys", "broncos", "lions", "packers", "texans", "colts", "jaguars",
                "chiefs", "raiders", "chargers", "rams", "dolphins", "vikings", "patriots",
                "saints", "giants", "jets", "eagles", "steelers", "49ers", "seahawks", "buccaneers",
                "titans", "commanders"],
        "mlb": ["diamondbacks", "braves", "orioles", "red sox", "cubs", "white sox", "reds",
                "guardians", "rockies", "tigers", "astros", "royals", "angels", "dodgers", "marlins",
                "brewers", "twins", "mets", "yankees", "athletics", "phillies", "pirates", "padres",
                "giants", "mariners", "cardinals", "rays", "rangers", "blue jays", "nationals"],
        "nhl": ["ducks", "coyotes", "bruins", "sabres", "flames", "hurricanes", "blackhawks",
                "avalanche", "jackets", "stars", "wings", "oilers", "panthers", "kings", "wild",
                "canadiens", "predators", "devils", "islanders", "rangers", "senators", "flyers",
                "penguins", "sharks", "kraken", "blues", "lightning", "leafs", "canucks", "knights",
                "capitals", "jets"]
    }

    prefixes = sport_prefixes.get(sport.lower(), [])
    teams = [name for name in TEAM_NAME_MAP.values() if any(prefix in name.lower() for prefix in prefixes)]
    return list(set(teams))  # Remove duplicates
