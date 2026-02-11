import logging
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from side.storage.modules.audit import AuditService

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Manages the lifecycle of a Sidelith "Time Machine" Session.
    Persists the current session ID to `.side/session.json`.
    """

    def __init__(self, project_path: Path, audit_service: AuditService):
        self.project_path = project_path
        self.audit = audit_service
        self.session_file = self.project_path / ".side" / "session.json"
        
        self._current_session_id: Optional[str] = None
        self._load_active_session()

    def _load_active_session(self):
        """Loads the active session from disk."""
        if self.session_file.exists():
            try:
                data = json.loads(self.session_file.read_text())
                if data.get("active", False):
                    self._current_session_id = data.get("id")
            except Exception as e:
                logger.warning(f"Failed to load session file: {e}")

    def _persist_state(self, session_data: Dict[str, Any]):
        """Persists session state to disk."""
        try:
            self.session_file.parent.mkdir(parents=True, exist_ok=True)
            self.session_file.write_text(json.dumps(session_data, indent=2))
        except Exception as e:
            logger.error(f"Failed to persist session state: {e}")

    def get_active_session_id(self) -> Optional[str]:
        return self._current_session_id

    def start_session(self, name: str = "Auto-Session", context: str = "") -> str:
        """Starts a new recording session."""
        if self._current_session_id:
            logger.info("Closing previous session before starting new one.")
            self.end_session()

        session_id = str(uuid.uuid4())
        self._current_session_id = session_id
        
        # 1. Get current Git Hash (The Anchor)
        start_commit = self._get_git_shad()
        
        # 2. Persist State
        state = {
            "id": session_id,
            "name": name,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "start_commit": start_commit,
            "active": True,
            "context_summary": context[:200]
        }
        self._persist_state(state)
        
        # 3. Log Start
        self.audit.log_activity(
            project_id=self.project_path.name, # Using directory name as ID for local dev
            tool="session_manager",
            action="session_start",
            session_id=session_id,
            payload={"name": name, "start_commit": start_commit}
        )
        
        logger.info(f"🔴 [SESSION STARTED]: {name} ({session_id[:8]})")
        return session_id

    def end_session(self) -> str | None:
        """Ends the current session."""
        if not self._current_session_id:
            return None
            
        session_id = self._current_session_id
        
        # 1. Get End Commit
        end_commit = self._get_git_shad()
        
        # 2. Update Persisted State
        state = {
            "id": session_id,
            "end_time": datetime.now(timezone.utc).isoformat(),
            "end_commit": end_commit,
            "active": False
        }
        self._persist_state(state)
        
        # 3. Log End
        self.audit.log_activity(
            project_id=self.project_path.name,
            tool="session_manager",
            action="session_end",
            session_id=session_id,
            payload={"end_commit": end_commit}
        )
        
        self._current_session_id = None
        logger.info(f"⏹️ [SESSION ENDED]: {session_id[:8]}")
        return session_id

    def _get_git_shad(self) -> str:
        try:
            import subprocess
            return subprocess.check_output(
                ["git", "rev-parse", "HEAD"], 
                cwd=self.project_path, 
                text=True
            ).strip()
        except:
            return "0000000"
