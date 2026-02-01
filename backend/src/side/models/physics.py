"""
Sovereign Physics Models (Pydantic V2).
The Single Source of Truth for Invariant Enforcement.
"""
from typing import List, Dict, Optional
from enum import Enum
from pydantic import BaseModel, Field

class PulseStatus(str, Enum):
    SECURE = "SECURE"
    DRIFT = "DRIFT"
    VIOLATION = "VIOLATION"

class PulseResult(BaseModel):
    """
    The outcome of a Sovereign Pulse Check.
    """
    status: PulseStatus
    latency_ms: float
    violations: List[str] = Field(default_factory=list)
    context: Dict = Field(default_factory=dict)

class SiliconVelocity(BaseModel):
    """
    [METRIC]: The speed of value delivery sans friction.
    """
    velocity_score: float  # 0.0 - 100.0
    drift_factor: float    # 0.0 - 1.0 (Higher is worse)
    feature_rate: float    # Features / Day
    bug_rate: float        # Bugs / Day
