import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class PlanStore:
    def __init__(self, engine):
        self.engine = engine

    def init_schema(self, conn):
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
                is_pinned INTEGER DEFAULT 0,
                FOREIGN KEY (parent_id) REFERENCES plans(id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_plans_project ON plans(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_plans_type ON plans(type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_plans_status ON plans(status, due_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_plans_parent ON plans(parent_id)")

        # Progress tracking sub-table
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

    def save_plan(self, project_id: str, plan_id: str, title: str, plan_type: str = "goal",
                  description: str | None = None, due_date: str | None = None,
                  parent_id: str | None = None, priority: int = 0) -> None:
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
        with self.engine.connection() as conn:
            row = conn.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
            return dict(row) if row else None

    def list_plans(self, project_id: str | None = None, plan_type: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
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
        if not symbols: return []
        objectives = []
        with self.engine.connection() as conn:
            for symbol in symbols:
                query_val = "%" + symbol + "%"
                rows = conn.execute("""
                    SELECT id, title, type FROM plans 
                    WHERE project_id = ? AND status != 'done'
                    AND (title LIKE ? OR description LIKE ? OR notes LIKE ?)
                """, (project_id, query_val, query_val, query_val)).fetchall()
                
                if not rows:
                    segments = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)', symbol)
                    for seg in segments:
                        if len(seg) < 3: continue
                        seg_query = "%" + seg + "%"
                        rows += conn.execute("""
                            SELECT id, title, type FROM plans 
                            WHERE project_id = ? AND status != 'done'
                            AND (title LIKE ? OR description LIKE ? OR notes LIKE ?)
                        """, (project_id, seg_query, seg_query, seg_query)).fetchall()
                for row in rows: objectives.append(dict(row))
        unique_objs = {obj['id']: obj for obj in objectives}.values()
        return list(unique_objs)

    def update_plan_status(self, plan_id: str, status: str) -> bool:
        with self.engine.connection() as conn:
            completed_at = datetime.now(timezone.utc).isoformat() if status == "done" else None
            cursor = conn.execute(
                "UPDATE plans SET status = ?, completed_at = ? WHERE id = ?",
                (status, completed_at, plan_id),
            )
            return cursor.rowcount > 0

    def delete_plan(self, plan_id: str) -> bool:
        with self.engine.connection() as conn:
            cursor = conn.execute("DELETE FROM plans WHERE id = ?", (plan_id,))
            return cursor.rowcount > 0

    def save_check_in(self, check_in_id: str, plan_id: str, status: str, note: str | None = None) -> None:
        with self.engine.connection() as conn:
            conn.execute(
                "INSERT INTO check_ins (id, plan_id, status, note) VALUES (?, ?, ?, ?)",
                (check_in_id, plan_id, status, note),
            )

    def list_check_ins(self, plan_id: str) -> list[dict[str, Any]]:
        with self.engine.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM check_ins WHERE plan_id = ? ORDER BY created_at DESC",
                (plan_id,)
            ).fetchall()
            return [dict(row) for row in rows]

    # --- PLAN LINEAGE (RECURSIVE CONTEXT) ---

    def resolve_hierarchy(self, plan_id: str) -> List[Dict[str, Any]]:
        """
        [PLAN LINEAGE]: Resolves the full lineage of a plan from Leaf to Root.
        Returns ordered list: [Leaf, Parent, Grandparent, ... Root]
        """
        with self.engine.connection() as conn:
            # recursive_cte_query
            query = """
            WITH RECURSIVE lineage(id, project_id, title, type, status, parent_id, priority, created_at, level) AS (
                -- Anchor member: The starting plan
                SELECT id, project_id, title, type, status, parent_id, priority, created_at, 0
                FROM plans WHERE id = ?
                
                UNION ALL
                
                -- Recursive member: Join parent
                SELECT p.id, p.project_id, p.title, p.type, p.status, p.parent_id, p.priority, p.created_at, l.level + 1
                FROM plans p
                INNER JOIN lineage l ON p.id = l.parent_id
            )
            SELECT * FROM lineage ORDER BY level ASC;
            """
            rows = conn.execute(query, (plan_id,)).fetchall()
            return [dict(row) for row in rows]

    def get_plan_hierarchy(self, plan_id: str) -> Dict[str, Any]:
        """
        [CONTEXT HIERARCHY]: Generates the 'Full Context' for a task.
        Combines the specific task with the high-level goal of its ancestors.
        """
        chain = self.resolve_hierarchy(plan_id)
        if not chain:
            return {}

        # Leaf is chain[0], Root is chain[-1]
        leaf = chain[0]
        root = chain[-1]
        
        # Calculate Depth
        depth = len(chain)
        
        # Synthesize Context string (The "Why")
        # Format: "Root Goal > Strategy > Tactic > Task"
        breadcrumbs = " > ".join([p["title"] for p in reversed(chain)])
        
        return {
            "plan_id": leaf["id"],
            "title": leaf["title"],
            "depth": depth,
            "root_goal": root["title"] if root else None,
            "breadcrumbs": breadcrumbs,
            "full_chain": chain,
            "strategic_alignment": f"Adjusting '{leaf['title']}' to serve '{root['title']}'"
        }
