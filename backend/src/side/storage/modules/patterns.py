"""
Sovereign Pattern Store - Executable Knowledge & Workflows.
Implements the 'Dash' Strategy: Storing not just data, but *how* to solve problems.
Uses "Hybrid Lite" Search: SQLite FTS5 + Semantic Tagging.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from side.utils.crypto import shield
from .base import SovereignEngine

logger = logging.getLogger(__name__)

class PatternStore:
    def __init__(self, engine: SovereignEngine):
        self.engine = engine
        with self.engine.connection() as conn:
            self.init_schema(conn)

    def init_schema(self, conn):
        """Initialize pattern tables and FTS indexes."""
        
        # ─────────────────────────────────────────────────────────────
        # TABLE 1: PATTERNS - The Golden Scripts
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL DEFAULT 'default',
                intent TEXT NOT NULL,         -- "Fix Docker Build Failure"
                tool_sequence JSON NOT NULL,  -- The exact steps [tool_name, args]
                keywords JSON,                -- [docker, build, python, error] (For Search)
                success_count INTEGER DEFAULT 1,
                last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_patterns_project ON patterns(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_patterns_success ON patterns(success_count DESC)")

        # ─────────────────────────────────────────────────────────────
        # VIRTUAL TABLE: FTS5 SHADOW INDEX (Hybrid Lite)
        # ─────────────────────────────────────────────────────────────
        # We index the 'intent' and 'keywords' for blazing fast recall.
        # We DO NOT index the 'tool_sequence' JSON blob (it's noise).
        try:
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts USING fts5(
                    id, 
                    intent, 
                    keywords, 
                    tokenize='porter uni'
                )
            """)
            
            # TRIGGER: Auto-Update FTS on INSERT
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS patterns_ai AFTER INSERT ON patterns BEGIN
                    INSERT INTO patterns_fts(id, intent, keywords) 
                    VALUES (new.id, new.intent, new.keywords);
                END;
            """)
            
            # TRIGGER: Auto-Update FTS on DELETE
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS patterns_ad AFTER DELETE ON patterns BEGIN
                    DELETE FROM patterns_fts WHERE id = old.id;
                END;
            """)
            
            # TRIGGER: Auto-Update FTS on UPDATE
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS patterns_au AFTER UPDATE ON patterns BEGIN
                    UPDATE patterns_fts SET 
                        intent = new.intent, 
                        keywords = new.keywords 
                    WHERE id = old.id;
                END;
            """)
            
        except Exception as e:
            # Fallback for systems without FTS5 (rare, but safe)
            logger.warning(f"FTS5 Not Supported: {e}. Pattern search will fall back to slow legacy mode.")

    def save_pattern(self, pattern_id: str, intent: str, tool_sequence: List[Dict[str, Any]], 
                     keywords: List[str], project_id: str = "default") -> None:
        """
        Save a verified pattern (executable knowledge).
        """
        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO patterns (id, project_id, intent, tool_sequence, keywords)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    tool_sequence = excluded.tool_sequence,
                    keywords = excluded.keywords,
                    success_count = success_count + 1,
                    last_used_at = CURRENT_TIMESTAMP
                """,
                (
                    pattern_id, 
                    project_id, 
                    intent, 
                    json.dumps(tool_sequence), 
                    json.dumps(keywords) # Stored as JSON string "[a, b]" for SQL, but accessed as text for FTS
                )
            )

    def search_patterns(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        [Active Recall]: Fastest possible search using FTS5.
        """
        with self.engine.connection() as conn:
            # Try FTS5 first
            try:
                # Sanitize query for FTS syntax
                safe_query = query.replace('"', '""').replace("'", "''")
                
                # We rank by BM25 (default) implicitly by order of return? 
                # Actually SQLite FTS5 supports 'rank', but simple SELECT is usually ordered by relevance.
                # Let's join back to the main table to get full data.
                rows = conn.execute(f"""
                    SELECT p.* 
                    FROM patterns_fts fts
                    JOIN patterns p ON fts.id = p.id
                    WHERE patterns_fts MATCH '{safe_query}'
                    ORDER BY rank
                    LIMIT ?
                """, (limit,)).fetchall()
                
                if rows:
                    return self._hydrate_rows(rows)
                    
            except Exception as e:
                logger.debug(f"FTS Search failed ({e}), falling back to Legacy Search.")

            # Fallback: Naive LIKE Search (Hybrid Lite Bailout)
            q = f"%{query}%"
            rows = conn.execute("""
                SELECT * FROM patterns 
                WHERE intent LIKE ? OR keywords LIKE ?
                ORDER BY success_count DESC
                LIMIT ?
            """, (q, q, limit)).fetchall()
            
            return self._hydrate_rows(rows)

    def _hydrate_rows(self, rows) -> List[Dict[str, Any]]:
        results = []
        for row in rows:
            d = dict(row)
            try: d['tool_sequence'] = json.loads(d['tool_sequence'])
            except: d['tool_sequence'] = []
            try: d['keywords'] = json.loads(d['keywords'])
            except: d['keywords'] = []
            results.append(d)
        return results
