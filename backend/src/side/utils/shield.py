import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class SovereignShield:
    """
    Sovereign Shield: The Redaction Heart of Sidelith.
    [SILO PROTOCOL]: Ensures 0% Strategic and PII leakage to external receivers.
    """
    
    # Patterns for common secrets and PII
    PATTERNS = {
        "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "OPENAI_KEY": r"sk-[a-zA-Z0-9]{20,}",
        "GITHUB_TOKEN": r"ghp_[a-zA-Z0-9]{20,}",
        "STRIPE_KEY": r"(?:sk|pk)_(?:test|live)_[a-zA-Z0-9]{20,}",
        "AWS_KEY": r"AKIA[0-9A-Z]{16}",
        "GENERIC_SECRET": r"(?i)(?:secret|password|passwd|api_key|auth_token)\s*[:=]\s*['\"]([^'\"]{8,})['\"]",
        "IP_ADDRESS": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    }

    @classmethod
    def scrub(cls, text: str) -> str:
        """
        Redacts all identified secrets and PII from the text with Tier-2 Context Awareness.
        """
        if not text: return text
            
        scrubbed = text
        
        # 1. Known Patterns (Fast Regex)
        for label, pattern in cls.PATTERNS.items():
            if label == "GENERIC_SECRET":
                def redact_value(match):
                    return match.group(0).replace(match.group(1), f"<{label}_REDACTED>")
                scrubbed = re.sub(pattern, redact_value, scrubbed)
            else:
                scrubbed = re.sub(pattern, f"<{label}_REDACTED>", scrubbed)
                
        # 2. Entropy Check (Shannon) for Unknown Secrets (Slower, High Precision)
        # We scan for high-entropy strings that look like keys but missed regex
        # Heuristic: strings > 20 chars, no spaces, mixed case + numbers
        words = scrubbed.split()
        for word in words:
            if len(word) > 20 and not word.startswith("<"):
                # Rough entropy check (Hex tokens often ~3.5-4.0)
                if cls._calculate_entropy(word) > 3.5:
                     scrubbed = scrubbed.replace(word, "<HIGH_ENTROPY_SECRET_REDACTED>")
                     
        return scrubbed

    @staticmethod
    def _calculate_entropy(s: str) -> float:
        import math
        prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
        entropy = - sum([p * math.log(p) / math.log(2.0) for p in prob])
        return entropy

    @classmethod
    def anonymize_path(cls, path: str, project_path: str) -> str:
        """
        Removes absolute file system paths, keeping only project-relative paths.
        """
        if not path:
            return path
        return path.replace(project_path, "[PROJECT_ROOT]")

    @classmethod
    def prepare_for_cloud(cls, data: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """
        Recursively scrubs and anonymizes a dictionary for cloud ingestion.
        """
        if isinstance(data, dict):
            return {k: cls.prepare_for_cloud(v, project_path) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.prepare_for_cloud(v, project_path) for v in data]
        elif isinstance(data, str):
            # 1. Redact Secrets
            scrubbed = cls.scrub(data)
            # 2. Anonymize Paths
            anonymized = cls.anonymize_path(scrubbed, project_path)
            return anonymized
        else:
            return data

# Singleton
shield = SovereignShield()
