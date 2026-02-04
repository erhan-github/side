"""
Sovereign Operational Store - Cache, Metadata, & System Stats.
Refined: Purged Universal Mesh (Social Bloat).
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
        query_str = f"{query_type}:{json.dumps(query_params, sort_keys=True)}"
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()[:16]
        expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)

        with self.engine.connection() as conn:
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
