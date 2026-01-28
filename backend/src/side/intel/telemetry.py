
import logging
import re
from pathlib import Path
from typing import List, Dict, Any
from side.storage.simple_db import SimplifiedDatabase

logger = logging.getLogger(__name__)

class ProactiveForensicObserver:
    """
    The 'Always-Watching' Strategic Eye.
    Runs lightweight forensic checks on file content to detect structural drift.
    """
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path).resolve()
        self.db = SimplifiedDatabase()
        self.project_id = self.db.get_project_id(self.project_path)
        
        # High-Speed Forensic Rules (Subset of Pulse)
        self.rules = [
            {
                "id": "arch_layer_violation_ui",
                "pattern": r"import\s+(sqlite3|psycopg2|sqlalchemy|side\.storage\.modules)",
                "scope": "web/app",
                "severity": "CRITICAL",
                "message": "Direct Database access detected in UI layer. Route via ForensicStore."
            },
            {
                "id": "security_leak_env",
                "pattern": r"[\"'](sk-|AIza|ghp_)[\"']",
                "scope": ".",
                "severity": "WARNING",
                "message": "Potential hardcoded API Secret detected."
            }
        ]

    def scan_file(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Scans a single file for structural violations."""
        findings = []
        file_path = Path(file_path).resolve()
        rel_path = str(file_path.relative_to(self.project_path))
        
        for rule in self.rules:
            # Check if file is in scope
            if rule["scope"] != "." and rule["scope"] not in rel_path:
                continue
                
            if re.search(rule["pattern"], content):
                finding = {
                    "type": rule["id"],
                    "severity": rule["severity"],
                    "message": rule["message"],
                    "file_path": rel_path
                }
                findings.append(finding)
                
                # Log to Sovereign Ledger
                self.db.save_telemetry_alert(
                    project_id=self.project_id,
                    alert_type=rule["id"],
                    severity=rule["severity"],
                    message=rule["message"],
                    file_path=rel_path
                )
                logger.warning(f"🚨 [TELEMETRY]: {rule['severity']} violation in {rel_path}: {rule['message']}")
                
        return findings

def run_proactive_scan(project_path: Path, file_path: Path):
    """Entry point for the background observer."""
    try:
        if not file_path.exists():
            return
            
        content = file_path.read_text(errors="ignore")
        observer = ProactiveForensicObserver(project_path)
        observer.scan_file(file_path, content)
    except Exception as e:
        logger.error(f"❌ [TELEMETRY_ERROR]: Scan failed for {file_path}: {e}")
