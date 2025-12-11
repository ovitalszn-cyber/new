"""Persistence layer for historical odds and props data."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger()


class DataPersistence:
    """SQLite-based persistence for historical data."""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = "data/v6_historical.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS odds_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_key TEXT NOT NULL,
                    sport TEXT NOT NULL,
                    game_id TEXT NOT NULL,
                    data JSON NOT NULL,
                    fetched_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS props_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_key TEXT NOT NULL,
                    sport TEXT NOT NULL,
                    player_id TEXT NOT NULL,
                    stat_type_id INTEGER NOT NULL,
                    stat_value REAL NOT NULL,
                    direction TEXT NOT NULL,
                    odds INTEGER NOT NULL,
                    fetched_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    tags JSON,
                    timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better query performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_odds_book_sport ON odds_history(book_key, sport)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_props_book_player ON props_history(book_key, player_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_type_name ON api_metrics(metric_type, metric_name)")
            
            conn.commit()
    
    def store_odds_snapshot(self, book_key: str, sport: str, odds_data: List[Dict[str, Any]]) -> None:
        """Store odds snapshot for historical tracking."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                fetched_at = datetime.now(timezone.utc).isoformat()
                
                for game_data in odds_data:
                    conn.execute("""
                        INSERT INTO odds_history (book_key, sport, game_id, data, fetched_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (book_key, sport, game_data.get("game_id"), json.dumps(game_data), fetched_at))
                
                conn.commit()
                logger.info("Stored odds snapshot", book=book_key, sport=sport, games=len(odds_data))
                
        except Exception as exc:
            logger.error("Failed to store odds snapshot", book=book_key, sport=sport, error=str(exc))
    
    def store_props_snapshot(self, book_key: str, sport: str, props_data: List[Dict[str, Any]]) -> None:
        """Store props snapshot for historical tracking."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                fetched_at = datetime.now(timezone.utc).isoformat()
                
                for prop_data in props_data:
                    conn.execute("""
                        INSERT INTO props_history (
                            book_key, sport, player_id, stat_type_id, stat_value, 
                            direction, odds, fetched_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        book_key, sport, prop_data.get("player_id"), 
                        prop_data.get("stat_type_id"), prop_data.get("stat_value"),
                        prop_data.get("direction"), prop_data.get("odds"), fetched_at
                    ))
                
                conn.commit()
                logger.info("Stored props snapshot", book=book_key, sport=sport, props=len(props_data))
                
        except Exception as exc:
            logger.error("Failed to store props snapshot", book=book_key, sport=sport, error=str(exc))
    
    def store_metric(self, metric_type: str, metric_name: str, value: float, 
                    tags: Optional[Dict[str, str]] = None) -> None:
        """Store metric data for monitoring."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                timestamp = datetime.now(timezone.utc).isoformat()
                
                conn.execute("""
                    INSERT INTO api_metrics (metric_type, metric_name, value, tags, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (metric_type, metric_name, value, json.dumps(tags or {}), timestamp))
                
                conn.commit()
                
        except Exception as exc:
            logger.error("Failed to store metric", metric_type=metric_type, metric_name=metric_name, error=str(exc))
    
    def get_odds_history(self, book_key: str, sport: str, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Retrieve historical odds data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT data, fetched_at FROM odds_history
                    WHERE book_key = ? AND sport = ? 
                    AND fetched_at > datetime('now', '-{} hours')
                    ORDER BY fetched_at DESC
                """.format(hours_back), (book_key, sport))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "data": json.loads(row[0]),
                        "fetched_at": row[1],
                    })
                
                return results
                
        except Exception as exc:
            logger.error("Failed to retrieve odds history", book=book_key, sport=sport, error=str(exc))
            return []
    
    def get_props_history(self, book_key: str, player_id: str, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Retrieve historical props data for a player."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT stat_type_id, stat_value, direction, odds, fetched_at
                    FROM props_history
                    WHERE book_key = ? AND player_id = ?
                    AND fetched_at > datetime('now', '-{} hours')
                    ORDER BY fetched_at DESC
                """.format(hours_back), (book_key, player_id))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "stat_type_id": row[0],
                        "stat_value": row[1],
                        "direction": row[2],
                        "odds": row[3],
                        "fetched_at": row[4],
                    })
                
                return results
                
        except Exception as exc:
            logger.error("Failed to retrieve props history", book=book_key, player_id=player_id, error=str(exc))
            return []
    
    def get_metrics_summary(self, hours_back: int = 1) -> Dict[str, Any]:
        """Get metrics summary for monitoring."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT metric_type, metric_name, AVG(value) as avg_value, 
                           COUNT(*) as count, MAX(timestamp) as last_seen
                    FROM api_metrics
                    WHERE timestamp > datetime('now', '-{} hours')
                    GROUP BY metric_type, metric_name
                    ORDER BY metric_type, metric_name
                """.format(hours_back))
                
                results = {}
                for row in cursor.fetchall():
                    metric_type = row[0]
                    if metric_type not in results:
                        results[metric_type] = {}
                    
                    results[metric_type][row[1]] = {
                        "avg_value": row[2],
                        "count": row[3],
                        "last_seen": row[4],
                    }
                
                return results
                
        except Exception as exc:
            logger.error("Failed to retrieve metrics summary", error=str(exc))
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> None:
        """Clean up old historical data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Clean up odds history
                cursor = conn.execute("""
                    DELETE FROM odds_history 
                    WHERE created_at < datetime('now', '-{} days')
                """.format(days_to_keep))
                odds_deleted = cursor.rowcount
                
                # Clean up props history
                cursor = conn.execute("""
                    DELETE FROM props_history 
                    WHERE created_at < datetime('now', '-{} days')
                """.format(days_to_keep))
                props_deleted = cursor.rowcount
                
                # Clean up old metrics (keep shorter history)
                cursor = conn.execute("""
                    DELETE FROM api_metrics 
                    WHERE created_at < datetime('now', '-7 days')
                """)
                metrics_deleted = cursor.rowcount
                
                conn.commit()
                logger.info("Cleaned up old data", 
                           odds_deleted=odds_deleted, 
                           props_deleted=props_deleted,
                           metrics_deleted=metrics_deleted)
                
        except Exception as exc:
            logger.error("Failed to cleanup old data", error=str(exc))


# Global persistence instance
_persistence: Optional[DataPersistence] = None


def get_persistence() -> DataPersistence:
    """Get global persistence instance."""
    global _persistence
    if _persistence is None:
        _persistence = DataPersistence()
    return _persistence
