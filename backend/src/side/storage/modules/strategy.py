"""
Strategic Store - Plans, Decisions, & Learnings.
Delegates to specialized sub-stores for scalability.
"""

import logging
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from side.models.core import StrategicDecision, Rejection
from .base import ContextEngine

from .substores.plans import PlanStore
from .substores.decisions import DecisionStore
from .substores.rejections import RejectionStore
from .substores.patterns import PublicPatternStore
from .substores.memory import MemoryStore

logger = logging.getLogger(__name__)

class StrategyStore:
    """
    [STRATEGY]: Orchestrator for Time-Weighted Strategic Memory.
    Provides "Fractal Context" and "Temporal Search" capabilities.
    """
    def __init__(self, engine: ContextEngine):
        self.engine = engine
        
        # Initialize Sub-stores
        self.plans = PlanStore(engine)
        self.decisions = DecisionStore(engine)
        self.rejections = RejectionStore(engine)
        self.patterns = PublicPatternStore(engine)
        self.memory = MemoryStore(engine)
        
        # Self-Initialize Schema
        with self.engine.connection() as conn:
            self.init_schema(conn)

    def init_schema(self, conn: sqlite3.Connection) -> None:
        """Initialize all sub-store schemas."""
        self.plans.init_schema(conn)
        self.decisions.init_schema(conn)
        self.rejections.init_schema(conn)
        self.patterns.init_schema(conn)
        self.memory.init_schema(conn)
        
        # Migration: Add is_pinned to plans and learnings (managed by their respective stores)
        for table in ["plans", "learnings", "rejections", "public_patterns"]:
            try:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN is_pinned INTEGER DEFAULT 0")
            except: pass
            
        logger.info("MIGRATION: ChronosStore schema sync check complete.")

    # --- PLAN DELEGATION ---

    def save_plan(self, *args, **kwargs):
        return self.plans.save_plan(*args, **kwargs)

    def get_plan(self, *args, **kwargs):
        return self.plans.get_plan(*args, **kwargs)

    def list_plans(self, *args, **kwargs):
        return self.plans.list_plans(*args, **kwargs)

    def update_plan_status(self, *args, **kwargs):
        return self.plans.update_plan_status(*args, **kwargs)

    def delete_plan(self, *args, **kwargs):
        return self.plans.delete_plan(*args, **kwargs)

    def find_objectives_by_symbols(self, *args, **kwargs):
        return self.plans.find_objectives_by_symbols(*args, **kwargs)

    def save_check_in(self, *args, **kwargs):
        return self.plans.save_check_in(*args, **kwargs)

    def list_check_ins(self, *args, **kwargs):
        return self.plans.list_check_ins(*args, **kwargs)

    def list_check_ins(self, *args, **kwargs):
        return self.plans.list_check_ins(*args, **kwargs)

    def resolve_hierarchy(self, *args, **kwargs):
        return self.plans.resolve_hierarchy(*args, **kwargs)

    def get_fractal_context(self, *args, **kwargs):
        return self.plans.get_fractal_context(*args, **kwargs)

    # --- DECISION DELEGATION ---

    def save_decision(self, *args, **kwargs):
        return self.decisions.save_decision(*args, **kwargs)

    def list_decisions(self, *args, **kwargs):
        return self.decisions.list_decisions(*args, **kwargs)

    def save_learning(self, *args, **kwargs):
        return self.decisions.save_learning(*args, **kwargs)

    def list_learnings(self, *args, **kwargs):
        return self.decisions.list_learnings(*args, **kwargs)

    # --- REJECTION DELEGATION ---

    def save_rejection(self, *args, **kwargs):
        return self.rejections.save_rejection(*args, **kwargs)

    def save_rejections_batch(self, *args, **kwargs):
        return self.rejections.save_rejections_batch(*args, **kwargs)

    def list_rejections(self, *args, **kwargs):
        return self.rejections.list_rejections(*args, **kwargs)

    def purge_stale_rejections(self, *args, **kwargs):
        return self.rejections.purge_stale_rejections(*args, **kwargs)

    # --- PATTERN DELEGATION ---

    def save_public_pattern(self, *args, **kwargs):
        return self.patterns.save_public_pattern(*args, **kwargs)

    def save_public_patterns_batch(self, *args, **kwargs):
        return self.patterns.save_public_patterns_batch(*args, **kwargs)

    def list_public_patterns(self, *args, **kwargs):
        return self.patterns.list_public_patterns(*args, **kwargs)

    def search_patterns(self, *args, **kwargs):
        return self.patterns.search_patterns(*args, **kwargs)

    def search_wisdom(self, query: str, limit: int = 5):
        """Backwards compatibility for search_patterns."""
        return self.patterns.search_patterns(query, limit)

    # --- MEMORY DELEGATION ---

    def save_fact(self, *args, **kwargs):
        return self.memory.save_fact(*args, **kwargs)

    def recall_facts(self, *args, **kwargs):
        return self.memory.recall_facts(*args, **kwargs)

    def search_wisdom_relational(self, query: str, project_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Backwards compatibility for recall_facts."""
        return self.memory.recall_facts(query, project_id, limit)

    # --- CHRONOS (TIME-WEIGHTED SEARCH) ---

    def search_chronos(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        [CHRONOS VECTOR]: Time-Weighted Semantic Search.
        Rank = Relevance * (1 / (DaysOld + 1))
        """
        # 1. Get raw matches from patterns
        raw_results = self.patterns.search_patterns(query, limit=limit*2)
        
        # 2. Apply Time Decay
        weighted_results = []
        now = datetime.now(timezone.utc).timestamp()
        
        for res in raw_results:
            # Parse created_at
            try:
                # Naive ISO8601 parse
                created_ts = datetime.fromisoformat(res.get("created_at", "")).timestamp()
            except:
                created_ts = now
                
            age_days = (now - created_ts) / 86400
            relevance = res.get("score", 1.0) # Assume search_patterns returns score or default 1.0
            
            # Decay formula: 50% value after 30 days
            decay_factor = 1.0 / (1.0 + (age_days / 30.0))
            
            # Boost if pinned
            if res.get("is_pinned"):
                decay_factor = 1.0
                
            final_score = relevance * decay_factor
            res["chronos_score"] = final_score
            weighted_results.append(res)
            
        # 3. Re-sort
        weighted_results.sort(key=lambda x: x["chronos_score"], reverse=True)
        return weighted_results[:limit]

    # --- HOUSEKEEPING ---

    def decay_strategic_fat(self, days: int = 30) -> Dict[str, int]:
        """
        [CACHE DECAY]: Prunes low-entropy strategic data.
        """
        counts = {}
        with self.engine.connection() as conn:
            # 1. Decay Low-Impact Learnings
            cursor = conn.execute(
                "DELETE FROM learnings WHERE is_pinned = 0 AND impact = 'low' AND created_at < datetime('now', ?)",
                (f'-{days} days',)
            )
            counts["learnings"] = cursor.rowcount
            
            # 2. Decay stale done tasks
            cursor = conn.execute(
                "DELETE FROM plans WHERE is_pinned = 0 AND status = 'done' AND type = 'task' AND created_at < datetime('now', ?)",
                (f'-7 days',) 
            )
            counts["plans"] = cursor.rowcount
            
        return counts


    # --- COMPATIBILITY ALIASES ---
    add_plan = save_plan
    record_decision = save_decision
    add_rejection = save_rejection
    
    def list_public_patterns(self, *args, **kwargs):
        return self.patterns.list_public_patterns(*args, **kwargs)
