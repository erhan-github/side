import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AccountingStore:
    """
    Manages the 'Sovereign Economy'.
    Tracks SU (Service Unit) balance and deductions.
    """
    def __init__(self, engine):
        self.engine = engine
        self._ensure_table()

    def _ensure_table(self):
        with self.engine.connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS accounting_ledger (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    amount INTEGER,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS su_balance (
                    project_id TEXT PRIMARY KEY,
                    balance INTEGER DEFAULT 500,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def get_balance(self, project_id: str) -> int:
        with self.engine.connection() as conn:
            row = conn.execute("SELECT balance FROM su_balance WHERE project_id = ?", (project_id,)).fetchone()
            if row:
                return row[0]
            # Initialize with default trial balance if not exists
            conn.execute("INSERT INTO su_balance (project_id, balance) VALUES (?, ?)", (project_id, 500))
            return 500

    def deduct_su(self, project_id: str, amount: int, reason: str) -> bool:
        """
        Deducts SUs from the project balance and logs the transaction.
        """
        if amount <= 0:
            return True

        current_balance = self.get_balance(project_id)
        if current_balance < amount:
            logger.warning(f"🏦 [ECONOMY]: Insufficient SUs for project {project_id}. Required: {amount}, Available: {current_balance}")
            return False

        with self.engine.connection() as conn:
            new_balance = current_balance - amount
            conn.execute("UPDATE su_balance SET balance = ?, updated_at = ? WHERE project_id = ?", 
                         (new_balance, datetime.now(timezone.utc).isoformat(), project_id))
            
            conn.execute("""
                INSERT INTO accounting_ledger (id, project_id, amount, reason)
                VALUES (?, ?, ?, ?)
            """, (str(uuid.uuid4()), project_id, amount, reason))
            
        logger.info(f"🏦 [ECONOMY]: Deducted {amount} SUs from {project_id}. Reason: {reason}. New Balance: {new_balance}")
        return True

    def get_history(self, project_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        with self.engine.connection() as conn:
            rows = conn.execute("""
                SELECT id, amount, reason, created_at 
                FROM accounting_ledger 
                WHERE project_id = ? 
                ORDER BY created_at DESC LIMIT ?
            """, (project_id, limit)).fetchall()
            return [{"id": r[0], "amount": r[1], "reason": r[2], "date": r[3]} for r in rows]
