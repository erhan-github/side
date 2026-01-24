"""
ForensicEngine - The Orchestrator for Code Intelligence

This is the consolidated entry point for all forensic detection.
It leverages the modular TechnicalAnalyzer to perform unified high-performance scans.
"""

import asyncio
import hashlib
from typing import List, Dict
from pathlib import Path
from .technical import TechnicalAnalyzer
from .analyzers.base import Finding

# Global cache for file-content based caching
_FORENSIC_CACHE: Dict[str, List[Finding]] = {}

class ForensicEngine:
    """
    Forensic-tier forensic orchestrator.
    Detects architectural violations, security gaps, and strategic drift.
    
    Features:
    - File-content caching (90% hit rate target)
    - Async parallelism
    - Smart routing
    """

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.analyzer = TechnicalAnalyzer()
        self.findings: List[Finding] = []

    async def scan(self) -> List[Finding]:
        """
        Unified Forensic Scan [Absolute DRY].
        Delegates all logic to ForensicAuditRunner.
        """
        from side.forensic_audit.runner import ForensicAuditRunner
        from side.forensic_audit.core import AuditStatus
        
        # Check cache first
        cache_key = self._get_cache_key()
        if cache_key in _FORENSIC_CACHE:
            self.findings = _FORENSIC_CACHE[cache_key]
            return self.findings

        # Execute Unified Audit
        runner = ForensicAuditRunner(str(self.project_root))
        summary = await runner.run()
        
        # Map AuditResults back to legacy Finding format for backward compatibility
        self.findings = []
        for dim, results in summary.results_by_dimension.items():
            for res in results:
                if res.status in [AuditStatus.FAIL, AuditStatus.WARN]:
                    # Map to legacy format
                    self.findings.append(Finding(
                        type=res.check_name,
                        severity=res.severity.value.upper(),
                        file=res.evidence[0].file_path if res.evidence and res.evidence[0].file_path else "Project",
                        line=res.evidence[0].line_number if res.evidence and hasattr(res.evidence[0], 'line_number') else 0,
                        message=f"{res.notes}. {res.recommendation or ''}",
                        action=res.recommendation or "Review finding",
                        metadata={
                            "check_id": res.check_id, 
                            "dimension": res.dimension,
                            "evidence": [e.description for e in res.evidence] if res.evidence else []
                        }
                    ))
        
        # Store in cache
        _FORENSIC_CACHE[cache_key] = self.findings
        
        return self.findings
    
    def _get_cache_key(self) -> str:
        """Generate cache key by hashing all Python file contents."""
        hasher = hashlib.sha256()
        
        # Hash all Python files in project
        python_files = sorted(self.project_root.rglob('*.py'))
        for file in python_files:
            try:
                # Skip venv, node_modules, .git
                if any(part in file.parts for part in ['venv', 'node_modules', '.git', '__pycache__']):
                    continue
                
                content = file.read_bytes()
                hasher.update(content)
            except Exception:
                # Skip files we can't read
                continue
        
        return hasher.hexdigest()

if __name__ == "__main__":
    import sys
    
    async def main():
        # Simple CLI
        path = sys.argv[1] if len(sys.argv) > 1 else "."
        engine = ForensicEngine(path)
        findings = await engine.scan()
        
        # Summary
        print(f"\n--- Unified Forensic Audit for: {path} ---")
        print(f"Total Findings: {len(findings)}")
        
        # Specific counts
        counts = {}
        for f in findings:
            counts[f.type] = counts.get(f.type, 0) + 1
        
        for f_type, count in counts.items():
            print(f"- {f_type}: {count}")
        
        print("\n--- All Findings ---")
        for f in findings:
            line_str = f":{f.line}" if f.line else ""
            print(f"[{f.type}] ({f.severity}) {f.file}{line_str} - {f.message}")
        
        print("\nAudit Complete.")

    asyncio.run(main())

