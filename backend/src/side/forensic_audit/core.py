"""
Core audit types and enums.

Forensic-level structured types for all audit results.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime


class AuditStatus(Enum):
    """Audit check status."""
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"
    ERROR = "error"
    INFO = "info"


class Severity(Enum):
    """Finding severity levels."""
    CRITICAL = "critical"  # Must fix before production
    HIGH = "high"          # Should fix soon
    MEDIUM = "medium"      # Fix when convenient
    LOW = "low"            # Nice to have
    INFO = "info"          # Informational only


class Tier(Enum):
    """Probe execution tier."""
    FAST = "fast"   # Regex, static analysis (<1s)
    DEEP = "deep"   # LLM-based, comprehensive (>1s)


class AuditFixRisk(Enum):
    """Risk level of applying a fix."""
    SAFE = "safe"       # Deterministic, safe to auto-fix
    REVIEW = "review"   # Logic change, requires user review
    MANUAL = "manual"   # Complex, manual refactor needed
    NONE = "none"       # No fix available/needed


@dataclass
class AuditEvidence:
    """Evidence supporting an audit finding."""
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    context: Optional[str] = None
    suggested_fix: Optional[str] = None


@dataclass
class AuditResult:
    """
    Single audit check result.
    
    Forensic-level structured output for each check.
    """
    check_id: str
    check_name: str
    dimension: str
    status: AuditStatus
    severity: Severity
    evidence: List[AuditEvidence] = field(default_factory=list)
    notes: Optional[str] = None
    confidence: float = 1.0
    recommendation: Optional[str] = None
    effort_hours: Optional[int] = None
    fix_risk: AuditFixRisk = AuditFixRisk.MANUAL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'check_id': self.check_id,
            'check_name': self.check_name,
            'dimension': self.dimension,
            'status': self.status.value,
            'severity': self.severity.value,
            'evidence': [
                {
                    'description': e.description,
                    'file_path': e.file_path,
                    'line_number': e.line_number,
                    'context': e.context,
                    'suggested_fix': e.suggested_fix
                }
                for e in self.evidence
            ],
            'notes': self.notes,
            'confidence': self.confidence,
            'recommendation': self.recommendation,
            'effort_hours': self.effort_hours,
            'fix_risk': self.fix_risk.value
        }


@dataclass
class ProbeContext:
    """Context passed to all probes."""
    project_root: str
    files: List[str]
    config: Dict[str, Any] = field(default_factory=dict)
    git_enabled: bool = True


@dataclass
class AuditSummary:
    """
    Complete audit summary.
    
    Aggregates all results with scoring.
    """
    total_checks: int
    passed: int
    failed: int
    warnings: int
    skipped: int
    score_percentage: float
    critical_findings: int
    high_findings: int
    results_by_dimension: Dict[str, List[AuditResult]]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def grade(self) -> str:
        """Letter grade based on score."""
        if self.score_percentage >= 90:
            return "A"
        elif self.score_percentage >= 80:
            return "B"
        elif self.score_percentage >= 70:
            return "C"
        elif self.score_percentage >= 60:
            return "D"
        else:
            return "F"
    
    @property
    def grade_label(self) -> str:
        """Human-readable explanation for the grade."""
        labels = {
            "A": "Production Ready",
            "B": "Needs Polish", 
            "C": "MVP Quality",
            "D": "Significant Issues",
            "F": "Critical Fixes Needed"
        }
        return labels.get(self.grade, "Unknown")
