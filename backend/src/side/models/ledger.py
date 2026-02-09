"""
System Ledger Models (Pydantic V2).
The Single Source of Truth for the Transactional Record.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid
from pydantic import BaseModel, Field

class LedgerEntryType(str, Enum):
    ACTIVITY = "ACTIVITY"
    AUDIT = "AUDIT"
    WORK_CONTEXT = "WORK_CONTEXT"
    OUTCOME = "OUTCOME"

class LedgerEntry(BaseModel):
    """
    A unified entry in the System Ledger.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    entry_type: LedgerEntryType
    
    # Metadata
    tool: Optional[str] = None
    action: Optional[str] = None
    severity: Optional[str] = None # INFO, WARN, ERROR, CRITICAL
    
    # Economics
    cost_tokens: int = 0
    tier: str = "free"
    
    # Content
    payload: Dict[str, Any] = Field(default_factory=dict) # Sealed JSON
    message: Optional[str] = None
    
    # Temporal
    created_at: datetime = Field(default_factory=datetime.now)
    
class ForensicEvent(BaseModel):
    """
    A specific forensic finding or audit log.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    tool: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    severity: str = "INFO"
    score: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    run_at: datetime = Field(default_factory=datetime.now)
