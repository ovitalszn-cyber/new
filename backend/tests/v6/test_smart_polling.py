
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from v6.background_worker import V6BackgroundWorker

@pytest.fixture
def mock_cache_manager():
    manager = AsyncMock()
    manager.get_hash.return_value = None
    manager.set_hash.return_value = True
    return manager

@pytest.fixture
def mock_odds_engine():
    engine = AsyncMock()
    # Default snapshot
    engine.get_signal_snapshot.return_value = {"hash": "hash_1", "timestamp": "now"}
    return engine

@pytest.fixture
def worker(mock_cache_manager, mock_odds_engine):
    with patch("v6.background_worker.get_historical_db"), \
         patch("v6.background_worker.get_metrics"), \
         patch("v6.background_worker.OptimizedOddsEngine", return_value=mock_odds_engine), \
         patch("v6.background_worker.OptimizedPropsEngine"):
        
        worker = V6BackgroundWorker(
            cache_manager=mock_cache_manager,
            active_books=["draftkings"],
            poll_interval=0.1
        )
        # Inject mocks directly as init creates new instances
        worker.odds_engine = mock_odds_engine
        worker.cache_manager = mock_cache_manager
        return worker

@pytest.mark.asyncio
async def test_update_needed_no_existing_hash(worker):
    """Should update if no hash exists in Redis."""
    worker.cache_manager.get_hash.return_value = None
    worker.odds_engine.get_signal_snapshot.return_value = {"hash": "new_hash"}
    
    needs_update = await worker._check_for_updates("sport_test")
    assert needs_update is True

@pytest.mark.asyncio
async def test_update_needed_hash_mismatch(worker):
    """Should update if new hash differs from old hash."""
    worker.cache_manager.get_hash.return_value = "old_hash"
    worker.odds_engine.get_signal_snapshot.return_value = {"hash": "new_hash"}
    
    needs_update = await worker._check_for_updates("sport_test")
    assert needs_update is True

@pytest.mark.asyncio
async def test_no_update_needed_hash_match(worker):
    """Should NOT update if hashes match."""
    worker.cache_manager.get_hash.return_value = "same_hash"
    worker.odds_engine.get_signal_snapshot.return_value = {"hash": "same_hash"}
    
    needs_update = await worker._check_for_updates("sport_test")
    assert needs_update is False

@pytest.mark.asyncio
async def test_fail_open_on_error(worker):
    """Should default to update if check fails."""
    worker.odds_engine.get_signal_snapshot.side_effect = Exception("API Error")
    
    needs_update = await worker._check_for_updates("sport_test")
    assert needs_update is True
