import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class MemoryStore:
    def __init__(self, engine):
        self.engine = engine

    def init_schema(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL DEFAULT 'default',
                content TEXT NOT NULL,
                tags TEXT, 
                metadata TEXT, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_project ON memory(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_created ON memory(created_at DESC)")

    def save_fact(self, fact_id: str, project_id: str, content: str, 
                  tags: list | None = None, metadata: dict | None = None) -> None:
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
                (fact_id, project_id, content, json.dumps(tags or []), json.dumps(metadata or {})),
            )

    def recall_facts(self, query: str, project_id: str, limit: int = 5) -> list[dict[str, Any]]:
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
