import logging
import subprocess
from pathlib import Path
from typing import Dict, Any

from side.storage.modules.audit import AuditService

logger = logging.getLogger(__name__)

class RewindEngine:
    """
    The Time Machine Engine.
    Executes the dangerous operations: Git Reset and DB Rollback.
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
        logger.warning(f"⏪ [REWIND]: Initiating rollback to session {session_id} (Commit: {start_commit})")
        
        # 1. GIT RESET (The Anchor)
        try:
            # Check if clean working tree first? Sidelith policy: Force it?
            # For safety, stash changes if dirty?
            # Strategy: "The Rabbit Hole Rescue" assumes user WANTS to nuke the current state.
            # But let's check safety.
            
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
        # We need to mark all activities *after* the session start as 'rolled_back' or similar.
        # Actually, if we rewind, we are effectively jumping back in time.
        # We should logically 'soft delete' or 'mark invalid' the activities from the abandoned sessions.
        try:
            # Mark activities in this session (and potentially subsequent ones if we tracked sequence) as 'rewound'
            # Simple strategy: Just log the rewind event. The old activities remain as history of "failures".
            # But we might want to hide them from future context injection.
            
            # LOG THE REWIND
            self.audit.log_activity(
                project_id=self.project_path.name,
                tool="rewind_engine",
                action="session_rewind",
                session_id=session_id,
                payload={"target_commit": start_commit}
            )
            
            # Optional: Mark next-session activities as invalid? 
            # For V1, we just reset the code. The semantic context (memory) requires knowing "Current Time".
            # The 'Universal Adapter' will see the new (old) file state and adapt.
            
        except Exception as e:
            logger.error(f"❌ DB Update failed: {e}")
            # Non-fatal to the code reset
        
        return {
            "success": True, 
            "message": f"Rewound to {start_commit}",
            "session_id": session_id
        }
