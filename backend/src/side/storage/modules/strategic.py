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
        # Self-Initialize Schema and Migrations
        with self.engine.connection() as conn:
            self.init_schema(conn)

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
                signal_hash INTEGER, -- Sparse Semantic Hash (SimHash)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_pinned INTEGER DEFAULT 0
            )
        """)
        
        # ─────────────────────────────────────────────────────────────
        # CORE TABLE 6: PUBLIC_WISDOM - Architectural Patterns
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS public_wisdom (
                id TEXT PRIMARY KEY,
                origin_node TEXT,
                category TEXT, -- e.g. 'pattern', 'anti-pattern'
                signal_pattern TEXT, -- The triggering signal (e.g. 'auth_bypass')
                signal_hash INTEGER,
                wisdom_text TEXT NOT NULL,
                confidence INTEGER DEFAULT 5,
                source_type TEXT DEFAULT 'mesh',
                source_file TEXT,
                is_pinned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ─────────────────────────────────────────────────────────────
        # VIRTUAL TABLE: FTS5 SHADOW INDEX (Hybrid Lite)
        # ─────────────────────────────────────────────────────────────
        try:
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS public_wisdom_fts USING fts5(
                    id, 
                    wisdom_text, 
                    category, 
                    signal_pattern
                )
            """)
            # Triggers ensure the FTS index is always in sync with the main table
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS public_wisdom_ai AFTER INSERT ON public_wisdom BEGIN
                    INSERT INTO public_wisdom_fts(id, wisdom_text, category, signal_pattern) 
                    VALUES (new.id, new.wisdom_text, new.category, new.signal_pattern);
                END;
            """)
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS public_wisdom_ad AFTER DELETE ON public_wisdom BEGIN
                    DELETE FROM public_wisdom_fts WHERE id = old.id;
                END;
            """)
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS public_wisdom_au AFTER UPDATE ON public_wisdom BEGIN
                    UPDATE public_wisdom_fts SET 
                        wisdom_text = new.wisdom_text,
                        category = new.category,
                        signal_pattern = new.signal_pattern
                    WHERE id = old.id;
                END;
            """)
        except Exception as e:
             logger.warning(f"FTS5 setup for public_wisdom failed: {e}")
        # ─────────────────────────────────────────────────────────────
        # CORE TABLE 7: MEMORY - Long-Term Unstructured Facts [KAR-6.19]
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL DEFAULT 'default',
                content TEXT NOT NULL,
                tags TEXT, -- JSON Array
                metadata TEXT, -- JSON Object
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_project ON memory(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_created ON memory(created_at DESC)")

        # ─────────────────────────────────────────────────────────────
        # MIGRATIONS: Upgrade existing schemas (Must run before index creation)
        # ─────────────────────────────────────────────────────────────
        try:
            conn.execute("ALTER TABLE rejections ADD COLUMN signal_hash INTEGER")
        except: pass
        try:
            conn.execute("ALTER TABLE public_wisdom ADD COLUMN source_type TEXT DEFAULT 'mesh'")
        except: pass
        try:
            conn.execute("ALTER TABLE public_wisdom ADD COLUMN source_file TEXT")
        except: pass
        
        # [STRATEGIC AUDIT] Add is_pinned to prevent over-aggressive Neural Decay
        # Explicit calls to avoid f-string injection patterns for Semgrep
        for table in ["plans", "learnings", "rejections", "public_wisdom"]:
            try:
                if table == "plans":
                    conn.execute("ALTER TABLE plans ADD COLUMN is_pinned INTEGER DEFAULT 0")
                elif table == "learnings":
                    conn.execute("ALTER TABLE learnings ADD COLUMN is_pinned INTEGER DEFAULT 0")
                elif table == "rejections":
                    conn.execute("ALTER TABLE rejections ADD COLUMN is_pinned INTEGER DEFAULT 0")
                elif table == "public_wisdom":
                    conn.execute("ALTER TABLE public_wisdom ADD COLUMN is_pinned INTEGER DEFAULT 0")
            except: pass
            
        logger.info("MIGRATION: StrategicStore schema sync check complete.")

        try:
            conn.execute("ALTER TABLE public_wisdom ADD COLUMN signal_hash INTEGER")
            logger.info("MIGRATION: Added signal_hash to public_wisdom")
        except: pass

        conn.execute("CREATE INDEX IF NOT EXISTS idx_rejections_project ON rejections(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rejections_hash ON rejections(instruction_hash)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rejections_signal_hash ON rejections(signal_hash)")

        conn.execute("CREATE INDEX IF NOT EXISTS idx_public_wisdom_signal ON public_wisdom(signal_pattern)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_public_wisdom_hash ON public_wisdom(signal_hash)")


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

    def find_objectives_by_symbols(self, project_id: str, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        [TECH-04]: Maps architectural symbols (classes/functions) to strategic objectives.
        Uses fuzzy title/description matching.
        """
        if not symbols:
            return []
            
        objectives = []
        with self.engine.connection() as conn:
            for symbol in symbols:
                # 1. Try exact/contained match first
                query_val = "%" + symbol + "%"
                rows = conn.execute("""
                    SELECT id, title, type FROM plans 
                    WHERE project_id = ? AND status != 'done'
                    AND (title LIKE ? OR description LIKE ? OR notes LIKE ?)
                """, (project_id, query_val, query_val, query_val)).fetchall()
                
                # 2. If no match, try matching segments (CamelCase split)
                if not rows:
                    import re
                    segments = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)', symbol)
                    for seg in segments:
                        if len(seg) < 3: continue
                        seg_query = "%" + seg + "%"
                        rows += conn.execute("""
                            SELECT id, title, type FROM plans 
                            WHERE project_id = ? AND status != 'done'
                            AND (title LIKE ? OR description LIKE ? OR notes LIKE ?)
                        """, (project_id, seg_query, seg_query, seg_query)).fetchall()

                for row in rows:
                    objectives.append(dict(row))
        
        # Deduplicate results
        unique_objs = {obj['id']: obj for obj in objectives}.values()
        return list(unique_objs)

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
                       instruction_hash: str | None = None, diff_signature: str | None = None, **kwargs) -> None:
        """Save a single Correction Vector (Rejection)."""
        self.save_rejections_batch([{
            'id': rejection_id,
            'file_path': file_path,
            'reason': reason,
            'instruction_hash': instruction_hash,
            'diff_signature': diff_signature,
            'signal_hash': kwargs.get("signal_hash"),
            'project_id': kwargs.get("project_id", "default")
        }])

    def save_rejections_batch(self, rejections: List[Dict[str, Any]]) -> None:
        """Save multiple rejections in a single transaction."""
        with self.engine.connection() as conn:
            for rej in rejections:
                conn.execute(
                    """
                    INSERT INTO rejections (id, file_path, rejection_reason, instruction_hash, diff_signature, signal_hash, project_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        rejection_reason = excluded.rejection_reason,
                        diff_signature = excluded.diff_signature
                    """,
                    (rej['id'], rej['file_path'], rej['reason'], rej.get('instruction_hash'), 
                     rej.get('diff_signature'), rej.get('signal_hash'), rej.get('project_id', 'default')),
                )

    def list_rejections(self, limit: int = 10) -> list[dict[str, Any]]:
        """List recent rejections for the Sovereign Footer."""
        with self.engine.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM rejections ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [dict(row) for row in rows]

    def save_public_wisdom(self, wisdom_id: str, wisdom_text: str, origin_node: str | None = None,
                           category: str | None = None, signal_pattern: str | None = None,
                           confidence: int = 5, **kwargs) -> None:
        """Save a single architectural wisdom fragment."""
        self.save_public_wisdom_batch([{
            'id': wisdom_id,
            'text': wisdom_text,
            'origin': origin_node,
            'category': category,
            'pattern': signal_pattern,
            'confidence': confidence,
            'signal_hash': kwargs.get("signal_hash")
        }])

    def save_public_wisdom_batch(self, wisdom_list: List[Dict[str, Any]]) -> None:
        """Save multiple wisdom fragments in a single transaction."""
        with self.engine.connection() as conn:
            for w in wisdom_list:
                conn.execute(
                    """
                    INSERT INTO public_wisdom (id, origin_node, category, signal_pattern, signal_hash, wisdom_text, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        wisdom_text = excluded.wisdom_text,
                        signal_hash = excluded.signal_hash,
                        confidence = excluded.confidence
                    """,
                    (w['id'], w.get('origin'), w.get('category'), w.get('pattern'), 
                     w.get('signal_hash'), w['text'], w.get('confidence', 5)),
                )

    def list_public_wisdom(self, signal_pattern: str | None = None) -> List[Dict[str, Any]]:
        """Retrieve public wisdom, optionally filtered by architectural signal."""
        with self.engine.connection() as conn:
            if signal_pattern:
                rows = conn.execute(
                    "SELECT * FROM public_wisdom WHERE signal_pattern = ? ORDER BY confidence DESC",
                    (signal_pattern,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM public_wisdom ORDER BY created_at DESC").fetchall()
            return [dict(row) for row in rows]

    def search_wisdom(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        [Active Recall]: Search architectural wisdom using FTS5 (Hybrid Lite).
        """
        with self.engine.connection() as conn:
            try:
                # FTS5 Match
                safe_query = query.replace('"', '""').replace("'", "''")
                rows = conn.execute(f"""
                    SELECT w.* 
                    FROM public_wisdom_fts fts
                    JOIN public_wisdom w ON fts.id = w.id
                    WHERE public_wisdom_fts MATCH '{safe_query}'
                    ORDER BY rank
                    LIMIT ?
                """, (limit,)).fetchall()
                if rows:
                    return [dict(row) for row in rows]
            except Exception:
                pass
                
            # Fallback
            q = f"%{query}%"
            rows = conn.execute("""
                SELECT * FROM public_wisdom 
                WHERE wisdom_text LIKE ? OR signal_pattern LIKE ?
                ORDER BY confidence DESC
                LIMIT ?
            """, (q, q, limit)).fetchall()
            return [dict(row) for row in rows]

    # ─────────────────────────────────────────────────────────────
    # MEMORY METHODS (JSON-FREE PERSISTENCE)
    # ─────────────────────────────────────────────────────────────

    def save_fact(self, fact_id: str, project_id: str, content: str, 
                  tags: list | None = None, metadata: dict | None = None) -> None:
        """Saves an unstructured fact to the relational core."""
        import json
        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO memory (id, project_id, content, tags, metadata)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    content = excluded.content,
                    tags = excluded.tags,
                    metadata = excluded.metadata
                """,
                (
                    fact_id, 
                    project_id, 
                    content, 
                    json.dumps(tags or []), 
                    json.dumps(metadata or {})
                ),
            )

    def recall_facts(self, query: str, project_id: str, limit: int = 5) -> list[dict[str, Any]]:
        """Simple SQL-based fuzzy recall for facts."""
        import json
        with self.engine.connection() as conn:
            q = f"%{query}%"
            rows = conn.execute(
                """
                SELECT * FROM memory 
                WHERE project_id = ? AND (content LIKE ? OR tags LIKE ?)
                ORDER BY created_at DESC LIMIT ?
                """,
                (project_id, q, q, limit)
            ).fetchall()
            
            results = []
            for row in rows:
                d = dict(row)
                d["tags"] = json.loads(d["tags"]) if d["tags"] else []
                d["metadata"] = json.loads(d["metadata"]) if d["metadata"] else {}
                results.append(d)
            return results

    def purge_stale_rejections(self, days: int = 180) -> int:
        """
        Removes rejections older than N days.
        [NEURAL DECAY]: Strategic laws have a half-life.
        [STRATEGIC AUDIT]: Respects 'is_pinned' flag.
        """
        with self.engine.connection() as conn:
            cursor = conn.execute(
                "DELETE FROM rejections WHERE is_pinned = 0 AND created_at < datetime('now', ?)",
                (f'-{days} days',)
            )
            return cursor.rowcount

    def decay_strategic_fat(self, days: int = 30) -> Dict[str, int]:
        """
        [NEURAL DECAY]: Prunes low-entropy strategic data.
        - Keeps Objectives (priority > 5 or pinned) forever.
        - Prunes low-impact learnings older than 30 days.
        """
        counts = {}
        with self.engine.connection() as conn:
            # 1. Decay Low-Impact Learnings
            cursor = conn.execute(
                "DELETE FROM learnings WHERE is_pinned = 0 AND impact = 'low' AND created_at < datetime('now', ?)",
                (f'-{days} days',)
            )
            counts["learnings"] = cursor.rowcount
            
            # 2. Decay stale done tasks
            cursor = conn.execute(
                "DELETE FROM plans WHERE is_pinned = 0 AND status = 'done' AND type = 'task' AND created_at < datetime('now', ?)",
                (f'-7 days',) # Forgotten faster once achieved
            )
            counts["plans"] = cursor.rowcount
            
        return counts

