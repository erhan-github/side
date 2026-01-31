import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import Finding, ForensicsAdapter, Severity

logger = logging.getLogger(__name__)

class GosecAdapter(ForensicsAdapter):
    """
    Adapter for Gosec (Go Security Scanner).
    Checks for security issues in Go code.
    """

    def get_tool_name(self) -> str:
        return "gosec"

    def is_available(self) -> bool:
        import shutil
        return shutil.which("gosec") is not None

    def get_install_instructions(self) -> str:
        return "go install github.com/securego/gosec/v2/cmd/gosec@latest"

    def install(self) -> bool:
        """Attempt to install gosec via go install."""
        try:
            logger.info("📦 [INSTALL]: Installing gosec via go install...")
            subprocess.run(["go", "install", "github.com/securego/gosec/v2/cmd/gosec@latest"], check=True)
            return self.is_available()
        except Exception as e:
            logger.error(f"❌ Failed to install gosec: {e}")
            return False

    def parse_output(self, output: str) -> List[Finding]:
        """Parses Gosec JSON output into normalized Finding objects."""
        if not output.strip():
            return []

        try:
            data = json.loads(output)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Gosec JSON: {e}")
            return []

        findings = []
        for issue in data.get("Issues", []):
            try:
                # Map Gosec severity (LOW, MEDIUM, HIGH)
                gosec_severity = issue.get("severity", "LOW")
                severity = Severity.LOW
                if gosec_severity == "HIGH":
                    severity = Severity.HIGH
                elif gosec_severity == "MEDIUM":
                    severity = Severity.MEDIUM

                # Extract line and file
                file_path = issue.get("file", "")
                line = int(issue.get("line", "1"))
                
                # Normalize file path
                try:
                    rel_path = str(Path(file_path).relative_to(self.project_path))
                except ValueError:
                    rel_path = file_path

                finding = Finding(
                    tool="gosec",
                    rule_id=issue.get("rule_id", "unknown"),
                    file_path=rel_path,
                    line=line,
                    column=int(issue.get("column", 1)),
                    severity=severity,
                    message=issue.get("details", ""),
                    code_snippet=issue.get("code", ""),
                    cwe_id=issue.get("cwe", {}).get("ID"),
                    owasp_category=None,
                    confidence=issue.get("confidence"),
                    metadata={
                        "rule_text": issue.get("rule_text")
                    }
                )
                findings.append(finding)
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse Gosec issue: {e}")
                continue

        return findings

    async def scan(self, target_paths: Optional[List[Path]] = None) -> List[Finding]:
        """Runs Gosec scan on Go files."""
        if not self.is_available():
            logger.error(f"❌ Gosec not available. {self.get_install_instructions()}")
            return []

        # Gosec command: -fmt json
        cmd = [
            "gosec",
            "-fmt", "json",
            "-quiet"
        ]

        if target_paths:
            cmd.extend([str(p) for p in target_paths])
        else:
            cmd.append("./...")

        logger.info(f"🔍 [GOSEC] Running scan: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_path
            )

            # Gosec returns 1 if issues found, 0 if clean.
            if result.returncode not in [0, 1]:
                logger.error(f"❌ Gosec failed with exit code {result.returncode}: {result.stderr}")
                return []

            findings = self.parse_output(result.stdout)
            logger.info(f"✅ [GOSEC] Found {len(findings)} issues")

            return findings

        except Exception as e:
            logger.error(f"❌ Gosec execution failed: {e}")
            return []
