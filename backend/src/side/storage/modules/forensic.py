"""
Sovereign Forensic Store - Audits, Activities, & Work Context.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from side.utils.crypto import shield
from .base import SovereignEngine, InsufficientTokensError

logger = logging.getLogger(__name__)

class ForensicStore:
    def __init__(self, engine: SovereignEngine):
        self.engine = engine

    def init_schema(self, conn):
        """Initialize forensic tables."""
        # ─────────────────────────────────────────────────────────────
        # CORE TABLE 7: AUDITS - Forensic History
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                tool TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                file_path TEXT,
                line_number INTEGER,
                run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSON
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audits_project ON audits(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audits_severity ON audits(severity)")

        # ─────────────────────────────────────────────────────────────
        # CORE TABLE 8: WORK_CONTEXT - Active work tracking
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS work_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_path TEXT NOT NULL,
                focus_area TEXT,
                recent_files JSON,
                recent_commits JSON,
                current_branch TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                confidence FLOAT DEFAULT 0.0
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_work_context_path ON work_context(project_path)")

        # ─────────────────────────────────────────────────────────────
        # CORE TABLE 11: ACTIVITIES - System Logs
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                tool TEXT NOT NULL,
                action TEXT NOT NULL,
                cost_tokens INTEGER DEFAULT 0,
                tier TEXT DEFAULT 'free',
                payload JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_activities_project ON activities(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_activities_tool ON activities(tool)")

        # ─────────────────────────────────────────────────────────────
        # CORE TABLE 12: OUTCOMES_LEDGER - Result history
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS outcomes_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                source_tool TEXT,
                outcome_type TEXT,
                success BOOLEAN,
                latency_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def log_activity(self, project_id: str, tool: str, action: str, 
                     cost_tokens: int = 0, tier: str = 'free', 
                     payload: dict[str, Any] | None = None) -> None:
        """Log an activity and debit token wallet."""
        with self.engine.connection() as conn:
            if cost_tokens > 0:
                row = conn.execute("SELECT token_balance FROM profile WHERE id = ?", (project_id,)).fetchone()
                balance = row['token_balance'] if row else 0
                if balance < cost_tokens:
                    logger.warning(f"🚫 Hard Stop: Insufficient tokens for {project_id} ({balance} available, {cost_tokens} needed)")
                    raise InsufficientTokensError(f"Insufficient tokens. {balance} remaining.")

            # SEAL SENSITIVE PAYLOAD
            sealed_payload = shield.seal(json.dumps(payload or {}))

            conn.execute(
                """
                INSERT INTO activities (
                    project_id, tool, action, cost_tokens, tier, payload
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (project_id, tool, action, cost_tokens, tier, sealed_payload)
            )
            
            if cost_tokens > 0:
                conn.execute(
                    "UPDATE profile SET token_balance = token_balance - ? WHERE id = ?",
                    (cost_tokens, project_id)
                )

    def get_recent_activities(self, project_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Get recent activities."""
        with self.engine.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM activities WHERE project_id = ? ORDER BY created_at DESC LIMIT ?",
                (project_id, limit)
            ).fetchall()
            results = []
            for row in rows:
                d = dict(row)
                if d.get("payload"):
                    try:
                        d["payload"] = json.loads(shield.unseal(d["payload"]))
                    except Exception:
                        # Fallback for old unencrypted data
                        try:
                            d["payload"] = json.loads(d["payload"])
                        except Exception:
                             d["payload"] = {"error": "[PAYLOAD_SEALED]"}
                results.append(d)
            return results

    def get_recent_audits(self, project_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent audits."""
        with self.engine.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM audits WHERE project_id = ? ORDER BY run_at DESC LIMIT ?",
                (project_id, limit)
            ).fetchall()
            return [dict(row) for row in rows]

    def get_audit_summary(self, project_id: str) -> dict[str, int]:
        """Get audit summary."""
        with self.engine.connection() as conn:
            rows = conn.execute(
                "SELECT severity, count(*) as count FROM audits WHERE project_id = ? GROUP BY severity",
                (project_id,)
            ).fetchall()
            return {row['severity']: row['count'] for row in rows}

    def save_work_context(self, project_path: str, focus_area: str, 
                          recent_files: list[str], recent_commits: list[dict[str, Any]],
                          current_branch: str | None = None, confidence: float = 0.8) -> None:
        """Save current work context."""
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO work_context (
                    project_path, focus_area, recent_files, recent_commits,
                    current_branch, expires_at, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (project_path, focus_area, json.dumps(recent_files),
                 json.dumps(recent_commits), current_branch,
                 expires_at.isoformat(), confidence),
            )

    def get_latest_work_context(self, project_path: str) -> dict[str, Any] | None:
        """Get latest work context."""
        with self.engine.connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM work_context 
                WHERE project_path = ? AND expires_at > ?
                ORDER BY detected_at DESC LIMIT 1
                """,
                (project_path, datetime.now(timezone.utc).isoformat()),
            ).fetchone()
            if row is None:
                return None
            return {
                "focus_area": row["focus_area"],
                "recent_files": json.loads(row["recent_files"]) if row["recent_files"] else [],
                "recent_commits": json.loads(row["recent_commits"]) if row["recent_commits"] else [],
                "current_branch": row["current_branch"],
                "detected_at": row["detected_at"],
                "confidence": row["confidence"],
            }

    def cleanup_expired_data(self) -> dict[str, int]:
        """Cleanup expired forensic data."""
        now = datetime.now(timezone.utc).isoformat()
        deleted = {}
        with self.engine.connection() as conn:
            # Cleanup work_context
            cursor = conn.execute("DELETE FROM work_context WHERE expires_at < ?", (now,))
            deleted["work_context"] = cursor.rowcount
            
            # Cleanup query_cache (will be handled by OperationalStore but listed here for consistency if needed)
            # Actually, let's keep it here if it's considered forensic/cleanup.
            # But the plan says TransientStore handles it.
            
            return deleted

    def prune_activities(self, days: int = 30) -> int:
        """
        Prune activity logs older than 'days' to prevent Fat DB syndrome.
        """
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        with self.engine.connection() as conn:
            cursor = conn.execute("DELETE FROM activities WHERE created_at < ?", (cutoff,))
            count = cursor.rowcount
            if count > 0:
                logger.info(f"🧹 Pruned {count} activities older than {days} days.")
            return count
