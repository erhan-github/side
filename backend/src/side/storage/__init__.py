"""
sideMCP Storage Layer.

Simplified storage with local-first architecture.
"""

from side.storage.simple_db import SimplifiedDatabase

__all__ = [
    "SimplifiedDatabase",
    "get_forensic_store",
    "get_operational_store",
]

# Storage accessor functions for friction-point handlers
from typing import Optional
from side.storage.modules.forensic import ForensicStore
from side.storage.modules.transient import OperationalStore
from side.storage.modules.base import ContextEngine

_forensic_store: Optional[ForensicStore] = None
_operational_store: Optional[OperationalStore] = None
_engine: Optional[ContextEngine] = None


def initialize_storage(db_path: str = None):
    """Initialize storage instances."""
    global _forensic_store, _operational_store, _engine
    
    from side.env import env
    if db_path is None:
        db_path = env.get_side_root() / "data.db"
    
    _engine = ContextEngine(db_path=db_path)
    _forensic_store = ForensicStore(_engine)
    _operational_store = OperationalStore(_engine)


def get_forensic_store() -> ForensicStore:
    """Get forensic store instance."""
    global _forensic_store
    if _forensic_store is None:
        initialize_storage()
    return _forensic_store


def get_operational_store() -> OperationalStore:
    """Get operational store instance."""
    global _operational_store
    if _operational_store is None:
        initialize_storage()
    return _operational_store
