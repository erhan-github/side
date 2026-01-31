"""
Conversation Session Data Models

Palantir-Grade ontology for LLM-User exchange tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
import uuid


class IntentCategory(Enum):
    """Categories of user intent derived from session content."""
    DEBUGGING = "DEBUGGING"
    IMPLEMENTING = "IMPLEMENTING"
    RESEARCHING = "RESEARCHING"
    REFACTORING = "REFACTORING"
    CONFIGURING = "CONFIGURING"
    UNKNOWN = "UNKNOWN"


class ClaimedOutcome(Enum):
    """What the LLM/User claimed as the session outcome."""
    FIXED = "FIXED"
    ONGOING = "ONGOING"
    ABANDONED = "ABANDONED"
    UNKNOWN = "UNKNOWN"


class VerifiedOutcome(Enum):
    """Ground-truth verification of the claimed outcome."""
    CONFIRMED = "CONFIRMED"           # Signals confirm fix worked
    FALSE_POSITIVE = "FALSE_POSITIVE" # LLM claimed fixed, but error recurred
    UNVERIFIABLE = "UNVERIFIABLE"     # No signal data to verify
    NOT_APPLICABLE = "NOT_APPLICABLE" # Session wasn't a fix attempt


class IntentSignalType(Enum):
    """Types of intent signals derived from session analysis."""
    REPETITION = "REPETITION"         # User asked same thing before
    ESCALATION = "ESCALATION"         # Issue getting worse over sessions
    RESOLUTION = "RESOLUTION"         # Verified fix (institutional knowledge)
    ABANDONMENT = "ABANDONMENT"       # User gave up (product feedback)
    FALSE_POSITIVE = "FALSE_POSITIVE" # LLM was wrong


@dataclass
class ConversationSession:
    """A single LLM-User exchange session from Antigravity."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    
    # Temporal Anchors
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Intent Extraction
    raw_intent: str = ""                                    # From .metadata.json summary
    intent_vector: List[str] = field(default_factory=list)  # Keywords for matching
    intent_category: IntentCategory = IntentCategory.UNKNOWN
    
    # Outcome
    claimed_outcome: ClaimedOutcome = ClaimedOutcome.UNKNOWN
    verified_outcome: Optional[VerifiedOutcome] = None
    
    # Linkage
    prior_sessions: List[str] = field(default_factory=list)
    follow_up_sessions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "project_id": self.project_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": self.duration_seconds,
            "raw_intent": self.raw_intent,
            "intent_vector": self.intent_vector,
            "intent_category": self.intent_category.value,
            "claimed_outcome": self.claimed_outcome.value,
            "verified_outcome": self.verified_outcome.value if self.verified_outcome else None,
            "prior_sessions": self.prior_sessions,
            "follow_up_sessions": self.follow_up_sessions,
        }


@dataclass
class IntentSignal:
    """A derived signal from intent analysis."""
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    
    # The Signal
    signal_type: IntentSignalType = IntentSignalType.REPETITION
    confidence: float = 0.0  # 0.0 - 1.0
    
    # Evidence
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    # For Phase 4 injection
    context_snippet: str = ""
    
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "session_id": self.session_id,
            "signal_type": self.signal_type.value,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "context_snippet": self.context_snippet,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SimilarSession:
    """A session similar to the current query."""
    session: ConversationSession
    similarity: float  # 0.0 - 1.0
