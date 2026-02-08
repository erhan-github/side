"""
[LAYER 5] Chronos Store - The 4D Memory Vector.
Treats Time as a dimension to enable "Time-Travel Debugging" and Narrative Reconstruction.
Platform Agnostic: Works for Claude, Cursor, and Terminals.
"""

import logging
import json
import uuid
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from side.storage.modules.base import ContextEngine

logger = logging.getLogger(__name__)

class TimelineStore:
    def __init__(self, engine: ContextEngine):
        self.engine = engine
        with self.engine.connection() as conn:
            self._init_schema(conn)

    def _init_schema(self, conn):
        """
        [TIMELINE-1]: The 4D Schema.
        Stores events with semantic embeddings (simulated) and temporal weights.
        """
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chronos_timeline (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                event_type TEXT NOT NULL, -- BOOT, INTENT, ACTION, OUTCOME
                source TEXT NOT NULL,     -- CLAUDE, CURSOR, TERMINAL
                content TEXT NOT NULL,
                semantic_tag TEXT,        -- CRITICAL, STRATEGIC, ROUTINE
                surprise_score FLOAT,     -- 0.0 to 1.0
                temporal_weight FLOAT,    -- 1.0 = Now, 0.0 = Ancient
                occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                meta JSON
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chronos_time ON chronos_timeline(occurred_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chronos_project ON chronos_timeline(project_id)")
        
        # Migration: Add columns if missing
        import sqlite3
        try:
            conn.execute("ALTER TABLE chronos_timeline ADD COLUMN semantic_tag TEXT")
            conn.execute("ALTER TABLE chronos_timeline ADD COLUMN surprise_score FLOAT")
        except sqlite3.OperationalError:
            pass

    async def capture_event(self, project_id: str, event_type: str, source: str, content: str, meta: Dict[str, Any] = None) -> str:
        """
        [UNIVERSAL HOOK]: Captures a Lifecycle Event from ANY platform.
        Triggers 'ReflectionEngine' for OUTCOME events to assign Semantic Tags.
        """
        from side.intel.reflection import ReflectionEngine
        
        event_id = str(uuid.uuid4())
        temporal_weight = 1.0 
        meta = meta or {}
        
        # Smart Tagging (The Adaptive Tagging Protocol)
        tag = "ROUTINE"
        score = 0.1
        
        if event_type.upper() == "OUTCOME":
            # Fire-and-forget reflection (simulated sync for now, should be async task)
            reflector = ReflectionEngine()
            intent = meta.get("intent", "Unknown Intent")
            tool = meta.get("tool", "unknown_tool")
            tag, score = await reflector.reflect_on_outcome(tool, intent, content)
            
        try:
            with self.engine.connection() as conn:
                conn.execute("""
                    INSERT INTO chronos_timeline (id, project_id, event_type, source, content, semantic_tag, surprise_score, temporal_weight, meta)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event_id,
                    project_id,
                    event_type.upper(),
                    source.upper(),
                    content,
                    tag,
                    score,
                    temporal_weight,
                    json.dumps(meta)
                ))
            return event_id
        except Exception as e:
            logger.error(f"Chronos capture failed: {e}")
            return ""

    def get_narrative_arc(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Reconstructs the 'Story' of the project.
        Returns events sorted by time, simulating a 'Replay'.
        """
        with self.engine.connection() as conn:
            rows = conn.execute("""
                SELECT event_type, source, content, occurred_at, meta
                FROM chronos_timeline
                WHERE project_id = ?
                ORDER BY occurred_at DESC
                LIMIT ?
            """, (project_id, limit)).fetchall()
            
        return [
            {
                "type": r[0],
                "source": r[1],
                "content": r[2],
                "time": r[3],
                "meta": json.loads(r[4])
            }
            for r in rows
        ]

    def prune_timeline(self, retention_days: int = 30):
        """
        [GOVERNANCE]: GDPR/Compliance automated deletion.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
        with self.engine.connection() as conn:
            conn.execute("DELETE FROM chronos_timeline WHERE occurred_at < ?", (cutoff,))
