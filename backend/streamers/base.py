"""
Base streamer class defining the interface for all data streamers.
"""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import structlog

logger = structlog.get_logger()


class BaseStreamer(ABC):
    """Abstract base class for all data streamers."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.is_running = False
        self.last_update = None
        self.error_count = 0
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 5)
        
        # Callbacks
        self.on_data_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None
        self.on_status_change_callback: Optional[Callable] = None
        
        logger.info("Initialized streamer", name=name, config=config)
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to data source."""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Close connection to data source."""
        pass
    
    @abstractmethod
    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch data from the source."""
        pass
    
    @abstractmethod
    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw data into standardized format."""
        pass
    
    async def start(self):
        """Start the data streaming process."""
        if self.is_running:
            logger.warning("Streamer already running", name=self.name)
            return
        
        try:
            logger.info("Starting streamer", name=self.name)
            
            # Connect to data source
            if not await self.connect():
                raise Exception("Failed to connect to data source")
            
            self.is_running = True
            self._notify_status_change("started")
            
            # Start streaming loop
            await self._stream_loop()
            
        except Exception as e:
            logger.error("Failed to start streamer", name=self.name, error=str(e))
            self._notify_error(e)
            raise
    
    async def stop(self):
        """Stop the data streaming process."""
        if not self.is_running:
            logger.warning("Streamer not running", name=self.name)
            return
        
        try:
            logger.info("Stopping streamer", name=self.name)
            
            self.is_running = False
            await self.disconnect()
            self._notify_status_change("stopped")
            
        except Exception as e:
            logger.error("Error stopping streamer", name=self.name, error=str(e))
            self._notify_error(e)
    
    async def _stream_loop(self):
        """Main streaming loop."""
        interval = self.config.get("interval", 1.0)
        
        while self.is_running:
            try:
                # Fetch and process data
                raw_data = await self.fetch_data()
                processed_data = await self.process_data(raw_data)
                
                # Update timestamp
                self.last_update = datetime.utcnow()
                
                # Notify data callback
                if self.on_data_callback:
                    await self.on_data_callback(processed_data)
                
                # Reset error count on success
                self.error_count = 0
                
                # Wait for next interval
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.error_count += 1
                logger.error(
                    "Error in stream loop", 
                    name=self.name, 
                    error=str(e), 
                    error_count=self.error_count
                )
                
                self._notify_error(e)
                
                # Implement exponential backoff
                if self.error_count <= self.max_retries:
                    delay = self.retry_delay * (2 ** (self.error_count - 1))
                    logger.info(
                        "Retrying after delay", 
                        name=self.name, 
                        delay=delay, 
                        attempt=self.error_count
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        "Max retries exceeded, stopping streamer", 
                        name=self.name
                    )
                    await self.stop()
                    break
    
    def set_data_callback(self, callback: Callable):
        """Set callback for when new data is received."""
        self.on_data_callback = callback
    
    def set_error_callback(self, callback: Callable):
        """Set callback for when errors occur."""
        self.on_error_callback = callback
    
    def set_status_change_callback(self, callback: Callable):
        """Set callback for when status changes."""
        self.on_status_change_callback = callback
    
    def _notify_data(self, data: Dict[str, Any]):
        """Notify data callback if set."""
        if self.on_data_callback:
            asyncio.create_task(self.on_data_callback(data))
    
    def _notify_error(self, error: Exception):
        """Notify error callback if set."""
        if self.on_error_callback:
            asyncio.create_task(self.on_error_callback(error))
    
    def _notify_status_change(self, status: str):
        """Notify status change callback if set."""
        if self.on_status_change_callback:
            asyncio.create_task(self.on_status_change_callback(status))
    
    def get_status(self) -> Dict[str, Any]:
        """Get current streamer status."""
        return {
            "name": self.name,
            "is_running": self.is_running,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "error_count": self.error_count,
            "config": self.config
        }
    
    def get_health(self) -> Dict[str, Any]:
        """Get streamer health information."""
        return {
            "name": self.name,
            "status": "healthy" if self.is_running and self.error_count == 0 else "unhealthy",
            "is_running": self.is_running,
            "error_count": self.error_count,
            "last_update": self.last_update.isoformat() if self.last_update else None
        }
