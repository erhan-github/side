"""
sideMCP Storage Layer.

Simplified storage with local-first architecture.
"""

from side.storage.simple_db import SimplifiedDatabase

__all__ = [
    "SimplifiedDatabase",
    "get_audit_store",
    "get_operational_store",
]

from typing import Optional, TYPE_CHECKING
from side.storage.simple_db import SimplifiedDatabase

if TYPE_CHECKING:
    from side.storage.modules.audit import AuditStore
    from side.storage.modules.transient import OperationalStore
    from side.storage.modules.base import ContextEngine

__all__ = [
    "SimplifiedDatabase",
    "get_audit_store",
    "get_operational_store",
]

_audit_store: Optional["AuditStore"] = None
_operational_store: Optional["OperationalStore"] = None
_engine: Optional["ContextEngine"] = None


def initialize_storage(db_path: str = None):
    """Initialize storage instances."""
    global _audit_store, _operational_store, _engine
    
    from ..env import env
    from .modules.base import ContextEngine
    from side.storage.modules.audit import AuditStore
    from side.storage.modules.transient import OperationalStore

    if db_path is None:
        db_path = env.get_side_root() / "data.db"
    
    _engine = ContextEngine(db_path=db_path)
    _audit_store = AuditStore(_engine)
    _operational_store = OperationalStore(_engine)


def get_audit_store() -> "AuditStore":
    """Get audit store instance."""
    global _audit_store
    if _audit_store is None:
        initialize_storage()
    return _audit_store


def get_operational_store() -> "OperationalStore":
    """Get operational store instance."""
    global _operational_store
    if _operational_store is None:
        initialize_storage()
    return _operational_store
