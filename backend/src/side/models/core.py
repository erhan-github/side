"""
Core Pydantic models for Sidelith.
Provides type-safe, self-documenting data contracts across the entire mesh.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class Finding(BaseModel):
    """Forensic finding from the intelligence layer."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Unique finding identifier")
    project_id: str = Field(..., description="Project identifier")
    category: str = Field(..., description="Finding category (security, performance, architecture)")
    severity: str = Field(..., description="Severity level (critical, high, medium, low, info)")
    title: str = Field(..., description="Finding title")
    description: str = Field(..., description="Detailed description")
    file_path: Optional[str] = Field(None, description="File path where finding was detected")
    line_number: Optional[int] = Field(None, description="Line number in file")
    code_snippet: Optional[str] = Field(None, description="Relevant code snippet")
    recommendation: Optional[str] = Field(None, description="Recommended fix")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    @classmethod
    def from_row(cls, row: tuple) -> "Finding":
        """Create Finding from SQLite row."""
        return cls(
            id=row[0],
            project_id=row[1],
            category=row[2],
            severity=row[3],
            title=row[4],
            description=row[5],
            file_path=row[6],
            line_number=row[7],
            code_snippet=row[8],
            recommendation=row[9],
            metadata=row[10] if isinstance(row[10], dict) else {},
            created_at=row[11] if len(row) > 11 else datetime.utcnow()
        )


class Pattern(BaseModel):
    """Architectural or generic pattern."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Unique pattern identifier")
    topic: str = Field(..., description="Pattern topic or category")
    content: str = Field(..., description="Pattern content or description")
    context_hash: Optional[str] = Field(None, description="DNA hash for context matching")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    source: Optional[str] = Field(None, description="Pattern source (user, system, inferred)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    @classmethod
    def from_row(cls, row: tuple) -> "Pattern":
        """Create Pattern from SQLite row."""
        return cls(
            id=row[0],
            topic=row[1],
            content=row[2],
            context_hash=row[3] if len(row) > 3 else None,
            confidence=row[4] if len(row) > 4 else 1.0,
            source=row[5] if len(row) > 5 else None,
            metadata=row[6] if len(row) > 6 and isinstance(row[6], dict) else {},
            created_at=row[7] if len(row) > 7 else datetime.utcnow()
        )


class ExecutablePattern(BaseModel):
    """Tool sequence pattern."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Unique pattern identifier")
    project_id: str = Field(default="default", description="Project identifier")
    intent: str = Field(..., description="User intent mapped to this sequence")
    tool_sequence: List[Dict[str, Any]] = Field(..., description="List of tools and arguments")
    keywords: List[str] = Field(default_factory=list, description="Keywords for FTS discovery")
    success_count: int = Field(default=1, description="How many times this exact sequence worked")
    last_used_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def from_row(cls, row: tuple) -> "ExecutablePattern":
        """Create ExecutablePattern from SQLite row."""
        return cls(
            id=row[0],
            project_id=row[1],
            intent=row[2],
            tool_sequence=row[3] if isinstance(row[3], list) else [],
            keywords=row[4] if isinstance(row[4], list) else [],
            success_count=row[5] if len(row) > 5 else 1,
            last_used_at=row[6] if len(row) > 6 else datetime.utcnow(),
            created_at=row[7] if len(row) > 7 else datetime.utcnow()
        )


class AntiPattern(BaseModel):
    """Documented risks and how to avoid them."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Unique pattern identifier")
    issue_type: str = Field(..., description="Type of anti-pattern (complexity, security, etc)")
    context_trigger: str = Field(..., description="Keyword or code structure that triggers this warning")
    risk_description: str = Field(..., description="Why is this a risk?")
    remedy: Optional[Dict[str, Any]] = Field(None, description="Suggested refactor or remedy")
    occurrence_count: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def from_row(cls, row: tuple) -> "AntiPattern":
        """Create AntiPattern from SQLite row."""
        return cls(
            id=row[0],
            issue_type=row[1],
            context_trigger=row[2],
            risk_description=row[3],
            remedy=row[4] if isinstance(row[4], dict) else None,
            occurrence_count=row[5] if len(row) > 5 else 1,
            created_at=row[6] if len(row) > 6 else datetime.utcnow()
        )


class Identity(BaseModel):
    """User identity and subscription profile."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Project identifier (e.g. 'main')")
    name: Optional[str] = Field(None, description="User name")
    company: Optional[str] = Field(None, description="Company name")
    domain: Optional[str] = Field(None, description="Business domain")
    stage: Optional[str] = Field(None, description="Startup stage")
    business_model: Optional[str] = Field(None, description="Business model")
    target_raise: Optional[str] = Field(None, description="Target raise amount")
    tech_stack: Dict[str, Any] = Field(default_factory=dict, description="Technical stack details")
    tier: str = Field(default="hobby", description="Subscription tier (hobby, pro, elite)")
    token_balance: int = Field(default=500, description="Remaining SU balance")
    tokens_monthly: int = Field(default=500, description="Monthly SU limit")
    tokens_used: int = Field(default=0, description="Total SUs used this cycle")
    premium_requests: int = Field(default=0, description="Premium requests used")
    premium_limit: int = Field(default=0, description="Premium request limit")
    access_token: Optional[str] = Field(None, description="Sovereign access token (sk-...)")
    email: Optional[str] = Field(None, description="User email")
    design_pattern: str = Field(default="declarative", description="Preferred design pattern")
    is_airgapped: bool = Field(default=False, description="Air-gapped mode enabled")
    cycle_start: Optional[datetime] = Field(None, description="Billing cycle start")
    cycle_end: Optional[datetime] = Field(None, description="Billing cycle end")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_row(cls, row: dict | tuple) -> "Identity":
        """Create Identity from SQLite row."""
        if isinstance(row, tuple):
            # This would need mapping indexes if we used fetchall() without row_factory
            # But IdentityStore uses dict-like access usually.
            # However, for core models, we should be robust.
             return cls(**dict(zip(cls.model_fields.keys(), row))) # Dangerous if order differs
        
        # Row as dict (assuming keys match field names or aliases)
        data = dict(row)
        # Handle JSON fields
        if isinstance(data.get("tech_stack"), str):
            import json
            data["tech_stack"] = json.loads(data["tech_stack"])
        if isinstance(data.get("metadata"), str):
            import json
            data["metadata"] = json.loads(data["metadata"])
            
        return cls(**data)


class StrategicDecision(BaseModel):
    """Strategic decision or mandate."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Unique decision identifier")
    project_id: str = Field(..., description="Project identifier")
    category: str = Field(..., description="Decision category (mandate, rejection, learning)")
    question: str = Field(..., description="Original question or context")
    answer: str = Field(..., description="Decision or answer")
    reasoning: Optional[str] = Field(None, description="Reasoning behind decision")
    confidence: float = Field(default=5.0, description="Confidence score (1-10)")
    plan_id: Optional[str] = Field(None, description="Associated plan identifier")
    merkle_hash: Optional[str] = Field(None, description="Merkle hash for chain integrity")
    parent_hash: Optional[str] = Field(None, description="Hash of the previous decision")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    @classmethod
    def from_row(cls, row: tuple) -> "StrategicDecision":
        """Create StrategicDecision from SQLite row."""
        return cls(
            id=row[0],
            project_id=row[1],
            question=row[2],
            answer=row[3],
            reasoning=row[4],
            category=row[5],
            plan_id=row[6],
            confidence=float(row[7]) if row[7] is not None else 5.0,
            merkle_hash=row[8],
            parent_hash=row[9],
            created_at=row[10] if len(row) > 10 else datetime.utcnow()
        )


class Rejection(BaseModel):
    """Pattern rejection or anti-pattern."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Unique rejection identifier")
    project_id: str = Field(..., description="Project identifier")
    instruction_hash: Optional[str] = Field(None, description="Hash of the user instruction")
    file_path: str = Field(..., description="File path where rejection occurred")
    rejection_reason: str = Field(..., description="Reason for rejection")
    diff_signature: Optional[str] = Field(None, description="Signature of the rejected diff")
    signal_hash: Optional[int] = Field(None, description="Sparse semantic hash")
    is_pinned: bool = Field(default=False, description="Whether to prevent neural decay")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    @classmethod
    def from_row(cls, row: tuple) -> "Rejection":
        """Create Rejection from SQLite row."""
        return cls(
            id=row[0],
            project_id=row[1],
            instruction_hash=row[2],
            file_path=row[3],
            rejection_reason=row[4],
            diff_signature=row[5],
            signal_hash=row[6],
            created_at=row[7] if len(row) > 7 else datetime.utcnow(),
            is_pinned=bool(row[8]) if len(row) > 8 else False
        )


class Activity(BaseModel):
    """A single unit of work or system event."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = Field(None, description="Auto-incremented ID")
    project_id: str = Field(..., description="Project identifier")
    tool: str = Field(..., description="Tool that performed the action")
    action: str = Field(..., description="Action performed")
    cost_tokens: int = Field(default=0, description="Cost in Structural Units (SUs)")
    tier: str = Field(default="free", description="Subscription tier at time of action")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Activity payload (usually JSON)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    @classmethod
    def from_row(cls, row: tuple) -> "Activity":
        """Create Activity from SQLite row."""
        return cls(
            id=row[0] if len(row) > 0 else None,
            project_id=row[1] if len(row) > 1 else "default",
            tool=row[2] if len(row) > 2 else "",
            action=row[3] if len(row) > 3 else "",
            cost_tokens=row[4] if len(row) > 4 else 0,
            tier=row[5] if len(row) > 5 else "free",
            payload=row[6] if len(row) > 6 and isinstance(row[6], dict) else {},
            created_at=row[7] if len(row) > 7 else datetime.utcnow()
        )


class HardwareStats(BaseModel):
    """Hardware snapshots from Silicon Pulse."""
    
    temp: float = Field(default=0.0, description="CPU temperature in Celsius")
    cpu_total: float = Field(default=0.0, description="CPU utilization percentage")
    load_avg: float = Field(default=0.0, description="1-minute load average")
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp())


class OperationalSetting(BaseModel):
    """Key-Value operational setting."""
    
    key: str = Field(..., description="Unique setting key")
    value: str = Field(..., description="Setting value (usually JSON string)")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_row(cls, row: tuple) -> "OperationalSetting":
        """Create OperationalSetting from SQLite row."""
        return cls(
            key=row[0],
            value=row[1],
            updated_at=row[2] if len(row) > 2 else datetime.utcnow()
        )


class SignalReport(BaseModel):
    """Deep forensic report from Signal Auditor."""
    
    zsh_history: Dict[str, Any] = Field(..., description="Zsh history reachability and metadata")
    os_log: Dict[str, Any] = Field(..., description="OS log reachability")
    clipboard: Dict[str, Any] = Field(..., description="Clipboard access and entropy")
    lsof_side: Dict[str, Any] = Field(..., description="Internal FD health")
    disk_io: Dict[str, Any] = Field(..., description="Disk IO stats")
    created_at: datetime = Field(default_factory=datetime.utcnow)
