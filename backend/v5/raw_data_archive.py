"""Raw Data Archive - Stores all raw payloads permanently (simulating S3).

This is the "Raw Data Archives" component of the News Agency architecture.
Every raw piece of data from every reporter is immediately stored permanently
for replays, audits, and debugging.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import structlog
import json
import hashlib
import gzip

logger = structlog.get_logger()


class RawDataArchive:
    """
    Archives raw payloads from connectors.
    
    For MVP, stores to local filesystem. Future: migrate to S3.
    """
    
    def __init__(self, archive_dir: Optional[str] = None):
        """
        Initialize raw data archive.
        
        Args:
            archive_dir: Directory to store archives (defaults to data/raw_archive/)
        """
        if archive_dir is None:
            # Default to project root / data/raw_archive/
            archive_dir = Path(__file__).parent.parent.parent.parent / "data" / "raw_archive"
        
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Raw data archive initialized", archive_dir=str(self.archive_dir))
    
    async def archive_envelope(
        self,
        source: str,
        source_event_id: str,
        raw_payload: Dict[str, Any],
        timestamp: Optional[str] = None
    ) -> str:
        """
        Archive a raw payload envelope.
        
        Args:
            source: Source name (e.g., "novig", "pinnacle")
            source_event_id: Source-specific event ID
            raw_payload: Raw payload data
            timestamp: ISO timestamp (defaults to now)
            
        Returns:
            Archive path/key for this payload
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        
        # Create deterministic archive key
        payload_hash = self._hash_payload(raw_payload)
        date_str = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%Y%m%d')
        
        # Archive structure: {date}/{source}/{source_event_id}_{hash}.json.gz
        archive_path = self.archive_dir / date_str / source
        archive_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"{source_event_id}_{payload_hash[:12]}.json.gz"
        filepath = archive_path / filename
        
        # Compress and store
        try:
            payload_json = json.dumps(raw_payload, sort_keys=True, default=str)
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                f.write(payload_json)
            
            logger.debug(
                "Archived raw payload",
                source=source,
                source_event_id=source_event_id,
                archive_path=str(filepath),
                size_bytes=filepath.stat().st_size
            )
            
            return str(filepath)
        except Exception as e:
            logger.error(
                "Failed to archive raw payload",
                source=source,
                source_event_id=source_event_id,
                error=str(e)
            )
            raise
    
    async def retrieve_archive(
        self,
        archive_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a raw payload from archive.
        
        Args:
            archive_path: Path to archived file
            
        Returns:
            Raw payload dict or None if not found
        """
        filepath = Path(archive_path)
        
        if not filepath.exists():
            logger.warning("Archive file not found", path=archive_path)
            return None
        
        try:
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                payload = json.load(f)
            
            logger.debug("Retrieved archive", path=archive_path)
            return payload
        except Exception as e:
            logger.error("Failed to retrieve archive", path=archive_path, error=str(e))
            return None
    
    def _hash_payload(self, payload: Dict[str, Any]) -> str:
        """Create deterministic hash of payload."""
        payload_str = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(payload_str.encode()).hexdigest()
    
    async def list_archives(
        self,
        source: Optional[str] = None,
        date: Optional[str] = None
    ) -> List[str]:
        """
        List archived files.
        
        Args:
            source: Filter by source name
            date: Filter by date (YYYYMMDD format)
            
        Returns:
            List of archive paths
        """
        archives = []
        
        if date:
            search_dir = self.archive_dir / date
        else:
            search_dir = self.archive_dir
        
        if not search_dir.exists():
            return []
        
        if source:
            source_dir = search_dir / source
            if source_dir.exists():
                for filepath in source_dir.glob("*.json.gz"):
                    archives.append(str(filepath))
        else:
            for source_dir in search_dir.iterdir():
                if source_dir.is_dir():
                    for filepath in source_dir.glob("*.json.gz"):
                        archives.append(str(filepath))
        
        return sorted(archives)

