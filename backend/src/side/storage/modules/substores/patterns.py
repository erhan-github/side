import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from side.models.core import Pattern, ExecutablePattern, AntiPattern

logger = logging.getLogger(__name__)

class PublicPatternStore:
    """
    Sub-store for Architectural and Executable knowledge fragments.
    [PALANTIR-LEVEL]: Consolidated from legacy pattern_store.py.
    """
    def __init__(self, engine):
        self.engine = engine

    def init_schema(self, conn):
        """Initialize unified pattern tables and FTS indexes."""
        
        # 1. Architectural Patterns (Analytical insights)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS architectural_patterns (
                id TEXT PRIMARY KEY,
                intent TEXT,
                context_hash TEXT,
                pattern_json TEXT,
                success_count INTEGER DEFAULT 1,
                last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Anti-Patterns (Risks/Failed moves)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS anti_patterns (
                id TEXT PRIMARY KEY,
                issue_type TEXT,
                context_trigger TEXT,
                risk_description TEXT,
                remedy_json TEXT,
                occurrence_count INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. Executable Patterns (Tool sequences)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS executable_patterns (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL DEFAULT 'default',
                intent TEXT NOT NULL,
                tool_sequence JSON NOT NULL,
                keywords JSON,
                success_count INTEGER DEFAULT 1,
                last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 4. FTS Index
        try:
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS pattern_search_fts USING fts5(
                    id, 
                    intent, 
                    keywords, 
                    tokenize='porter uni'
                )
            """)
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS patterns_fts_ai AFTER INSERT ON executable_patterns BEGIN
                    INSERT INTO pattern_search_fts(id, intent, keywords) 
                    VALUES (new.id, new.intent, new.keywords);
                END;
            """)
        except Exception as e:
            logger.warning(f"FTS5 Not Supported: {e}")

    # --- Architectural Methods ---

    def store_architectural_move(self, intent: str, context_hash: str, pattern_data: Dict[str, Any]):
        with self.engine.connection() as conn:
            row = conn.execute(
                "SELECT id, success_count FROM architectural_patterns WHERE intent = ? AND context_hash = ?",
                (intent, context_hash)
            ).fetchone()
            
            if row:
                conn.execute(
                    "UPDATE architectural_patterns SET success_count = success_count + 1, last_used_at = ? WHERE id = ?",
                    (datetime.now(timezone.utc).isoformat(), row[0])
                )
            else:
                pattern = Pattern(
                    id=str(uuid.uuid4()),
                    topic=intent,
                    content=str(pattern_data.get("description", intent)),
                    context_hash=context_hash,
                    metadata=pattern_data,
                    source="system"
                )
                conn.execute("""
                    INSERT INTO architectural_patterns (id, intent, context_hash, pattern_json)
                    VALUES (?, ?, ?, ?)
                """, (pattern.id, pattern.topic, pattern.context_hash, pattern.model_dump_json(include={'metadata'})))

    def store_anti_pattern(self, issue_type: str, context_trigger: str, risk: str, remedy: Optional[Dict[str, Any]] = None):
        with self.engine.connection() as conn:
            row = conn.execute(
                "SELECT id, occurrence_count FROM anti_patterns WHERE issue_type = ? AND context_trigger = ?",
                (issue_type, context_trigger)
            ).fetchone()
            
            if row:
                conn.execute("UPDATE anti_patterns SET occurrence_count = occurrence_count + 1 WHERE id = ?", (row[0],))
            else:
                anti = AntiPattern(
                    id=str(uuid.uuid4()),
                    issue_type=issue_type,
                    context_trigger=context_trigger,
                    risk_description=risk,
                    remedy=remedy
                )
                conn.execute("""
                    INSERT INTO anti_patterns (id, issue_type, context_trigger, risk_description, remedy_json)
                    VALUES (?, ?, ?, ?, ?)
                """, (anti.id, anti.issue_type, anti.context_trigger, anti.risk_description, anti.model_dump_json(include={'remedy'})))

    # --- Executable Methods ---

    def save_executable_pattern(self, pattern_id: str, intent: str, tool_sequence: List[Dict[str, Any]], 
                               keywords: List[str], project_id: str = "default") -> None:
        pattern = ExecutablePattern(
            id=pattern_id,
            project_id=project_id,
            intent=intent,
            tool_sequence=tool_sequence,
            keywords=keywords
        )
        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO executable_patterns (id, project_id, intent, tool_sequence, keywords)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    tool_sequence = excluded.tool_sequence,
                    keywords = excluded.keywords,
                    success_count = success_count + 1,
                    last_used_at = CURRENT_TIMESTAMP
                """,
                (pattern.id, pattern.project_id, pattern.intent, 
                 pattern.model_dump_json(include={'tool_sequence'}), 
                 pattern.model_dump_json(include={'keywords'}))
            )

    def search_patterns(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        with self.engine.connection() as conn:
            try:
                safe_query = query.replace('"', '""').replace("'", "''")
                rows = conn.execute(f"""
                    SELECT p.* 
                    FROM pattern_search_fts fts
                    JOIN executable_patterns p ON fts.id = p.id
                    WHERE pattern_search_fts MATCH '{safe_query}'
                    ORDER BY rank LIMIT ?
                """, (limit,)).fetchall()
                if rows: return self._hydrate(rows)
            except Exception: pass
            
            q = f"%{query}%"
            rows = conn.execute("""
                SELECT * FROM executable_patterns 
                WHERE intent LIKE ? OR keywords LIKE ?
                ORDER BY success_count DESC LIMIT ?
            """, (q, q, limit)).fetchall()
            return self._hydrate(rows)

    def get_patterns(self, topic: str | None = None, context_hash: str | None = None, limit: int = 5) -> List[Dict[str, Any]]:
        results = []
        with self.engine.connection() as conn:
            if context_hash:
                rows = conn.execute(
                    "SELECT * FROM architectural_patterns WHERE context_hash = ? ORDER BY success_count DESC LIMIT ?",
                    (context_hash, limit)
                ).fetchall()
                results.extend([dict(row) for row in rows])

            if topic and len(results) < limit:
                remaining = limit - len(results)
                results.extend(self.search_patterns(topic, limit=remaining))

        if not results:
             with self.engine.connection() as conn:
                rows = conn.execute(
                    "SELECT * FROM architectural_patterns ORDER BY success_count DESC LIMIT ?",
                    (limit,)
                ).fetchall()
                results.extend([dict(row) for row in rows])
        return results

    def _hydrate(self, rows) -> List[Dict[str, Any]]:
        results = []
        for row in rows:
            d = dict(row)
            for key in ['tool_sequence', 'keywords']:
                try: d[key] = json.loads(d[key])
                except: d[key] = []
            results.append(d)
        return results

    # --- Backward Compatibility ---

    def list_public_patterns(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Backwards compatibility for AutoIntelligence sync."""
        return self.get_patterns(limit=limit)

    def save_public_pattern(self, pattern_id: str, pattern_text: str, origin_node: str | None = None,
                           category: str | None = None, signal_pattern: str | None = None,
                           confidence: int = 5, **kwargs) -> None:
        """Adapter: Logic-less stub or best-effort map to executable patterns."""
        # For now, we accept it but don't persist if it doesn't match new schema strictness
        # or we log as finding
        pass
