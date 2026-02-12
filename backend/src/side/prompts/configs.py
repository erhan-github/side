"""
Centralized configurations for LLM cognitive tasks.
Ensures deterministic behavior and single source of truth for model parameters.
"""

from typing import Dict, Any

class LLMConfigs:
    # --- [Core Intelligence] ---
    # --- [Core Intelligence] ---
    CODE_VALIDATOR = {"temperature": 0.1, "max_tokens": 1024}
    GOAL_VALIDATOR = {"temperature": 0.1, "max_tokens": 1024}
    AUDITS = {"temperature": 0.0, "max_tokens": 2048}
    
    # --- [Universal Intelligence] ---
    REFLECTION = {"temperature": 0.0, "max_tokens": 512}
    FACT_EXTRACTION = {"temperature": 0.1, "max_tokens": 2048}
    ARCHITECTURAL_PIVOT = {"temperature": 0.1, "max_tokens": 512}
    FOCUS_DETECTION = {"temperature": 0.1, "max_tokens": 256}
    STRATEGIC_AUDITOR = {"temperature": 0.3, "max_tokens": 1024}
    VALUE_ESTIMATION = {"temperature": 0.1, "max_tokens": 512}
    TEST_GENERATION = {"temperature": 0.1, "max_tokens": 4096}
    AUDIT_SYNTHESIS = {"temperature": 0.2, "max_tokens": 2048}
    
    # --- [Strategy & Planning] ---
    DECISION_MAKING = {"temperature": 0.3, "max_tokens": 1536}
    STRATEGIC_REVIEW = {"temperature": 0.3, "max_tokens": 2048}
    STRATEGIC_INSIGHT = {"temperature": 0.3, "max_tokens": 1024}
    FIX_VERIFIER = {"temperature": 0.0, "max_tokens": 10}
    COMMIT_ANALYSIS = {"temperature": 0.1, "max_tokens": 150}

    @classmethod
    def get_config(cls, task_name: str) -> Dict[str, Any]:
        """Retrieve config for a specific task."""
        return getattr(cls, task_name.upper(), {"temperature": 0.2})
