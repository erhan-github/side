import os
import base64
import logging
from pathlib import Path
import nacl.signing
import nacl.encoding
import nacl.exceptions

logger = logging.getLogger(__name__)

class SovereignSigner:
    """
    Sovereign Signer [Tier-5]: GPG-style signing for metabolic anchors.
    Ensures the 'sovereign.json' and identity files are untampered.
    """
    
    def __init__(self, key_path: str | Path | None = None):
        if key_path is None:
            from side.env import env
            key_path = env.get_side_root() / "sovereign.key"
        self.key_path = Path(key_path)
        self._signing_key = None
        self._verify_key = None
        self._initialize_keys()

    def _initialize_keys(self):
        """Load existing key or generate a new Sovereign Identity keypair."""
        try:
            if self.key_path.exists():
                seed_b64 = self.key_path.read_text().strip()
                seed = base64.b64decode(seed_b64)
                self._signing_key = nacl.signing.SigningKey(seed)
            else:
                self.key_path.parent.mkdir(parents=True, exist_ok=True)
                self._signing_key = nacl.signing.SigningKey.generate()
                seed_b64 = base64.b64encode(self._signing_key.encode()).decode()
                self.key_path.write_text(seed_b64)
                os.chmod(self.key_path, 0o600)
                logger.info(f"✨ Generated new Sovereign Identity Key: {self.key_path}")
            
            self._verify_key = self._signing_key.verify_key
        except Exception as e:
            logger.error(f"Failed to initialize SovereignSigner: {e}")

    def sign(self, data: str | bytes) -> str:
        """Signs data and returns a base64 encoded signature."""
        if not self._signing_key: return ""
        if isinstance(data, str): data = data.encode()
        
        signed = self._signing_key.sign(data)
        return base64.b64encode(signed.signature).decode()

    def verify(self, data: str | bytes, signature_b64: str) -> bool:
        """Verifies a signature against the data."""
        if not self._verify_key: return False
        if isinstance(data, str): data = data.encode()
        
        try:
            signature = base64.b64decode(signature_b64)
            self._verify_key.verify(data, signature)
            return True
        except (nacl.exceptions.BadSignatureError, Exception):
            return False

    def sign_file(self, file_path: str | Path):
        """Signs a file by creating a companion .sig file with secure permissions."""
        file_path = Path(file_path)
        if not file_path.exists(): return
        
        content = file_path.read_bytes()
        sig = self.sign(content)
        sig_path = file_path.with_suffix(file_path.suffix + ".sig")
        sig_path.write_text(sig)
        sig_path.chmod(0o600)  # Owner-only access (CIA-grade)

    def verify_file(self, file_path: str | Path) -> bool:
        """Verifies a file against its .sig companion."""
        file_path = Path(file_path)
        sig_path = file_path.with_suffix(file_path.suffix + ".sig")
        if not file_path.exists() or not sig_path.exists():
            return False
            
        content = file_path.read_bytes()
        sig = sig_path.read_text().strip()
        return self.verify(content, sig)

# Singleton
signer = SovereignSigner()
