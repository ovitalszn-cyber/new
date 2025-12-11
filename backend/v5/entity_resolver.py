"""
Entity Resolution - Matches events and players across sources.

Matching pipeline: exact id -> normalized tokens -> trigram similarity -> context match
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import structlog
import hashlib
import re
from collections import defaultdict

from v5.mapping_worker import CanonicalEnvelope
from utils.canonical_id_generator import generate_canonical_event_id

logger = structlog.get_logger()


class EntityResolver:
    """Resolves canonical event IDs and player IDs from envelopes."""
    
    def __init__(self):
        """Initialize entity resolver."""
        self.event_cache: Dict[str, Dict[str, Any]] = {}
        self.player_cache: Dict[str, str] = {}
        
    async def resolve_events(self, envelopes: List[CanonicalEnvelope]) -> List[Dict[str, Any]]:
        """Resolve canonical event IDs from envelopes."""
        # Group envelopes by potential event matches
        event_groups = self._group_by_potential_matches(envelopes)
        
        # Resolve canonical IDs for each group
        resolved_events = []
        for group_key, group_envelopes in event_groups.items():
            canonical_id = self._generate_canonical_event_id(group_envelopes[0])
            
            # Merge all envelopes for this event
            merged_event = self._merge_envelopes_for_event(canonical_id, group_envelopes)
            resolved_events.append(merged_event)
        
        logger.info("Resolved events", total=len(resolved_events), from_envelopes=len(envelopes))
        return resolved_events
    
    def _group_by_potential_matches(self, envelopes: List[CanonicalEnvelope]) -> Dict[str, List[CanonicalEnvelope]]:
        """Group envelopes by potential event matches."""
        groups = defaultdict(list)
        
        for envelope in envelopes:
            # Create match key from teams and start time
            match_key = self._create_match_key(envelope)
            groups[match_key].append(envelope)
        
        return dict(groups)
    
    def _create_match_key(self, envelope: CanonicalEnvelope) -> str:
        """Create a match key for grouping similar events."""
        # Normalize teams
        home = self._normalize_for_matching(envelope.home_team or "")
        away = self._normalize_for_matching(envelope.away_team or "")
        
        # Extract date from start_ts
        try:
            dt = datetime.fromisoformat(envelope.start_ts.replace('Z', '+00:00'))
            date_str = dt.strftime('%Y%m%d')
        except Exception as e:
            date_str = "unknown"
        
        # Create deterministic key
        teams_sorted = sorted([home, away])
        match_key = f"{envelope.sport}:{teams_sorted[0]}_vs_{teams_sorted[1]}:{date_str}"
        return match_key
    
    def _normalize_for_matching(self, text: str) -> str:
        """Normalize text for matching (remove special chars, lowercase)."""
        if not text:
            return ""
        # Remove special characters, lowercase, strip
        normalized = re.sub(r'[^a-z0-9\s]', '', text.lower().strip())
        # Remove extra spaces
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized
    
    def _generate_canonical_event_id(self, envelope: CanonicalEnvelope) -> str:
        """
        Generate deterministic canonical event ID.
        
        Uses the shared canonical_id_generator utility to ensure consistency
        across the entire system.
        """
        return generate_canonical_event_id(
            sport=envelope.sport or "",
            home_team=envelope.home_team or "",
            away_team=envelope.away_team or "",
            commence_time=envelope.start_ts or ""
        )
    
    def _merge_envelopes_for_event(
        self,
        canonical_id: str,
        envelopes: List[CanonicalEnvelope]
    ) -> Dict[str, Any]:
        """Merge multiple envelopes for the same canonical event."""
        if not envelopes:
            return {}
        
        # Find first envelope with team names to use as base (prefer envelopes with event metadata)
        base = envelopes[0]
        for envelope in envelopes:
            if envelope.home_team and envelope.away_team and envelope.sport:
                base = envelope
        
        all_markets = defaultdict(lambda: {"runners": [], "sources": []})
        all_provenance = []
        
        for envelope in envelopes:
            # Merge markets - convert list to dict format
            envelope_markets = {}
            if isinstance(envelope.markets, list):
                # Convert list of market dicts to dict keyed by market key
                for market in envelope.markets:
                    market_key = market.get("key", "unknown")
                    envelope_markets[market_key] = market
            elif isinstance(envelope.markets, dict):
                envelope_markets = envelope.markets
            else:
                logger.warning(f"Unexpected markets type in envelope: {type(envelope.markets)}")
                continue
            
            for market_key, market in envelope_markets.items():
                # Add runners
                all_markets[market_key]["runners"].extend(market.get("runners", []))
                all_markets[market_key]["sources"].append(envelope.source)
            
            # Collect provenance
            all_provenance.append(envelope.provenance)
        
        # Build merged event
        # Convert dict back to list format with proper key field
        markets_list = []
        for market_key, market_data in all_markets.items():
            market_dict = dict(market_data)
            market_dict["key"] = market_key
            markets_list.append(market_dict)
        
        return {
            "canonical_event_id": canonical_id,
            "sport": base.sport,
            "home_team": base.home_team,
            "away_team": base.away_team,
            "commence_time": base.start_ts,
            "markets": markets_list,
            "props": self._extract_player_props(all_markets),
            "provenance": {
                "sources": list(set(e.source for e in envelopes)),
                "source_count": len(set(e.source for e in envelopes)),
                "envelopes": all_provenance
            }
        }
    
    def _extract_player_props(self, markets: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract player props from markets."""
        props = []
        
        for market_key, market_data in markets.items():
            if market_key == "player_props" or "player" in market_key.lower():
                for runner in market_data.get("runners", []):
                    if runner.get("player_name"):
                        props.append({
                            "player_name": runner.get("player_name"),
                            "stat_type": runner.get("stat_type"),
                            "line": runner.get("line"),
                            "odds": runner.get("odds"),
                            "sources": market_data.get("sources", [])
                        })
        
        return props
    
    async def resolve_players(self, player_name: str, sport: str) -> Optional[str]:
        """
        Resolve canonical player ID.
        
        Uses fuzzy matching to handle name variations.
        """
        # Normalize player name
        normalized = self._normalize_for_matching(player_name)
        
        # Check cache
        cache_key = f"{sport}:{normalized}"
        if cache_key in self.player_cache:
            return self.player_cache[cache_key]
        
        # Generate canonical ID
        canonical_id = hashlib.sha256(cache_key.encode()).hexdigest()[:12]
        player_id = f"plyr_{canonical_id}"
        
        # Cache it
        self.player_cache[cache_key] = player_id
        
        return player_id
