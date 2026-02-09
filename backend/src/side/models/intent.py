"""
System Intent Models (Pydantic V2).
The Single Source of Truth for User-LLM Exchange.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid
from pydantic import BaseModel, Field

class IntentCategory(str, Enum):
    DEBUGGING = "DEBUGGING"
    IMPLEMENTING = "IMPLEMENTING"
    RESEARCHING = "RESEARCHING"
    REFACTORING = "REFACTORING"
    CONFIGURING = "CONFIGURING"
    UNKNOWN = "UNKNOWN"

class ClaimedOutcome(str, Enum):
    FIXED = "FIXED"
    ONGOING = "ONGOING"
    ABANDONED = "ABANDONED"
    UNKNOWN = "UNKNOWN"

class VerifiedOutcome(str, Enum):
    CONFIRMED = "CONFIRMED"
    FALSE_POSITIVE = "FALSE_POSITIVE" 
    UNVERIFIABLE = "UNVERIFIABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"

class IntentSignalType(str, Enum):
    REPETITION = "REPETITION"
    ESCALATION = "ESCALATION"
    RESOLUTION = "RESOLUTION"
    ABANDONMENT = "ABANDONMENT"
    FALSE_POSITIVE = "FALSE_POSITIVE"

class ConversationSession(BaseModel):
    """
    A single LLM-User exchange session from Antigravity.
    """
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    
    # Temporal Anchors
    started_at: datetime = Field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Intent Extraction
    raw_intent: str = ""
    intent_vector: List[str] = Field(default_factory=list)
    intent_category: IntentCategory = IntentCategory.UNKNOWN
    
    # Outcome
    claimed_outcome: ClaimedOutcome = ClaimedOutcome.UNKNOWN
    verified_outcome: Optional[VerifiedOutcome] = None
    
    # Linkage
    prior_sessions: List[str] = Field(default_factory=list)
    follow_up_sessions: List[str] = Field(default_factory=list)

class IntentSignal(BaseModel):
    """
    A derived signal from intent analysis.
    """
    signal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    
    # The Signal
    signal_type: IntentSignalType = IntentSignalType.REPETITION
    confidence: float = 0.0  # 0.0 - 1.0
    
    # Evidence
    evidence: Dict[str, Any] = Field(default_factory=dict)
    
    # For Phase 4 injection
    context_snippet: str = ""
    
    created_at: datetime = Field(default_factory=datetime.now)
