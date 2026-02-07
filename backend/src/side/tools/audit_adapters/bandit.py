import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import Finding, ForensicsAdapter, Severity

logger = logging.getLogger(__name__)

class BanditAdapter(ForensicsAdapter):
    """
    Adapter for Bandit (Python Security Scanner).
    Provides deep Python-specific analysis for SQL injection, shell injection, etc.
    """

    def get_tool_name(self) -> str:
        return "bandit"

    def is_available(self) -> bool:
        import shutil
        return shutil.which("bandit") is not None

    def get_install_instructions(self) -> str:
        return "pip install bandit"

    def install(self) -> bool:
        """Attempt to install bandit via pip."""
        try:
            logger.info("📦 [INSTALL]: Installing bandit via pip...")
            subprocess.run(["pip", "install", "bandit"], check=True)
            return self.is_available()
        except Exception as e:
            logger.error(f"❌ Failed to install bandit: {e}")
            return False

    def parse_output(self, output: str) -> List[Finding]:
        """Parses Bandit JSON output into normalized Finding objects."""
        if not output.strip():
            return []

        try:
            data = json.loads(output)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Bandit JSON: {e}")
            return []

        findings = []
        for result in data.get("results", []):
            try:
                # Map Bandit severity (LOW, MEDIUM, HIGH) to normalized Severity
                bandit_severity = result.get("issue_severity", "LOW")
                severity = Severity.LOW
                if bandit_severity == "HIGH":
                    severity = Severity.HIGH
                elif bandit_severity == "MEDIUM":
                    severity = Severity.MEDIUM

                # Map Bandit confidence (LOW, MEDIUM, HIGH)
                confidence = result.get("issue_confidence", "LOW")

                # Extract line and file
                line = int(result.get("line_number", 1))
                file_path = result.get("filename", "")
                
                # Normalize file path (make relative to project root)
                try:
                    rel_path = str(Path(file_path).relative_to(self.project_path))
                except ValueError:
                    rel_path = file_path

                finding = Finding(
                    tool="bandit",
                    rule_id=result.get("test_id", "unknown"),
                    file_path=rel_path,
                    line=line,
                    column=None,  # Bandit doesn't always provide column
                    severity=severity,
                    message=result.get("issue_text", ""),
                    code_snippet=result.get("code", ""),
                    cwe_id=f"CWE-{result.get('issue_cwe', {}).get('id', 'Unknown')}" if result.get('issue_cwe') else None,
                    owasp_category=None, # Bandit doesn't provide OWASP mapping directly
                    confidence=confidence,
                    metadata={
                        "test_name": result.get("test_name"),
                        "more_info": result.get("more_info")
                    }
                )
                findings.append(finding)
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse Bandit result: {e}")
                continue

        return findings

    async def scan(self, target_paths: Optional[List[Path]] = None) -> List[Finding]:
        """Runs Bandit scan on Python files."""
        if not self.is_available():
            logger.error(f"❌ Bandit not available. {self.get_install_instructions()}")
            return []

        # Bandit command: -r (recursive), -f json (output format), -q (quiet)
        cmd = [
            "bandit",
            "-r",
            "-f", "json",
            "-q",
            "-x", "node_modules,venv,.venv,dist,build,target,.git"
        ]

        if target_paths:
            cmd.extend([str(p) for p in target_paths])
        else:
            cmd.append(str(self.project_path))

        logger.info(f"🔍 [BANDIT] Running scan: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300, # 5 minute timeout
                cwd=self.project_path
            )

            # Bandit returns 1 if issues found, 0 if clean. Error if > 1.
            if result.returncode not in [0, 1]:
                logger.error(f"❌ Bandit failed with exit code {result.returncode}: {result.stderr}")
                return []

            findings = self.parse_output(result.stdout)
            logger.info(f"✅ [BANDIT] Found {len(findings)} issues")

            return findings

        except subprocess.TimeoutExpired:
            logger.error("❌ Bandit scan timed out after 5 minutes")
            return []
        except Exception as e:
            logger.error(f"❌ Bandit execution failed: {e}")
            return []
