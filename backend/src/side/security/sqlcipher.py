"""
SQLCipher Integration for Full Database Encryption.

Provides transparent encryption for the entire local.db database
using SQLCipher (256-bit AES encryption).

For High Tech tier customers requiring full disk encryption.
"""
import logging
import os
from pathlib import Path
from typing import Optional
import sqlite3

logger = logging.getLogger(__name__)


class SQLCipherManager:
    """
    Manages SQLCipher encrypted database connections.
    
    SQLCipher provides:
    - 256-bit AES encryption
    - Transparent encryption of all database pages
    - Password-based key derivation (PBKDF2)
    - Secure memory handling
    """
    
    def __init__(self, db_path: Path, key: Optional[str] = None):
        self.db_path = db_path
        self.key = key or self._get_default_key()
        self._is_sqlcipher_available = self._check_sqlcipher()
    
    def _check_sqlcipher(self) -> bool:
        """Check if SQLCipher is available."""
        try:
            # Try to import pysqlcipher3 or sqlcipher3
            try:
                from pysqlcipher3 import dbapi2 as sqlcipher
                self._sqlcipher = sqlcipher
                return True
            except ImportError:
                pass
            
            try:
                import sqlcipher3 as sqlcipher
                self._sqlcipher = sqlcipher
                return True
            except ImportError:
                pass
            
            logger.warning("🔒 [SQLCIPHER]: Not installed. pip install pysqlcipher3")
            return False
            
        except Exception as e:
            logger.error(f"🔒 [SQLCIPHER]: Check failed: {e}")
            return False
    
    def _get_default_key(self) -> str:
        """Get encryption key from environment or generate."""
        key = os.getenv("SIDELITH_DB_KEY")
        if key:
            return key
        
        # Try to retrieve from Keychain
        try:
            from side.security.keychain import get_keychain
            keychain = get_keychain()
            stored = keychain.retrieve_key()
            if stored:
                return stored.decode('utf-8')
        except Exception:
            pass
        
        # Generate a new key
        import secrets
        return secrets.token_hex(32)
    
    @property
    def is_available(self) -> bool:
        """Check if SQLCipher encryption is available."""
        return self._is_sqlcipher_available
    
    def connect(self) -> sqlite3.Connection:
        """
        Create an encrypted database connection.
        
        Returns:
            Encrypted SQLite connection
        """
        if not self._is_sqlcipher_available:
            logger.warning("🔒 [SQLCIPHER]: Falling back to unencrypted SQLite")
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        
        conn = self._sqlcipher.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        # Set encryption key (Using parameterization for security)
        conn.execute("PRAGMA key = ?", (self.key,))
        
        # Optimize settings
        conn.execute("PRAGMA cipher_page_size = 4096")
        conn.execute("PRAGMA kdf_iter = 256000")  # PBKDF2 iterations
        conn.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA512")
        conn.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512")
        
        # Standard optimizations
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA foreign_keys = ON")
        
        logger.info("🔒 [SQLCIPHER]: Encrypted connection established")
        return conn
    
    def encrypt_existing_database(self, plaintext_db: Path) -> bool:
        """
        Encrypt an existing unencrypted database.
        
        Args:
            plaintext_db: Path to the unencrypted database
            
        Returns:
            True if encryption successful
        """
        if not self._is_sqlcipher_available:
            logger.error("🔒 [SQLCIPHER]: Cannot encrypt - SQLCipher not available")
            return False
        
        try:
            encrypted_db = plaintext_db.with_suffix('.encrypted.db')
            
            # Connect to plaintext
            plain_conn = sqlite3.connect(plaintext_db)
            
            # Create encrypted database
            enc_conn = self._sqlcipher.connect(str(encrypted_db))
            enc_conn.execute("PRAGMA key = ?", (self.key,))
            
            # Copy all data
            plain_conn.backup(enc_conn)
            
            plain_conn.close()
            enc_conn.close()
            
            # Replace original with encrypted
            plaintext_db.unlink()
            encrypted_db.rename(plaintext_db)
            
            logger.info(f"🔒 [SQLCIPHER]: Encrypted {plaintext_db}")
            return True
            
        except Exception as e:
            logger.error(f"🔒 [SQLCIPHER]: Encryption failed: {e}")
            return False
    
    def verify_encryption(self) -> bool:
        """Verify that the database is properly encrypted."""
        if not self._is_sqlcipher_available:
            return False
        
        try:
            conn = self.connect()
            # If we can query, encryption is working
            conn.execute("SELECT count(*) FROM sqlite_master")
            conn.close()
            return True
        except Exception:
            return False


def get_encrypted_engine(db_path: Path, key: Optional[str] = None) -> SQLCipherManager:
    """Factory function for SQLCipher manager."""
    return SQLCipherManager(db_path, key)
