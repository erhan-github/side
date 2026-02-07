import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import Finding, ForensicsAdapter, Severity

logger = logging.getLogger(__name__)

class DetektAdapter(ForensicsAdapter):
    """
    Adapter for Detekt (Android/Kotlin Security/Quality Scanner).
    Checks for security issues and code quality in Kotlin code.
    """

    def get_tool_name(self) -> str:
        return "detekt"

    def is_available(self) -> bool:
        import shutil
        return shutil.which("detekt") is not None

    def get_install_instructions(self) -> str:
        return "brew install detekt"

    def install(self) -> bool:
        """Attempt to install detekt via brew."""
        try:
            logger.info("📦 [INSTALL]: Installing detekt via brew...")
            subprocess.run(["brew", "install", "detekt"], check=True)
            return self.is_available()
        except Exception as e:
            logger.error(f"❌ Failed to install detekt: {e}")
            return False

    def parse_output(self, output: str) -> List[Finding]:
        """Parses Detekt JSON output into normalized Finding objects."""
        if not output.strip():
            return []

        try:
            data = json.loads(output)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Detekt JSON: {e}")
            return []

        findings = []
        # Detekt JSON output format varies, but usually it's under 'findings' or 'results'
        # If using --report json, it usually looks like this:
        for finding_group in data.get("findings", []):
            for issue in data.get("findings", {}).get(finding_group, []):
                try:
                    # Detekt has various rules, some are security related
                    # We'll map them based on rule name or category if possible
                    severity = Severity.MEDIUM
                    
                    # Extract line and file
                    location = issue.get("location", {})
                    file_path = location.get("file", "")
                    line = int(location.get("line", 1))
                    
                    # Normalize file path
                    try:
                        rel_path = str(Path(file_path).relative_to(self.project_path))
                    except ValueError:
                        rel_path = file_path

                    finding = Finding(
                        tool="detekt",
                        rule_id=issue.get("id", "unknown"),
                        file_path=rel_path,
                        line=line,
                        column=int(location.get("column", 1)),
                        severity=severity,
                        message=issue.get("message", ""),
                        code_snippet=None,
                        cwe_id=None,
                        owasp_category=None,
                        confidence="MEDIUM",
                        metadata={
                            "category": issue.get("category")
                        }
                    )
                    findings.append(finding)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to parse Detekt issue: {e}")
                    continue

        return findings

    async def scan(self, target_paths: Optional[List[Path]] = None) -> List[Finding]:
        """Runs Detekt scan on Kotlin files."""
        if not self.is_available():
            logger.error(f"❌ Detekt not available. {self.get_install_instructions()}")
            return []

        # Detekt command: --report json:<output_file>
        # Note: Detekt often requires a config file or runs on a project.
        # For simplicity, we assume we can run it on the current dir.
        
        output_file = Path("/tmp/detekt_output.json")
        cmd = [
            "detekt",
            "--report", f"json:{output_file}",
            "--input", str(self.project_path)
        ]

        logger.info(f"🔍 [DETEKT] Running scan: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_path
            )

            # Detekt returns non-zero if issues found.
            # We check the output file instead.
            if output_file.exists():
                with open(output_file, "r") as f:
                    findings = self.parse_output(f.read())
                output_file.unlink() # Cleanup
                logger.info(f"✅ [DETEKT] Found {len(findings)} issues")
                return findings
            else:
                logger.warning("⚠️ Detekt did not produce an output file.")
                return []

        except Exception as e:
            logger.error(f"❌ Detekt execution failed: {e}")
            return []
