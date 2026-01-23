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
        """Execute full forensic scan via unified architecture with caching."""
        # Check cache first
        cache_key = self._get_cache_key()
        if cache_key in _FORENSIC_CACHE:
            # Cache hit - instant return
            self.findings = _FORENSIC_CACHE[cache_key]
            return self.findings
        
        # Cache miss - perform scan
        intel = await self.analyzer.analyze(self.project_root)
        self.findings = intel.findings
        
        # --- BRIDGE: Integrate ForensicAuditRunner ---
        # Run the new audit runner and convert results to legacy Finding format
        try:
            from side.forensic_audit.runner import ForensicAuditRunner
            from side.forensic_audit.core import AuditStatus
            from side.forensic_audit.deployment_gotchas import DeploymentGotchaDetector
            
            # 1. Run Standard Audits
            runner = ForensicAuditRunner(str(self.project_root))
            audit_summary = await runner.run() # Async run
            
            mapped_findings = []
            for dim_results in audit_summary.results_by_dimension.values():
                for res in dim_results:
                    if res.status in [AuditStatus.FAIL, AuditStatus.WARN]:
                        # Map AuditResult -> Finding
                        mapped_findings.append(Finding(
                            type=res.check_name,
                            severity=res.severity.value.upper(),
                            file=res.evidence[0].file_path if res.evidence and res.evidence[0].file_path else "Project",
                            line=res.evidence[0].line_number if res.evidence and hasattr(res.evidence[0], 'line_number') else 0,
                            message=f"{res.notes}. {res.recommendation or ''}",
                            action=res.recommendation or "Review finding",
                            metadata={"check_id": res.check_id, "dimension": res.dimension}
                        ))

            # 2. Run Deployment Gotcha Detector
            deploy_detector = DeploymentGotchaDetector(str(self.project_root))
            deploy_issues = deploy_detector.scan()
            
            for issue in deploy_issues:
                mapped_findings.append(Finding(
                    type=issue["type"],
                    severity=issue["severity"],
                    file=issue["file"],
                    line=issue.get("line", 1),
                    message=issue["message"],
                    action=issue["action"],
                    metadata={"reference": issue.get("reference")}
                ))
                        
            # Merge findings
            self.findings.extend(mapped_findings)
            
        except Exception as e:
            # Fallback if runner fails, don't crash the legacy engine
            logging.getLogger(__name__).error(f"Forensic Runner failed: {e}")
        # ---------------------------------------------
        
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

