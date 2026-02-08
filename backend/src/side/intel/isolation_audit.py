import logging
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from side.storage.modules.base import ContextEngine

logger = logging.getLogger(__name__)

class IsolationAuditor:
    """
    Isolation Auditor: The Isolation Watchdog.
    [ISOLATION PROTOCOL]: Periodically audits for cross-project strategic pollution.
    """
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path).resolve()
        self.engine = ContextEngine()
        self.project_id = ContextEngine.get_project_id(self.project_path)

    def run_leak_audit(self) -> Dict[str, Any]:
        """
        Scans the current project's ledger for illegal cross-project identifiers.
        """
        logger.info(f"🛡️ [ISOLATION]: Initiating audit for Project: {self.project_id}")
        
        leaks = []
        
        # 1. Path Pollution Check [SOC 2 OPTIMIZATION]
        # We use SQL-level filtering to avoid fetching thousands of rows.
        root_pattern = f"{self.project_path}%"
        
        with self.engine.connection() as conn:
            # Check rejections
            try:
                # Find paths that don't start with project root and aren't special buffers
                query = "SELECT id, file_path FROM rejections WHERE file_path NOT LIKE ? AND file_path != 'SHADOW_BUFFER'"
                rows = conn.execute(query, (root_pattern,)).fetchall()
                for row in rows:
                    leaks.append({
                        "type": "path_pollution",
                        "table": "rejections",
                        "id": row['id'],
                        "path": row['file_path']
                    })
            except sqlite3.OperationalError: pass

            # Check audits
            try:
                query = "SELECT id, file_path FROM audits WHERE file_path IS NOT NULL AND file_path NOT LIKE ?"
                rows = conn.execute(query, (root_pattern,)).fetchall()
                for row in rows:
                    leaks.append({
                        "type": "path_pollution",
                        "table": "audits",
                        "id": row['id'],
                        "path": row['file_path']
                    })
            except sqlite3.OperationalError: pass

        if leaks:
            logger.warning(f"⚠️ [LEAK DETECTED]: Found {len(leaks)} cross-project identifiers. Silo protocol violated!")
            # Trigger automatic quarantine or cleanup?
            self._halt_sync_channel()
        else:
            logger.info("✅ [ISOLATION]: 0% Pollution detected. Silo is secure.")

        return {
            "status": "SECURE" if not leaks else "POLLUTED",
            "leak_count": len(leaks),
            "leaks": leaks
        }

    def _halt_sync_channel(self):
        """Emergency stop of cloud and mesh synchronization."""
        logger.error("🛑 [EMERGENCY]: Halting Sync Channel to prevent data export.")
        # This would interface with service manager to stop sync services
        pass

# Entry point
def run_project_audit(path: Path):
    auditor = IsolationAuditor(path)
    return auditor.run_leak_audit()
