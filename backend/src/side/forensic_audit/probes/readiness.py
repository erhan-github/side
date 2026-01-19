"""
Readiness Probe - Product completeness and mock detection.

Forensic-level checks for production readiness:
- Mock data detection (stubbed responses)
- Demo component detection
- Placeholder content (Lorem Ipsum)
- Incomplete implementation markers (TODOs)
"""

import re
from pathlib import Path
from typing import List
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier, AuditFixRisk


class ReadinessProbe:
    """Forensic-level production readiness probe."""
    
    id = "forensic.readiness"
    name = "Product Readiness"
    tier = Tier.FAST
    dimension = "Product Readiness"
    
    def run(self, context: ProbeContext) -> List[AuditResult]:
        return [
            self._check_mock_data(context),
            self._check_placeholders(context),
            self._check_incomplete_features(context),
        ]
    
    def _check_mock_data(self, context: ProbeContext) -> AuditResult:
        """Check for mock/dummy data usage."""
        evidence = []
        
        # Patterns for mock data variables and filenames
        var_patterns = [
            (r'(mock|dummy|stub|fake)[A-Z][a-zA-Z0-9]*\s*=', "Mock data variable"),
            (r'(users|items|products)\s*=\s*\[.*\{.*name.*:.*(John|Jane|Test).*\}', "Hardcoded list of dummy items"),
        ]
        
        file_patterns = [
            (r'mock', "Mock file"),
            (r'dummy', "Dummy file"),
            (r'stub', "Stub file"),
        ]
        
        for file_path in context.files:
            # Check filename
            path_obj = Path(file_path)
            fname = path_obj.name.lower()
            
            # Skip test files, they are supposed to have mocks
            if 'test' in fname or 'spec' in fname:
                continue

            # Skip self (this file defines the patterns)
            if 'readiness.py' in str(path_obj):
                continue

            for pattern, desc in file_patterns:
                if pattern in fname:
                    evidence.append(AuditEvidence(
                        description=f"{desc} detected (Filename)",
                        file_path=file_path,
                        suggested_fix="Replace with real data integration"
                    ))
            
            # Check content
            if path_obj.suffix not in ['.ts', '.tsx', '.js', '.jsx', '.py']:
                continue
                
            try:
                content = path_obj.read_text(errors='ignore')
                for line_idx, line in enumerate(content.splitlines(), 1):
                    for pattern, desc in var_patterns:
                        if re.search(pattern, line):
                            evidence.append(AuditEvidence(
                                description=f"{desc} detected (Code)",
                                file_path=file_path,
                                line_number=line_idx,
                                context=line.strip()[:80],
                                suggested_fix="Connect to real API/Database"
                            ))
            except Exception:
                continue
                
        return AuditResult(
            check_id="RDY-001",
            check_name="Mock Data Usage",
            dimension=self.dimension,
            status=AuditStatus.WARN if evidence else AuditStatus.PASS,
            severity=Severity.MEDIUM,
            evidence=evidence[:10],
            notes=f"Found {len(evidence)} mock/stub artifacts",
            recommendation="Replace mocks with real data integration before launch"
        )

    def _check_placeholders(self, context: ProbeContext) -> AuditResult:
        """Check for placeholder text like Lorem Ipsum."""
        evidence = []
        patterns = [
            (r'lorem\s+ipsum', "Lorem Ipsum text"),
            (r'foo\s+bar', "Foo Bar placeholder"),
            (r'TODO\s*:\s*replace', "Replace-me marker"),
            (r'\[\s*INSERT\s+.*\]', "[INSERT ...] placeholder"),
        ]
        
        for file_path in context.files:
            path_obj = Path(file_path)
            if path_obj.suffix not in ['.html', '.tsx', '.jsx', '.vue', '.md']:
                continue

            # Skip self (this file defines the patterns)
            if 'readiness.py' in str(path_obj):
                continue
            
            try:
                content = path_obj.read_text(errors='ignore')
                for line_idx, line in enumerate(content.splitlines(), 1):
                    for pattern, desc in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            evidence.append(AuditEvidence(
                                description=f"Placeholder content: {desc}",
                                file_path=file_path,
                                line_number=line_idx,
                                context=line.strip()[:80],
                                suggested_fix="Add real copy/content"
                            ))
            except Exception:
                continue

        return AuditResult(
            check_id="RDY-002",
            check_name="Placeholder Content",
            dimension=self.dimension,
            status=AuditStatus.INFO if evidence else AuditStatus.PASS,
            severity=Severity.LOW,
            evidence=evidence[:10],
            notes=f"Found {len(evidence)} placeholders",
            recommendation="Update UI with final copy"
        )

    def _check_incomplete_features(self, context: ProbeContext) -> AuditResult:
        """Check for explicit incomplete feature markers."""
        evidence = []
        patterns = [
            (r'TODO\s*:\s*Implement', "Unimplemented feature"),
            (r'TODO\s*:\s*Auth', "Pending Authentication logic"),
            (r'TODO\s*:\s*Payment', "Pending Payment logic"),
            (r'NotImplementedError', "NotImplementedError raised"),
        ]
        
        for file_path in context.files:
            if not file_path.endswith(('.py', '.ts', '.tsx', '.js')):
                continue

            # Skip self (this file defines the patterns)
            if 'readiness.py' in file_path:
                continue
            
            try:
                content = Path(file_path).read_text(errors='ignore')
                for line_idx, line in enumerate(content.splitlines(), 1):
                    for pattern, desc in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            evidence.append(AuditEvidence(
                                description=desc,
                                file_path=file_path,
                                line_number=line_idx,
                                context=line.strip()[:80],
                                suggested_fix="Complete the feature implementation"
                            ))
            except Exception:
                continue

        return AuditResult(
            check_id="RDY-003",
            check_name="Feature Completeness",
            dimension=self.dimension,
            status=AuditStatus.WARN if evidence else AuditStatus.PASS,
            severity=Severity.HIGH,
            evidence=evidence[:10],
            notes=f"Found {len(evidence)} incomplete feature markers",
            recommendation="Prioritize implementing these missing core features"
        )
