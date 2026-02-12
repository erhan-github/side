import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from .base import ContextEngine

logger = logging.getLogger(__name__)

class Ledger:
    """
    Manages the 'Context Economy'.
    Tracks SU (Service Unit) balance and deductions.
    """
    def __init__(self, engine: ContextEngine):
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
            # Initialize with default Pro tier balance (750 SU)
            conn.execute("INSERT INTO su_balance (project_id, balance) VALUES (?, ?)", (project_id, 750))
            return 750

    def deduct_su(self, project_id: str, amount: int, reason: str) -> bool:
        """
        Deducts SUs from the project balance and logs the transaction.
        """
        # [CURSOR LOGGING]: Allow 0 amount to be logged
        if amount < 0:
            return False

        current_balance = self.get_balance(project_id)
        if current_balance < amount:
            masked_id = f"{project_id[:4]}...{project_id[-4:]}" if len(project_id) > 8 else project_id
            logger.warning(f"🏦 [ECONOMY]: Insufficient SUs for project {masked_id}. Required: {amount}, Available: {current_balance}")
            return False

        with self.engine.connection() as conn:
            new_balance = current_balance - amount
            conn.execute("UPDATE su_balance SET balance = ?, updated_at = ? WHERE project_id = ?", 
                         (new_balance, datetime.now(timezone.utc).isoformat(), project_id))
            
            conn.execute("""
                INSERT INTO accounting_ledger (id, project_id, amount, reason)
                VALUES (?, ?, ?, ?)
            """, (str(uuid.uuid4()), project_id, amount, reason))
            
        masked_id = f"{project_id[:4]}...{project_id[-4:]}" if len(project_id) > 8 else project_id
        logger.info(f"🏦 [ECONOMY]: Deducted {amount} SUs from {masked_id}. Reason: {reason}. New Balance: {new_balance}")
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

    # ─────────────────────────────────────────────────────────────
    # DYNAMIC SU PRICING ENGINE (Phase 1)
    # ─────────────────────────────────────────────────────────────
    
    # Task-type cost mapping (base algorithmic costs)
    ALGO_MULTIPLIERS = {
        "dna_search": 2.0,          # Fast structural search
        "ast_extraction": 1.5,      # Python AST symbol extraction
        "intent_correlation": 3.0,  # Strategic linking (SQL + fuzzy match)
        "pulse_scan": 0.5,          # Regex pre-commit validation
        "mesh_wisdom": 4.0,         # Cross-project knowledge sharing
        "context_synthesis": 2.5,   # 30-day intelligence assembly
        "audit_log": 0.3,        # SQLite write operation
        "shield_fix": 1.5,          # Vault integration + auto-fix
        "roi_calculation": 1.0,     # Counterfactual ROI logic
    }
    
    # LLM costs (2026 pricing per 1M tokens)
    # Phase 1 (Months 1-2): Groq
    # Phase 2 (Month 3+): Gemini 3 Flash
    LLM_COSTS = {
        # Groq (MVP - Current)
        "llama-3.1-70b-versatile": {"input": 0.20, "output": 0.30},
        
        # Gemini (Production - Future)
        "gemini-3-flash-thinking": {"input": 0.50, "output": 3.00},
        "gemini-2.5-flash": {"input": 0.30, "output": 2.50},
        "gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40},
    }
    
    # Free tasks (habit-forming, no SU charge)
    FREE_TASKS = {
        "pulse_scan",
        "ast_extraction",
        "audit_log",
        "file_watcher",
        "git_hook_detection",
        "intent_correlation"
    }
    
    def calculate_task_su(
        self,
        task_type: str,
        llm_tokens_in: int = 0,
        llm_tokens_out: int = 0,
        llm_model: str = "llama-3.1-70b-versatile",  # Groq for MVP
        operations: List[str] = None,
        value_delivered: Dict[str, Any] = None
    ) -> int:
        """
        Calculate SU cost for a task based on:
        1. LLM token usage
        2. Algorithmic complexity
        3. Value delivered (ROI-based)
        
        Args:
            task_type: Type of task (e.g., "atomic_context", "semantic_boost")
            llm_tokens_in: Input tokens consumed
            llm_tokens_out: Output tokens generated
            llm_model: LLM model used (default: Claude Sonnet 4.5)
            operations: List of algorithmic operations performed
            value_delivered: Dict of value metrics (e.g., {"disaster_averted_usd": 50000})
        
        Returns:
            Total SU cost (integer), 0 if free task
        """
        # Check if task is free (habit-forming)
        if task_type in self.FREE_TASKS:
            logger.debug(f"💰 [SU CALC]: {task_type} → FREE (habit-forming)")
            return 0
        
        operations = operations or []
        value_delivered = value_delivered or {}
        
        # 1. LLM Cost Component
        llm_cost_usd = 0.0
        if llm_tokens_in or llm_tokens_out:
            costs = self.LLM_COSTS.get(llm_model, self.LLM_COSTS["llama-3.1-70b-versatile"])
            llm_cost_usd = (
                (llm_tokens_in * costs["input"] / 1_000_000) +
                (llm_tokens_out * costs["output"] / 1_000_000)
            )
        
        # Convert USD to SU ($0.001 = 1 SU)
        llm_su = llm_cost_usd * 1000
        
        # 2. Algorithmic Value Component
        algo_su = sum(self.ALGO_MULTIPLIERS.get(op, 1.0) for op in operations)
        
        # 3. Value Multiplier (ROI-based)
        value_su = 0
        if "disaster_averted_usd" in value_delivered:
            # Award SUs based on disaster prevention
            value_su += min(value_delivered["disaster_averted_usd"] / 1000, 20)  # Cap at 20 SU
        if "time_saved_hours" in value_delivered:
            # Award 0.5 SU per hour saved
            value_su += value_delivered["time_saved_hours"] * 0.5
        if "objective_advanced" in value_delivered:
            # Award 2 SU for strategic progress
            value_su += 2.0
        
        # Final calculation
        total_su = max(1, int(llm_su + algo_su + value_su))
        
        logger.debug(
            f"💰 [SU CALC]: {task_type} → LLM: {llm_su:.2f}, Algo: {algo_su:.2f}, "
            f"Value: {value_su:.2f} = {total_su} SU"
        )
        
        return total_su
    
    def deduct_task_su(
        self,
        project_id: str,
        task_type: str,
        llm_tokens_in: int = 0,
        llm_tokens_out: int = 0,
        llm_model: str = "groq-llama-70b",
        operations: List[str] = None,
        value_delivered: Dict[str, Any] = None
    ) -> bool:
        """
        Calculate and deduct SUs for a specific task in one call.
        
        Returns:
            True if deduction successful, False if insufficient balance
        """
        su_cost = self.calculate_task_su(
            task_type=task_type,
            llm_tokens_in=llm_tokens_in,
            llm_tokens_out=llm_tokens_out,
            llm_model=llm_model,
            operations=operations,
            value_delivered=value_delivered
        )
        
        reason = f"{task_type}"
        if llm_tokens_in or llm_tokens_out:
            reason += f" (LLM: {llm_tokens_in + llm_tokens_out} tokens)"
            
        # [CURSOR LOGGING]: Even if cost is 0, we deduct_su to ensure it hits the ledger
        return self.deduct_su(project_id, su_cost, reason)
