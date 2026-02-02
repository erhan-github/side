import base64
import os
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.fernet import Fernet, InvalidToken
from cryptography.exceptions import InvalidTag
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
    def aesgcm(self) -> AESGCM:
        """Lazy-loads the AES-GCM engine (AES-256)."""
        if self._key is None:
             self._init_keys()
        return self._aesgcm

    @property
    def fernet(self) -> Fernet:
        """Lazy-loads Fernet for backward compatibility."""
        if self._fernet is None:
            self._init_keys()
        return self._fernet

    def _init_keys(self):
        """Initializes cryptographic engines."""
        raw_key = self._get_or_create_master_key()
        # Ensure we have 32 bytes for AES-256
        if len(raw_key) == 32:
            self._key = raw_key
        else:
            # Fallback/Legacy: If key is base64 string from Fernet generation
            try:
                self._key = base64.urlsafe_b64decode(raw_key)
            except Exception:
                # If truly raw bytes but wrong length, force 32 bytes hash
                digest = hashes.Hash(hashes.SHA256())
                digest.update(raw_key)
                self._key = digest.finalize()
        
        self._aesgcm = AESGCM(self._key)
        # Fernet needs 32-byte url-safe base64. 
        self._fernet = Fernet(base64.urlsafe_b64encode(self._key))

    def _get_or_create_master_key(self) -> bytes:
        """Retrieves or generates a machine-persisted master key."""
        from side.storage.modules.base import SovereignEngine
        from side.storage.modules.transient import OperationalStore
        engine = SovereignEngine()
        op_store = OperationalStore(engine)
        key_str = op_store.get_setting("neural_shield_key")
        
        if not key_str:
            logger.info("🛡️ [SHIELD]: Generating new AES-256 Master Key...")
            # Generate 32 bytes for AES-256
            key = AESGCM.generate_key(bit_length=256)
            encoded_key = base64.urlsafe_b64encode(key).decode() # Store as b64 string
            op_store.set_setting("neural_shield_key", encoded_key)
            return key # Return raw bytes
        
        # Stored as base64 string
        return base64.urlsafe_b64decode(key_str.encode())

    def seal(self, data: str) -> bytes:
        """Encrypts data string into bytes using AES-256-GCM."""
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, data.encode(), None)
        return nonce + ciphertext

    def seal_bytes(self, data: bytes) -> bytes:
        """Encrypts raw bytes into bytes using AES-256-GCM."""
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, data, None)
        return nonce + ciphertext

    def unseal(self, encrypted_data: bytes | str) -> str:
        """Decrypts bytes/str into original string. Tries AES-256, falls back to Fernet."""
        if isinstance(encrypted_data, str):
            # If it's a string, it might be b64 encoded or raw bytes that got messed up.
            # Usually seal returns bytes. If passed str, might be legacy b64.
            # Try to encode to bytes
            try:
                encrypted_data = encrypted_data.encode()
            except:
                pass
        
        # 1. Try AES-256-GCM
        try:
            if len(encrypted_data) > 12:
                nonce = encrypted_data[:12]
                ct = encrypted_data[12:]
                return self.aesgcm.decrypt(nonce, ct, None).decode()
        except (InvalidTag, ValueError):
            pass
            
        # 2. Fallback to Fernet (Legacy)
        try:
            return self.fernet.decrypt(encrypted_data).decode()
        except InvalidToken:
            raise ValueError("Decryption failed (Invalid Token/Tag).")

    def unseal_bytes(self, encrypted_data: bytes | str) -> bytes:
        """Decrypts bytes/str into original bytes. Tries AES-256, falls back to Fernet."""
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
            
        # 1. Try AES-256-GCM
        try:
            if len(encrypted_data) > 12:
                nonce = encrypted_data[:12]
                ct = encrypted_data[12:]
                return self.aesgcm.decrypt(nonce, ct, None)
        except (InvalidTag, ValueError):
            pass
            
        # 2. Fallback to Fernet
        try:
            return self.fernet.decrypt(encrypted_data)
        except InvalidToken:
            raise ValueError("Decryption failed (Invalid Token/Tag).")

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
