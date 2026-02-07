"""
Semgrep Adapter - Primary security scanning engine.

Semgrep is our universal detection tool supporting all languages.
"""

import json
import logging
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base import ForensicsAdapter, Finding, Severity

logger = logging.getLogger(__name__)


class SemgrepAdapter(ForensicsAdapter):
    """
    Adapter for Semgrep static analysis tool.
    
    Semgrep is our primary engine because:
    - Supports all major languages
    - Rich rule registry (OWASP, Security, etc.)
    - Fast and accurate
    - Industry standard
    """
    
    SEVERITY_MAP = {
        "ERROR": Severity.HIGH,
        "WARNING": Severity.MEDIUM,
        "INFO": Severity.LOW,
    }
    
    def get_tool_name(self) -> str:
        return "semgrep"
    
    def is_available(self) -> bool:
        """Check if semgrep CLI is installed."""
        return shutil.which("semgrep") is not None
    
    def get_install_instructions(self) -> str:
        return "Install Semgrep: pip install semgrep"

    def install(self) -> bool:
        """Attempt to install semgrep via pip."""
        try:
            logger.info("📦 [INSTALL]: Installing semgrep via pip...")
            subprocess.run(["pip", "install", "semgrep"], check=True)
            return self.is_available()
        except Exception as e:
            logger.error(f"❌ Failed to install semgrep: {e}")
            return False
    
    async def scan(self, target_paths: Optional[List[Path]] = None) -> List[Finding]:
        """
        Run Semgrep scan on the project.
        
        Args:
            target_paths: Specific paths to scan (defaults to project root)
        
        Returns:
            List of normalized Finding objects
        """
        if not self.is_available():
            logger.error(f"❌ Semgrep not available. {self.get_install_instructions()}")
            return []
        
        # Build command
        cmd = [
            "semgrep",
            "--config", "auto",  # Use Semgrep Registry (OWASP, security, etc.)
            "--json",            # JSON output for parsing
            "--quiet",           # Suppress progress output
            "--exclude", "node_modules",
            "--exclude", "venv",
            "--exclude", ".venv",
            "--exclude", "dist",
            "--exclude", "build",
            "--exclude", "target",
            "--exclude", ".git",
        ]
        
        # Add target paths
        if target_paths:
            cmd.extend([str(p) for p in target_paths])
        else:
            cmd.append(str(self.project_path))
        
        logger.info(f"🔍 [SEMGREP] Running scan: {' '.join(cmd)}")
        
        try:
            # Execute Semgrep
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=self.project_path
            )
            
            # Semgrep returns exit code 1 if findings exist, which is normal
            if result.returncode not in [0, 1]:
                logger.error(f"❌ Semgrep failed: {result.stderr}")
                return []
            
            # Parse JSON output
            findings = self.parse_output(result.stdout)
            logger.info(f"✅ [SEMGREP] Found {len(findings)} issues")
            
            return findings
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Semgrep scan timed out after 5 minutes")
            return []
        except Exception as e:
            logger.error(f"❌ Semgrep execution failed: {e}")
            return []
    
    def parse_output(self, raw_output: str) -> List[Finding]:
        """
        Parse Semgrep JSON output into Finding objects.
        
        Semgrep JSON structure:
        {
            "results": [
                {
                    "check_id": "python.lang.security.audit.exec-used",
                    "path": "app.py",
                    "start": {"line": 42, "col": 5},
                    "end": {"line": 42, "col": 15},
                    "extra": {
                        "message": "Detected use of exec()",
                        "severity": "WARNING",
                        "metadata": {...}
                    }
                }
            ]
        }
        """
        try:
            data = json.loads(raw_output)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Semgrep JSON: {e}")
            return []
        
        findings = []
        
        for result in data.get("results", []):
            try:
                # Extract core fields
                rule_id = result.get("check_id", "unknown")
                file_path = result.get("path", "")
                
                # Line/column info
                start = result.get("start", {})
                line = start.get("line", 0)
                column = start.get("col")
                
                # Severity and message from 'extra'
                extra = result.get("extra", {})
                severity_str = extra.get("severity", "INFO")
                message = extra.get("message", "No description")
                
                # Metadata
                metadata = extra.get("metadata", {})
                cwe = metadata.get("cwe", [])
                cwe_id = f"CWE-{cwe[0]}" if cwe else None
                owasp = metadata.get("owasp", [])
                owasp_category = owasp[0] if owasp else None
                confidence = metadata.get("confidence", "MEDIUM").upper()
                
                # Code snippet (if available)
                code_snippet = result.get("extra", {}).get("lines")
                
                # Normalize severity
                severity = self.SEVERITY_MAP.get(severity_str, Severity.INFO)
                
                # Create finding
                finding = Finding(
                    tool="semgrep",
                    rule_id=rule_id,
                    file_path=file_path,
                    line=line,
                    column=column,
                    severity=severity,
                    message=message,
                    code_snippet=code_snippet,
                    cwe_id=cwe_id,
                    owasp_category=owasp_category,
                    confidence=confidence,
                    metadata=metadata
                )
                
                findings.append(finding)
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse Semgrep result: {e}")
                continue
        
        return findings
