"""
Sidelith Sovereign Database - Privacy-First Strategic Storage.

This is a modular facade that delegates to specialized domain stores:
1. Base Engine (base.py)
2. Strategic Ledger (strategic.py)
3. Identity Store (identity.py)
4. Forensic Store (forensic.py)
5. Operational Store (transient.py)
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from side.utils.helpers import safe_get

from .modules.base import SovereignEngine, InsufficientTokensError
from .modules.strategic import StrategicStore
from .modules.identity import IdentityStore
from .modules.forensic import ForensicStore
from .modules.transient import OperationalStore

logger = logging.getLogger(__name__)

# Re-export for compatibility
InsufficientTokensError = InsufficientTokensError

class SimplifiedDatabase:
    """
    Privacy-first SQLite storage for Side (Modular Facade).
    """

    def __init__(self, db_path: str | Path | None = None):
        self.engine = SovereignEngine(db_path)
        self.db_path = self.engine.db_path
        
        # Initialize sub-stores
        self.identity = IdentityStore(self.engine)
        self.strategic = StrategicStore(self.engine)
        self.forensic = ForensicStore(self.engine)
        self.operational = OperationalStore(self.engine)

        # Startup lifecycle
        self.engine.atomic_backup()
        self._init_schema()
        self._run_migrations()
        self.engine.harden_permissions()

    def _init_schema(self) -> None:
        """Initialize all sub-store schemas."""
        with self.engine.connection() as conn:
            self.operational.init_schema(conn)
            self.strategic.init_schema(conn)
            self.identity.init_schema(conn)
            self.forensic.init_schema(conn)

    def _run_migrations(self) -> None:
        """Handle CTO-level schema resilience."""
        version = self.operational.get_version()
        # [Handover Note] Add version-based migrations here via self.operational.set_version()
        logger.info(f"Sidelith Sovereign Schema: v{version}")

    def _connection(self):
        """Legacy compatibility for internal tools."""
        return self.engine.connection()

    @staticmethod
    def get_project_id(project_path: str | Path | None = None) -> str:
        """Persists project ID in a hidden file for stable isolation."""
        if project_path is None:
            project_path = Path.cwd()
        else:
            project_path = Path(project_path)
            
        project_path = project_path.resolve()
        id_file = project_path / ".side-id"
        
        if id_file.exists():
            try:
                return id_file.read_text().strip()
            except Exception:
                pass
        
        import hashlib
        path_hash = hashlib.sha256(str(project_path).encode()).hexdigest()[:16]
        try:
            id_file.write_text(path_hash)
        except Exception:
            pass
            
        return path_hash

    # --- Identity Delegation ---
    def update_profile(self, project_id: str, profile_data: dict[str, Any]) -> None:
        return self.identity.update_profile(project_id, profile_data)

    def get_profile(self, project_id: str) -> dict[str, Any] | None:
        return self.identity.get_profile(project_id)

    def get_token_balance(self, project_id: str) -> dict[str, Any]:
        return self.identity.get_token_balance(project_id)

    def update_token_balance(self, project_id: str, amount: int) -> int:
        return self.identity.update_token_balance(project_id, amount)

    def set_token_balance(self, balance: int) -> None:
        return self.identity.set_token_balance(balance)

    def get_profile_count(self) -> int:
        return self.identity.get_profile_count()

    # --- Strategic Delegation ---
    def save_plan(self, project_id: str, plan_id: str, title: str, plan_type: str = "goal",
                  description: str | None = None, due_date: str | None = None,
                  parent_id: str | None = None, priority: int = 0) -> None:
        return self.strategic.save_plan(project_id, plan_id, title, plan_type, description, due_date, parent_id, priority)

    def get_plan(self, plan_id: str) -> dict[str, Any] | None:
        return self.strategic.get_plan(plan_id)

    def list_plans(self, project_id: str | None = None, plan_type: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        return self.strategic.list_plans(project_id, plan_type, status)

    def update_plan_status(self, plan_id: str, status: str) -> bool:
        return self.strategic.update_plan_status(plan_id, status)

    def save_decision(self, decision_id: str, question: str, answer: str,
                      reasoning: str | None = None, category: str | None = None,
                      plan_id: str | None = None, confidence: int = 5) -> None:
        return self.strategic.save_decision(decision_id, question, answer, reasoning, category, plan_id, confidence)

    def list_decisions(self, category: str | None = None) -> list[dict[str, Any]]:
        return self.strategic.list_decisions(category)

    def save_learning(self, learning_id: str, insight: str, source: str | None = None,
                      impact: str = "medium", plan_id: str | None = None) -> None:
        return self.strategic.save_learning(learning_id, insight, source, impact, plan_id)

    def list_learnings(self, impact: str | None = None) -> list[dict[str, Any]]:
        return self.strategic.list_learnings(impact)

    def save_check_in(self, check_in_id: str, plan_id: str, status: str, note: str | None = None) -> None:
        return self.strategic.save_check_in(check_in_id, plan_id, status, note)

    def list_check_ins(self, plan_id: str) -> list[dict[str, Any]]:
        return self.strategic.list_check_ins(plan_id)

    def save_rejection(self, rejection_id: str, file_path: str, reason: str, 
                       instruction_hash: str | None = None, diff_signature: str | None = None) -> None:
        return self.strategic.save_rejection(rejection_id, file_path, reason, instruction_hash, diff_signature)

    def list_rejections(self, limit: int = 10) -> list[dict[str, Any]]:
        return self.strategic.list_rejections(limit)


    # --- Goal Compatibility ---
    def save_goal(self, goal_id: str, title: str, description: str | None = None,
                  due_date: str | None = None, parent_id: str | None = None,
                  priority: int = 0, goal_type: str = "goal") -> None:
        return self.strategic.save_plan("main", goal_id, title, goal_type, description, due_date, parent_id, priority)

    def get_goal(self, goal_id: str) -> dict[str, Any] | None:
        return self.strategic.get_plan(goal_id)

    def list_goals(self, status: str | None = None) -> list[dict[str, Any]]:
        return self.strategic.list_plans(plan_type="goal", status=status)

    def update_goal_status(self, goal_id: str, status: str) -> bool:
        return self.strategic.update_plan_status(goal_id, status)

    def delete_goal(self, goal_id: str) -> bool:
        return self.strategic.delete_plan(goal_id)

    def get_overdue_goals(self) -> list[dict[str, Any]]:
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return [p for p in self.strategic.list_plans(plan_type="goal") 
                if p["status"] not in ("done", "completed") and p["due_date"] and p["due_date"] < today]

    def get_stalled_goals(self, days: int = 3) -> list[dict[str, Any]]:
        from datetime import datetime, timezone, timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        return [p for p in self.strategic.list_plans(plan_type="goal") 
                if p["status"] not in ("done", "completed") and p["created_at"] < cutoff]

    def update_goal_activity(self, goal_id: str) -> bool:
        # Compatibility touch
        return self.strategic.update_plan_status(goal_id, "active")

    # --- Forensic Delegation ---
    def log_activity(self, project_id: str, tool: str, action: str, 
                     cost_tokens: int = 0, tier: str = 'free', 
                     payload: dict[str, Any] | None = None) -> None:
        return self.forensic.log_activity(project_id, tool, action, cost_tokens, tier, payload)

    def get_recent_activities(self, project_id: str, limit: int = 20) -> list[dict[str, Any]]:
        return self.forensic.get_recent_activities(project_id, limit)

    def get_recent_ledger(self, limit: int = 20) -> list[dict[str, Any]]:
        """Cross-project strategic ledger (Global)."""
        return self.forensic.get_recent_activities(project_id="global", limit=limit)

    def get_recent_audits(self, project_id: str, limit: int = 10) -> list[dict[str, Any]]:
        return self.forensic.get_recent_audits(project_id, limit)

    def get_audit_summary(self, project_id: str) -> dict[str, int]:
        return self.forensic.get_audit_summary(project_id)

    def save_work_context(self, project_path: str, focus_area: str, 
                          recent_files: list[str], recent_commits: list[dict[str, Any]],
                          current_branch: str | None = None, confidence: float = 0.8) -> None:
        return self.forensic.save_work_context(project_path, focus_area, recent_files, recent_commits, current_branch, confidence)

    def get_latest_work_context(self, project_path: str) -> dict[str, Any] | None:
        return self.forensic.get_latest_work_context(project_path)

    def cleanup_expired_data(self) -> dict[str, int]:
        return self.forensic.cleanup_expired_data()

    def prune_activities(self, days: int = 30) -> int:
        return self.forensic.prune_activities(days)

    # --- Operational Delegation ---
    def save_query_cache(self, query_type: str, query_params: dict[str, Any], 
                         result: Any, ttl_hours: int = 1) -> None:
        return self.operational.save_query_cache(query_type, query_params, result, ttl_hours)

    def get_query_cache(self, query_type: str, query_params: dict[str, Any]) -> Any | None:
        return self.operational.get_query_cache(query_type, query_params)

    def invalidate_query_cache(self, query_type: str | None = None) -> int:
        return self.operational.invalidate_query_cache(query_type)

    def get_database_stats(self) -> dict[str, Any]:
        return self.operational.get_database_stats(self.db_path)

    def discover_sovereign_nodes(self) -> List[Path]:
        return self.operational.discover_sovereign_nodes()

    def get_global_stats(self) -> Dict[str, Any]:
        return self.operational.get_global_stats()

    def register_mesh_node(self, project_id: str, path: Path, dna_summary: str | None = None) -> None:
        return self.operational.register_mesh_node(project_id, path, dna_summary)

    def list_mesh_nodes(self) -> List[Dict[str, Any]]:
        return self.operational.list_mesh_nodes()

    def search_mesh_wisdom(self, query: str) -> List[Dict[str, Any]]:
        return self.operational.search_mesh_wisdom(query)

    def save_telemetry_alert(self, project_id: str, alert_type: str, severity: str, 
                             message: str, file_path: str | None = None) -> None:
        return self.operational.save_telemetry_alert(project_id, alert_type, severity, message, file_path)

    def get_active_telemetry_alerts(self, project_id: str | None = None) -> List[Dict[str, Any]]:
        return self.operational.get_active_telemetry_alerts(project_id)

    def resolve_telemetry_alert(self, alert_id: int) -> None:
        return self.operational.resolve_telemetry_alert(alert_id)

    def save_public_wisdom(self, wisdom_id: str, wisdom_text: str, origin_node: str | None = None,
                           category: str | None = None, signal_pattern: str | None = None,
                           confidence: int = 5) -> None:
        return self.strategic.save_public_wisdom(wisdom_id, wisdom_text, origin_node, category, signal_pattern, confidence)

    def list_public_wisdom(self, signal_pattern: str | None = None) -> List[Dict[str, Any]]:
        return self.strategic.list_public_wisdom(signal_pattern)

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        return self.operational.get_setting(key, default)

    def set_setting(self, key: str, value: str) -> None:
        return self.operational.set_setting(key, value)

    # --- Core Mechanics ---
    def check_integrity(self) -> bool:
        return self.engine.check_integrity()

    def _atomic_backup(self) -> None:
        return self.engine.atomic_backup()
