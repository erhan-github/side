"""
System Operational Store - Cache, Metadata, & System Stats.
Refined: Purged Project Graph.
"""

import json
import logging
import hashlib
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base import ContextEngine

logger = logging.getLogger(__name__)

class OperationalStore:
    """Enterprise-grade Operational Store - Handles Cache, Metadata, and Telemetry."""
    def __init__(self, engine: ContextEngine):
        self.engine = engine
        with self.engine.connection() as conn:
            self.init_schema(conn)

    def init_schema(self, conn):
        """Initialize operational tables."""
        # ─────────────────────────────────────────────────────────────
        # META TABLE - Database versioning & Settings
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        conn.execute("INSERT OR IGNORE INTO meta (key, value) VALUES ('version', '1.1')")

        # ─────────────────────────────────────────────────────────────
        # QUERY_CACHE - High-performance local cache
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS query_cache (
                query_hash TEXT PRIMARY KEY,
                query_type TEXT NOT NULL,
                result JSON NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_query_cache_expires ON query_cache(expires_at)")

        # ─────────────────────────────────────────────────────────────
        # TELEMETRY_ALERTS - Local proactive observations
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                file_path TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_status ON telemetry_alerts(status)")
        
        # ─────────────────────────────────────────────────────────────
        # REPO_FINGERPRINT - Persistent Cache for project profiles
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS repo_fingerprint (
                project_id TEXT PRIMARY KEY,
                data JSON NOT NULL,
                stats JSON NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def get_version(self) -> str:
        """Get the database schema version."""
        return self.get_setting("version", "1.0")

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        """Get a global system setting."""
        with self.engine.connection() as conn:
            row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        """Set a global system setting."""
        with self.engine.connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
                (key, str(value))
            )

    def save_query_cache(self, query_type: str, query_params: dict[str, Any], 
                         result: Any, ttl_hours: int = 1) -> None:
        """Cache query result."""
        from side.config import config
        
        query_str = f"{query_type}:{json.dumps(query_params, sort_keys=True)}"
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()[:16]
        expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)

        with self.engine.connection() as conn:
            # Check cache size and evict if necessary
            if config.enable_cache_eviction:
                stats = self.get_cache_stats()
                if stats["entry_count"] >= config.max_cache_entries:
                    # Evict oldest entries (LRU strategy)
                    evict_count = config.cache_eviction_batch_size
                    logger.warning(
                        f"Cache limit reached ({stats['entry_count']}/{config.max_cache_entries}), "
                        f"evicting {evict_count} oldest entries"
                    )
                    conn.execute(
                        """
                        DELETE FROM query_cache 
                        WHERE query_hash IN (
                            SELECT query_hash FROM query_cache 
                            ORDER BY cached_at ASC 
                            LIMIT ?
                        )
                        """,
                        (evict_count,)
                    )
            
            # Insert new entry
            conn.execute(
                """
                INSERT INTO query_cache (query_hash, query_type, result, expires_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(query_hash) DO UPDATE SET
                    result = excluded.result,
                    cached_at = CURRENT_TIMESTAMP,
                    expires_at = excluded.expires_at
                """,
                (query_hash, query_type, json.dumps(result), expires_at.isoformat()),
            )

    def get_query_cache(self, query_type: str, query_params: dict[str, Any]) -> Any | None:
        """Get cached query result."""
        query_str = f"{query_type}:{json.dumps(query_params, sort_keys=True)}"
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()[:16]

        with self.engine.connection() as conn:
            row = conn.execute(
                "SELECT result FROM query_cache WHERE query_hash = ? AND expires_at > ?",
                (query_hash, datetime.now(timezone.utc).isoformat()),
            ).fetchone()
            return json.loads(row["result"]) if row else None

    def invalidate_query_cache(self, query_type: str | None = None) -> int:
        """Invalidate query cache."""
        with self.engine.connection() as conn:
            if query_type:
                cursor = conn.execute("DELETE FROM query_cache WHERE query_type = ?", (query_type,))
            else:
                cursor = conn.execute("DELETE FROM query_cache")
            return cursor.rowcount
    
    def get_cache_stats(self) -> dict[str, Any]:
        """
        Get cache statistics for memory diagnostics.
        
        Returns:
            Dictionary with cache metrics
        """
        with self.engine.connection() as conn:
            # Get entry count
            count_row = conn.execute("SELECT COUNT(*) as count FROM query_cache").fetchone()
            entry_count = count_row["count"] if count_row else 0
            
            # Get total size estimate (JSON length)
            size_row = conn.execute("SELECT SUM(LENGTH(result)) as total_size FROM query_cache").fetchone()
            total_size_bytes = size_row["total_size"] if size_row and size_row["total_size"] else 0
            
            # Get oldest and newest entries
            oldest_row = conn.execute("SELECT MIN(cached_at) as oldest FROM query_cache").fetchone()
            newest_row = conn.execute("SELECT MAX(cached_at) as newest FROM query_cache").fetchone()
            
            return {
                "entry_count": entry_count,
                "size_bytes": total_size_bytes,
                "size_mb": total_size_bytes / (1024 * 1024),
                "oldest_entry": oldest_row["oldest"] if oldest_row else None,
                "newest_entry": newest_row["newest"] if newest_row else None
            }

    def save_telemetry_alert(self, project_id: str, alert_type: str, severity: str, 
                             message: str, file_path: str | None = None) -> None:
        """Log a proactive local warning."""
        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO telemetry_alerts (project_id, type, severity, message, file_path)
                VALUES (?, ?, ?, ?, ?)
                """,
                (project_id, alert_type, severity, message, file_path),
            )

    def get_active_telemetry_alerts(self, project_id: str | None = None) -> List[Dict[str, Any]]:
        """Retrieve active local warnings."""
        with self.engine.connection() as conn:
            if project_id:
                rows = conn.execute(
                    "SELECT * FROM telemetry_alerts WHERE project_id = ? AND status = 'active' ORDER BY timestamp DESC",
                    (project_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM telemetry_alerts WHERE status = 'active' ORDER BY timestamp DESC"
                ).fetchall()
            return [dict(row) for row in rows]

    def resolve_telemetry_alert(self, alert_id: int) -> None:
        """Mark a telemetry alert as resolved."""
        with self.engine.connection() as conn:
            conn.execute(
                "UPDATE telemetry_alerts SET status = 'resolved' WHERE id = ?",
                (alert_id,)
            )

    def get_database_stats(self, db_path: Path) -> dict[str, Any]:
        """Get local database statistics."""
        with self.engine.connection() as conn:
            stats = {}
            tables = ["profile", "plans", "decisions", "learnings", "work_context", "query_cache", "activities", "audits", "wisdom_patterns", "wisdom_antipatterns"]
            for table in tables:
                try:
                    row = conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchone()
                    stats[f"{table}_count"] = row["count"] if row else 0
                except sqlite3.OperationalError:
                    stats[f"{table}_count"] = 0

            stats["db_size_bytes"] = db_path.stat().st_size if db_path.exists() else 0
            stats["db_size_mb"] = stats["db_size_bytes"] / (1024 * 1024)
            return stats

    def save_fingerprint(self, project_id: str, data: Dict, stats: Dict) -> None:
        """Saves repo fingerprint to avoid re-scanning."""
        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO repo_fingerprint (project_id, data, stats, last_updated)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (project_id, json.dumps(data), json.dumps(stats))
            )

    def get_fingerprint(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached fingerprinted state."""
        with self.engine.connection() as conn:
            row = conn.execute(
                "SELECT data, stats, last_updated FROM repo_fingerprint WHERE project_id = ?",
                (project_id,)
            ).fetchone()
            if row:
                return {
                    "data": json.loads(row["data"]),
                    "stats": json.loads(row["stats"]),
                    "last_updated": row["last_updated"]
                }
        return None


# Export names for backward compatibility and service standardization
SessionCache = OperationalStore
