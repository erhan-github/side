"""
Sovereign Forensic Models.
Capturing the 'Physics' of the codebase (Decisions, Costs, Outcomes).
"""
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class Activity(BaseModel):
    """
    A single unit of work/decision in the Sovereign Mesh.
    Mapped to 'activities' table in SQLite.
    """
    id: Optional[str] = None
    project_id: str
    action: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    cost_tokens: int = 0
    outcome: str = "PENDING"

    class Config:
        from_attributes = True
