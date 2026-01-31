
import time
import hashlib
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from side.intel.relevance_engine import Signal
from side.storage.modules.forensic import ForensicStore
from side.storage.modules.base import SovereignEngine

logger = logging.getLogger(__name__)

@dataclass
class ActiveIssue:
    """Represents an issue being actively debugged."""
    fingerprint: str       # Hash of focus_cluster + initial_error
    focus_file: str
    focus_cluster: List[str]
    initial_error: str
    initial_signals: List[Signal]
    created_at: float
    fix_attempts: int = 0
    resolved: bool = False

class VerificationDirector:
    """
    [ACE-3] The Verification Loop Director.
    Tracks active issues and confirms resolution after fixes.
    """
    
    def __init__(self, forensic: ForensicStore = None):
        self.forensic = forensic or ForensicStore(SovereignEngine())
        self.active_issues: Dict[str, ActiveIssue] = {}

    def register_issue(
        self,
        focus_file: str,
        focus_cluster: List[str],
        error_signals: List[Signal]
    ) -> str:
        """
        Registers a new active issue for verification tracking.
        
        Returns:
            The issue fingerprint (ID).
        """
        # Create fingerprint from cluster + initial error
        cluster_str = ":".join(sorted(focus_cluster))
        error_str = ":".join(s.content[:50] for s in error_signals[:3])
        fingerprint = hashlib.sha256(f"{cluster_str}|{error_str}".encode()).hexdigest()[:16]
        
        if fingerprint not in self.active_issues:
            self.active_issues[fingerprint] = ActiveIssue(
                fingerprint=fingerprint,
                focus_file=focus_file,
                focus_cluster=focus_cluster,
                initial_error=error_str,
                initial_signals=error_signals,
                created_at=time.time()
            )
            logger.info(f"🎯 [VERIFY]: Registered Issue {fingerprint[:8]}... ({len(error_signals)} error signals)")
        
        return fingerprint

    def verify_fix(
        self,
        fingerprint: str,
        current_signals: List[Signal]
    ) -> Dict[str, Any]:
        """
        Verifies if the issue has been resolved.
        
        Args:
            fingerprint: The issue ID.
            current_signals: Fresh signals from all sources (filtered by cluster).
        
        Returns:
            A dict with verification status and next action.
        """
        issue = self.active_issues.get(fingerprint)
        if not issue:
            return {"status": "NOT_FOUND", "message": "Issue not registered."}
        
        issue.fix_attempts += 1
        
        # Check if original errors are gone
        original_contents = set(s.content[:50] for s in issue.initial_signals)
        current_errors = [s for s in current_signals if s.severity in ("ERROR", "CRITICAL", "FATAL")]
        current_contents = set(s.content[:50] for s in current_errors)
        
        # Calculate overlap
        remaining_errors = original_contents & current_contents
        new_errors = current_contents - original_contents
        
        if not remaining_errors and not new_errors:
            # SUCCESS: All original errors are gone, no new errors
            issue.resolved = True
            self._log_averted_disaster(issue)
            return {
                "status": "RESOLVED",
                "message": f"✅ Issue {fingerprint[:8]} resolved after {issue.fix_attempts} attempt(s).",
                "action": "CLOSE"
            }
        elif new_errors:
            # REGRESSION: Fix introduced new errors
            return {
                "status": "REGRESSION",
                "message": f"⚠️ Fix introduced {len(new_errors)} new error(s).",
                "action": "RETRY",
                "new_signals": [s for s in current_errors if s.content[:50] in new_errors]
            }
        else:
            # INCOMPLETE: Original errors still present
            return {
                "status": "INCOMPLETE",
                "message": f"🔄 {len(remaining_errors)} original error(s) still present.",
                "action": "RETRY",
                "remaining_signals": [s for s in current_errors if s.content[:50] in remaining_errors]
            }

    def _log_averted_disaster(self, issue: ActiveIssue):
        """Logs a successful fix to the ROI ledger."""
        project_id = SovereignEngine.get_project_id(".")
        self.forensic.log_averted_disaster(
            project_id=project_id,
            reason=f"Resolved issue in {issue.focus_file}: {issue.initial_error[:50]}",
            su_saved=50 * issue.fix_attempts,  # More SU saved if multiple attempts
            technical_debt=f"Cluster: {', '.join(issue.focus_cluster[:3])}"
        )
        logger.info(f"🛡️ [ROI]: Averted Disaster logged for {issue.fingerprint[:8]}.")

    def get_active_issues(self) -> List[ActiveIssue]:
        """Returns all currently active (unresolved) issues."""
        return [i for i in self.active_issues.values() if not i.resolved]

    def clear_resolved(self):
        """Clears resolved issues from memory."""
        resolved = [fp for fp, issue in self.active_issues.items() if issue.resolved]
        for fp in resolved:
            del self.active_issues[fp]
        logger.info(f"🧹 [VERIFY]: Cleared {len(resolved)} resolved issues.")

if __name__ == "__main__":
    # Quick Test
    director = VerificationDirector()
    
    initial_signals = [
        Signal("FORENSIC", "session.py", "session.user can be None", "ERROR", time.time(), ["Session"], 50),
    ]
    
    fp = director.register_issue("auth.py", ["auth.py", "session.py"], initial_signals)
    
    # Simulate fix: error is gone
    new_signals = []
    result = director.verify_fix(fp, new_signals)
    print(result)
