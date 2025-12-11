"""
Merge Service - Aggregates odds by market and computes consensus fair odds.

Preserves full provenance and returns merged markets with consensus odds.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
from collections import defaultdict

logger = structlog.get_logger()


class MergedMarket:
    """Represents a merged market with consensus odds."""
    
    def __init__(self, market_key: str):
        self.market_key = market_key
        self.runners: List[Dict[str, Any]] = []
        self.sources: List[str] = []
        self.consensus_odds: Dict[str, float] = {}  # runner_id -> consensus probability (no-vig)
        self.fair_odds: Dict[str, float] = {}  # runner_id -> fair probability (same as consensus for no-vig)
        self.provenance: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.market_key,
            "runners": self.runners,
            "consensus_odds": self.consensus_odds,
            "fair_odds": self.fair_odds,
            "sources": list(set(self.sources)),
            "source_count": len(set(self.sources)),
            "provenance": self.provenance
        }


class MergeService:
    """Service that merges odds from multiple sources."""
    
    def __init__(self):
        """Initialize merge service."""
        # Source confidence weights (sharp books get higher weight)
        self.source_weights = {
            "novig": 1.0,
            "pinnacle": 1.0,
            "draftkings": 0.3,
            "betmgm": 0.3,
            "caesars": 0.3,
            "fanduel": 0.3,
            "bet365": 1.0,
            "bovada": 0.3,
            "dabble": 0.3,  # DFS-style book
            "prizepicks": 0.3,  # DFS-style book
            "splashsports": 0.3,  # DFS-style book
            "rebet": 0.3,
            "sleeper": 0.3,
            "underdog": 0.3,
        }
        
    async def merge_event_odds(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge odds from all sources for an event.
        
        Args:
            event: Resolved event with markets from entity resolver
            
        Returns:
            Merged markets with consensus odds and full provenance
        """
        markets = event.get("markets", [])
        print(f"[DEBUG] MergeService.merge_event_odds - Processing event {event.get('canonical_event_id')}")
        print(f"[DEBUG] Input markets: {len(markets)} markets")
        
        for i, market in enumerate(markets):
            market_key = market.get("key", "unknown")
            runners = market.get("runners", [])
            print(f"[DEBUG] Processing market: {market_key} with {len(runners)} runners")
            
            # Debug: Show sample runners and their prop IDs
            for j, runner in enumerate(runners[:3]):  # Show first 3
                prop_id = runner.get("id", "no_id")
                player = runner.get("player_name", "no_player")
                stat = runner.get("stat_type", "no_stat")
                source = runner.get("source", "no_source")  # Individual runner source
                print(f"[DEBUG] Runner {j}: {prop_id} - {player} {stat} from source: {source}")
        
        # EntityResolver already merged markets by key, so just process each market directly
        merged_markets: Dict[str, Dict[str, Any]] = {}
        for market in markets:
            market_key = market.get("key", "unknown")
            print(f"[DEBUG] Merging market: {market_key}")
            merged_market = await self._merge_market(market_key, market)
            merged_markets[market_key] = merged_market.to_dict()
        
        # Build per-book view
        books_view = self._build_per_book_view(list(merged_markets.values()))
        
        return {
            "markets": merged_markets,
            "books": books_view,
            "provenance": event.get("provenance", {}),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    async def _merge_market(
        self,
        market_key: str,
        market_data: Dict[str, Any]
    ) -> MergedMarket:
        """Merge a single market."""
        merged = MergedMarket(market_key)
        
        # Group runners by identifier
        runner_groups = defaultdict(list)
        
        # Track PrizePicks runners for debugging
        prizepicks_runners = []
        
        for runner in market_data.get("runners", []):
            runner_id = runner.get("id")
            source = runner.get("source", "unknown")
            
            # Track PrizePicks runners
            if source == "prizepicks":
                prizepicks_runners.append(runner)
            
            if runner_id:
                runner_groups[runner_id].append(runner)
        
        # Track sources for this market once (outside runner loop)
        merged.sources.extend(market_data.get("sources", []))
        
        # Debug PrizePicks runners
        if prizepicks_runners:
            print(f"[DEBUG] PrizePicks runners in {market_key}: {len(prizepicks_runners)}")
            for runner in prizepicks_runners[:3]:  # Show first 3
                print(f"  Runner {runner.get('id')}: odds={runner.get('odds')}, source={runner.get('source')}")
        
        # Compute consensus for each runner
        print(f"[DEBUG] MergeService._merge_market - Processing {len(runner_groups)} runner groups for market {market_key}")
        for runner_id, runner_list in runner_groups.items():
            print(f"[DEBUG] Processing runner group {runner_id} with {len(runner_list)} runners")
            
            # Collect all odds for this runner (only from sources that have odds)
            odds_with_weights = []
            sources_with_odds = []
            sources_without_odds = []
            all_odds = []  # This should contain per-source odds for book view
            
            for runner in runner_list:
                odds = runner.get("odds")
                source = runner.get("source", "unknown")
                print(f"[DEBUG] Runner from {source} has odds: {odds}")
                
                # Add to all_odds for book view
                all_odds.append({
                    "source": source,
                    "odds": odds,
                    "available": odds is not None and odds > 0
                })
                
                # Accept both probabilities (0.0-1.0) and decimal odds (>1.0)
                if odds and odds > 0:
                    weight = self.source_weights.get(source, 0.5)
                    odds_with_weights.append((odds, weight, source))
                    sources_with_odds.append(source)
                else:
                    # Track sources that don't have this outcome available
                    sources_without_odds.append(source)
            
            if odds_with_weights:
                # Weighted average for consensus (Novig probabilities are already no-vig)
                total_weight = sum(w for _, w, _ in odds_with_weights)
                if total_weight > 0:
                    consensus = sum(odds * weight for odds, weight, _ in odds_with_weights) / total_weight
                    merged.consensus_odds[runner_id] = round(consensus, 4)
                    # Novig probabilities are already no-vig, so consensus = fair odds
                    merged.fair_odds[runner_id] = round(consensus, 4)
            
            # Add runner to merged market - use best odds from all sources
            best_odds = None
            best_odds_source = None
            for runner in runner_list:
                odds = runner.get("odds")
                # Accept both probabilities (0.0-1.0) and decimal odds (>1.0)
                if odds and odds > 0:
                    # For probabilities, higher is better. For decimal odds, higher is also better.
                    if best_odds is None or odds > best_odds:
                        best_odds = odds
                        best_odds_source = runner.get("source", "unknown")
            
            # Build all_odds list with availability status
            all_odds_list = []
            for runner in runner_list:
                source = runner.get("source", "unknown")
                odds = runner.get("odds")
                if odds and odds > 0:
                    all_odds_list.append({"odds": odds, "source": source, "available": True})
                else:
                    all_odds_list.append({"odds": None, "source": source, "available": False})
            
            merged.runners.append({
                "id": runner_id,
                "odds": best_odds,  # Best odds from available sources, None if no source has it
                "line": runner_list[0].get("line"),
                "player_name": runner_list[0].get("player_name"),
                "stat_type": runner_list[0].get("stat_type"),
                "direction": runner_list[0].get("direction"),  # Include direction
                "sources": list(set(r.get("source", "unknown") for r in runner_list)),
                "sources_with_odds": list(set(sources_with_odds)),  # Sources that have odds for this outcome
                "sources_without_odds": list(set(sources_without_odds)),  # Sources where this outcome is not available
                "all_odds": all_odds_list
            })
        
        # Build provenance
        merged.provenance = {
            "sources": list(set(merged.sources)),
            "source_count": len(set(merged.sources)),
            "runner_count": len(merged.runners)
        }
        
        # Log matching statistics for player props
        if market_key == "player_props":
            matched_props = sum(1 for r in merged.runners if len(r.get("sources", [])) > 1)
            unmatched_props = len(merged.runners) - matched_props
            logger.info("Merged player props market",
                       market_key=market_key,
                       total_runners=len(merged.runners),
                       matched_props=matched_props,
                       unmatched_props=unmatched_props,
                       match_rate=f"{(matched_props/len(merged.runners)*100):.1f}%" if merged.runners else "0%")
        
        return merged
    
    def _build_per_book_view(self, markets: List[Dict]) -> Dict[str, Dict[str, Any]]:
        """Build per-book view of odds using runner source attribution."""
        print(f"[DEBUG] MergeService._build_per_book_view - Input markets: {len(markets)} markets")
        books = defaultdict(lambda: {"markets": {}})
        
        try:
            for market in markets:
                market_key = market.get("key", "unknown")
                runners = market.get("runners", [])
                print(f"[DEBUG] Processing market: {market_key} with {len(runners)} runners")
                
                for runner in runners:
                    all_odds = runner.get("all_odds", [])
                    print(f"[DEBUG] Runner {runner.get('id')} has {len(all_odds)} all_odds entries")
    
                    if not all_odds:
                        print(f"[DEBUG] No all_odds, using fallback sources: {runner.get('sources', [])}")
                        logger.debug(
                            "Per-book view runner missing all_odds; falling back to merged odds",
                            market_key=market_key,
                            runner_id=runner.get("id"),
                            runner_sources=runner.get("sources"),
                        )
                        fallback_sources = runner.get("sources", []) or []
                        for source in fallback_sources:
                            book_market = books[source]["markets"].setdefault(market_key, {"runners": []})
                            book_market["runners"].append({
                                "id": runner.get("id"),
                                "odds": runner.get("odds"),
                                "available": runner.get("odds") is not None,
                                "line": runner.get("line"),
                                "player_name": runner.get("player_name"),
                                "stat_type": runner.get("stat_type"),
                                "direction": runner.get("direction"),
                            })
                        continue
    
                    for odds_entry in all_odds:
                        print(f"[DEBUG] Processing odds entry from source: {odds_entry.get('source')}")
                        source = odds_entry.get("source")
                        if not source:
                            logger.debug(
                                "Per-book view skipping odds entry without source",
                                market_key=market_key,
                                runner_id=runner.get("id"),
                            )
                            continue
    
                        book_market = books[source]["markets"].setdefault(market_key, {"runners": []})
                        book_market["runners"].append({
                            "id": runner.get("id"),
                            "odds": odds_entry.get("odds"),
                            "available": odds_entry.get("available", odds_entry.get("odds") is not None),
                            "line": runner.get("line"),
                            "player_name": runner.get("player_name"),
                            "stat_type": runner.get("stat_type"),
                            "direction": runner.get("direction"),
                        })
    
            print(f"[DEBUG] MergeService._build_per_book_view - Final books dict has {len(books)} books: {list(books.keys())}")
            return {book: data for book, data in books.items()}
        except Exception as e:
            logger.error(f"Error building story for event: {e}", exc_info=True)
            raise  # Re-raise if needed
    
    async def merge_event_odds_market_first(
        self,
        event: Dict[str, Any],
        requested_markets: List[str]
    ) -> Dict[str, Any]:
        """
        Merge odds in market-first format - the plug-and-play format.
        
        Returns: {
            "markets": {
                "h2h": {
                    "Team Name": {
                        "draftkings": 2.10,
                        "betmgm": 2.05
                    }
                }
            }
        }
        """
        markets = event.get("markets", {})
        market_first = {}
        all_sources = set()
        
        # Filter to requested markets
        requested_set = set(m.lower() for m in requested_markets)
        
        for market in markets:
            # Normalize market key for comparison
            market_normalized = market.get("key", "").lower().replace("_", "")
            if requested_set and not any(req in market_normalized for req in requested_set):
                continue
            
            # Build outcome -> {book: odds} structure
            outcome_odds = defaultdict(dict)
            
            for runner in market.get("runners", []):
                runner_id = runner.get("id", "")
                odds = runner.get("odds")
                source = runner.get("source", "unknown")
                
                if odds and odds > 1.0:  # Valid odds
                    # Create outcome key (include line if present)
                    if runner.get("line"):
                        outcome_key = f"{runner_id} {runner.get('line', '')}"
                    else:
                        outcome_key = runner_id
                    
                    outcome_odds[outcome_key][source] = round(odds, 2)
                    all_sources.add(source)
            
            if outcome_odds:
                market_first[market.get("key", "unknown")] = dict(outcome_odds)
        
        return {
            "markets": market_first,
            "sources": list(all_sources),
            "source_count": len(all_sources)
        }
