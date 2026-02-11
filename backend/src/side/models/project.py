"""
System Project Models (Pydantic V2).
The Single Source of Truth for the Project Index.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ProjectStats(BaseModel):
    nodes: int
    total_size_bytes: int = 0
    total_lines: int = 0
    mode: str = "Distributed"

class DNA(BaseModel):
    detected_stack: List[str] = Field(default_factory=list)
    primary_languages: List[str] = Field(default_factory=list)
    signals: List[str] = Field(default_factory=list)

class CodeSemantics(BaseModel):
    classes: List[str] = Field(default_factory=list)
    functions: List[str] = Field(default_factory=list)
    signals: List[str] = Field(default_factory=list)

class ProjectNode(BaseModel):
    """
    A single file or directory in the Project Index.
    """
    path: str
    type: str # "file" or "dir"
    name: str
    size: int
    lines: int
    digest: str # SHA-256
    semantics: Optional[CodeSemantics] = None
    
class IntentSnapshot(BaseModel):
    objectives: List[Dict[str, Any]] = Field(default_factory=list)
    directives: List[Dict[str, Any]] = Field(default_factory=list)
    intel_signals: List[Dict[str, Any]] = Field(default_factory=list)
    latest_destination: str = "Unknown"

class ContextSnapshot(BaseModel):
    """
    The Serialized State of the Context Engine at a specific point in time.
    Replaces `context.schema.json`.
    """
    version: str = "3.1.0"
    last_scan: datetime = Field(default_factory=datetime.now)
    dna: DNA = Field(default_factory=DNA)
    stats: ProjectStats
    
    # The Intent Layer
    intent: IntentSnapshot = Field(default_factory=IntentSnapshot)
    
    # The Project Layer (Raw Distributed Index)
    project_root: Dict[str, Any] = Field(default_factory=dict)
    
    # Context
    history_fragments: List[Dict[str, Any]] = Field(default_factory=list)
    strategic_timeline: List[Dict[str, Any]] = Field(default_factory=list)
