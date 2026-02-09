"""
Side Database Layer (SQLModel Edition)
Replaces simple_db.py with standard ORM patterns.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
from sqlmodel import Field, SQLModel, Session, create_engine, select, JSON
from sqlalchemy.engine import Engine

# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------

class Project(SQLModel, table=True):
    """System Identity Profile (replaces 'profile' table)."""
    __tablename__ = "profile" # Map to existing table name
    
    id: str = Field(primary_key=True, default="main") # Usually 'main' or project hash
    name: Optional[str] = None
    company: Optional[str] = None
    domain: Optional[str] = None
    stage: Optional[str] = None
    business_model: Optional[str] = None
    target_raise: Optional[str] = None
    tech_stack: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    tier: str = Field(default="free")
    token_balance: int = Field(default=5000)
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Activity(SQLModel, table=True):
    """Transparency Log (replaces 'activities' table)."""
    __tablename__ = "activities"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: str = Field(index=True)
    tool: str = Field(index=True)
    action: str
    cost_tokens: int = Field(default=0)
    tier: str = Field(default="free")
    payload: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    created_at: str = Field(index=True, default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Finding(SQLModel, table=True):
    """Forensic Findings (replaces 'audits' table)."""
    __tablename__ = "audits"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: str = Field(index=True)
    audit_type: str = Field(index=True)
    severity: str # INFO, WARNING, CRITICAL
    finding: str
    recommendation: Optional[str] = None
    is_fixed: int = Field(default=0)
    run_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# -----------------------------------------------------------------------------
# Engine & Session
# -----------------------------------------------------------------------------

_engine: Optional[Engine] = None

def get_engine(db_path: Optional[str] = None) -> Engine:
    """Get or create singleton engine."""
    global _engine
    if _engine:
        return _engine
    
    if not db_path:
        from ..env import env
        db_path = str(env.get_db_path())
    
    # Check if DB exists to avoid creating empty files in wrong places?
    # SQLModel create_engine is lazy.
    
    sqlite_url = f"sqlite:///{db_path}"
    _engine = create_engine(sqlite_url)
    return _engine

def get_session(db_path: Optional[str] = None) -> Session:
    """Get a new DB session."""
    engine = get_engine(db_path)
    return Session(engine)

def init_db(db_path: Optional[str] = None):
    """Idempotent schema creation (safe to run on existing DB)."""
    engine = get_engine(db_path)
    SQLModel.metadata.create_all(engine)
