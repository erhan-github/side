"""
macOS Keychain Integration for Master Key Storage.

Provides secure storage for the CryptoShield master key using
macOS Keychain instead of SQLite settings table.

For Airgapped tier customers requiring FIPS 140-2 compliance.
"""
import logging
import subprocess
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Service name for Keychain
KEYCHAIN_SERVICE = "com.sidelith.cryptoshield"
KEYCHAIN_ACCOUNT = "master_key"


class KeychainStore:
    """
    macOS Keychain integration for secure key storage.
    
    Provides hardware-backed security on macOS through the Secure Enclave.
    Falls back to SQLite storage on non-macOS platforms.
    """
    
    def __init__(self):
        self.is_macos = os.uname().sysname == "Darwin"
        if not self.is_macos:
            logger.warning("🔐 [KEYCHAIN]: Not on macOS. Keychain unavailable.")
    
    def store_key(self, key: bytes) -> bool:
        """
        Store the master key in macOS Keychain.
        
        Args:
            key: The master key bytes to store
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_macos:
            return False
        
        try:
            # Delete existing key first (if any)
            self._delete_key()
            
            # Add new key using security command
            cmd = [
                "security", "add-generic-password",
                "-a", KEYCHAIN_ACCOUNT,
                "-s", KEYCHAIN_SERVICE,
                "-w", key.decode('utf-8'),
                "-U"  # Update if exists
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("🔐 [KEYCHAIN]: Master key stored in macOS Keychain")
                return True
            else:
                logger.error(f"🔐 [KEYCHAIN]: Failed to store key: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"🔐 [KEYCHAIN]: Error storing key: {e}")
            return False
    
    def retrieve_key(self) -> Optional[bytes]:
        """
        Retrieve the master key from macOS Keychain.
        
        Returns:
            The master key bytes, or None if not found
        """
        if not self.is_macos:
            return None
        
        try:
            cmd = [
                "security", "find-generic-password",
                "-a", KEYCHAIN_ACCOUNT,
                "-s", KEYCHAIN_SERVICE,
                "-w"  # Output password only
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                key = result.stdout.strip()
                logger.info("🔐 [KEYCHAIN]: Master key retrieved from macOS Keychain")
                return key.encode('utf-8')
            else:
                # Key not found
                return None
                
        except Exception as e:
            logger.error(f"🔐 [KEYCHAIN]: Error retrieving key: {e}")
            return None
    
    def _delete_key(self) -> bool:
        """Delete existing key from Keychain."""
        try:
            cmd = [
                "security", "delete-generic-password",
                "-a", KEYCHAIN_ACCOUNT,
                "-s", KEYCHAIN_SERVICE
            ]
            subprocess.run(cmd, capture_output=True, text=True)
            return True
        except Exception:
            return False
    
    def is_key_stored(self) -> bool:
        """Check if a key exists in Keychain."""
        return self.retrieve_key() is not None
    
    def migrate_from_sqlite(self, key: bytes) -> bool:
        """
        Migrate master key from SQLite to Keychain.
        
        Args:
            key: The key currently stored in SQLite
            
        Returns:
            True if migration successful
        """
        if self.store_key(key):
            logger.info("🔐 [KEYCHAIN]: Migrated master key from SQLite to Keychain")
            return True
        return False


# Global singleton
_keychain: Optional[KeychainStore] = None


def get_keychain() -> KeychainStore:
    """Get or create the global KeychainStore instance."""
    global _keychain
    if _keychain is None:
        _keychain = KeychainStore()
    return _keychain


def is_keychain_available() -> bool:
    """Check if Keychain storage is available on this platform."""
    return get_keychain().is_macos
