"""
Ontology Store - Semantic Shadow (Entity-to-Entity Relationships).
"""

import logging
from typing import Any, Dict, List, Optional
from .base import ContextEngine

logger = logging.getLogger(__name__)

class OntologyStore:
    def __init__(self, engine: ContextEngine):
        self.engine = engine
        # Self-Initialize Schema
        with self.engine.connection() as conn:
            self.init_schema(conn)

    def init_schema(self, conn):
        """Initialize ontology tables."""
        # [MIGRATION]: Drop old relationships to relax constraints
        try:
            # Check if FK exists by looking at schema
            res = conn.execute("PRAGMA table_info(relationships)").fetchall()
            if res:
                # Simple approach: Drop and recreate since it's Phase 52 early dev
                conn.execute("DROP TABLE IF EXISTS relationships")
        except: pass

        # ─────────────────────────────────────────────────────────────
        # CORE TABLE 1: ENTITIES - Structural Anchors (Classes, Functions)
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL DEFAULT 'default',
                name TEXT NOT NULL,
                entity_type TEXT NOT NULL, -- 'class', 'function', 'module', 'table'
                file_path TEXT,
                signature TEXT,
                parent_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES entities(id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_entities_project ON entities(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name)")

        # ─────────────────────────────────────────────────────────────
        # CORE TABLE 2: RELATIONSHIPS - The "Semantic Shadow" (Call Graph/Usage)
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL DEFAULT 'default',
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation_type TEXT NOT NULL, -- 'calls', 'uses', 'inherits', 'references'
                confidence REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_project ON relationships(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relation_type)")

    def save_entities_batch(self, entities: List[Dict[str, Any]]) -> None:
        """Batch save structural entities."""
        with self.engine.connection() as conn:
            for ent in entities:
                conn.execute(
                    """
                    INSERT INTO entities (id, project_id, name, entity_type, file_path, signature, parent_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name = excluded.name,
                        entity_type = excluded.entity_type,
                        file_path = excluded.file_path,
                        signature = excluded.signature
                    """,
                    (ent['id'], ent.get('project_id', 'default'), ent['name'], 
                     ent['entity_type'], ent.get('file_path'), ent.get('signature'), ent.get('parent_id')),
                )

    def save_relationships_batch(self, relationships: List[Dict[str, Any]]) -> None:
        """Batch save entity relationships."""
        with self.engine.connection() as conn:
            for rel in relationships:
                conn.execute(
                    """
                    INSERT INTO relationships (id, project_id, source_id, target_id, relation_type, confidence)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO NOTHING
                    """,
                    (rel['id'], rel.get('project_id', 'default'), rel['source_id'], 
                     rel['target_id'], rel['relation_type'], rel.get('confidence', 1.0)),
                )

    def get_entity_by_name(self, project_id: str, name: str, entity_type: Optional[str] = None) -> Dict[str, Any] | None:
        """Fetch entity details by name."""
        with self.engine.connection() as conn:
            query = "SELECT * FROM entities WHERE project_id = ? AND name = ?"
            params = [project_id, name]
            if entity_type:
                query += " AND entity_type = ?"
                params.append(entity_type)
            row = conn.execute(query, params).fetchone()
            return dict(row) if row else None

    def list_relationships(self, source_id: Optional[str] = None, target_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List relationships for an entity."""
        with self.engine.connection() as conn:
            query = "SELECT * FROM relationships WHERE 1=1"
            params = []
            if source_id:
                query += " AND source_id = ?"
                params.append(source_id)
            if target_id:
                query += " AND target_id = ?"
                params.append(target_id)
            
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
