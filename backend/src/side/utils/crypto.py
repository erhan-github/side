import os
import re
import logging
import base64
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken
from cryptography.exceptions import InvalidTag
from pathlib import Path

logger = logging.getLogger(__name__)

class CryptoShield:
    """
    Seals and Unseals System Data.
    Ensures that .side files are encrypted at rest.
    Also handles PII scrubbing and anonymization.
    """
    
    # [HARDENING]: Patterns are now loaded from external JSON database
    # Fallback patterns in case JSON is missing
    FALLBACK_PATTERNS = {
        "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "OPENAI_KEY": r"sk-[a-zA-Z0-9]{20,}",
        "GENERIC_SECRET": r"(?i)(?:secret|password|passwd|api_key|auth_token)\s*[:=]\s*['\"]([^'\"]{8,})['\"]",
        "IP_ADDRESS": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    }
    
    PATTERNS = {} # Populated on init

    def __init__(self):
        self._key = None
        self._fernet = None
        self._load_patterns()

    def _load_patterns(self):
        """Loads comprehensive secret patterns from side/data/secret_patterns.json."""
        try:
            import json
            # Locate data file relative to this file
            base_path = Path(__file__).resolve().parent.parent / "data" / "secret_patterns.json"
            
            if base_path.exists():
                data = json.loads(base_path.read_text())
                # Flatten the categorized JSON into a single dictionary
                self.PATTERNS = {}
                for category, patterns in data.items():
                    if category == "_meta": continue
                    for name, regex in patterns.items():
                        self.PATTERNS[name] = regex
                logger.info(f"🛡️ [SHIELD]: Loaded {len(self.PATTERNS)} secret signatures from database.")
            else:
                logger.warning(f"⚠️ [SHIELD]: Pattern DB not found at {base_path}. Using fallbacks.")
                self.PATTERNS = self.FALLBACK_PATTERNS
        except Exception as e:
            logger.error(f"❌ [SHIELD]: Failed to load pattern DB: {e}")
            self.PATTERNS = self.FALLBACK_PATTERNS

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

    def _init_keys(self, engine=None, op_store=None):
        """Initializes cryptographic engines."""
        raw_key = self._get_or_create_master_key(engine=engine, op_store=op_store)
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

    def _get_or_create_master_key(self, engine=None, op_store=None) -> bytes:
        """Retrieves or generates a machine-persisted master key."""
        if not op_store:
            from side.storage.modules.base import ContextEngine
            from side.storage.modules.transient import SessionCache
            engine = engine or ContextEngine()
            op_store = SessionCache(engine)
        
        key_str = op_store.get_setting("crypto_shield_key")
        
        if not key_str:
            # Legacy fallback
            key_str = op_store.get_setting("neural_shield_key")

        if not key_str:
            logger.info("🛡️ [SHIELD]: Generating new AES-256 Master Key...")
            # Generate 32 bytes for AES-256
            key = AESGCM.generate_key(bit_length=256)
            encoded_key = base64.urlsafe_b64encode(key).decode() # Store as b64 string
            op_store.set_setting("crypto_shield_key", encoded_key)
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
        """Writes encrypted data to a file with secure permissions."""
        if isinstance(data, str):
            encrypted = self.seal(data)
        else:
            encrypted = self.seal_bytes(data)
        file_path.write_bytes(encrypted)
        file_path.chmod(0o600)  # Owner-only access (CIA-grade)

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

    @staticmethod
    def _calculate_entropy(data: str) -> float:
        """Calculates Shannon entropy of a string."""
        import math
        if not data: return 0
        entropy = 0
        for x in set(data):
            p_x = data.count(x) / len(data)
            entropy += - p_x * math.log2(p_x)
        return entropy

    @staticmethod
    def _luhn_check(card_number: str) -> bool:
        """
        Validates a credit card number using the Luhn checksum algorithm.
        Essential for reducing false positives in PCI detection.
        """
        # Remove non-digits
        digits = re.sub(r'\D', '', card_number)
        if len(digits) < 13: return False # Basic length check
        
        # Luhn Algorithm
        total = 0
        reverse_digits = digits[::-1]
        for i, d in enumerate(reverse_digits):
            n = int(d)
            if i % 2 == 1:
                n *= 2
                if n > 9: n -= 9
            total += n
        return total % 10 == 0

    def scrub(self, text: str) -> str:
        """
        Scrubs PII and high-entropy secrets from text.
        [HARDENING]: Uses Shannon Entropy > 4.5 for secrets.
        [COMPLIANCE]: Uses Luhn Algorithm for Credit Cards (PCI).
        """
        if not text: return text
        scrubbed = text
        
        # 1. Regex-based Scrubbing with Validation
        for label, pattern in self.PATTERNS.items():
            if label == "CREDIT_CARD":
                # Special handling for PCI Compliance with False Positive reduction
                for match in re.finditer(pattern, scrubbed):
                    candidate = match.group(0)
                    if self._luhn_check(candidate):
                        scrubbed = scrubbed.replace(candidate, f"<{label}_REDACTED>")
            elif label == "GENERIC_SECRET":
                def redact_value(match):
                    return match.group(0).replace(match.group(1), f"<{label}_REDACTED>")
                scrubbed = re.sub(pattern, redact_value, scrubbed)
            else:
                scrubbed = re.sub(pattern, f"<{label}_REDACTED>", scrubbed)
                
        # 2. Entropy-based Scrubbing (Chaos Detection)
        # Find potential secret candidates: simple tokens > 20 chars without spaces
        tokens = re.finditer(r'\b([a-zA-Z0-9_=-]{20,})\b', scrubbed)
        
        for match in tokens:
            token = match.group(1)
            # Filter out common false positives
            if any(x in token for x in ["REDACTED", "UUID", "sha256", "md5"]): continue
            
            # Calculate entropy
            entropy = self._calculate_entropy(token)
            
            # Thresholds: 
            # Hex (0-9a-f) max entropy = 4.0. 
            # Base64 (A-Za-z0-9+/) max entropy = 6.0.
            # We target > 4.5 to catch high-density secrets (API keys) while ignoring simple hex hashes.
            if entropy > 4.5:
                scrubbed = scrubbed.replace(token, f"<ENTROPY_REDACTED:{entropy:.1f}>")
                
        return scrubbed

    def anonymize_path(self, path: str, project_path: str) -> str:
        """Anonymizes file paths relative to project root."""
        if not path: return path
        return path.replace(project_path, "[PROJECT_ROOT]")

    def prepare_for_cloud(self, data: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """Recursively scrubs and anonymizes data structure."""
        if isinstance(data, dict):
            return {k: self.prepare_for_cloud(v, project_path) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.prepare_for_cloud(v, project_path) for v in data]
        elif isinstance(data, str):
            scrubbed = self.scrub(data)
            return self.anonymize_path(scrubbed, project_path)
        return data

# Global instance
shield = CryptoShield()
