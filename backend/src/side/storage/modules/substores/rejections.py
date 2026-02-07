import logging
from typing import Any, Dict, List
from side.models.core import Rejection

logger = logging.getLogger(__name__)

class RejectionStore:
    def __init__(self, engine):
        self.engine = engine

    def init_schema(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rejections (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL DEFAULT 'default',
                instruction_hash TEXT,
                file_path TEXT,
                rejection_reason TEXT, 
                diff_signature TEXT,
                signal_hash INTEGER,
                is_pinned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rejections_project ON rejections(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rejections_hash ON rejections(instruction_hash)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rejections_signal_hash ON rejections(signal_hash)")

    def save_rejection(self, rejection_id: str, file_path: str, reason: str, 
                       instruction_hash: str | None = None, diff_signature: str | None = None, **kwargs) -> None:
        self.save_rejections_batch([{
            'id': rejection_id,
            'file_path': file_path,
            'reason': reason,
            'instruction_hash': instruction_hash,
            'diff_signature': diff_signature,
            'signal_hash': kwargs.get("signal_hash"),
            'project_id': kwargs.get("project_id", "default")
        }])

    def save_rejections_batch(self, rejections: List[Dict[str, Any] | Rejection]) -> None:
        parsed_rejections = []
        for r in rejections:
            if isinstance(r, dict):
                parsed_rejections.append(Rejection(
                    id=r['id'],
                    project_id=r.get('project_id', 'default'),
                    file_path=r['file_path'],
                    rejection_reason=r['reason'],
                    instruction_hash=r.get('instruction_hash'),
                    diff_signature=r.get('diff_signature'),
                    signal_hash=r.get('signal_hash')
                ))
            else:
                parsed_rejections.append(r)

        with self.engine.connection() as conn:
            for rej in parsed_rejections:
                conn.execute(
                    """
                    INSERT INTO rejections (id, project_id, instruction_hash, file_path, rejection_reason, diff_signature, signal_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        rejection_reason = excluded.rejection_reason,
                        diff_signature = excluded.diff_signature
                    """,
                    (rej.id, rej.project_id, rej.instruction_hash, rej.file_path, 
                     rej.rejection_reason, rej.diff_signature, rej.signal_hash),
                )

    def list_rejections(self, limit: int = 10) -> list[Rejection]:
        with self.engine.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM rejections ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [Rejection.from_row(row) for row in rows]

    def purge_stale_rejections(self, days: int = 180) -> int:
        with self.engine.connection() as conn:
            cursor = conn.execute(
                "DELETE FROM rejections WHERE is_pinned = 0 AND created_at < datetime('now', ?)",
                (f'-{days} days',)
            )
            return cursor.rowcount
