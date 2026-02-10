"""
sideMCP Storage Layer.

Simplified storage with local-first architecture.
"""

from side.storage.simple_db import SimplifiedDatabase

__all__ = [
    "SimplifiedDatabase",
    "get_activity_ledger",
    "get_transient_cache",
]

from typing import Optional, TYPE_CHECKING
from side.storage.simple_db import SimplifiedDatabase

if TYPE_CHECKING:
    from side.storage.modules.audit import AuditService
    from side.storage.modules.transient import SessionCache
    from side.storage.modules.base import ContextEngine

_activity_ledger: Optional["AuditService"] = None
_transient_cache: Optional["SessionCache"] = None
_engine: Optional["ContextEngine"] = None


def initialize_storage(db_path: str = None):
    """Initialize storage instances."""
    global _activity_ledger, _transient_cache, _engine
    
    from ..env import env
    from .modules.base import ContextEngine
    from side.storage.modules.audit import AuditService
    from side.storage.modules.transient import SessionCache

    if db_path is None:
        db_path = env.get_side_root() / "data.db"
    
    _engine = ContextEngine(db_path=db_path)
    _activity_ledger = AuditService(_engine)
    _transient_cache = SessionCache(_engine)


def get_activity_ledger() -> "AuditService":
    """Get activity ledger instance."""
    global _activity_ledger
    if _activity_ledger is None:
        initialize_storage()
    return _activity_ledger


def get_transient_cache() -> "SessionCache":
    """Get transient cache instance."""
    global _transient_cache
    if _transient_cache is None:
        initialize_storage()
    return _transient_cache
