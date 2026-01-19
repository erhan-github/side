"""
Compliance Probe - Regulatory compliance audit.
"""

from pathlib import Path
from typing import List
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier


class ComplianceProbe:
    """Forensic-level compliance audit probe."""
    
    id = "forensic.compliance"
    name = "Compliance Audit"
    tier = Tier.FAST
    dimension = "Compliance"
    
    def run(self, context: ProbeContext) -> List[AuditResult]:
        return [
            self._check_privacy_policy(context),
            self._check_data_retention(context),
            self._check_security_docs(context),
        ]
    
    def _check_privacy_policy(self, context: ProbeContext) -> AuditResult:
        """Check for privacy documentation."""
        root = Path(context.project_root)
        privacy_files = ['PRIVACY.md', 'privacy-policy.md', 'docs/privacy.md']
        has_privacy = any((root / pf).exists() for pf in privacy_files)
        
        return AuditResult(
            check_id="COMP-001",
            check_name="Privacy Documentation",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_privacy else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Add PRIVACY.md documenting data handling"
        )
    
    def _check_data_retention(self, context: ProbeContext) -> AuditResult:
        """Check for data retention policies."""
        patterns = ['retention', 'auto_cleanup', 'delete_old', 'ttl', 'expire']
        has_retention = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content.lower() for p in patterns):
                    has_retention = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="COMP-002",
            check_name="Data Retention Policy",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_retention else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Implement auto-cleanup for old data"
        )
    
    def _check_security_docs(self, context: ProbeContext) -> AuditResult:
        """Check for security documentation."""
        root = Path(context.project_root)
        security_files = ['SECURITY.md', 'docs/security.md', '.github/SECURITY.md']
        has_security = any((root / sf).exists() for sf in security_files)
        
        return AuditResult(
            check_id="COMP-003",
            check_name="Security Documentation",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_security else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Add SECURITY.md with vulnerability reporting process"
        )
