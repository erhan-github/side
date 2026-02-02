"""
[LAYER 6] Governance Policy - The Compliance Moat.
Ensures Enterprise Safety via Automated Redaction and Retention.
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GovernancePolicy:
    def __init__(self):
        # [SECRET-ZERO]: Patterns that must NEVER be stored
        self.redaction_patterns = [
            (r"sk-[a-zA-Z0-9]{20,}", "[REDACTED_API_KEY]"),
            (r"ghp_[a-zA-Z0-9]{20,}", "[REDACTED_GITHUB_TOKEN]"),
            (r"eyJ[a-zA-Z0-9\-_]+\.eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+", "[REDACTED_JWT]"),
            (r"-----BEGIN PRIVATE KEY-----", "[REDACTED_PRIVATE_KEY]"),
            # Simple PII (Email) - Configurable for enterprise
            (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[REDACTED_EMAIL]")
        ]

    def sanitize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively scrubs secrets from dictionaries before storage.
        """
        clean = {}
        for k, v in payload.items():
            if isinstance(v, dict):
                clean[k] = self.sanitize_payload(v)
            elif isinstance(v, str):
                clean[k] = self._scrub_text(v)
            elif isinstance(v, list):
                clean[k] = [
                    self.sanitize_payload(i) if isinstance(i, dict) else (self._scrub_text(i) if isinstance(i, str) else i)
                    for i in v
                ]
            else:
                clean[k] = v
        return clean

    def _scrub_text(self, text: str) -> str:
        """Apply all redaction patterns."""
        for pattern, replacement in self.redaction_patterns:
            text = re.sub(pattern, replacement, text)
        return text

    def check_compliance(self, context_size_bytes: int) -> bool:
        """
        [QUOTA]: Prevents 'Data Hoarding' liability.
        """
        MAX_CONTEXT = 10 * 1024 * 1024 # 10MB per session
        if context_size_bytes > MAX_CONTEXT:
            logger.warning("Storage rejected: Context exceeds Compliance Quota.")
            return False
        return True
