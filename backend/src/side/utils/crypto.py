import base64
import os
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pathlib import Path

logger = logging.getLogger(__name__)

class NeuralShield:
    """
    Seals and Unseals Sidelith Intelligence.
    Ensures that .side files are encrypted at rest.
    """
    def __init__(self):
        self._key = None
        self._fernet = None

    @property
    def fernet(self) -> Fernet:
        """Lazy-loads the master key and initializes Fernet."""
        if self._fernet is None:
            self._key = self._get_or_create_master_key()
            self._fernet = Fernet(self._key)
        return self._fernet

    def _get_or_create_master_key(self) -> bytes:
        """Retrieves or generates a machine-persisted master key."""
        from side.storage.modules.base import SovereignEngine
        from side.storage.modules.transient import OperationalStore
        engine = SovereignEngine()
        op_store = OperationalStore(engine)
        key_str = op_store.get_setting("neural_shield_key")
        
        if not key_str:
            logger.info("🛡️ [SHIELD]: Generating new Master Key for this machine...")
            # Generate a strong random key
            key = Fernet.generate_key()
            op_store.set_setting("neural_shield_key", key.decode())
            return key
        
        return key_str.encode()

    def seal(self, data: str) -> bytes:
        """Encrypts data string into bytes."""
        return self.fernet.encrypt(data.encode())

    def seal_bytes(self, data: bytes) -> bytes:
        """Encrypts raw bytes into bytes."""
        return self.fernet.encrypt(data)

    def unseal(self, encrypted_data: bytes | str) -> str:
        """Decrypts bytes/str into original string."""
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        return self.fernet.decrypt(encrypted_data).decode()

    def unseal_bytes(self, encrypted_data: bytes | str) -> bytes:
        """Decrypts bytes/str into original bytes."""
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        return self.fernet.decrypt(encrypted_data)

    def seal_file(self, file_path: Path, data: str | bytes):
        """Writes encrypted data to a file."""
        if isinstance(data, str):
            encrypted = self.seal(data)
        else:
            encrypted = self.seal_bytes(data)
        file_path.write_bytes(encrypted)

    def unseal_file(self, file_path: Path, binary: bool = False) -> str | bytes:
        """Reads and decrypts data from a file."""
        if not file_path.exists():
            return "" if not binary else b""
        encrypted = file_path.read_bytes()
        try:
            if binary:
                return self.unseal_bytes(encrypted)
            return self.unseal(encrypted)
        except Exception as e:
            logger.error(f"❌ [SHIELD]: Decryption failure for {file_path}. Key mismatch? {e}")
            raise e

# Global instance
shield = NeuralShield()
