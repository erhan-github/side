"""
Core utilities and singletons for Side tools.

This module provides shared state and utility functions used across all tools.
Single source of truth for auto-intelligence, database, and market analyzer.
"""

from side.intel.auto_intelligence import AutoIntelligence

from side.storage.modules.base import ContextEngine
from side.storage.modules.identity import IdentityStore
from side.storage.modules.strategy import StrategyStore
from side.storage.modules.audit import AuditStore
from side.storage.modules.transient import OperationalStore

# Global singletons - initialized lazily
_engine: ContextEngine | None = None
_identity: IdentityStore | None = None
_strategic: StrategyStore | None = None
_audit: AuditStore | None = None
_operational: OperationalStore | None = None
_auto_intel: AutoIntelligence | None = None



def get_auto_intel() -> AutoIntelligence:
    """Get or create auto-intelligence singleton."""
    global _auto_intel
    if _auto_intel is None:
        _auto_intel = AutoIntelligence()
    return _auto_intel


def get_engine() -> ContextEngine:
    global _engine
    if _engine is None:
        _engine = ContextEngine()
    return _engine

def get_identity() -> IdentityStore:
    global _identity
    if _identity is None:
        _identity = IdentityStore(get_engine())
    return _identity

def get_strategic() -> StrategyStore:
    global _strategic
    if _strategic is None:
        _strategic = StrategyStore(get_engine())
    return _strategic

def get_audit() -> AuditStore:
    global _audit
    if _audit is None:
        _audit = AuditStore(get_engine())
    return _audit

def get_operational() -> OperationalStore:
    global _operational
    if _operational is None:
        _operational = OperationalStore(get_engine())
    return _operational

def get_database():
    """Legacy compatibility bridge."""
    from side.storage.simple_db import SimplifiedDatabase
    return SimplifiedDatabase()



