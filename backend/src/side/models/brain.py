"""
Sovereign Brain Models (Pydantic V2).
The Single Source of Truth for the Fractal Graph.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class BrainStats(BaseModel):
    nodes: int
    total_size_bytes: int = 0
    total_lines: int = 0
    mode: str = "Distributed"

class DNA(BaseModel):
    detected_stack: List[str] = Field(default_factory=list)
    primary_languages: List[str] = Field(default_factory=list)
    signals: List[str] = Field(default_factory=list)

class FractalSemantics(BaseModel):
    classes: List[str] = Field(default_factory=list)
    functions: List[str] = Field(default_factory=list)
    signals: List[str] = Field(default_factory=list)

class FractalNode(BaseModel):
    """
    A single file or directory in the Fractal Index.
    """
    path: str
    type: str # "file" or "dir"
    name: str
    size: int
    lines: int
    digest: str # SHA-256
    semantics: Optional[FractalSemantics] = None
    
class IntentSnapshot(BaseModel):
    objectives: List[Dict[str, Any]] = Field(default_factory=list)
    directives: List[Dict[str, Any]] = Field(default_factory=list)
    intel_signals: List[Dict[str, Any]] = Field(default_factory=list)
    latest_destination: str = "Unknown"

class ContextSnapshot(BaseModel):
    """
    The Serialized State of the Context Engine at a specific point in time.
    Replaces `sovereign.schema.json`.
    """
    version: str = "3.1.0"
    last_scan: datetime = Field(default_factory=datetime.now)
    dna: DNA = Field(default_factory=DNA)
    stats: BrainStats
    
    # The Intent Layer
    intent: IntentSnapshot = Field(default_factory=IntentSnapshot)
    
    # The Fractal Layer (Raw Distributed Index)
    fractal_root: Dict[str, Any] = Field(default_factory=dict)
    
    # Context
    history_fragments: List[Dict[str, Any]] = Field(default_factory=list)
    strategic_timeline: List[Dict[str, Any]] = Field(default_factory=list)
