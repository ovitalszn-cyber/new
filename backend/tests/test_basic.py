"""
Basic tests for KashRock Data Stream service.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient

from main import create_app


@pytest.fixture
def app():
    """Create a test app instance."""
    return create_app()


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "endpoints" in data


def test_api_streams_list(client):
    """Test the streams list endpoint."""
    response = client.get("/api/v1/streams")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)


def test_websocket_info(client):
    """Test the WebSocket info endpoint."""
    response = client.get("/ws")
    assert response.status_code == 200
    
    data = response.json()
    assert "active_connections" in data
    assert "topics" in data


@pytest.mark.asyncio
async def test_app_lifespan():
    """Test the app lifespan manager."""
    app = create_app()
    
    # Test startup
    async with app.router.lifespan_context(app):
        # App should be running
        assert app.state is not None
    
    # App should be shut down
    pass


def test_config_loading():
    """Test that configuration can be loaded."""
    from config import get_settings
    
    settings = get_settings()
    assert settings.app_name == "KashRock Data Stream"
    assert settings.app_version == "0.1.0"
    assert isinstance(settings.debug, bool)
    assert isinstance(settings.port, int)


if __name__ == "__main__":
    pytest.main([__file__])
