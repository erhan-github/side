import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import Finding, ForensicsAdapter, Severity

logger = logging.getLogger(__name__)

class SwiftLintAdapter(ForensicsAdapter):
    """
    Adapter for SwiftLint (iOS Security/Quality Scanner).
    Checks for security issues and code quality in Swift code.
    """

    def get_tool_name(self) -> str:
        return "swiftlint"

    def is_available(self) -> bool:
        import shutil
        return shutil.which("swiftlint") is not None

    def get_install_instructions(self) -> str:
        return "brew install swiftlint"

    def install(self) -> bool:
        """Attempt to install swiftlint via brew."""
        try:
            logger.info("📦 [INSTALL]: Installing swiftlint via brew...")
            subprocess.run(["brew", "install", "swiftlint"], check=True)
            return self.is_available()
        except Exception as e:
            logger.error(f"❌ Failed to install swiftlint: {e}")
            return False

    def parse_output(self, output: str) -> List[Finding]:
        """Parses SwiftLint JSON output into normalized Finding objects."""
        if not output.strip():
            return []

        try:
            data = json.loads(output)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse SwiftLint JSON: {e}")
            return []

        findings = []
        for issue in data:
            try:
                # Map SwiftLint severity (Warning, Error)
                sl_severity = issue.get("severity", "Warning")
                severity = Severity.MEDIUM if sl_severity == "Warning" else Severity.HIGH

                # Extract line and file
                file_path = issue.get("file", "")
                line = int(issue.get("line", 1))
                
                # Normalize file path
                try:
                    rel_path = str(Path(file_path).relative_to(self.project_path))
                except ValueError:
                    rel_path = file_path

                finding = Finding(
                    tool="swiftlint",
                    rule_id=issue.get("rule_id", "unknown"),
                    file_path=rel_path,
                    line=line,
                    column=int(issue.get("character", 1)),
                    severity=severity,
                    message=issue.get("reason", ""),
                    code_snippet=None,
                    cwe_id=None,
                    owasp_category=None,
                    confidence="MEDIUM",
                    metadata={
                        "type": issue.get("type")
                    }
                )
                findings.append(finding)
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse SwiftLint issue: {e}")
                continue

        return findings

    async def scan(self, target_paths: Optional[List[Path]] = None) -> List[Finding]:
        """Runs SwiftLint scan on Swift files."""
        if not self.is_available():
            logger.error(f"❌ SwiftLint not available. {self.get_install_instructions()}")
            return []

        # SwiftLint command: lint --reporter json
        cmd = [
            "swiftlint",
            "lint",
            "--reporter", "json",
            "--quiet"
        ]

        if target_paths:
            cmd.extend([str(p) for p in target_paths])
        else:
            cmd.append(str(self.project_path))

        logger.info(f"🔍 [SWIFTLINT] Running scan: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_path
            )

            # SwiftLint returns 1 if issues found (errors), 0 if clean or warnings only.
            # We accept 0 and 1.
            if result.returncode not in [0, 1]:
                logger.error(f"❌ SwiftLint failed with exit code {result.returncode}: {result.stderr}")
                return []

            findings = self.parse_output(result.stdout)
            logger.info(f"✅ [SWIFTLINT] Found {len(findings)} issues")

            return findings

        except Exception as e:
            logger.error(f"❌ SwiftLint execution failed: {e}")
            return []
