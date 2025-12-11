"""
KashRock Data Stream - Real-time sports data streaming service.

This package provides a scalable, high-performance data streaming infrastructure
for handling real-time sports data, odds updates, and live event streaming.
"""

__version__ = "0.1.0"
__author__ = "KashRock Team"
__email__ = "team@kashrock.com"

from config import get_settings
from main import create_app

__all__ = ["get_settings", "create_app"]
