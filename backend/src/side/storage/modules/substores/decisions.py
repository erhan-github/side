import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from side.models.core import StrategicDecision
from side.utils.crypto import shield
from ..base import MerkleManager

logger = logging.getLogger(__name__)

class DecisionStore:
    def __init__(self, engine):
        self.engine = engine

    def init_schema(self, conn):
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
                merkle_hash TEXT,
                parent_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plan_id) REFERENCES plans(id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_decisions_project ON decisions(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_decisions_category ON decisions(category)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_decisions_plan ON decisions(plan_id)")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS learnings (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL DEFAULT 'default',
                insight TEXT NOT NULL,
                source TEXT,
                impact TEXT DEFAULT 'medium',
                plan_id TEXT,
                is_pinned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plan_id) REFERENCES plans(id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_learnings_project ON learnings(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_learnings_impact ON learnings(impact)")

    def save_decision(self, decision_id: str, question: str, answer: str,
                      reasoning: str | None = None, category: str | None = None,
                      plan_id: str | None = None, confidence: float = 5.0) -> None:
        with self.engine.connection() as conn:
            parent = conn.execute(
                "SELECT merkle_hash FROM decisions ORDER BY ROWID DESC LIMIT 1"
            ).fetchone()
            parent_hash = parent[0] if parent else None

        content = {"question": question, "answer": answer, "plan_id": plan_id, "category": category}
        merkle_hash = MerkleManager.calculate_hash(content, parent_hash)

        decision = StrategicDecision(
            id=decision_id,
            project_id="default",
            question=question,
            answer=answer,
            reasoning=shield.seal(reasoning) if reasoning else None,
            category=category or "general",
            plan_id=plan_id,
            confidence=confidence,
            merkle_hash=merkle_hash,
            parent_hash=parent_hash
        )

        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO decisions (id, project_id, question, answer, reasoning, category, plan_id, confidence, merkle_hash, parent_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    answer = excluded.answer,
                    reasoning = excluded.reasoning,
                    confidence = excluded.confidence,
                    merkle_hash = excluded.merkle_hash
                """,
                (decision.id, decision.project_id, decision.question, decision.answer, 
                 decision.reasoning, decision.category, decision.plan_id, 
                 decision.confidence, decision.merkle_hash, decision.parent_hash),
            )

    def list_decisions(self, category: str | None = None) -> list[StrategicDecision]:
        with self.engine.connection() as conn:
            if category:
                rows = conn.execute(
                    "SELECT * FROM decisions WHERE category = ? ORDER BY created_at DESC",
                    (category,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM decisions ORDER BY created_at DESC").fetchall()
            
            results = []
            for row in rows:
                dec = StrategicDecision.from_row(row)
                if dec.reasoning:
                    try: dec.reasoning = shield.unseal(dec.reasoning)
                    except Exception: dec.reasoning = "[ENCRYPTED_PRIVATE_REASONING]"
                results.append(dec)
            return results

    def save_learning(self, learning_id: str, insight: str, source: str | None = None,
                      impact: str = "medium", plan_id: str | None = None) -> None:
        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO learnings (id, insight, source, impact, plan_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (learning_id, insight, source, impact, plan_id),
            )

    def list_learnings(self, impact: str | None = None) -> list[dict[str, Any]]:
        with self.engine.connection() as conn:
            if impact:
                rows = conn.execute(
                    "SELECT * FROM learnings WHERE impact = ? ORDER BY created_at DESC",
                    (impact,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM learnings ORDER BY created_at DESC").fetchall()
            return [dict(row) for row in rows]
