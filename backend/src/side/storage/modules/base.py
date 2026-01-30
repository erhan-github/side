"""
Sovereign Base Engine - Core SQLite Connectivity.
"""

import sqlite3
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class InsufficientTokensError(Exception):
    """Raised when the user has run out of Strategic Units (SU)."""
    pass

class SovereignEngine:
    """
    Core engine handling SQLite lifecycle and resiliency.
    """

    def __init__(self, db_path: str | Path | None = None):
        if db_path is None:
            db_path = Path.home() / ".side" / "local.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize sub-stores
        from side.storage.modules.strategic import StrategicStore
        from side.storage.modules.forensic import ForensicStore
        from side.storage.modules.accounting import AccountingStore
        
        self.strategic = StrategicStore(self)
        self.forensic = ForensicStore(self)
        self.accounting = AccountingStore(self)

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Create a thread-safe SQLite connection with optimized pragmas.
        """
        try:
            conn = sqlite3.connect(
                self.db_path, 
                timeout=30.0,
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row
            
            # Optimize for speed and resilience
            conn.execute("PRAGMA journal_mode=WAL") 
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA foreign_keys=ON")
            
            try:
                yield conn
                conn.commit()
            except sqlite3.OperationalError as e:
                if "database or disk is full" in str(e).lower():
                    logger.critical(f"FATAL: Database or disk is full at {self.db_path}. Intelligence persistence disabled.")
                conn.rollback()
                raise
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
        except sqlite3.OperationalError as e:
            if "database or disk is full" in str(e).lower():
                logger.critical(f"FATAL: Could not open database. Disk full at {self.db_path}.")
            raise

    def check_integrity(self) -> bool:
        """Run a forensic SQLite integrity check."""
        try:
            with self.connection() as conn:
                result = conn.execute("PRAGMA integrity_check;").fetchone()
                return result[0] == "ok"
        except Exception as e:
            logger.error(f"Integrity check failed: {e}")
            return False

    def atomic_backup(self) -> None:
        """Maintain a rotational .db.bak for disaster recovery."""
        bak_path = self.db_path.with_suffix(".db.bak")
        if self.db_path.exists():
            try:
                import shutil
                if self.check_integrity():
                    shutil.copy2(self.db_path, bak_path)
                    logger.debug("Disaster Recovery: Atomic backup created.")
            except Exception as e:
                logger.warning(f"Disaster Recovery: Backup failed: {e}")

    def harden_permissions(self) -> None:
        """Ensure local.db is only readable by the user (mode 600)."""
        if self.db_path.exists():
            import os
            try:
                os.chmod(self.db_path, 0o600)
            except Exception:
                pass

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
