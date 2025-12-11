#!/usr/bin/env python3
"""
Production startup script for KashRock Data Stream service.
"""

import os
import asyncio
from pathlib import Path
import sys

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import app
from config import get_settings
import uvicorn
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

def main():
    """Main entry point for production."""
    settings = get_settings()
    
    logger.info(
        "Starting KashRock Data Stream service",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        debug=settings.debug
    )
    
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers if not settings.debug else 1,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True,
        use_colors=False  # Better for production logs
    )

if __name__ == "__main__":
    main()
