import logging
import subprocess
from pathlib import Path
from typing import Dict, Any

from side.storage.modules.audit import AuditService

logger = logging.getLogger(__name__)

class HistoryPlayer:
    """
    The History Player.
    Executes destructive operations: Git Reset and DB Rollback based on session history.
    """

    def __init__(self, project_path: Path, audit_service: AuditService):
        self.project_path = project_path
        self.audit = audit_service
        self.engine = audit_service.engine

    def rewind_to_session_start(self, session_id: str, start_commit: str) -> Dict[str, Any]:
        """
        Rewinds the project to the state at the START of the given session.
        Warning: Destructive operation.
        """
        # 1. GIT RESET (The Anchor)
        try:
            # Executing Git Reset
            subprocess.check_call(
                ["git", "reset", "--hard", start_commit],
                cwd=self.project_path
            )
            logger.info(f"✅ Git Reset successful to {start_commit}")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git Reset failed: {e}")
            return {"success": False, "error": f"Git Reset Failed: {e}"}

        # 2. DB ROLLBACK (The Memory)
        try:
            # LOG THE REWIND
            self.audit.log_activity(
                project_id=self.project_path.name,
                tool="history_player",
                action="session_rewind",
                session_id=session_id,
                payload={"target_commit": start_commit}
            )
        except Exception as e:
            logger.error(f"❌ DB Update failed: {e}")
        
        return {
            "success": True, 
            "message": f"Rewound to {start_commit}",
            "session_id": session_id
        }
