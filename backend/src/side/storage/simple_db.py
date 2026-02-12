"""
Sidelith Database - Privacy-First Strategic Storage.

This is a modular facade that delegates to specialized domain stores:
1. Base Engine (base.py)
2. Project Plan (strategy.py)
3. User Profile (identity.py)
4. Audit Log (audit.py)
5. Billing Ledger (accounting.py)
6. Operational Cache (transient.py)
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from side.utils.helpers import safe_get

from .modules.base import ContextEngine, InsufficientTokensError
from .modules.strategy import DecisionStore
from .modules.identity import IdentityService
from .modules.audit import AuditService
from .modules.accounting import Ledger
from .modules.transient import SessionCache
from .modules.goal_tracker import GoalTracker

logger = logging.getLogger(__name__)

# Re-export for compatibility
InsufficientTokensError = InsufficientTokensError

class SimplifiedDatabase:
    """
    Privacy-first SQLite storage for Sidelith.
    Access services directly: db.plans, db.profile, db.auditss, etc.
    """

    def __init__(self, db_path: str | Path | None = None):
        self.engine = ContextEngine(db_path)
        self.db_path = self.engine.db_path
        
        # Initialize services (The Source of Truth)
        self.profile = IdentityService(self.engine)
        self.plans = DecisionStore(self.engine)
        self.auditss = AuditService(self.engine)
        self.ledger = Ledger(self.engine)
        self.operational = SessionCache(self.engine)
        self.goal_tracker = GoalTracker(self.engine)

        # Startup lifecycle
        self.engine.atomic_backup()
        self._init_schema()
        self._run_migrations()
        self.engine.harden_permissions()

    def _init_schema(self) -> None:
        """Initialize all service schemas."""
        with self.engine.connection() as conn:
            self.operational.init_schema(conn)
            self.plans.init_schema(conn)
            self.profile.init_schema(conn)
            self.auditss.init_schema(conn)

    def _run_migrations(self) -> None:
        """Handle CTO-level schema resilience."""
        version = self.operational.get_version()
        logger.info(f"Sidelith System Schema: v{version}")

    def get_project_id(self, project_path: str | Path | None = None) -> str:
        """Delegates to ContextEngine for stable isolation."""
        return ContextEngine.get_project_id(project_path)
