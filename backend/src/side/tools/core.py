"""
sideMCP Tools Core.

Single source of truth for auto-intelligence, database, and market analyzer.
"""

from side.intel.auto_intelligence import ContextService

from side.storage.modules.base import ContextEngine
from side.storage.modules.identity import IdentityService
from side.storage.modules.strategy import DecisionStore
from side.storage.modules.audit import AuditService
from side.storage.modules.transient import SessionCache

# Global singletons - initialized lazily
_engine: ContextEngine | None = None
_profile: IdentityService | None = None
_registry: DecisionStore | None = None
_ledger: AuditService | None = None
_cache: SessionCache | None = None
_context_service: ContextService | None = None


def get_engine() -> ContextEngine:
    """Provides a thread-local ContextEngine instance."""
    global _engine
    if _engine is None:
        _engine = ContextEngine()
    return _engine


def get_profile() -> IdentityService:
    """Provides a thread-local IdentityService instance."""
    global _profile
    if _profile is None:
        _profile = IdentityService(get_engine())
    return _profile


def get_strategic() -> DecisionStore:
    """Provides a thread-local DecisionStore instance."""
    global _registry
    if _registry is None:
        _registry = DecisionStore(get_engine())
    return _registry


def get_ledger() -> AuditService:
    """Provides a thread-local AuditService instance."""
    global _ledger
    if _ledger is None:
        _ledger = AuditService(get_engine())
    return _ledger


def get_cache() -> SessionCache:
    """Provides a thread-local SessionCache instance."""
    global _cache
    if _cache is None:
        _cache = SessionCache(get_engine())
    return _cache


def get_context_service() -> ContextService:
    """Provides a thread-local ContextService instance."""
    global _context_service
    if _context_service is None:
        _context_service = ContextService()
    return _context_service


# Legacy Aliases
get_identity = get_profile
get_strategic = get_registry
get_audit = get_ledger
get_operational = get_cache
get_auto_intel = get_context_service


def get_database():
    """Legacy compatibility bridge."""
    from side.storage.simple_db import SimplifiedDatabase
    return SimplifiedDatabase()
