"""
Sports configuration for V6 Stats Engine.
Maps sport names to their theScore API endpoints and configurations.
"""

from typing import Dict, List, Optional
from enum import Enum

class SportType(Enum):
    """Type of sport - determines data structure and models needed."""
    TEAM = "team"  # Football, basketball, baseball, hockey, soccer
    INDIVIDUAL = "individual"  # Golf, tennis, MMA, racing
    TOURNAMENT = "tournament"  # March Madness, World Cup

class SportConfig:
    """Configuration for a single sport."""
    def __init__(
        self,
        endpoint: str,
        sport_type: SportType,
        display_name: str,
        has_teams: bool = True,
        has_box_score: bool = True,
        has_players: bool = True,
        has_standings: bool = True
    ):
        self.endpoint = endpoint
        self.sport_type = sport_type
        self.display_name = display_name
        self.has_teams = has_teams
        self.has_box_score = has_box_score
        self.has_players = has_players
        self.has_standings = has_standings

# Team Sports - use current Game model
TEAM_SPORTS = {
    "nfl": SportConfig("nfl", SportType.TEAM, "NFL", True, True, True, True),
    "ncaaf": SportConfig("ncaaf", SportType.TEAM, "NCAA Football", True, True, True, True),
    "nba": SportConfig("nba", SportType.TEAM, "NBA", True, True, True, True),
    "ncaab": SportConfig("ncaab", SportType.TEAM, "NCAA Men's Basketball", True, True, True, True),
    "wnba": SportConfig("wnba", SportType.TEAM, "WNBA", True, True, True, True),
    "mlb": SportConfig("mlb", SportType.TEAM, "MLB", True, True, True, True),
    "nhl": SportConfig("nhl", SportType.TEAM, "NHL", True, True, True, True),
    
    # Soccer - to be tested
    "mls": SportConfig("mls", SportType.TEAM, "MLS", True, True, True, True),
    "epl": SportConfig("soccer_epl", SportType.TEAM, "Premier League", True, True, True, True),
    "laliga": SportConfig("soccer_laliga", SportType.TEAM, "La Liga", True, True, True, True),
    "seriea": SportConfig("soccer_seriea", SportType.TEAM, "Serie A", True, True, True, True),
    "bundesliga": SportConfig("soccer_bundesliga", SportType.TEAM, "Bundesliga", True, True, True, True),
    "ligue1": SportConfig("soccer_ligue1", SportType.TEAM, "Ligue 1", True, True, True, True),
    "champions": SportConfig("soccer_uefa_champions", SportType.TEAM, "Champions League", True, True, True, True),
    "europa": SportConfig("soccer_uefa_europa", SportType.TEAM, "Europa League", True, True, True, True),
}

# Individual Sports - need different models (to be implemented later)
INDIVIDUAL_SPORTS = {
    "pga": SportConfig("golf", SportType.INDIVIDUAL, "PGA Tour", False, False, False, False),
    "atp": SportConfig("tennis_atp", SportType.INDIVIDUAL, "ATP Tour", False, False, False, False),
    "wta": SportConfig("tennis_wta", SportType.INDIVIDUAL, "WTA Tour", False, False, False, False),
    "nascar": SportConfig("racing_nascar", SportType.INDIVIDUAL, "NASCAR", False, False, False, False),
    "f1": SportConfig("racing_f1", SportType.INDIVIDUAL, "Formula 1", False, False, False, False),
    "mma": SportConfig("mma", SportType.INDIVIDUAL, "MMA", False, False, False, False),
}

# All sports combined
ALL_SPORTS = {**TEAM_SPORTS, **INDIVIDUAL_SPORTS}

def get_team_sports() -> Dict[str, SportConfig]:
    """Get all team sports that work with current Game model."""
    return TEAM_SPORTS

def get_individual_sports() -> Dict[str, SportConfig]:
    """Get individual sports that need special handling."""
    return INDIVIDUAL_SPORTS

def get_all_sports() -> Dict[str, SportConfig]:
    """Get all configured sports."""
    return ALL_SPORTS

def get_sport_config(sport_key: str) -> Optional[SportConfig]:
    """Get configuration for a specific sport."""
    return ALL_SPORTS.get(sport_key.lower())

def is_team_sport(sport_key: str) -> bool:
    """Check if a sport uses the team-based Game model."""
    config = get_sport_config(sport_key)
    return config and config.sport_type == SportType.TEAM

def get_supported_sports() -> List[str]:
    """Get list of all supported sport keys."""
    return list(ALL_SPORTS.keys())
