"""
Intent Fusion Store - Session & Signal Storage for Sidelith.
"""

import logging
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from side.utils.crypto import shield
from .base import ContextEngine

logger = logging.getLogger(__name__)

class IntentFusionStore:
    def __init__(self, engine: ContextEngine
):
        self.engine = engine
        with self.engine.connection() as conn:
            self.init_schema(conn)

    def init_schema(self, conn):
        """Initialize intent fusion tables."""
        # ─────────────────────────────────────────────────────────────
        # TABLE 1: CONVERSATION_SESSIONS - LLM Exchanges
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                session_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                started_at TIMESTAMP NOT NULL,
                ended_at TIMESTAMP,
                duration_seconds REAL,
                
                -- Intent
                raw_intent TEXT,
                intent_vector TEXT,  -- JSON Array
                intent_category TEXT,
                
                -- Outcome
                claimed_outcome TEXT,
                verified_outcome TEXT,
                
                -- Linkage
                prior_sessions TEXT,   -- JSON Array
                follow_up_sessions TEXT, -- JSON Array
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_project ON conversation_sessions(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_start ON conversation_sessions(started_at DESC)")

        # ─────────────────────────────────────────────────────────────
        # TABLE 2: INTENT_SIGNALS - Derived Intelligence
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS intent_signals (
                signal_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                evidence TEXT,  -- JSON Object
                context_snippet TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES conversation_sessions(session_id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_signals_session ON intent_signals(session_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_signals_type ON intent_signals(signal_type)")

    def save_session_dict(self, session_data: Dict[str, Any]) -> None:
        """Save a conversation session with AES-256 field-level encryption."""
        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO conversation_sessions (
                    session_id, project_id, started_at, ended_at, duration_seconds,
                    raw_intent, intent_vector, intent_category,
                    claimed_outcome, verified_outcome,
                    prior_sessions, follow_up_sessions
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    ended_at = excluded.ended_at,
                    duration_seconds = excluded.duration_seconds,
                    intent_category = excluded.intent_category,
                    claimed_outcome = excluded.claimed_outcome,
                    verified_outcome = excluded.verified_outcome,
                    follow_up_sessions = excluded.follow_up_sessions
                """,
                (
                    session_data['session_id'],
                    session_data['project_id'],
                    session_data['started_at'],
                    session_data['ended_at'],
                    session_data['duration_seconds'],
                    # [AES-256 SEALING]: Authenticated encryption for sensitive intents
                    shield.seal(session_data['raw_intent']),
                    json.dumps(session_data['intent_vector']),
                    session_data['intent_category'],
                    session_data['claimed_outcome'],
                    session_data['verified_outcome'],
                    json.dumps(session_data['prior_sessions']),
                    json.dumps(session_data['follow_up_sessions'])
                )
            )

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a session by ID with AES-256 decryption."""
        with self.engine.connection() as conn:
            row = conn.execute("SELECT * FROM conversation_sessions WHERE session_id = ?", (session_id,)).fetchone()
            if not row:
                return None
            
            d = dict(row)
            # [AES-256 UNSEALING]
            if d['raw_intent']:
                d['raw_intent'] = shield.unseal(d['raw_intent'])

            # Parse JSON fields
            try: d['intent_vector'] = json.loads(d['intent_vector']) 
            except: d['intent_vector'] = []
            try: d['prior_sessions'] = json.loads(d['prior_sessions'])
            except: d['prior_sessions'] = []
            try: d['follow_up_sessions'] = json.loads(d['follow_up_sessions'])
            except: d['follow_up_sessions'] = []
            return d

    def list_sessions(self, project_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent sessions."""
        with self.engine.connection() as conn:
            query = "SELECT * FROM conversation_sessions"
            params = []
            if project_id:
                query += " WHERE project_id = ?"
                params.append(project_id)
            
            query += " ORDER BY started_at DESC LIMIT ?"
            params.append(limit)
            
            rows = conn.execute(query, params).fetchall()
            results = []
            for row in rows:
                d = dict(row)
                try: d['intent_vector'] = json.loads(d['intent_vector']) 
                except: d['intent_vector'] = []
                results.append(d)
            return results

    def save_signal_dict(self, signal_data: Dict[str, Any]) -> None:
        """Save an intent signal."""
        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO intent_signals (
                    signal_id, session_id, signal_type, confidence,
                    evidence, context_snippet, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(signal_id) DO UPDATE SET
                    confidence = excluded.confidence,
                    evidence = excluded.evidence
                """,
                (
                    signal_data['signal_id'],
                    signal_data['session_id'],
                    signal_data['signal_type'],
                    signal_data['confidence'],
                    json.dumps(signal_data.get('evidence', {})),
                    signal_data['context_snippet'],
                    signal_data['created_at']
                )
            )

    def get_signals_for_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve signals associated with a session."""
        with self.engine.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM intent_signals WHERE session_id = ? ORDER BY created_at",
                (session_id,)
            ).fetchall()
            
            results = []
            for row in rows:
                d = dict(row)
                try: d['evidence'] = json.loads(d['evidence'])
                except: d['evidence'] = {}
                results.append(d)
            return results
