"""
 Governance Policy - The Compliance Moat.
Ensures Enterprise Safety via Automated Redaction and Retention.
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GovernancePolicy:
    def __init__(self):
        # [SECRET-ZERO]: Patterns that must NEVER be stored (CIA-grade)
        self.redaction_patterns = [
            # API Keys
            (r"sk-[a-zA-Z0-9]{20,}", "[REDACTED_OPENAI_KEY]"),
            (r"sk_live_[a-zA-Z0-9]{20,}", "[REDACTED_STRIPE_LIVE_KEY]"),
            (r"sk_test_[a-zA-Z0-9]{20,}", "[REDACTED_STRIPE_TEST_KEY]"),
            (r"ghp_[a-zA-Z0-9]{20,}", "[REDACTED_GITHUB_TOKEN]"),
            (r"ghs_[a-zA-Z0-9]{20,}", "[REDACTED_GITHUB_SECRET]"),
            (r"github_pat_[a-zA-Z0-9_]{22,}", "[REDACTED_GITHUB_PAT]"),
            (r"xoxb-[a-zA-Z0-9-]+", "[REDACTED_SLACK_BOT]"),
            (r"xoxp-[a-zA-Z0-9-]+", "[REDACTED_SLACK_USER]"),
            (r"AKIA[0-9A-Z]{16}", "[REDACTED_AWS_ACCESS_KEY]"),
            (r"AIza[0-9A-Za-z\-_]{35}", "[REDACTED_GOOGLE_API_KEY]"),
            (r"SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}", "[REDACTED_SENDGRID_KEY]"),
            # JWTs and Tokens
            (r"eyJ[a-zA-Z0-9\-_]+\.eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+", "[REDACTED_JWT]"),
            (r"Bearer\s+[a-zA-Z0-9\-_\.]+", "[REDACTED_BEARER_TOKEN]"),
            # Cryptographic Keys
            (r"-----BEGIN PRIVATE KEY-----", "[REDACTED_PRIVATE_KEY]"),
            (r"-----BEGIN RSA PRIVATE KEY-----", "[REDACTED_RSA_KEY]"),
            (r"-----BEGIN EC PRIVATE KEY-----", "[REDACTED_EC_KEY]"),
            (r"-----BEGIN PGP PRIVATE KEY-----", "[REDACTED_PGP_KEY]"),
            # Database Credentials
            (r"postgres://[^\s]+", "[REDACTED_POSTGRES_URL]"),
            (r"mysql://[^\s]+", "[REDACTED_MYSQL_URL]"),
            (r"mongodb(\+srv)?://[^\s]+", "[REDACTED_MONGODB_URL]"),
            (r"redis://[^\s]+", "[REDACTED_REDIS_URL]"),
            # PII - Configurable for enterprise
            (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[REDACTED_EMAIL]"),
            (r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b", "[REDACTED_SSN]"),
            (r"\b(?:\d{4}[-\s]?){3}\d{4}\b", "[REDACTED_CREDIT_CARD]"),
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
            logger.warning("Storage rejected: Context exceeds Compliance Quota. [DATA_RETENTION_LB_BREACH]")
            return False
        return True
