"""
Sovereign Operational Store - Cache, Metadata, & System Stats.
"""

import json
import logging
import hashlib
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base import SovereignEngine

logger = logging.getLogger(__name__)

class OperationalStore:
    def __init__(self, engine: SovereignEngine):
        self.engine = engine

    def init_schema(self, conn):
        """Initialize operational tables."""
        # ─────────────────────────────────────────────────────────────
        # META TABLE - Database versioning
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        conn.execute("INSERT OR IGNORE INTO meta (key, value) VALUES ('version', '1.0')")

        # ─────────────────────────────────────────────────────────────
        # OPERATIONAL TABLE: QUERY_CACHE
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


    def get_version(self) -> float:
        """Get current database version."""
        try:
            with self.engine.connection() as conn:
                row = conn.execute("SELECT value FROM meta WHERE key = 'version'").fetchone()
                return float(row["value"]) if row else 1.0
        except sqlite3.OperationalError:
            return 1.0

    def set_version(self, version: float) -> None:
        """Set database version."""
        with self.engine.connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES ('version', ?)",
                (str(version),)
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

    def get_database_stats(self, db_path: Path) -> dict[str, Any]:
        """Get database statistics."""
        with self.engine.connection() as conn:
            stats = {}
            tables = ["profile", "plans", "decisions", "learnings", "work_context", "query_cache", "activities", "audits"]
            for table in tables:
                try:
                    row = conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchone()
                    stats[f"{table}_count"] = row["count"] if row else 0
                except sqlite3.OperationalError:
                    stats[f"{table}_count"] = 0

            stats["db_size_bytes"] = db_path.stat().st_size if db_path.exists() else 0
            stats["db_size_mb"] = stats["db_size_bytes"] / (1024 * 1024)
            return stats

    def discover_sovereign_nodes(self) -> List[Path]:
        """Find all Sovereign nodes."""
        side_root = Path.home() / ".side"
        return list(side_root.glob("*.db"))

    def get_global_stats(self) -> Dict[str, Any]:
        """Aggregate stats across all discovered nodes."""
        nodes = self.discover_sovereign_nodes()
        total_size = 0
        total_profiles = 0
        node_details = []
        
        for node in nodes:
            try:
                size = node.stat().st_size
                total_size += size
                with sqlite3.connect(node) as conn:
                    # FIX: Use 'profile' instead of 'profiles'
                    count = conn.execute("SELECT COUNT(*) FROM profile").fetchone()[0]
                    total_profiles += count
                    node_details.append({
                        "name": node.name,
                        "size_mb": size / (1024 * 1024),
                        "profiles": count
                    })
            except Exception:
                continue
                
        return {
            "total_nodes": len(nodes),
            "total_size_mb": total_size / (1024 * 1024),
            "total_profiles": total_profiles,
            "nodes": node_details
        }
