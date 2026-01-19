"""
Dependencies Probe - Dependency health audit.
"""

import re
from pathlib import Path
from typing import List
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier


class DependencyProbe:
    """Forensic-level dependency audit probe."""
    
    id = "forensic.dependencies"
    name = "Dependencies Audit"
    tier = Tier.FAST
    dimension = "Dependencies"
    
    def run(self, context: ProbeContext) -> List[AuditResult]:
        return [
            self._check_lock_files(context),
            self._check_pinned_versions(context),
            self._check_dev_dependencies(context),
        ]
    
    def _check_lock_files(self, context: ProbeContext) -> AuditResult:
        """Check for lock files."""
        root = Path(context.project_root)
        lock_files = ['poetry.lock', 'Pipfile.lock', 'package-lock.json', 'yarn.lock', 'requirements.txt']
        found = [lf for lf in lock_files if (root / lf).exists()]
        
        return AuditResult(
            check_id="DEP-001",
            check_name="Lock Files Present",
            dimension=self.dimension,
            status=AuditStatus.PASS if found else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            notes=f"Found: {', '.join(found)}" if found else "No lock files found",
            recommendation="Use poetry.lock or requirements.txt for reproducible builds"
        )
    
    def _check_pinned_versions(self, context: ProbeContext) -> AuditResult:
        """Check for pinned dependency versions."""
        root = Path(context.project_root)
        req_path = root / 'requirements.txt'
        
        if not req_path.exists():
            return AuditResult(
                check_id="DEP-002",
                check_name="Pinned Versions",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.MEDIUM,
                notes="No requirements.txt found"
            )
        
        content = req_path.read_text()
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.startswith('#')]
        pinned = sum(1 for l in lines if '==' in l or '~=' in l)
        total = len(lines)
        
        ratio = pinned / total if total > 0 else 0
        
        return AuditResult(
            check_id="DEP-002",
            check_name="Pinned Versions",
            dimension=self.dimension,
            status=AuditStatus.PASS if ratio >= 0.8 else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            notes=f"{pinned}/{total} dependencies are pinned ({ratio*100:.0f}%)",
            recommendation="Pin versions with == for production stability"
        )
    
    def _check_dev_dependencies(self, context: ProbeContext) -> AuditResult:
        """Check for dev dependency separation."""
        root = Path(context.project_root)
        
        has_separation = (
            (root / 'requirements-dev.txt').exists() or
            (root / 'pyproject.toml').exists()  # Poetry separates by default
        )
        
        return AuditResult(
            check_id="DEP-003",
            check_name="Dev Dependencies Separated",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_separation else AuditStatus.INFO,
            severity=Severity.LOW,
            recommendation="Use pyproject.toml or requirements-dev.txt"
        )
