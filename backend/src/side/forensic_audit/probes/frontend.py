"""
Frontend Probe - Enterprise frontend audit.

Forensic-level frontend checks covering:
- Bundle size
- Performance patterns
- Security headers in frontend
"""

from pathlib import Path
from typing import List
import re
import json
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier


class FrontendProbe:
    """Forensic-level frontend audit probe."""
    
    id = "forensic.frontend"
    name = "Frontend Audit"
    tier = Tier.FAST
    dimension = "Frontend"
    
    def run(self, context: ProbeContext) -> List[AuditResult]:
        return [
            self._check_bundle_size(context),
            self._check_code_splitting(context),
            self._check_react_patterns(context),
            self._check_deps_audit(context),
        ]
    
    def _check_bundle_size(self, context: ProbeContext) -> AuditResult:
        """Check for bundle size configuration."""
        root = Path(context.project_root)
        package_json = root / "package.json"
        
        if not package_json.exists():
            return AuditResult(
                check_id="FRONT-001",
                check_name="Bundle Size Limits",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.MEDIUM,
                notes="No package.json found (not a JS project)"
            )
        
        # Check for bundle analyzer or size limit tools
        content = package_json.read_text()
        size_tools = ['size-limit', 'bundlewatch', 'webpack-bundle-analyzer', 'source-map-explorer']
        has_size_check = any(tool in content for tool in size_tools)
        
        return AuditResult(
            check_id="FRONT-001",
            check_name="Bundle Size Limits",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_size_check else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Add size-limit or bundlewatch to CI"
        )
    
    def _check_code_splitting(self, context: ProbeContext) -> AuditResult:
        """Check for code splitting patterns."""
        patterns = ['React.lazy', 'dynamic import', 'import(', 'loadable', 'Suspense']
        has_splitting = False
        
        for file_path in context.files:
            if not any(file_path.endswith(ext) for ext in ['.js', '.jsx', '.ts', '.tsx']):
                continue
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in patterns):
                    has_splitting = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="FRONT-002",
            check_name="Code Splitting",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_splitting else AuditStatus.INFO,
            severity=Severity.LOW,
            recommendation="Use React.lazy or dynamic imports for large components"
        )
    
    def _check_react_patterns(self, context: ProbeContext) -> AuditResult:
        """Check for React performance patterns."""
        evidence = []
        
        for file_path in context.files:
            if not any(file_path.endswith(ext) for ext in ['.jsx', '.tsx']):
                continue
            try:
                content = Path(file_path).read_text()
                
                # Check for inline function in JSX
                if re.search(r'onClick=\{.*=>', content):
                    evidence.append(AuditEvidence(
                        description="Inline arrow function in JSX (re-creates on every render)",
                        file_path=file_path,
                        suggested_fix="Use useCallback for event handlers"
                    ))
                
                # Check for missing key in map
                if '.map(' in content and 'key=' not in content:
                    evidence.append(AuditEvidence(
                        description="Array map without key prop",
                        file_path=file_path
                    ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="FRONT-003",
            check_name="React Performance Patterns",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.INFO,
            severity=Severity.LOW,
            evidence=evidence[:5],
            recommendation="Use useCallback/useMemo for expensive operations"
        )
    
    def _check_deps_audit(self, context: ProbeContext) -> AuditResult:
        """Check for dependency audit in CI."""
        patterns = ['npm audit', 'yarn audit', 'pnpm audit', 'snyk']
        has_audit = False
        
        # Check CI files
        ci_paths = ['.github/workflows', '.gitlab-ci.yml']
        root = Path(context.project_root)
        
        for ci_path in ci_paths:
            path = root / ci_path
            if path.exists():
                if path.is_dir():
                    for f in path.glob('*.yml'):
                        if any(p in f.read_text() for p in patterns):
                            has_audit = True
                            break
                else:
                    if any(p in path.read_text() for p in patterns):
                        has_audit = True
        
        return AuditResult(
            check_id="FRONT-004",
            check_name="Dependency Audit in CI",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_audit else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Add 'npm audit' or Snyk to CI pipeline"
        )
