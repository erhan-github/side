"""
Testing Probe - Comprehensive testing audit.

Forensic-level testing checks covering:
- Test coverage
- Test organization
- CI integration
"""

import re
from pathlib import Path
from typing import List
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier


class TestingProbe:
    """Forensic-level testing audit probe."""
    
    id = "forensic.testing"
    name = "Testing Audit"
    tier = Tier.FAST
    dimension = "Testing"
    
    def run(self, context: ProbeContext) -> List[AuditResult]:
        return [
            self._check_test_files_exist(context),
            self._check_pytest_config(context),
            self._check_test_coverage(context),
            self._check_fixtures(context),
        ]
    
    def _check_test_files_exist(self, context: ProbeContext) -> AuditResult:
        """Check for test files."""
        test_files = [f for f in context.files if 'test' in f.lower() and f.endswith('.py')]
        
        return AuditResult(
            check_id="TEST-001",
            check_name="Test Files Exist",
            dimension=self.dimension,
            status=AuditStatus.PASS if test_files else AuditStatus.FAIL,
            severity=Severity.HIGH,
            notes=f"Found {len(test_files)} test files",
            recommendation="Create tests/ directory with test files"
        )
    
    def _check_pytest_config(self, context: ProbeContext) -> AuditResult:
        """Check for pytest configuration."""
        config_files = ['pytest.ini', 'pyproject.toml', 'setup.cfg', 'conftest.py']
        has_config = any(Path(context.project_root) / cf for cf in config_files if (Path(context.project_root) / cf).exists())
        
        return AuditResult(
            check_id="TEST-002",
            check_name="Pytest Configuration",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_config else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Add pytest.ini or [tool.pytest] to pyproject.toml"
        )
    
    def _check_test_coverage(self, context: ProbeContext) -> AuditResult:
        """Check for coverage configuration."""
        coverage_patterns = ['pytest-cov', 'coverage', '.coveragerc']
        has_coverage = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(cp in content for cp in coverage_patterns):
                    has_coverage = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="TEST-003",
            check_name="Test Coverage Setup",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_coverage else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Add pytest-cov for coverage reporting"
        )
    
    def _check_fixtures(self, context: ProbeContext) -> AuditResult:
        """Check for test fixtures."""
        has_fixtures = False
        
        for file_path in context.files:
            if 'conftest.py' in file_path or 'fixture' in file_path.lower():
                has_fixtures = True
                break
        
        return AuditResult(
            check_id="TEST-004",
            check_name="Test Fixtures",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_fixtures else AuditStatus.INFO,
            severity=Severity.LOW,
            recommendation="Add conftest.py with shared fixtures"
        )
