"""
Player-related models for theScore API responses.
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from .common import BaseModelWithTimestamps, Sport, League


class PlayerStats(BaseModel):
    """Player statistics for a game or season - flexible structure."""
    
    # Basic info
    games_played: int = 0
    
    # Football offensive stats
    passing_yards: int = 0
    passing_touchdowns: int = 0
    passing_interceptions: int = 0
    completions: int = 0
    attempts: int = 0
    
    # Football defensive stats
    tackles: int = 0
    sacks: int = 0
    interceptions: int = 0
    fumbles_recovered: int = 0
    
    # Football rushing stats
    rushing_yards: int = 0
    rushing_touchdowns: int = 0
    rushing_attempts: int = 0
    
    # Football receiving stats
    receptions: int = 0
    receiving_yards: int = 0
    receiving_touchdowns: int = 0
    
    # Basketball stats (for future expansion)
    points: int = 0
    rebounds: int = 0
    assists: int = 0
    steals: int = 0
    blocks: int = 0
    
    # Metadata
    season: Optional[str] = None
    week: Optional[int] = None
    opponent_team_id: Optional[int] = None
    
    class Config:
        extra = "allow"


class Player(BaseModelWithTimestamps):
    """Complete player information - matches actual theScore API structure."""
    id: int
    
    # Names - use actual API field names
    primary_name: Optional[str] = None  # Make optional since not all players have it
    full_name: Optional[str] = None
    short_name: Optional[str] = None
    medium_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    first_initial_and_last_name: Optional[str] = None
    
    # Physical attributes from API - extracted from player_extra_info via properties
    # No direct fields since they come from player_extra_info array
    
    # Sport/Team info
    sport: Optional[str] = None
    team_id: Optional[int] = None
    team: Optional[Union[str, Dict[str, Any]]] = None  # Can be string or dict
    
    # Position and jersey
    position: Optional[str] = None
    position_abbreviation: Optional[str] = None
    jersey_number: Optional[int] = None
    number: Optional[int] = None  # API uses 'number' field
    abbreviation: Optional[str] = None
    
    # Status and info
    status: str = "active"
    suspended: bool = False
    injury: Optional[Dict[str, Any]] = None
    
    # Experience and background - extracted from player_extra_info via properties
    # No direct fields since they come from player_extra_info array
    player_extra_info: Optional[List[Dict[str, Any]]] = None
    
    # Statistics - use flexible dict for complex API data
    season_stats: Optional[Dict[str, Any]] = None
    career_stats: Optional[Dict[str, Any]] = None
    
    # Visuals
    headshots: Optional[Dict[str, str]] = None
    
    # Metadata
    has_headshots: bool = False
    has_transparent_headshots: bool = False
    has_extra_info: bool = False
    has_stats: bool = False
    has_career_stats: Optional[bool] = None
    has_game_logs: bool = False
    
    # Properties for convenience
    @property
    def display_name(self) -> str:
        """Get display name in order of preference."""
        return (
            self.first_initial_and_last_name or 
            self.full_name or 
            self.medium_name or 
            self.primary_name or 
            f"{self.first_name or ''} {self.last_name or ''}".strip()
        )
    
    @property
    def position_display(self) -> str:
        """Get position display."""
        return self.position_abbreviation or self.position or ""
    
    @property
    def jersey_display(self) -> str:
        """Get jersey number display."""
        num = self.jersey_number or self.number
        return f"#{num}" if num else ""
    
    def _get_extra_info(self, label: str) -> Optional[str]:
        """Extract value from player_extra_info array by label."""
        if not self.player_extra_info:
            return None
        for info in self.player_extra_info:
            if info.get('label') == label:
                return info.get('value')
        return None
    
    @property
    def height(self) -> Optional[str]:
        """Extract height from player_extra_info."""
        return self._get_extra_info('Height')
    
    @property
    def weight(self) -> Optional[str]:
        """Extract weight from player_extra_info."""
        return self._get_extra_info('Weight')
    
    @property
    def school(self) -> Optional[str]:
        """Extract school from player_extra_info."""
        return self._get_extra_info('School')
    
    @property
    def birth_place(self) -> Optional[str]:
        """Extract birth place from player_extra_info."""
        return self._get_extra_info('Birth Place')
    
    @property
    def birth_date(self) -> Optional[str]:
        """Extract birth date from player_extra_info."""
        return self._get_extra_info('Birth Date')
    
    @property
    def draft_info(self) -> Optional[str]:
        """Extract draft info from player_extra_info."""
        return self._get_extra_info('Draft')
    
    @property
    def stats_summary(self) -> str:
        """Get a meaningful stats summary."""
        if not self.season_stats:
            return "No stats available"
        
        games = self.season_stats.get('games', 0)
        
        # Handle players who haven't played
        if games == 0:
            return "No games played this season"
        
        # Get stats as strings and convert to float for validation
        points_avg = self.season_stats.get('points_average', '0')
        rebounds_avg = self.season_stats.get('rebounds_total_average', '0')
        
        try:
            points_float = float(points_avg)
            rebounds_float = float(rebounds_avg)
            
            if points_float == 0 and rebounds_float == 0 and games > 0:
                return f"{games} games played, no scoring"
            else:
                return f"{points_avg} PPG, {rebounds_avg} RPG ({games} games)"
        except (ValueError, TypeError):
            return f"{points_avg} PPG, {rebounds_avg} RPG ({games} games)"
    
    @property
    def per_game_stats(self) -> Dict[str, Any]:
        """Get all per-game average statistics - sport-agnostic."""
        if not self.season_stats:
            return {}
        
        # Common per-game patterns across all sports
        per_game_patterns = [
            'points_average', 'rebounds_total_average', 'assists_average',
            'steals_average', 'blocked_shots_average', 'turnovers_average',
            'goals_average', 'assists_average', 'saves_average',
            'passing_yards_average', 'rushing_yards_average',
            'receiving_yards_average', 'batting_average'
        ]
        
        # Include any field ending in "_average" or "_percentage"
        avg_fields = [field for field in self.season_stats.keys() 
                     if field.endswith('_average') or field.endswith('_percentage')]
        
        all_fields = list(set(per_game_patterns + avg_fields))
        return {field: self.season_stats.get(field) for field in all_fields 
                if self.season_stats.get(field) is not None}
    
    @property
    def offensive_stats(self) -> Dict[str, Any]:
        """Get offensive statistics - sport-agnostic."""
        if not self.season_stats:
            return {}
        
        # Basketball offensive
        basketball_offensive = [
            'points', 'points_average', 'field_goals_made', 'field_goals_attempted',
            'three_point_field_goals_made', 'free_throws_made', 'assists'
        ]
        
        # Football offensive  
        football_offensive = [
            'passing_yards', 'passing_touchdowns', 'passing_completions',
            'rushing_yards', 'rushing_touchdowns', 'receiving_yards', 'receiving_touchdowns',
            'receptions', 'receiving_targets', 'receiving_yards_per_reception',
            'receiving_targets_percent_caught', 'receiving_yards_after_catch',
            'receiving_drops', 'receiving_yards_per_game', 'passing_completions_percentage'
        ]
        
        # Baseball offensive
        baseball_offensive = [
            'batting_average', 'home_runs', 'hits', 'runs_scored', 'rbis',
            'doubles', 'triples', 'at_bats', 'slugging_percentage'
        ]
        
        # Hockey offensive
        hockey_offensive = [
            'goals', 'assists', 'points', 'shots_on_goal', 'power_play_goals'
        ]
        
        # Soccer offensive
        soccer_offensive = [
            'goals', 'assists', 'shots', 'shots_on_target', 'touches_total',
            'touches_passes', 'duels_won', 'penalty_kicks_goals'
        ]
        
        all_offensive = basketball_offensive + football_offensive + baseball_offensive + hockey_offensive + soccer_offensive
        return {field: self.season_stats.get(field) for field in all_offensive 
                if self.season_stats.get(field) is not None}
    
    @property
    def defensive_stats(self) -> Dict[str, Any]:
        """Get defensive statistics - sport-agnostic."""
        if not self.season_stats:
            return {}
        
        # Basketball defensive
        basketball_defensive = [
            'rebounds_total', 'rebounds_offensive', 'rebounds_defensive',
            'steals', 'blocked_shots', 'personal_fouls'
        ]
        
        # Football defensive
        football_defensive = [
            'tackles', 'sacks', 'interceptions', 'fumbles_recovered',
            'passes_defended', 'forced_fumbles'
        ]
        
        # Baseball defensive
        baseball_defensive = [
            'fielding_percentage', 'errors', 'putouts', 'assists_fielding',
            'double_plays', 'caught_stealing'
        ]
        
        # Hockey defensive
        hockey_defensive = [
            'plus_minus', 'penalty_minutes', 'short_handed_goals',
            'blocked_shots_hockey', 'hits'
        ]
        
        # Soccer defensive
        soccer_defensive = [
            'tackles', 'clearances', 'blocked_shots', 'fouls_committed',
            'touches_interceptions', 'goals_allowed', 'clean_sheets'
        ]
        
        all_defensive = basketball_defensive + football_defensive + baseball_defensive + hockey_defensive + soccer_defensive
        return {field: self.season_stats.get(field) for field in all_defensive 
                if self.season_stats.get(field) is not None}
    
    @property
    def efficiency_stats(self) -> Dict[str, Any]:
        """Get efficiency metrics - sport-agnostic."""
        if not self.season_stats:
            return {}
        
        efficiency_fields = [
            'player_efficiency_rating', 'true_shooting_percentage', 
            'usage_percentage', 'field_goals_percentage', 'free_throws_percentage',
            'three_point_field_goals_percentage', 'passing_completions_percentage',
            'on_base_percentage', 'slugging_percentage', 'ops', 'whip',
            'save_percentage', 'receiving_targets_percent_caught',
            'receiving_yards_per_reception', 'receiving_yards_per_game',
            'passing_yards_per_attempt', 'rushing_yards_per_attempt',
            'clean_sheets', 'penalty_kicks_saves', 'saves', 'goals_against_average'
        ]
        
        return {field: self.season_stats.get(field) for field in efficiency_fields 
                if self.season_stats.get(field) is not None}
    
    @property
    def situational_stats(self) -> Dict[str, Any]:
        """Get situational statistics - sport-agnostic."""
        if not self.season_stats:
            return {}
        
        situational_fields = [
            'points_in_paint', 'fast_break_pts', 'points_off_turnovers',
            'power_play_points', 'short_handed_points', 'game_winning_goals',
            'clutch_stats', 'fourth_quarter_points', 'overtime_points'
        ]
        
        return {field: self.season_stats.get(field) for field in situational_fields 
                if self.season_stats.get(field) is not None}
    
    @property
    def discipline_stats(self) -> Dict[str, Any]:
        """Get discipline and foul statistics - sport-agnostic."""
        if not self.season_stats:
            return {}
        
        discipline_fields = [
            'personal_fouls', 'technical_fouls', 'flagrant_fouls',
            'ejections', 'penalty_minutes', 'suspensions',
            'personal_fouls_disqualifications', 'coach_ejections'
        ]
        
        return {field: self.season_stats.get(field) for field in discipline_fields 
                if self.season_stats.get(field) is not None}
    
    @property
    def achievement_stats(self) -> Dict[str, Any]:
        """Get achievement-based statistics - sport-agnostic."""
        if not self.season_stats:
            return {}
        
        achievement_fields = [
            'double_doubles', 'triple_doubles', 'high_game_points',
            'points_highest', 'shutouts', 'no_hitters', 'perfect_games',
            'game_winning_goals', 'game_tying_goals', 'hat_tricks'
        ]
        
        return {field: self.season_stats.get(field) for field in achievement_fields 
                if self.season_stats.get(field) is not None}
    
    @property
    def sport_specific_stats(self) -> Dict[str, Any]:
        """Get sport-specific statistics that don't fit other categories."""
        if not self.season_stats:
            return {}
        
        # Fields that are sport-specific but don't fit above categories
        sport_specific = [
            'games', 'games_started', 'minutes', 'minutes_average',
            'innings_pitched', 'complete_games', 'quality_starts'
        ]
        
        return {field: self.season_stats.get(field) for field in sport_specific 
                if self.season_stats.get(field) is not None}
    
    @property
    def all_stats_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get all stats categories organized for comprehensive modeling - works for all sports."""
        return {
            'per_game': self.per_game_stats,
            'offensive': self.offensive_stats,
            'defensive': self.defensive_stats,
            'efficiency': self.efficiency_stats,
            'situational': self.situational_stats,
            'discipline': self.discipline_stats,
            'achievements': self.achievement_stats,
            'sport_specific': self.sport_specific_stats,
            'raw_data': self.season_stats  # Full access to all fields
        }
    
    class Config:
        extra = "allow"  # Allow extra fields from API


class PlayerRoster(BaseModel):
    """Team roster response."""
    team_id: int
    players: List[Player]
    total_count: int
    updated_at: str  # Keep as string for RFC 2822 format
    
    class Config:
        extra = "allow"


class BoxScore(BaseModel):
    """Complete box score for a game - flexible structure."""
    game_id: int
    home_team_stats: Dict[str, Any] = Field(default_factory=dict)
    away_team_stats: Dict[str, Any] = Field(default_factory=dict)
    home_players: List[Dict[str, Any]] = Field(default_factory=list)
    away_players: List[Dict[str, Any]] = Field(default_factory=list)
    game_info: Dict[str, Any] = Field(default_factory=dict)
    updated_at: str  # Keep as string for RFC 2822 format
    
    class Config:
        extra = "allow"
