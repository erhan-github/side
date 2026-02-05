"""
[PHASE 4.1] Shared Types Module
Central definitions for all intelligence data structures.
"""
import time
import uuid
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

# ---------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------

class Severity(Enum):
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"

class EventType(Enum):
    ISSUE_DETECTED = "ISSUE_DETECTED"
    CONTEXT_INJECTED = "CONTEXT_INJECTED"
    FIX_APPLIED = "FIX_APPLIED"
    VERIFICATION_PASSED = "VERIFICATION_PASSED"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    REGRESSION_DETECTED = "REGRESSION_DETECTED"

class Difficulty(Enum):
    LOW = "LOW"       # 1 attempt, small cluster
    MEDIUM = "MEDIUM" # 2-3 attempts, or medium cluster
    HIGH = "HIGH"     # 4+ attempts, or large cluster, or P0 severity

# ---------------------------------------------------------------------
# SIGNAL (Unified Intelligence Signal)
# ---------------------------------------------------------------------

@dataclass
class Signal:
    """A single intelligence signal from any source."""
    source: str              # e.g., "FORENSIC", "LOG_SCAVENGER", "SHADOW_INTENT"
    file_path: str           # The file this signal relates to (if any)
    content: str             # The actual data (error message, code snippet, etc.)
    severity: str            # "CRITICAL", "ERROR", "WARNING", "INFO"
    timestamp: float         # Unix timestamp (ms precision)
    symbols: List[str]       # Mentioned functions/classes ["auth", "Session.user"]
    token_cost: int          # Estimated tokens for this signal
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "source": self.source,
            "file_path": self.file_path,
            "content": self.content,
            "severity": self.severity,
            "timestamp": self.timestamp,
            "symbols": self.symbols,
            "token_cost": self.token_cost
        }

# ---------------------------------------------------------------------
# REASONING NODE (Immutable Audit Trail)
# ---------------------------------------------------------------------

@dataclass
class ReasoningNode:
    """A single node in the reasoning timeline (immutable chain)."""
    event_id: str            # UUID
    event_type: str          # EventType value
    timestamp: float         # Unix timestamp (ms precision)
    payload: Dict[str, Any]  # Event-specific data
    parent_id: Optional[str] = None  # Link to previous node in chain
    signature: str = ""      # Hash for integrity verification

    def __post_init__(self):
        if not self.signature:
            self.signature = self._compute_signature()

    def _compute_signature(self) -> str:
        """Computes integrity signature from event data."""
        data = f"{self.event_id}:{self.parent_id}:{self.event_type}:{self.timestamp}:{str(self.payload)}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]

    def verify(self) -> bool:
        """Verifies the node's integrity."""
        return self.signature == self._compute_signature()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "parent_id": self.parent_id,
            "payload": self.payload,
            "signature": self.signature
        }

# ---------------------------------------------------------------------
# VERIFIED FIX (Cloud-Ready Schema)
# ---------------------------------------------------------------------

@dataclass
class FixMetrics:
    """Multi-dimensional metrics for a verified fix."""
    time_spent_seconds: float = 0.0     # From detection to verification
    fix_attempts: int = 1               # How many attempts to resolve
    persistence_score: float = 0.0      # 0.0-1.0, how long issue persisted
    commonality_index: float = 0.0      # 0.0-1.0, global pattern frequency
    difficulty: str = "MEDIUM"          # Difficulty enum value
    cluster_size: int = 1               # Number of files in blast radius

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time_spent_seconds": self.time_spent_seconds,
            "fix_attempts": self.fix_attempts,
            "persistence_score": self.persistence_score,
            "commonality_index": self.commonality_index,
            "difficulty_rating": self.difficulty,
            "cluster_size": self.cluster_size
        }

@dataclass
class VerifiedFix:
    """A cloud-ready, distilled fix record."""
    fix_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    
    # Timestamps (ISO8601)
    issue_detected_at: str = ""
    fix_applied_at: str = ""
    verification_confirmed_at: str = ""
    
    # Metrics
    metrics: FixMetrics = field(default_factory=FixMetrics)
    
    # Reasoning Chain
    reasoning_chain: List[ReasoningNode] = field(default_factory=list)
    
    # Distilled Insight (LLM-generated summary)
    distilled_insight: str = ""
    
    # Focus Context
    focus_file: str = ""
    focus_cluster: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "$schema": "https://sidelith.com/schemas/verified_fix_v1.json",
            "fix_id": self.fix_id,
            "project_id": self.project_id,
            "timestamps": {
                "issue_detected": self.issue_detected_at,
                "fix_applied": self.fix_applied_at,
                "verification_confirmed": self.verification_confirmed_at
            },
            "metrics": self.metrics.to_dict(),
            "reasoning_chain": [n.to_dict() for n in self.reasoning_chain],
            "distilled_insight": self.distilled_insight,
            "focus_file": self.focus_file,
            "focus_cluster": self.focus_cluster
        }

    def is_cloud_worthy(self) -> bool:
        """Determines if this fix should sync to cloud."""
        return (
            self.metrics.persistence_score > 0.3 or
            self.metrics.commonality_index > 0.5 or
            self.metrics.difficulty in ("MEDIUM", "HIGH") or
            self.metrics.fix_attempts >= 2
        )

# ---------------------------------------------------------------------
# FACTORY FUNCTIONS
# ---------------------------------------------------------------------

def create_signal(
    source: str,
    file_path: str,
    content: str,
    severity: str = "INFO",
    symbols: List[str] = None,
    token_cost: int = None
) -> Signal:
    """Factory function to create a Signal with defaults."""
    if token_cost is None:
        token_cost = len(content) // 4
    return Signal(
        source=source,
        file_path=file_path,
        content=content,
        severity=severity,
        timestamp=time.time(),
        symbols=symbols or [],
        token_cost=token_cost
    )

def create_reasoning_node(
    event_type: str,
    payload: Dict[str, Any],
    parent_id: str = None
) -> ReasoningNode:
    """Factory function to create a ReasoningNode."""
    return ReasoningNode(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        timestamp=time.time(),
        payload=payload,
        parent_id=parent_id
    )
