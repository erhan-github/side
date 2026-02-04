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

from .modules.base import ContextEngine, InsufficientTokensError
from .modules.strategic import StrategicStore
from .modules.identity import IdentityStore
from .modules.forensic import ForensicStore
from .modules.transient import OperationalStore
from .modules.intent_fusion import IntentFusionStore

logger = logging.getLogger(__name__)

# Re-export for compatibility
InsufficientTokensError = InsufficientTokensError

class SimplifiedDatabase:
    """
    Privacy-first SQLite storage for Side (No-Fat Core).
    Access sub-stores directly: db.strategic, db.identity, etc.
    """

    def __init__(self, db_path: str | Path | None = None):
        self.engine = ContextEngine(db_path)
        self.db_path = self.engine.db_path
        
        # Initialize sub-stores (The Source of Truth)
        self.identity = IdentityStore(self.engine)
        self.strategic = StrategicStore(self.engine)
        self.forensic = ForensicStore(self.engine)
        self.operational = OperationalStore(self.engine)
        self.intent_fusion = IntentFusionStore(self.engine)

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
            self.intent_fusion.init_schema(conn)

    def _run_migrations(self) -> None:
        """Handle CTO-level schema resilience."""
        version = self.operational.get_version()
        logger.info(f"Sidelith Sovereign Schema: v{version}")

    def get_project_id(self, project_path: str | Path | None = None) -> str:
        """Delegates to ContextEngine for stable isolation."""
        return ContextEngine.get_project_id(project_path)
