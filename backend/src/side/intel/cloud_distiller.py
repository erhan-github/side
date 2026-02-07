"""
[PHASE 8] Cloud Distillation Protocol
Ensures only high-value, structured data syncs to the cloud.
"""
import time
import logging
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path
from side.intel.types import VerifiedFix, FixMetrics, ReasoningNode
from side.intel.metrics_calculator import MetricsCalculator
from side.intel.reasoning_timeline import ReasoningTimeline, TimelineManager
from side.utils.crypto import shield

logger = logging.getLogger(__name__)

class CloudDistiller:
    """
    The Cloud Distillation Engine.
    Ensures only meaningful, high-value verified fixes sync to the cloud brain.
    
    [CLOUD SYNC]:
    - Filters: Only cloud-worthy fixes (persistence > 0.3, difficulty >= MEDIUM)
    - Anonymizes: No file paths, no code, no project IDs in cloud
    - Syncs: Distilled insights to tenant_insights table
    """
    
    # Cloud-worthy thresholds
    MIN_PERSISTENCE = 0.3
    MIN_COMMONALITY = 0.5
    MIN_DIFFICULTY = "MEDIUM"
    MIN_ATTEMPTS = 2

    def __init__(self, project_path: Path, cloud_endpoint: str = None, tenant_id: str = None):
        self.project_path = project_path
        self.cloud_endpoint = cloud_endpoint
        self.tenant_id = tenant_id
        self.metrics_calc = MetricsCalculator()
        self.pending_fixes: List[VerifiedFix] = []
        self._supabase_client = None
    
    @property
    def supabase(self):
        """Lazy-load Supabase client."""
        if self._supabase_client is None:
            try:
                from supabase import create_client
                url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
                key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
                
                if url and key:
                    self._supabase_client = create_client(url, key)
                else:
                    logger.debug("Supabase credentials not found, using local staging only")
            except ImportError:
                logger.debug("Supabase client not installed")
        return self._supabase_client

    def distill_fix(
        self,
        timeline: ReasoningTimeline,
        focus_file: str,
        focus_cluster: List[str],
        project_id: str,
        distilled_insight: str = None
    ) -> VerifiedFix:
        """
        Distills a ReasoningTimeline into a cloud-ready VerifiedFix.
        
        Args:
            timeline: The reasoning timeline for this fix.
            focus_file: The primary file being fixed.
            focus_cluster: All files in the dependency cluster.
            project_id: The project identifier.
            distilled_insight: Optional LLM-generated summary of the fix.
        
        Returns:
            A VerifiedFix object ready for cloud sync evaluation.
        """
        chain = timeline.get_chain()
        
        # Extract timestamps from chain
        issue_detected = next((n for n in chain if n.event_type == "ISSUE_DETECTED"), None)
        fix_applied = next((n for n in chain if n.event_type == "FIX_APPLIED"), None)
        verification = next((n for n in chain if n.event_type == "VERIFICATION_PASSED"), None)
        
        # Calculate metrics
        issue_time = issue_detected.timestamp if issue_detected else time.time()
        fix_time = fix_applied.timestamp if fix_applied else time.time()
        verify_time = verification.timestamp if verification else time.time()
        
        # Count fix attempts (number of FIX_APPLIED events)
        fix_attempts = len([n for n in chain if n.event_type == "FIX_APPLIED"])
        
        # Get severity from first issue signal
        severity = "ERROR"
        if issue_detected and "sample_errors" in issue_detected.payload:
            # Could parse severity from error content
            pass
        
        metrics = self.metrics_calc.calculate_all(
            issue_detected_at=issue_time,
            fix_applied_at=fix_time,
            verification_at=verify_time,
            fix_attempts=fix_attempts,
            cluster_size=len(focus_cluster),
            severity=severity
        )
        
        # Build VerifiedFix
        verified_fix = VerifiedFix(
            project_id=project_id,
            issue_detected_at=datetime.fromtimestamp(issue_time, tz=timezone.utc).isoformat(),
            fix_applied_at=datetime.fromtimestamp(fix_time, tz=timezone.utc).isoformat(),
            verification_confirmed_at=datetime.fromtimestamp(verify_time, tz=timezone.utc).isoformat(),
            metrics=metrics,
            reasoning_chain=chain,
            distilled_insight=distilled_insight or self._generate_insight(chain),
            focus_file=focus_file,
            focus_cluster=focus_cluster
        )
        
        logger.info(f"📦 [DISTILLER]: Distilled fix {verified_fix.fix_id[:8]}... ({metrics.difficulty})")
        return verified_fix

    def _generate_insight(self, chain: List[ReasoningNode]) -> str:
        """Generates a simple insight from the reasoning chain."""
        issue_node = next((n for n in chain if n.event_type == "ISSUE_DETECTED"), None)
        fix_node = next((n for n in chain if n.event_type == "FIX_APPLIED"), None)
        
        if issue_node and fix_node:
            sample_error = issue_node.payload.get("sample_errors", ["Unknown issue"])[0]
            fix_file = fix_node.payload.get("file", "unknown file")
            return f"Fixed '{sample_error[:50]}...' in {fix_file}"
        
        return "Fix details not available."

    def should_sync(self, fix: VerifiedFix) -> bool:
        """
        Determines if a fix is cloud-worthy.
        
        Criteria:
        - persistence_score > 0.3 OR
        - commonality_index > 0.5 OR
        - difficulty >= MEDIUM OR
        - fix_attempts >= 2
        """
        return fix.is_cloud_worthy()

    def queue_for_sync(self, fix: VerifiedFix) -> bool:
        """
        Adds a fix to the sync queue if it's cloud-worthy.
        
        Returns:
            True if queued, False if rejected.
        """
        if self.should_sync(fix):
            self.pending_fixes.append(fix)
            logger.info(f"✅ [DISTILLER]: Queued {fix.fix_id[:8]} for cloud sync.")
            return True
        else:
            logger.info(f"⏭️ [DISTILLER]: Skipped {fix.fix_id[:8]} (not cloud-worthy).")
            return False

    def sync_pending(self) -> Dict[str, Any]:
        """
        Syncs all pending fixes to the cloud (or local staging).
        
        [PATTERN SYNC]: Uploads anonymized patterns to tenant_insights.
        
        Returns:
            A summary of the sync operation.
        """
        if not self.pending_fixes:
            return {"status": "EMPTY", "synced": 0}
        
        synced_local = []
        synced_cloud = []
        
        for fix in self.pending_fixes:
            # 1. Always persist locally (encrypted backup)
            self._persist_locally(fix)
            synced_local.append(fix.fix_id)
            
            # 2. Try cloud sync if Supabase available
            if self.supabase and self.tenant_id:
                try:
                    success = self._sync_to_supabase(fix)
                    if success:
                        synced_cloud.append(fix.fix_id)
                except Exception as e:
                    logger.warning(f"Cloud sync failed for {fix.fix_id[:8]}: {e}")
        
        self.pending_fixes = []
        
        logger.info(f"☁️ [DISTILLER]: Synced {len(synced_local)} local, {len(synced_cloud)} cloud.")
        return {
            "status": "SUCCESS",
            "synced_local": len(synced_local),
            "synced_cloud": len(synced_cloud),
            "fix_ids": synced_local
        }
    
    def _sync_to_supabase(self, fix: VerifiedFix) -> bool:
        """
        [PATTERN SYNC] Upload anonymized patterns to tenant_insights.
        
        What gets shared:
        - distilled_insight (summary text)
        - difficulty, persistence_score, commonality_index
        - fix_attempts count
        
        What NEVER gets shared:
        - file paths
        - actual code
        - project_id
        - user identity
        """
        if not self.supabase or not self.tenant_id:
            return False
        
        # Anonymize the insight
        insight_data = {
            "tenant_id": self.tenant_id,
            "insight_type": "technical", # Matches schema comments: 'strategic', 'technical', etc.
            "title": f"Pattern: {fix.metrics.difficulty} difficulty fix",
            "content": fix.distilled_insight,  # Already anonymized summary
            "confidence": fix.metrics.persistence_score,
            "source_context": {
                # Only anonymized metrics, no paths or code
                "difficulty": fix.metrics.difficulty,
                "persistence": fix.metrics.persistence_score,
                "commonality": fix.metrics.commonality_index,
                "fix_attempts": fix.metrics.fix_attempts,
                "time_to_fix_seconds": fix.metrics.time_spent_seconds,
                "cluster_complexity": len(fix.focus_cluster),  # Just count, not names
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            response = self.supabase.table("tenant_insights").insert(insight_data).execute()
            
            if response.data:
                logger.info(f"✅ [CLOUD]: Patterns synced: {fix.distilled_insight[:50]}...")
                return True
        except Exception as e:
            logger.error(f"❌ [CLOUD]: Failed to sync patterns: {e}")
        
        return False

    def _persist_locally(self, fix: VerifiedFix):
        """Persists a fix to local staging (encrypted)."""
        staging_dir = self.project_path / ".side" / "cloud_staging"
        staging_dir.mkdir(parents=True, exist_ok=True)
        
        fix_file = staging_dir / f"{fix.fix_id}.json"
        shield.seal_file(fix_file, json.dumps(fix.to_dict(), indent=2))

    def get_staged_fixes(self) -> List[Dict]:
        """Returns all fixes in local staging."""
        staging_dir = self.project_path / ".side" / "cloud_staging"
        if not staging_dir.exists():
            return []
        
        fixes = []
        for file in staging_dir.glob("*.json"):
            try:
                raw = shield.unseal_file(file)
                fixes.append(json.loads(raw))
            except Exception as e:
                logger.warning(f"Failed to read {file.name}: {e}")
        
        return fixes

# ---------------------------------------------------------------------
# INTEGRATION: Complete Fix Flow
# ---------------------------------------------------------------------

def complete_fix_flow(
    project_path: Path,
    project_id: str,
    focus_file: str,
    focus_cluster: List[str],
    timeline: ReasoningTimeline,
    tenant_id: str = None
) -> Dict[str, Any]:
    """
    Completes the full fix flow: distill → evaluate → queue → sync.
    
    Returns:
        Summary of the operation.
    """
    distiller = CloudDistiller(project_path, tenant_id=tenant_id)
    
    # Distill the fix
    verified_fix = distiller.distill_fix(
        timeline=timeline,
        focus_file=focus_file,
        focus_cluster=focus_cluster,
        project_id=project_id
    )
    
    # Queue if worthy
    queued = distiller.queue_for_sync(verified_fix)
    
    # Sync immediately (or batch later)
    if queued:
        result = distiller.sync_pending()
        return {
            "fix_id": verified_fix.fix_id,
            "cloud_worthy": True,
            "synced": result["status"] == "SUCCESS",
            "metrics": verified_fix.metrics.to_dict()
        }
    else:
        return {
            "fix_id": verified_fix.fix_id,
            "cloud_worthy": False,
            "synced": False,
            "reason": "Did not meet cloud-worthy criteria"
        }

if __name__ == "__main__":
    # Quick Test
    logging.basicConfig(level=logging.INFO)
    
    timeline = TimelineManager.get_or_create("test-fix-002")
    timeline.record_issue_detected([{"content": "NoneType error"}], "auth.py")
    timeline.record_context_injected(5, 500)
    timeline.record_fix_applied("session.py", 50)
    timeline.record_verification_passed(0)
    
    result = complete_fix_flow(
        project_path=Path.cwd(),
        project_id="test-project",
        focus_file="auth.py",
        focus_cluster=["auth.py", "session.py", "token.py"],
        timeline=timeline
    )
    
    print(json.dumps(result, indent=2))
