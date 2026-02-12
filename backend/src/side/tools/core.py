"""
sideMCP Tools Core.

Single source of truth for auto-intelligence, database, and market analyzer.
"""

from side.intel.context_service import ContextService
from side.storage.modules.base import ContextEngine
from side.storage.modules.identity import IdentityService
from side.storage.modules.strategy import DecisionStore
from side.storage.modules.audit import AuditService
from side.storage.modules.transient import OperationalStore
from typing import Any

# Global singletons - initialized lazily
_engine: ContextEngine | None = None
_profile: IdentityService | None = None
_registry: DecisionStore | None = None
_audit_log: AuditService | None = None
_cache: OperationalStore | None = None
_ai_memory: ContextService | None = None
_billing_ledger: Any | None = None


def get_engine() -> ContextEngine:
    """Provides a thread-local ContextEngine instance."""
    global _engine
    if _engine is None:
        _engine = ContextEngine()
    return _engine


def get_user_profile() -> IdentityService:
    """Provides a thread-local IdentityService instance (**User Profile**)."""
    global _profile
    if _profile is None:
        _profile = IdentityService(get_engine())
    return _profile


def get_project_plan() -> DecisionStore:
    """Provides a thread-local DecisionStore instance (**Project Plan**)."""
    global _registry
    if _registry is None:
        _registry = DecisionStore(get_engine())
    return _registry


def get_audit_log() -> AuditService:
    """Provides a thread-local AuditService instance (**Audit Log**)."""
    global _audit_log
    if _audit_log is None:
        _audit_log = AuditService(get_engine())
    return _audit_log


def get_cache() -> OperationalStore:
    """Provides a thread-local OperationalStore instance."""
    global _cache
    if _cache is None:
        _cache = OperationalStore(get_engine())
    return _cache


def get_ai_memory() -> ContextService:
    """Provides a thread-local ContextService instance (**AI Memory**)."""
    global _ai_memory
    if _ai_memory is None:
        # Avoid circular import if ContextService needs tools
        from side.intel.context_service import ContextService
        _ai_memory = ContextService(get_engine().get_repo_root(), get_engine())
    return _ai_memory


def get_billing_ledger():
    """Provides a thread-local Billing Ledger (Ledger)."""
    global _billing_ledger
    if _billing_ledger is None:
        from side.storage.modules.accounting import Ledger
        _billing_ledger = Ledger(get_engine())
    return _billing_ledger


def get_database():
    """Legacy compatibility bridge: REDIRECTING to engine."""
    return get_engine()
