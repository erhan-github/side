import logging
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from .base import AuditAdapter, Finding, Severity
from side.tools.audit_scanner import DebtScanner

logger = logging.getLogger(__name__)

class DebtAdapter(AuditAdapter):
    """
    Adapter for the Sidelith custom Debt Scanner.
    Direct integration of structural and lexical code rot detection.
    """
    
    def __init__(self, project_path: Path):
        super().__init__(project_path)
        self.scanner = DebtScanner(project_path)
    
    def is_available(self) -> bool:
        """Sidelith internal tools are always available."""
        return True
    
    def get_tool_name(self) -> str:
        return "sidelith-audits"
    
    async def scan(self, target_paths: Optional[List[Path]] = None) -> List[Finding]:
        """Runs the DebtScanner and normalizes results into Findings."""
        raw_results = self.scanner.scan()
        return self.parse_output(raw_results)
    
    def parse_output(self, raw_results: Dict[str, Any]) -> List[Finding]:
        findings = []
        
        # Map Severity
        sev_map = {
            "critical": Severity.CRITICAL,
            "technical_debt": Severity.MEDIUM,
            "placeholders": Severity.INFO
        }
        
        for category, items in raw_results.items():
            if category == "scanned_at": continue
            
            severity = sev_map.get(category, Severity.INFO)
            
            for item in items:
                findings.append(Finding(
                    tool=self.get_tool_name(),
                    rule_id=item.get("type", "CODE_ROT"),
                    file_path=item.get("file"),
                    line=item.get("line", 0),
                    column=1,
                    severity=severity,
                    message=item.get("snippet", "Audit signal detected."),
                    code_snippet=item.get("snippet"),
                    cwe_id="CWE-1100", # General Code Rot / Technical Debt
                    owasp_category="A04:2021-Insecure Design", # Structural debt mapping
                    confidence="HIGH",
                    explanation=f"Detected structural or lexical signal of incomplete/unprofessional implementation: {item.get('type')}",
                    suggested_fix="Perform immediate remediation or formalize the implementation to meet High-Integrity standards."
                ))
                
        return findings
    
    def install(self) -> bool:
        return True
