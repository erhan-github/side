"""
Timeline Store - The Project Timeline.
Treats Time as a categorical axis to enable "Time-Travel Debugging" and Narrative Reconstruction.
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
        Timeline Schema.
        Stores events with contextual indexing and temporal weights.
        """
        conn.execute("""
            CREATE TABLE IF NOT EXISTS event_timeline (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                event_type TEXT NOT NULL, -- BOOT, INTENT, ACTION, OUTCOME
                source TEXT NOT NULL,     -- CLAUDE, CURSOR, TERMINAL
                content TEXT NOT NULL,
                temporal_weight FLOAT,    -- 1.0 = Now, 0.0 = Ancient
                occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                meta JSON
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timeline_time ON event_timeline(occurred_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timeline_project ON event_timeline(project_id)")
        
        try:
            # We no longer add pseudo-scientific columns
            pass
        except:
            pass

    async def capture_event(self, project_id: str, event_type: str, source: str, content: str, meta: Dict[str, Any] = None) -> str:
        """
        Captures a Lifecycle Event from any integrated platform.
        """
        event_id = str(uuid.uuid4())
        temporal_weight = 1.0 
        meta = meta or {}
        
        # Clean logging without pseudo-scientific tagging
            
        try:
            with self.engine.connection() as conn:
                conn.execute("""
                    INSERT INTO event_timeline (id, project_id, event_type, source, content, temporal_weight, meta)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event_id,
                    project_id,
                    event_type.upper(),
                    source.upper(),
                    content,
                    temporal_weight,
                    json.dumps(meta)
                ))
            return event_id
        except Exception as e:
            logger.error(f"Event capture failed: {e}")
            return ""

    def get_narrative_arc(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Reconstructs the 'Story' of the project.
        Returns events sorted by time, simulating a 'Replay'.
        """
        with self.engine.connection() as conn:
            rows = conn.execute("""
                SELECT event_type, source, content, occurred_at, meta
                FROM event_timeline
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
            conn.execute("DELETE FROM event_timeline WHERE occurred_at < ?", (cutoff,))
