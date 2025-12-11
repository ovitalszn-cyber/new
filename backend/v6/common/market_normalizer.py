"""
V6 Market Normalizer - Extracted from V5 for unified endpoint support.

Normalizes sportsbook-specific market keys to canonical forms.
Handles traditional markets (h2h, spreads, totals) and player props across all sports.
"""

from typing import Dict, Any
import structlog

logger = structlog.get_logger()


class MarketNormalizer:
    """Standalone market key normalizer for V6 unified endpoints."""
    
    def __init__(self):
        """Initialize with default market mappings from V6."""
        self.market_map = {
            # Traditional markets
            "h2h": "h2h",
            "moneyline": "h2h",
            "money": "h2h",
            "spreads": "spreads",
            "spread": "spreads",
            "totals": "totals",
            "total": "totals",
            "over_under": "totals",
            "team_total": "team_totals",
            "team_totals": "team_totals",
            
            # Player props - basketball
            "player_points": "player_props",
            "player_rebounds": "player_props",
            "player_assists": "player_props",
            "player_steals": "player_props",
            "player_blocks": "player_props",
            "points": "player_props",
            "rebounds": "player_props",
            "assists": "player_props",
            "steals": "player_props",
            "blocks": "player_props",
            
            # Player props - NHL
            "player_goals": "player_props",
            "shots_on_goal": "player_props",
            "power_play_points": "player_props",
            "saves": "player_props",
            
            # Player props - NFL
            "passing": "player_props",
            "rushing": "player_props",
            "receiving": "player_props",
            "touchdowns": "player_props",
            "receptions": "player_props",
            "passing_yards": "player_props",
            "rushing_yards": "player_props",
            "receiving_yards": "player_props",
            "rushing_attempts": "player_props",
            "longest": "player_props",  # Longest reception/rush
            "interceptions": "player_props",
            "field": "player_props",  # Field goals
            "kicking": "player_props",
            
            # Player props - MLB
            "player_hits": "player_props",
            "player_home_runs": "player_props",
            "player_rbis": "player_props",
            "player_strikeouts": "player_props",
            "player_walks": "player_props",
            "hits": "player_props",
            "home_runs": "player_props",
            "rbis": "player_props",
            "strikeouts": "player_props",
            "walks": "player_props",
            "pitching_strikeouts": "player_props",
            "pitching_walks": "player_props",
            "pitching_hits": "player_props",
            "pitching_runs": "player_props",
            "earned_runs": "player_props",
        }
        
        # Player prop market types for detection
        self.player_prop_types = [
            # Basketball
            "player_points", "player_rebounds", "player_assists", "player_steals", "player_blocks",
            "points", "rebounds", "assists", "steals", "blocks",
            # NHL
            "player_goals", "points", "shots_on_goal", "assists", "saves", "power_play_points",
            # NFL
            "passing", "rushing", "receiving", "touchdowns", "receptions", "passing_yards",
            "rushing_yards", "receiving_yards", "rushing_attempts", "longest", "interceptions",
            "field", "kicking",
            # MLB
            "player_hits", "player_home_runs", "player_rbis", "player_strikeouts", "player_walks",
            "hits", "home_runs", "rbis", "strikeouts", "walks", "pitching_strikeouts",
            "pitching_walks", "pitching_hits", "pitching_runs", "earned_runs"
        ]
    
    def normalize_market_key(self, market_type: str, market_key: str, source_rules: Dict[str, Any] = None) -> str:
        """
        Normalize market key to canonical form.
        
        Args:
            market_type: The market type from the source (e.g., "moneyline", "player_points")
            market_key: The market key from the source (e.g., "h2h", "player_points_over")
            source_rules: Optional source-specific market mappings
            
        Returns:
            Canonical market key (e.g., "h2h", "player_props")
        """
        if source_rules is None:
            source_rules = {}
        
        # Create working copy of market map with source-specific overrides
        market_map = self.market_map.copy()
        source_market_map = source_rules.get("market_mappings", {})
        market_map.update(source_market_map)
        
        # Try market_type first, then market_key
        normalized = market_type.lower().strip() if market_type else ""
        
        # Check if it's a player prop market
        if "player" in normalized or normalized in self.player_prop_types:
            return "player_props"
        
        # Check market map
        if normalized in market_map:
            return market_map[normalized]
        
        # Fallback to market_key
        if market_key:
            normalized_key = market_key.lower().strip()
            if "player" in normalized_key or normalized_key in self.player_prop_types:
                return "player_props"
            
            if normalized_key in market_map:
                return market_map[normalized_key]
            
            # Take first part of underscore-separated keys
            first_part = normalized_key.split("_")[0]
            if first_part in market_map:
                return market_map[first_part]
        
        # Default fallback
        logger.warning("Unknown market type", market_type=market_type, market_key=market_key)
        return market_type.lower().strip() if market_type else "unknown"
    
    def is_player_prop_market(self, market_type: str, market_key: str = "") -> bool:
        """
        Check if a market is a player prop market.
        
        Args:
            market_type: The market type from the source
            market_key: The market key from the source (optional)
            
        Returns:
            True if this is a player prop market
        """
        normalized = market_type.lower().strip() if market_type else ""
        
        # Direct player prop indicators
        if "player" in normalized:
            return True
        
        # Check against known player prop types
        if normalized in self.player_prop_types:
            return True
        
        # Check market_key if provided
        if market_key:
            normalized_key = market_key.lower().strip()
            if "player" in normalized_key or normalized_key in self.player_prop_types:
                return True
        
        return False
    
    def get_canonical_markets(self) -> Dict[str, str]:
        """
        Get the complete market mapping dictionary.
        
        Returns:
            Dict mapping source market types to canonical forms
        """
        return self.market_map.copy()


# Global instance for easy import
market_normalizer = MarketNormalizer()


def normalize_market_key(market_type: str, market_key: str, source_rules: Dict[str, Any] = None) -> str:
    """
    Convenience function for market normalization.
    
    Args:
        market_type: The market type from the source
        market_key: The market key from the source
        source_rules: Optional source-specific market mappings
        
    Returns:
        Canonical market key
    """
    return market_normalizer.normalize_market_key(market_type, market_key, source_rules)


def is_player_prop_market(market_type: str, market_key: str = "") -> bool:
    """
    Convenience function to check if market is player prop.
    
    Args:
        market_type: The market type from the source
        market_key: The market key from the source (optional)
        
    Returns:
        True if this is a player prop market
    """
    return market_normalizer.is_player_prop_market(market_type, market_key)
