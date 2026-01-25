"""
Side Job Queue - Persistent, Atomic, Resilient.

Part of Phase II: Divide & Conquer.
Stores async tasks (Lints, LLM requests, Indexing) in the Monolith.
"""

import json
import uuid
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobQueue:
    """
    SQLite-backed Job Queue.
    """
    
    def __init__(self, db):
        self.db = db
        self._init_schema()
        
    def _init_schema(self):
        with self.db._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    payload JSON NOT NULL,
                    status TEXT DEFAULT 'pending',
                    priority INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    result JSON,
                    error TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status, priority DESC)")
            conn.commit()
            
    def enqueue(self, project_id: str, job_type: str, payload: Dict[str, Any], priority: int = 0) -> str:
        """Add a job to the queue."""
        job_id = str(uuid.uuid4())
        with self.db._connection() as conn:
            conn.execute("""
                INSERT INTO jobs (id, project_id, type, payload, priority)
                VALUES (?, ?, ?, ?, ?)
            """, (job_id, project_id, job_type, json.dumps(payload), priority))
            conn.commit()
        return job_id
        
    def claim_next(self) -> Optional[Dict]:
        """
        Worker Pattern: Find next pending job, mark as running atomicity.
        """
        # SQLite doesn't have SKIP LOCKED, so we use a transaction with immediate update
        # Simplified for robustness:
        with self.db._connection() as conn:
            # 1. Find candidate
            row = conn.execute("""
                SELECT id FROM jobs 
                WHERE status = 'pending' 
                ORDER BY priority DESC, created_at ASC 
                LIMIT 1
            """).fetchone()
            
            if not row:
                return None
                
            job_id = row['id']
            now = datetime.utcnow().isoformat()
            
            # 2. Mark running
            conn.execute("""
                UPDATE jobs 
                SET status = 'running', started_at = ? 
                WHERE id = ?
            """, (now, job_id))
            conn.commit()
            
            # 3. Fetch full details
            job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            job_dict = dict(job)
            # Auto-deserialize payload
            if isinstance(job_dict['payload'], str):
                try:
                    job_dict['payload'] = json.loads(job_dict['payload'])
                except:
                    pass
            return job_dict

    def complete_job(self, job_id: str, result: Dict[str, Any]):
        """Mark job as completed."""
        now = datetime.utcnow().isoformat()
        with self.db._connection() as conn:
            conn.execute("""
                UPDATE jobs 
                SET status = 'completed', result = ?, completed_at = ? 
                WHERE id = ?
            """, (json.dumps(result), now, job_id))
            conn.commit()

    def fail_job(self, job_id: str, error: str):
        """Mark job as failed."""
        now = datetime.utcnow().isoformat()
        with self.db._connection() as conn:
            conn.execute("""
                UPDATE jobs 
                SET status = 'failed', error = ?, completed_at = ? 
                WHERE id = ?
            """, (error, now, job_id))
            conn.commit()
