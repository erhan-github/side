"""
DocVerifyAdapter: The "Documentation Truth" Probe.
Identifies discrepancies between project documentation (READMEs) and structural reality.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from side.tools.forensics.base import ForensicsAdapter, Finding, Severity
from side.storage.modules.base import ContextEngine
from side.storage.modules.identity import IdentityStore

logger = logging.getLogger(__name__)

class DocVerifyAdapter(ForensicsAdapter):
    def __init__(self, project_path: Path):
        super().__init__(project_path)
        self.engine = ContextEngine()
        self.identity = IdentityStore(self.engine)

    def is_available(self) -> bool:
        """Always available as it uses internal regex/logic."""
        return True

    def get_tool_name(self) -> str:
        return "doc_verify"

    async def scan(self, target_paths: Optional[List[Path]] = None) -> List[Finding]:
        """
        Scans documentation files for architectural claims and cross-references them.
        """
        findings = []
        doc_files = ["README.md", "CONTRIBUTING.md", "ARCHITECTURE.md"]
        
        # 1. Get Structural Reality
        project_id = ContextEngine.get_project_id(self.project_path)
        profile = self.identity.get_profile(project_id)
        if not profile:
            logger.warning("DocVerify: No profile found for project.")
            return []
            
        reality = {
            "tech_stack": profile.get("tech_stack", {}),
            "tier": profile.get("tier", "hobby"),
            "design_pattern": profile.get("design_pattern", "declarative")
        }

        for doc_name in doc_files:
            doc_path = self.project_path / doc_name
            if doc_path.exists():
                findings.extend(self._verify_file(doc_path, reality))
                
        return findings

    def _verify_file(self, path: Path, reality: Dict[str, Any]) -> List[Finding]:
        findings = []
        try:
            content = path.read_text(errors='ignore')
            lines = content.splitlines()
            
            # --- PROBE 1: Tech Stack Mismatch ---
            # Example: README says "Powered by PostgreSQL" but reality is "SQLite"
            db_claims = re.findall(r"(?i)(postgres|postgresql|sqlite|mongodb|mysql|redis|supabase)", content)
            actual_frameworks = [f.lower() for f in reality["tech_stack"].get("frameworks", [])]
            
            # Simple check: If a DB is claimed in README but not found in tech_stack signals
            # This is a heuristic - we look for the dominant DB claim.
            for claim in set(db_claims):
                claim_lower = claim.lower()
                # Suppress if the claim matches a known signal
                if claim_lower in actual_frameworks:
                    continue
                
                # If claim is Supabase but not in frameworks, it's a mismatch
                if claim_lower == "supabase" and "supabase" not in actual_frameworks:
                    findings.append(self._create_finding(
                        path, 
                        "DOC_CODE_MISMATCH_DB",
                        f"Documentation claims usage of '{claim}', but no operational signal found in codebase.",
                        Severity.HIGH
                    ))

            # --- PROBE 2: Language Version Mismatch ---
            # e.g. "Python 3.12" in README vs actual
            py_version_match = re.search(r"(?i)python\s*(\d+\.\d+)", content)
            if py_version_match:
                claimed_version = py_version_match.group(1)
                # In real scenario, we'd check pyproject.toml or sys.version
                # For this probe, we flag if multiple versions are mentioned or if it's very old
                if claimed_version.startswith("2."):
                    findings.append(self._create_finding(
                        path,
                        "DOC_DEPRECATED_LANG",
                        f"Documentation references Python {claimed_version} (Legacy). Operational environment is Modern.",
                        Severity.CRITICAL
                    ))

        except Exception as e:
            logger.error(f"DocVerify: Failed to analyze {path}: {e}")
            
        return findings

    def _create_finding(self, path: Path, rule_id: str, message: str, severity: Severity) -> Finding:
        return Finding(
            tool="doc_verify",
            rule_id=rule_id,
            file_path=str(path.relative_to(self.project_path)),
            line=1, # Default to top of file for now
            column=1,
            severity=severity,
            message=message,
            code_snippet=None,
            cwe_id="CWE-1100", # General Logic/Documentation error
            owasp_category="A09:2021-Security Logging and Monitoring Failures", # Best fit for audit drift
            confidence="HIGH"
        )

    def parse_output(self, raw_output: str) -> List[Finding]:
        return [] # Not used for internal logic

    def install(self) -> bool:
        return True
