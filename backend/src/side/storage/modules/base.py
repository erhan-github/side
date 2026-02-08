"""
Core Intelligence Engine - SQLite Persistence Layer.
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

class MerkleManager:
    """
    Handles cryptographic sealing and integrity verification for the Decision Ledger.
    """
    @staticmethod
    def calculate_hash(content: dict[str, Any], parent_hash: str | None) -> str:
        """
        Derives a SHA-256 seal for a decision based on its content and predecessor.
        """
        import hashlib
        import json
        
        # Consistent serialization for deterministic hashing
        payload = {
            "content": content,
            "parent": parent_hash or "GENESIS"
        }
        encoded = json.dumps(payload, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()

class ContextEngine:
    """
    Core engine handling SQLite lifecycle and resiliency.
    """

    def __init__(self, db_path: str | Path | None = None):
        if db_path is None:
            from side.env import env
            db_path = env.get_db_path()
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Always enforce permissions on existing databases (Security hardening)
        if self.db_path.exists():
            self.harden_permissions()
        
        # Initialize sub-stores
        # Initialize sub-stores
        from side.storage.modules.strategy import StrategyStore
        from side.storage.modules.audit import AuditStore
        from side.storage.modules.accounting import AccountingStore
        from .identity import IdentityStore
        from .transient import OperationalStore
        from .substores.patterns import PublicPatternStore
        
        from side.storage.modules.ontology import OntologyStore
        
        self.strategic = StrategyStore(self)
        self.audit = AuditStore(self)
        self.accounting = AccountingStore(self)
        self.identity = IdentityStore(self)
        self.operational = OperationalStore(self)
        self.wisdom = PublicPatternStore(self)
        self.ontology = OntologyStore(self)

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Create a thread-safe SQLite connection with optimized pragmas.
        Auto-enables SQLCipher for HiTech/Enterprise tiers.
        """
        # Check if tier qualifies for SQLCipher
        use_encryption = self._should_use_encryption()
        
        try:
            if use_encryption:
                conn = self._create_encrypted_connection()
            else:
                conn = self._create_standard_connection()
            
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
    
    def _should_use_encryption(self) -> bool:
        """Check if current tier qualifies for SQLCipher encryption."""
        try:
            # Check tier from existing profile (if exists)
            if not self.db_path.exists():
                return False  # New DB, use standard until tier established
            
            # Quick check without full store initialization
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                # Check if profile table exists first
                res = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='profile'").fetchone()
                if not res:
                    return False
                
                cursor = conn.execute("SELECT tier FROM profile LIMIT 1")
                row = cursor.fetchone()
            
            if row and row[0] in ("high_tech", "enterprise"):
                # Check if SQLCipher is available
                try:
                    from side.security.sqlcipher import SQLCipherManager
                    return SQLCipherManager(self.db_path).is_available
                except ImportError:
                    return False
            return False
        except Exception:
            return False
    
    def _create_standard_connection(self) -> sqlite3.Connection:
        """Create standard SQLite connection."""
        conn = sqlite3.connect(
            self.db_path, 
            timeout=30.0,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn
    
    def _create_encrypted_connection(self) -> sqlite3.Connection:
        """Create SQLCipher encrypted connection for HiTech/Enterprise."""
        try:
            from side.security.sqlcipher import SQLCipherManager
            manager = SQLCipherManager(self.db_path)
            conn = manager.connect()
            logger.info("🔒 [ENGINE]: Using SQLCipher encryption (P2P/Enterprise tier)")
            return conn
        except Exception as e:
            logger.info(f"ℹ️ [STORAGE]: Standard Mode active. Install 'pysqlcipher3' for High-Tier IP-Sensitive Protection. {e}")
            return self._create_standard_connection()

    def check_integrity(self) -> bool:
        """Run a technical SQLite integrity check."""
        try:
            with self.connection() as conn:
                result = conn.execute("PRAGMA integrity_check;").fetchone()
                return result[0] == "ok"
        except Exception as e:
            logger.error(f"Integrity check failed: {e}")
            return False

    def perform_maintenance(self) -> None:
        """Runs routine intelligence hardening (VACUUM, rotational backups)."""
        bak_path = self.db_path.with_suffix(".db.bak")
        try:
            with self.connection() as conn:
                # 1. Vacuum to reclaim space and re-sort indices
                conn.execute("VACUUM")
                logger.info("🎨 [ENGINE]: Context VACUUM complete.")
                
            # 2. Atomic Backup
            if self.check_integrity():
                import shutil
                shutil.copy2(self.db_path, bak_path)
                logger.debug("Disaster Recovery: Atomic backup created.")
        except Exception as e:
            logger.warning(f"Maintenance failed: {e}")

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
        """Persists PROJECT_ID in a sealed file for stable isolation."""
        from side.utils.paths import get_repo_root
        from side.utils.crypto import shield
        
        if project_path is None or str(project_path) == ".":
            project_path = get_repo_root()
        else:
            project_path = Path(project_path)
            
        project_path = project_path.resolve()
        id_file = project_path / ".side-id"
        
        # [SEALED IDENTITY]: If file exists, unseal it
        if id_file.exists():
            try:
                raw_content = id_file.read_text().strip()
                # If it looks like a hash, seal it now (migration)
                if len(raw_content) == 16 and not raw_content.startswith("sealed:"):
                    unsealed = raw_content
                    id_file.write_text(f"sealed:{shield.seal(unsealed)}")
                    return unsealed
                elif raw_content.startswith("sealed:"):
                    return shield.unseal(raw_content[7:])
                return raw_content
            except Exception:
                pass
        
        import hashlib
        path_hash = hashlib.sha256(str(project_path).encode()).hexdigest()[:16]
        try:
            # Seal for first-time creation
            id_file.write_text(f"sealed:{shield.seal(path_hash)}")
            os.chmod(id_file, 0o600)
        except Exception:
            pass
            
        return path_hash

    def atomic_backup(self) -> None:
        """Alias for perform_maintenance to satisfy Tier-4 legacy probes."""
        self.perform_maintenance()
