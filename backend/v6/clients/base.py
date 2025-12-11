"""
Base API client with common functionality for sports data sources.
"""

import asyncio
import httpx
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from abc import ABC, abstractmethod
import structlog

logger = structlog.get_logger(__name__)


class BaseAPIClient(ABC):
    """Base class for sports API clients with common functionality."""
    
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        rate_limit_delay: float = 0.1
    ):
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        
        # HTTP client setup
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request with error handling and rate limiting."""
        
        # Rate limiting
        if self.rate_limit_delay > 0:
            await asyncio.sleep(self.rate_limit_delay)
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = {**self.headers, **(headers or {})}
        
        try:
            logger.debug(
                "Making API request",
                method=method,
                url=url,
                params=params
            )
            
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                headers=request_headers
            )
            response.raise_for_status()
            
            data = response.json()
            logger.debug(
                "API request successful",
                method=method,
                url=url,
                status_code=response.status_code
            )
            
            return data
            
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error in API request",
                method=method,
                url=url,
                status_code=e.response.status_code,
                error=str(e)
            )
            raise
        except httpx.RequestError as e:
            logger.error(
                "Request error in API request",
                method=method,
                url=url,
                error=str(e)
            )
            raise
        except Exception as e:
            logger.error(
                "Unexpected error in API request",
                method=method,
                url=url,
                error=str(e)
            )
            raise
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make a GET request."""
        return await self._make_request(endpoint, "GET", params, headers)
    
    @abstractmethod
    async def get_games(self, sport: str, league: str, **kwargs) -> List[Dict[str, Any]]:
        """Get games for a sport/league."""
        pass
    
    @abstractmethod
    async def get_teams(self, sport: str, league: str, **kwargs) -> List[Dict[str, Any]]:
        """Get teams for a sport/league."""
        pass
    
    @abstractmethod
    async def get_players(self, team_id: int, **kwargs) -> List[Dict[str, Any]]:
        """Get players for a team."""
        pass
