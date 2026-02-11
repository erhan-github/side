"""
Outcome Verifier.

Triangulates LLM claims against System Audit Signals.
Determines if a "fixed" issue actually stopped occuring in the logs.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

from side.intel.conversation_session import ConversationSession, VerifiedOutcome, ClaimedOutcome
from side.storage.simple_db import SimplifiedDatabase

logger = logging.getLogger(__name__)

class ResultChecker:
    """
    The Results Checker.
    Compares what the LLM *said* happened vs what the System *knows* happened.
    """

    def __init__(self, db: SimplifiedDatabase):
        self.db = db
        self.audit = db.audit
        self.store = db.goal_tracker

    def verify_session(self, session: ConversationSession) -> VerifiedOutcome:
        """
        Verify the outcome of a session.
        Returns the verified status based on Signal Triangulation.
        """
        if session.claimed_outcome != ClaimedOutcome.FIXED:
            return VerifiedOutcome.NOT_APPLICABLE
            
        if not session.ended_at:
            return VerifiedOutcome.UNVERIFIABLE # Session still open?
            
        # 1. Define Verification Window (e.g., 1 hour after fix)
        from side.config import config
        window_start = session.ended_at
        window_end = window_start + timedelta(hours=config.verification_window_hours)
        
        # 2. Check Audit Logs for Errors
        # We look for high-severity audits in the project window
        recent_audits = self.audit.get_recent_audits(session.project_id, limit=50)
        
        relevant_errors = []
        for audit in recent_audits:
            # Parse audit time
            try:
                run_at = datetime.fromisoformat(audit['run_at'])
                # Some logs might lack timezone, assume local/UTC matches system
                if run_at.tzinfo is None:
                    run_at = run_at.replace(tzinfo=timezone.utc)
            except:
                continue
                
            if window_start <= run_at <= window_end:
                if audit['severity'] in ('high', 'critical', 'error'):
                    relevant_errors.append(audit)
                    
        if relevant_errors:
            logger.info(f"🚫 [RESULT_CHECKER]: False Positive detected for session {session.session_id[:8]}. {len(relevant_errors)} errors found after fix.")
            return VerifiedOutcome.FALSE_POSITIVE
            
        # 3. Check for immediate user "undo" or "revert" (from FileWatcher/Activities)
        recent_activities = self.audit.get_recent_activities(session.project_id, limit=50)
        for act in recent_activities:
            # Parse timestamp (handle various formats)
            try:
                ts = act['created_at']
                if isinstance(ts, str):
                    act_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                else:
                    act_time = datetime.now() # Fallback
            except:
                continue

            if window_start <= act_time <= window_end:
                # Check for External Failures
                if act['tool'] == 'LOG_SCAVENGER':
                     logger.info(f"🚫 [RESULT_CHECKER]: External Failure detected: {act['action']}")
                     return VerifiedOutcome.FALSE_POSITIVE

                # Check for Reverts
                if "revert" in str(act.get('action', '')).lower() or "undo" in str(act.get('action', '')).lower():
                     return VerifiedOutcome.FALSE_POSITIVE

        # 4. If signals differ from Pre-Fix state
        # (Advanced: Check if specific previous error stopped)
        # For now, if no errors appear in window -> CONFIRMED
        
        logger.info(f"✅ [RESULT_CHECKER]: Session {session.session_id[:8]} confirmed fixed. No errors in window.")
        return VerifiedOutcome.CONFIRMED

    def verify_pending_sessions(self):
        """Batch job to verify recent UNKNOWN sessions."""
        """Batch job to verify recent UNKNOWN sessions."""
        # Get sessions that ended > 1 hour ago but are still UNKNOWN
        pending = self.store.get_pending_verification_sessions(limit=50)
        
        verified_count = 0
        for session_dict in pending:
            session = self._dict_to_session(session_dict)
            outcome = self.verify_session(session)
            
            if outcome != VerifiedOutcome.UNKNOWN:
                self.store.update_outcome(session.session_id, outcome)
                verified_count += 1
                
        logger.info(f"✅ [RESULT_CHECKER]: Batch results check complete. {verified_count} sessions finalized.")

    def _dict_to_session(self, data: Dict[str, Any]) -> ConversationSession:
        """Helper to hydrate session from DB dict (OutcomeVerifier version)."""
        # (Duplicate helper - in production this should be in a shared utility)
        return ConversationSession(
            session_id=data['session_id'],
            project_id=data['project_id'],
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            ended_at=datetime.fromisoformat(data['ended_at']) if data.get('ended_at') else None,
            duration_seconds=data.get('duration_seconds', 0),
            raw_intent=data.get('raw_intent', ''),
            intent_vector=data.get('intent_vector', []),
            claimed_outcome=ClaimedOutcome(data.get('claimed_outcome', 'unknown'))
        )
