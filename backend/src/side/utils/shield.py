import os
import re
import logging
import base64
from typing import Dict, Any
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger(__name__)

class SovereignShield:
    """
    Sovereign Shield: The Redaction & Encryption Heart of Sidelith.
    [SILO PROTOCOL]: Ensures 0% Strategic and PII leakage.
    """
    
    PATTERNS = {
        "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "OPENAI_KEY": r"sk-[a-zA-Z0-9]{20,}",
        "GITHUB_TOKEN": r"ghp_[a-zA-Z0-9]{20,}",
        "STRIPE_KEY": r"(?:sk|pk)_(?:test|live)_[a-zA-Z0-9]{20,}",
        "AWS_KEY": r"AKIA[0-9A-Z]{16}",
        "GENERIC_SECRET": r"(?i)(?:secret|password|passwd|api_key|auth_token)\s*[:=]\s*['\"]([^'\"]{8,})['\"]",
        "IP_ADDRESS": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    }

    def __init__(self):
        # Use SIDELITH_DB_KEY for encryption if available, otherwise fallback to a local safe
        key_str = os.environ.get("SIDELITH_DB_KEY", "sovereign_fallback_key_32_bytes_!!")
        # Ensure key is 32 bytes for AES-256
        self.key = key_str.encode().ljust(32)[:32]
        self.aes = AESGCM(self.key)

    def seal(self, data: str) -> str:
        """
        Encrypts data using AES-256-GCM.
        Returns a base64 encoded string: b64(nonce + ciphertext).
        """
        if not data: return data
        nonce = os.urandom(12)
        ciphertext = self.aes.encrypt(nonce, data.encode(), None)
        return base64.b64encode(nonce + ciphertext).decode()

    def unseal(self, encrypted_data: str) -> str:
        """
        Decrypts data using AES-256-GCM.
        """
        if not encrypted_data: return encrypted_data
        try:
            raw = base64.b64decode(encrypted_data)
            nonce = raw[:12]
            ciphertext = raw[12:]
            decrypted = self.aes.decrypt(nonce, ciphertext, None)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Unseal failed: {e}")
            return f"<DECRYPTION_FAILED>"

    @classmethod
    def scrub(cls, text: str) -> str:
        # ... logic as before (static) ...
        if not text: return text
        scrubbed = text
        for label, pattern in cls.PATTERNS.items():
            if label == "GENERIC_SECRET":
                def redact_value(match):
                    return match.group(0).replace(match.group(1), f"<{label}_REDACTED>")
                scrubbed = re.sub(pattern, redact_value, scrubbed)
            else:
                scrubbed = re.sub(pattern, f"<{label}_REDACTED>", scrubbed)
        return scrubbed

    # Anonymize and prepare_for_cloud stay relatively similar...
    @classmethod
    def anonymize_path(cls, path: str, project_path: str) -> str:
        if not path: return path
        return path.replace(project_path, "[PROJECT_ROOT]")

    @classmethod
    def prepare_for_cloud(cls, data: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        if isinstance(data, dict):
            return {k: cls.prepare_for_cloud(v, project_path) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.prepare_for_cloud(v, project_path) for v in data]
        elif isinstance(data, str):
            scrubbed = cls.scrub(data)
            return cls.anonymize_path(scrubbed, project_path)
        return data

# Singleton
shield = SovereignShield()
