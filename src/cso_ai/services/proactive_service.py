"""
Proactive IAnonymous Telemetry Service for sideMCP.deMCP.

Monitors the codebase for technical signals (HACK, TODO) that might indicate
strategic friction or vision drift.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any

from cso_ai.storage.simple_db import SimplifiedDatabase

logger = logging.getLogger(__name__)

class ProactiveService:
    """
    Monitors for 'Strategic Friction' signals in the codebase.
    Checks for TODO/HACK comments and cross-references them with active goals.
    """

    def __init__(self, db: SimplifiedDatabase, project_path: Path):
        self.db = db
        self.project_path = project_path

    async def check_for_friction(self) -> List[Dict[str, Any]]:
        """
        Scans for strategic friction and OSS Leverage opportunities.
        """
        # ... logic to scan for TODO/HACK ...
        return []

    def analyze_oss_leverage(self, comment: str) -> str | None:
        """
        [CTO Strategy] Detects if a TODO/HACK can be replaced by a reputable OSS alternative.
        Uses the 80/20 rule: 80% of value for 10% of code.
        """
        OSS_MAP = {
            "notification": "Novu / SuprSend",
            "auth": "Supabase Auth / Clerk / Kinde",
            "billing": "Stripe / Lago / Kill Bill",
            "audit": "sideMCP (Self-Referential Mastery)",
            "analytics": "PostHog / Umami",
            "job": "Temporal / BullMQ",
            "search": "Meilisearch / Typesense"
        }
        
        low_comment = comment.lower()
        for key, alt in OSS_MAP.items():
            if key in low_comment and ("build" in low_comment or "implement" in low_comment or "todo" in low_comment):
                return f"💡 **Strategy Shortcut**: Why build '{key}' from scratch? Use **{alt}**. You'll get 80% of the feature set in 1/10th of the time."
        
        return None

    def analyze_vision_drift(self, comment: str, goals: List[Dict[str, Any]]) -> str | None:
        """
        Cross-references a code comment with active $100M goals.
        Returns a warning if there is a potential vision-gap.
        """
        comment_low = comment.lower()
        for goal in goals:
            target = goal.get("title", "").lower()
            if target in comment_low and "hack" in comment_low:
                return f"⚠️ **Vision Drift Detected**: You added a HACK related to active goal '{goal['title']}'. This may introduce technical debt in a high-leverage area."
        return None

    def analyze_dead_end(self, comment: str, decisions: List[Dict[str, Any]]) -> str | None:
        """
        [CTO Vision Anchor] Checks if the user is building a feature previously rejected.
        Prevents wasting months on 'Dead-Ends'.
        """
        comment_low = comment.lower()
        for dec in decisions:
            # We look for decisions where the answer was "No" or "Rejected"
            answer = dec.get("answer", "").lower()
            if any(refusal in answer for refusal in ["no", "rejected", "won't do", "don't build"]):
                target = dec.get("question", "").lower()
                # If the comment contains keywords from the rejected question
                # (This is heuristic; real version would use NLP/Embeddings)
                keywords = [w for w in target.split() if len(w) > 4]
                if any(kw in comment_low for kw in keywords) and ("build" in comment_low or "implement" in comment_low):
                    return f"🚨 **Dead-End Relapse**: You are building something previously rejected in decision: '{dec['question']}'. Reason: {dec['answer']}. Stop building to preserve project velocity."
        return None
