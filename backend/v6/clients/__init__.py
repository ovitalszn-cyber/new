"""
V6 API clients for sports data sources.
"""

from .thescore import TheScoreClient
from .base import BaseAPIClient

__all__ = ["TheScoreClient", "BaseAPIClient"]
