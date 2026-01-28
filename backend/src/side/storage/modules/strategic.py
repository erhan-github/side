"""
Sovereign Strategic Store - Plans, Decisions, & Learnings.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from side.utils.crypto import shield
from .base import SovereignEngine

logger = logging.getLogger(__name__)

class StrategicStore:
    def __init__(self, engine: SovereignEngine):
        self.engine = engine

    def init_schema(self, conn):
        """Initialize strategic tables."""
        # ─────────────────────────────────────────────────────────────
        # CORE TABLE 1: PLANS - Strategic Roadmap
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL DEFAULT 'default',
                title TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL DEFAULT 'goal',
                status TEXT DEFAULT 'active',
                parent_id TEXT,
                due_date DATE,
                priority INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (parent_id) REFERENCES plans(id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_plans_project ON plans(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_plans_type ON plans(type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_plans_status ON plans(status, due_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_plans_parent ON plans(parent_id)")

        # ─────────────────────────────────────────────────────────────
        # CORE TABLE 2: DECISIONS - Strategic Choices
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL DEFAULT 'default',
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                reasoning TEXT,
                category TEXT,
                plan_id TEXT,
                confidence INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plan_id) REFERENCES plans(id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_decisions_project ON decisions(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_decisions_category ON decisions(category)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_decisions_plan ON decisions(plan_id)")

        # ─────────────────────────────────────────────────────────────
        # CORE TABLE 3: LEARNINGS - Insights & Discoveries
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS learnings (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL DEFAULT 'default',
                insight TEXT NOT NULL,
                source TEXT,
                impact TEXT DEFAULT 'medium',
                plan_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plan_id) REFERENCES plans(id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_learnings_project ON learnings(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_learnings_impact ON learnings(impact)")

        # ─────────────────────────────────────────────────────────────
        # CORE TABLE 4: CHECK_INS - Progress Tracking
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS check_ins (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL DEFAULT 'default',
                plan_id TEXT NOT NULL,
                status TEXT,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plan_id) REFERENCES plans(id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_check_ins_project ON check_ins(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_check_ins_plan ON check_ins(plan_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_check_ins_date ON check_ins(created_at DESC)")

        # ─────────────────────────────────────────────────────────────
        # CORE TABLE 5: REJECTIONS - Correction Vectors (The "Kill" Signal)
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rejections (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL DEFAULT 'default',
                instruction_hash TEXT,
                file_path TEXT,
                rejection_reason TEXT, 
                diff_signature TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rejections_project ON rejections(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rejections_hash ON rejections(instruction_hash)")


    def save_plan(self, project_id: str, plan_id: str, title: str, plan_type: str = "goal",
                  description: str | None = None, due_date: str | None = None,
                  parent_id: str | None = None, priority: int = 0) -> None:
        """Save a strategic plan item."""
        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO plans (id, project_id, title, type, description, due_date, parent_id, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    project_id = excluded.project_id,
                    title = excluded.title,
                    type = excluded.type,
                    description = excluded.description,
                    due_date = excluded.due_date,
                    priority = excluded.priority
                """,
                (plan_id, project_id, title, plan_type, description, due_date, parent_id, priority),
            )

    def get_plan(self, plan_id: str) -> dict[str, Any] | None:
        """Get a plan by ID."""
        with self.engine.connection() as conn:
            row = conn.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
            return dict(row) if row else None

    def list_plans(self, project_id: str | None = None, plan_type: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        """List plans, optionally filtered."""
        with self.engine.connection() as conn:
            query = "SELECT * FROM plans WHERE 1=1"
            params = []
            if project_id:
                query += " AND project_id = ?"
                params.append(project_id)
            if plan_type:
                query += " AND type = ?"
                params.append(plan_type)
            if status:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY priority DESC, due_date"
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def update_plan_status(self, plan_id: str, status: str) -> bool:
        """Update plan status."""
        with self.engine.connection() as conn:
            completed_at = datetime.now(timezone.utc).isoformat() if status == "done" else None
            cursor = conn.execute(
                "UPDATE plans SET status = ?, completed_at = ? WHERE id = ?",
                (status, completed_at, plan_id),
            )
            return cursor.rowcount > 0

    def delete_plan(self, plan_id: str) -> bool:
        """Delete a plan."""
        with self.engine.connection() as conn:
            cursor = conn.execute("DELETE FROM plans WHERE id = ?", (plan_id,))
            return cursor.rowcount > 0

    def save_decision(self, decision_id: str, question: str, answer: str,
                      reasoning: str | None = None, category: str | None = None,
                      plan_id: str | None = None, confidence: int = 5) -> None:
        """Save a strategic decision."""
        # SEAL SENSITIVE REASONING
        sealed_reasoning = shield.seal(reasoning) if reasoning else None

        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO decisions (id, question, answer, reasoning, category, plan_id, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    answer = excluded.answer,
                    reasoning = excluded.reasoning,
                    confidence = excluded.confidence
                """,
                (decision_id, question, answer, sealed_reasoning, category, plan_id, confidence),
            )

    def list_decisions(self, category: str | None = None) -> list[dict[str, Any]]:
        """List decisions."""
        with self.engine.connection() as conn:
            query = "SELECT * FROM decisions ORDER BY created_at DESC"
            if category:
                rows = conn.execute(
                    "SELECT * FROM decisions WHERE category = ? ORDER BY created_at DESC",
                    (category,)
                ).fetchall()
            else:
                rows = conn.execute(query).fetchall()
            results = []
            for row in rows:
                d = dict(row)
                if d.get("reasoning"):
                    try:
                        d["reasoning"] = shield.unseal(d["reasoning"])
                    except Exception:
                        d["reasoning"] = "[ENCRYPTED_PRIVATE_REASONING]"
                results.append(d)
            return results

    def save_learning(self, learning_id: str, insight: str, source: str | None = None,
                      impact: str = "medium", plan_id: str | None = None) -> None:
        """Save a learning/insight."""
        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO learnings (id, insight, source, impact, plan_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (learning_id, insight, source, impact, plan_id),
            )

    def list_learnings(self, impact: str | None = None) -> list[dict[str, Any]]:
        """List learnings."""
        with self.engine.connection() as conn:
            if impact:
                rows = conn.execute(
                    "SELECT * FROM learnings WHERE impact = ? ORDER BY created_at DESC",
                    (impact,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM learnings ORDER BY created_at DESC").fetchall()
            return [dict(row) for row in rows]

    def save_check_in(self, check_in_id: str, plan_id: str, status: str, note: str | None = None) -> None:
        """Save a progress check-in."""
        with self.engine.connection() as conn:
            conn.execute(
                "INSERT INTO check_ins (id, plan_id, status, note) VALUES (?, ?, ?, ?)",
                (check_in_id, plan_id, status, note),
            )

    def list_check_ins(self, plan_id: str) -> list[dict[str, Any]]:
        """List check-ins for a plan."""
        with self.engine.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM check_ins WHERE plan_id = ? ORDER BY created_at DESC",
                (plan_id,)
            ).fetchall()
            return [dict(row) for row in rows]

    def save_rejection(self, rejection_id: str, file_path: str, reason: str, 
                       instruction_hash: str | None = None, diff_signature: str | None = None) -> None:
        """
        Save a Correction Vector (Rejection). 
        This is the 'Negative Context' that stops 'Beautiful Wrong Directions'.
        """
        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO rejections (id, file_path, rejection_reason, instruction_hash, diff_signature)
                VALUES (?, ?, ?, ?, ?)
                """,
                (rejection_id, file_path, reason, instruction_hash, diff_signature),
            )

    def list_rejections(self, limit: int = 10) -> list[dict[str, Any]]:
        """List recent rejections for the Sovereign Footer."""
        with self.engine.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM rejections ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [dict(row) for row in rows]

