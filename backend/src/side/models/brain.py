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
    
class SovereignGraph(BaseModel):
    """
    The Indexed Brain of a Sidelith-managed Project.
    Replaces `sovereign.schema.json`.
    """
    version: str = "3.1.0"
    last_scan: datetime = Field(default_factory=datetime.now)
    dna: DNA = Field(default_factory=DNA)
    stats: BrainStats
    nodes: List[FractalNode] = Field(default_factory=list)
    
    # Context
    history_fragments: List[Dict[str, Any]] = Field(default_factory=list)
    strategic_timeline: List[Dict[str, Any]] = Field(default_factory=list)
