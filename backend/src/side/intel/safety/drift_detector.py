"""
Task Drift Detector.

Detects when user activity diverges from the stated intent (Ghost Tasks).
"""

import logging
from typing import List, Dict, Any, Optional
from side.intel.conversation_session import ConversationSession, IntentCategory

logger = logging.getLogger(__name__)

class DriftDetector:
    """
    Analyzes "Physical Activity" vs "Stated Intent".
    """
    
    def check_drift(self, session: ConversationSession, recent_files: List[str]) -> Optional[Dict[str, Any]]:
        """
        Checks if recent file edits match the session intent.
        
        Args:
            session: The active conversation session.
            recent_files: List of file paths modified recently.
            
        Returns:
            Dict with drift details if detected, else None.
        """
        if not recent_files or not session.intent_vector:
            return None
            
        # 1. Simple Keyword Matching (Heuristic)
        # Does the file path contain any intent keywords?
        # e.g. Intent: "Fix auth", Files: ["auth.py", "login.py"] -> Match
        # e.g. Intent: "Fix auth", Files: ["styles.css"] -> Drift?
        
        intent_keywords = set(session.intent_vector)
        matches = 0
        
        for file_path in recent_files:
            file_lower = file_path.lower()
            if any(k in file_lower for k in intent_keywords):
                matches += 1
                
        # 2. Score
        match_ratio = matches / len(recent_files)
        
        # 3. Decision
        # If user touched 5 files and NONE matched keywords, likely Drift.
        if len(recent_files) >= 3 and match_ratio < 0.2:
            return {
                "detected": True,
                "reason": "File activity diverges from intent keywords.",
                "intent": session.raw_intent,
                "activity": recent_files[:3],
                "confidence": 0.8
            }
            
        return None
