"""
Intent Analyzer.

Analyzes conversation sessions for patterns like repetition, escalation, and resolution.
Uses LLM-free algorithms (Jaccard Similarity) for high-speed detection.
"""

import logging
from typing import List, Optional, Dict, Any, Set
from datetime import datetime, timezone

from side.models.intent import (
    IntentCategory,
    ClaimedOutcome,
    VerifiedOutcome,
    ConversationSession,
    IntentSignal,
    IntentSignalType
)
from side.storage.simple_db import SimplifiedDatabase

# Helper for Jaccard results
from dataclasses import dataclass
@dataclass
class SimilarSession:
    session: ConversationSession
    similarity: float

logger = logging.getLogger(__name__)

class IntentAnalyzer:
    """
    Analyzes sessions to extract higher-order intent signals.
    """

    def __init__(self, db: SimplifiedDatabase):
        self.db = db
        self.store = self.db.goal_tracker

    def analyze_session(self, session: ConversationSession) -> List[IntentSignal]:
        """Main analysis pipeline for a session."""
        signals = []
        
        # 1. Repetition Detection
        repetition_signals = self._detect_repetition(session)
        signals.extend(repetition_signals)
        
        # 2. Escalation Detection
        if len(session.intent_vector) > 8 or session.duration_seconds > 600:
             signals.append(IntentSignal(
                 session_id=session.session_id,
                 signal_type=IntentSignalType.ESCALATION,
                 confidence=0.8,
                 evidence={"duration": session.duration_seconds, "complexity": len(session.intent_vector)},
                 context_snippet="⚠️ Session flagged as complex/escalating."
             ))
        # 3. False Positive Detection (Requires Signal Layer integration)
        
        # Persist signals
        for signal in signals:
            self.store.save_signal_dict(signal.to_dict())
            logger.info(f"🧠 [ANALYZER]: Generated {signal.signal_type.value} signal for session {session.session_id[:8]}")
            
        return signals

    def _detect_repetition(self, session: ConversationSession) -> List[IntentSignal]:
        """Detect if this intent has been seen before."""
        signals = []
        if not session.intent_vector:
            return []
            
        # Get recent sessions (last 50)
        recent_sessions = [
            self._dict_to_session(d) 
            for d in self.store.list_sessions(session.project_id, limit=50)
            if d['session_id'] != session.session_id # Exclude self
        ]
        
        similar_sessions = []
        for past_session in recent_sessions:
            score = self._calculate_jaccard_similarity(session.intent_vector, past_session.intent_vector)
            if score > 0.6: # Threshold for "Same Intent"
                similar_sessions.append(SimilarSession(past_session, score))
        
        # Sort by similarity
        similar_sessions.sort(key=lambda x: x.similarity, reverse=True)
        
        for sim in similar_sessions[:3]: # Top 3 only
            # Create Repetition Signal
            signal = IntentSignal(
                session_id=session.session_id,
                signal_type=IntentSignalType.REPETITION,
                confidence=sim.similarity,
                evidence={
                    "prior_session_id": sim.session.session_id,
                    "prior_intent": sim.session.raw_intent,
                    "prior_date": sim.session.started_at.isoformat() if sim.session.started_at else None,
                    "keywords": list(set(session.intent_vector) & set(sim.session.intent_vector))
                },
                context_snippet=f"⚠️ Similar session detected ({sim.session.started_at.date() if sim.session.started_at else 'Unknown'}): '{sim.session.raw_intent}'"
            )
            signals.append(signal)
            
        return signals

    def _calculate_jaccard_similarity(self, vec_a: List[str], vec_b: List[str]) -> float:
        """Calculate Jaccard similarity between two keyword vectors."""
        set_a = set(vec_a)
        set_b = set(vec_b)
        
        if not set_a or not set_b:
            return 0.0
            
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        
        return intersection / union if union > 0 else 0.0

    def _dict_to_session(self, data: Dict[str, Any]) -> ConversationSession:
        """Helper to hydrate session from DB dict."""
        # Clean up timestamp strings to datetime objects
        started = data.get('started_at')
        if isinstance(started, str):
            try: started = datetime.fromisoformat(started)
            except: started = None
            
        ended = data.get('ended_at')
        if isinstance(ended, str):
            try: ended = datetime.fromisoformat(ended)
            except: ended = None

        return ConversationSession(
            session_id=data['session_id'],
            project_id=data['project_id'],
            started_at=started,
            ended_at=ended,
            duration_seconds=data['duration_seconds'],
            raw_intent=data['raw_intent'],
            intent_vector=data['intent_vector'],
            # ... other fields mapped as needed
        )
