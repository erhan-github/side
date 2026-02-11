import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import Finding, AuditAdapter, Severity

logger = logging.getLogger(__name__)

class ESLintAdapter(AuditAdapter):
    """
    Adapter for ESLint (JavaScript/TypeScript Security Scanner).
    Uses eslint-plugin-security and other security-focused plugins.
    """

    def get_tool_name(self) -> str:
        return "eslint"

    def is_available(self) -> bool:
        import shutil
        return shutil.which("eslint") is not None

    def get_install_instructions(self) -> str:
        return "npm install -g eslint eslint-plugin-security"

    def install(self) -> bool:
        """Attempt to install eslint via npm."""
        try:
            logger.info("📦 [INSTALL]: Installing eslint globally via npm...")
            subprocess.run(["npm", "install", "-g", "eslint", "eslint-plugin-security"], check=True)
            return self.is_available()
        except Exception as e:
            logger.error(f"❌ Failed to install eslint: {e}")
            return False

    def parse_output(self, output: str) -> List[Finding]:
        """Parses ESLint JSON output into normalized Finding objects."""
        if not output.strip():
            return []

        try:
            data = json.loads(output)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse ESLint JSON: {e}")
            return []

        findings = []
        # ESLint returns a list of file results
        for file_result in data:
            file_path = file_result.get("filePath", "")
            
            # Normalize file path
            try:
                rel_path = str(Path(file_path).relative_to(self.project_path))
            except ValueError:
                rel_path = file_path

            for message in file_result.get("messages", []):
                try:
                    # Map ESLint severity (1 = warning, 2 = error)
                    eslint_severity = message.get("severity", 1)
                    severity = Severity.MEDIUM if eslint_severity == 1 else Severity.HIGH
                    
                    # Some rules might be lower severity
                    rule_id = message.get("ruleId", "unknown")
                    if "security" in rule_id or "no-eval" in rule_id:
                        severity = Severity.HIGH

                    finding = Finding(
                        tool="eslint",
                        rule_id=rule_id,
                        file_path=rel_path,
                        line=int(message.get("line", 1)),
                        column=int(message.get("column", 1)),
                        severity=severity,
                        message=message.get("message", ""),
                        code_snippet=None, # ESLint JSON doesn't include snippet by default
                        cwe_id=None, # ESLint doesn't provide CWE IDs directly
                        owasp_category=None,
                        confidence="MEDIUM", # ESLint is generally confident if rule triggers
                        metadata={
                            "nodeType": message.get("nodeType"),
                            "fatal": message.get("fatal", False)
                        }
                    )
                    findings.append(finding)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to parse ESLint message: {e}")
                    continue

        return findings

    async def scan(self, target_paths: Optional[List[Path]] = None) -> List[Finding]:
        """Runs ESLint scan on JS/TS files."""
        if not self.is_available():
            logger.error(f"❌ ESLint not available. {self.get_install_instructions()}")
            return []

        # ESLint command: --format json
        cmd = [
            "eslint",
            "--format", "json",
            "--no-error-on-unmatched-pattern",
            "--ignore-pattern", "node_modules/",
            "--ignore-pattern", "venv/",
            "--ignore-pattern", ".venv/",
            "--ignore-pattern", "dist/",
            "--ignore-pattern", "build/",
            "--ignore-pattern", "target/",
            "--ignore-pattern", ".git/"
        ]

        # Use security plugin if possible (relies on user's .eslintrc)
        # We could also provide a base config via --config
        
        if target_paths:
            cmd.extend([str(p) for p in target_paths])
        else:
            # Default to scanning current dir
            cmd.append(".")

        logger.info(f"🔍 [ESLINT] Running scan: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_path
            )

            # ESLint returns 1 if issues found, 0 if clean.
            # But it can also return > 1 for configuration errors.
            if result.returncode > 1 and not result.stdout:
                logger.error(f"❌ ESLint failed with exit code {result.returncode}: {result.stderr}")
                return []

            findings = self.parse_output(result.stdout)
            logger.info(f"✅ [ESLINT] Found {len(findings)} issues")

            return findings

        except Exception as e:
            logger.error(f"❌ ESLint execution failed: {e}")
            return []
