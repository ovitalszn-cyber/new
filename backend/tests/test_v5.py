"""
Basic tests for v5 unified endpoint.

These tests verify the pipeline components work together.
"""

import pytest
import asyncio
from datetime import datetime
from v5.connector_adapter import ConnectorAdapter, SourceEnvelope
from v5.mapping_worker import MappingWorker, CanonicalEnvelope
from v5.entity_resolver import EntityResolver
from v5.merge_service import MergeService
from v5.ev_engine import EVEngine
from v5.cache import CacheManager


def test_source_envelope_creation():
    """Test SourceEnvelope can be created."""
    envelope = SourceEnvelope(
        source="test",
        ts=datetime.utcnow().isoformat(),
        source_event_id="test_123",
        market_type="h2h",
        market_key="h2h_home",
        runner_id="Team A",
        odds=2.0,
        raw_payload={"test": "data"}
    )
    
    assert envelope.source == "test"
    assert envelope.odds == 2.0
    assert envelope.to_dict()["source"] == "test"


def test_mapping_worker_initialization():
    """Test MappingWorker can be initialized."""
    worker = MappingWorker()
    assert worker.mapping_repo_path.exists() or worker.mapping_repo_path.parent.exists()


def test_entity_resolver_initialization():
    """Test EntityResolver can be initialized."""
    resolver = EntityResolver()
    assert resolver is not None


def test_merge_service_initialization():
    """Test MergeService can be initialized."""
    service = MergeService()
    assert service.source_weights is not None
    assert "novig" in service.source_weights


def test_ev_engine_initialization():
    """Test EVEngine can be initialized."""
    engine = EVEngine(min_edge=2.0)
    assert engine.min_edge == 2.0
    assert engine.sharp_books == {"novig", "pinnacle"}


def test_cache_manager_initialization():
    """Test CacheManager can be initialized."""
    cache = CacheManager()
    assert cache is not None


@pytest.mark.asyncio
async def test_cache_set_get():
    """Test cache set and get operations."""
    cache = CacheManager()
    
    await cache.set("test_key", {"test": "value"}, ttl_seconds=60)
    value = await cache.get("test_key")
    
    assert value is not None
    assert value["test"] == "value"


def test_canonical_envelope_creation():
    """Test CanonicalEnvelope can be created."""
    envelope = CanonicalEnvelope(
        sport="basketball_nba",
        start_ts=datetime.utcnow().isoformat(),
        markets=[{"key": "h2h", "runners": []}],
        provenance={},
        source="test",
        source_event_id="test_123"
    )
    
    assert envelope.sport == "basketball_nba"
    assert len(envelope.markets) == 1


@pytest.mark.asyncio
async def test_mapping_worker_map_to_canonical():
    """Test mapping worker can map source envelope to canonical."""
    worker = MappingWorker()
    
    source_envelope = SourceEnvelope(
        source="test",
        ts=datetime.utcnow().isoformat(),
        source_event_id="test_123",
        market_type="h2h",
        market_key="h2h_home",
        runner_id="Lakers",
        odds=2.0,
        raw_payload={"test": "data"},
        sport="basketball_nba",
        home_team="Los Angeles Lakers",
        away_team="Golden State Warriors",
        commence_time=datetime.utcnow().isoformat()
    )
    
    canonical = await worker.map_to_canonical(source_envelope)
    
    assert canonical is not None
    assert canonical.sport == "basketball_nba"
    assert len(canonical.markets) > 0


@pytest.mark.asyncio
async def test_entity_resolver_resolve_events():
    """Test entity resolver can resolve events."""
    resolver = EntityResolver()
    
    envelopes = [
        CanonicalEnvelope(
            sport="basketball_nba",
            start_ts=datetime.utcnow().isoformat(),
            markets=[{"key": "h2h", "runners": []}],
            provenance={},
            source="test1",
            source_event_id="test_123",
            home_team="Los Angeles Lakers",
            away_team="Golden State Warriors"
        ),
        CanonicalEnvelope(
            sport="basketball_nba",
            start_ts=datetime.utcnow().isoformat(),
            markets=[{"key": "h2h", "runners": []}],
            provenance={},
            source="test2",
            source_event_id="test_456",
            home_team="Los Angeles Lakers",
            away_team="Golden State Warriors"
        )
    ]
    
    resolved = await resolver.resolve_events(envelopes)
    
    assert len(resolved) > 0
    assert "canonical_event_id" in resolved[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])




