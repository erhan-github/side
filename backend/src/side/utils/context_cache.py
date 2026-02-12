"""
Context Cache - Regeneratable Context Cache for LLM Injection.

[HYBRID ARCHITECTURE]: context.json is a READ-ONLY CACHE generated from context.db.
If deleted, it will be regenerated on next startup.

This is NOT the source of truth - the database is.
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from side.utils.crypto import shield

logger = logging.getLogger(__name__)

# Cache version - increment when schema changes
CACHE_VERSION = "5.0.0"


class ContextCache:
    """
    Manages the context.json cache file.
    
    [HYBRID ARCHITECTURE]:
    - context.json is a CACHE, not the source of truth
    - Generated from context.db on demand
    - Fast LLM context injection (no DB query needed)
    - Marked as "cache_of: context.db" in the file
    """
    
    def __init__(self, project_path: Path, db: Any):
        self.project_path = project_path
        self.db = db
        self.side_dir = project_path / ".side"
        self.cache_path = self.side_dir / "context.json"
    
    def generate(self, force: bool = False) -> Dict[str, Any]:
        """
        Generate context.json cache from database.
        
        Args:
            force: If True, regenerate even if cache exists and is fresh
            
        Returns:
            The generated cache data
        """
        # Check if cache is fresh (less than 5 minutes old)
        if not force and self._is_cache_fresh():
            logger.debug("🗃️ [CACHE]: Context cache is fresh, skipping regeneration")
            return self._read_cache()
        
        logger.info("🔄 [CACHE]: Regenerating context.json from database")
        
        project_id = self.db.get_project_id()
        
        # Collect data from database (the source of truth)
        cache_data = {
            # Metadata
            "version": CACHE_VERSION,
            "cache_of": "context.db",  # Marks as regeneratable cache
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "project_id": project_id,
            
            # Strategic context (from database)
            "strategic_timeline": self._get_strategic_timeline(project_id),
            "recent_facts": self._get_recent_facts(project_id),
            "fingerprint": self._get_fingerprint(project_id),
            
            # Metrics (summary only, details in DB)
            "metrics": {
                "plans_count": len(self.db.plans.list_plans(project_id=project_id)),
                "facts_count": len(self._get_recent_facts(project_id)),
                "last_activity": self._get_last_activity_time(project_id)
            }
        }
        
        # Write cache (encrypted)
        self._write_cache(cache_data)
        
        logger.info(f"✨ [CACHE]: Context cache regenerated at {self.cache_path}")
        return cache_data
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get context for LLM injection.
        
        If cache exists and is fresh, use it (fast path).
        Otherwise, regenerate from database.
        """
        if self._is_cache_fresh():
            return self._read_cache()
        return self.generate()
    
    def invalidate(self) -> None:
        """Invalidate the cache (will regenerate on next access)."""
        if self.cache_path.exists():
            self.cache_path.unlink()
            logger.info("🗑️ [CACHE]: Context cache invalidated")
    
    def _is_cache_fresh(self, max_age_seconds: int = 300) -> bool:
        """Check if cache exists and is fresh (default 5 minutes)."""
        if not self.cache_path.exists():
            return False
        
        try:
            cache_data = self._read_cache()
            generated_at = datetime.fromisoformat(cache_data.get("generated_at", ""))
            age = (datetime.now(timezone.utc) - generated_at).total_seconds()
            return age < max_age_seconds
        except Exception:
            return False
    
    def _read_cache(self) -> Dict[str, Any]:
        """Read encrypted cache file."""
        try:
            raw = shield.unseal_file(self.cache_path)
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"⚠️ [CACHE]: Failed to read cache: {e}")
            return {}
    
    def _write_cache(self, data: Dict[str, Any]) -> None:
        """Write encrypted cache file."""
        # Ensure .side directory exists (lazy creation)
        self.side_dir.mkdir(parents=True, exist_ok=True)
        
        # Write encrypted
        shield.seal_file(self.cache_path, json.dumps(data, indent=2))
    
    def _get_strategic_timeline(self, project_id: str) -> list:
        """Get strategic plans as timeline."""
        try:
            plans = self.db.plans.list_plans(project_id=project_id)
            return [
                {
                    "id": p.get("id"),
                    "title": p.get("title"),
                    "type": p.get("type"),
                    "status": p.get("status")
                }
                for p in plans[:20]  # Limit for LLM context size
            ]
        except Exception:
            return []
    
    def _get_recent_facts(self, project_id: str) -> list:
        """Get recent facts for context."""
        try:
            facts = self.db.plans.recall_facts("", project_id, limit=10)
            return [
                {
                    "content": f.get("content"),
                    "tags": f.get("tags", [])
                }
                for f in facts
            ]
        except Exception:
            return []
    
    def _get_fingerprint(self, project_id: str) -> dict:
        """Get project fingerprint."""
        try:
            return self.db.profile.get_project_fingerprint(project_id) or {}
        except Exception:
            return {}
    
    def _get_last_activity_time(self, project_id: str) -> Optional[str]:
        """Get last activity timestamp."""
        try:
            activities = self.db.audits.get_recent_activities(project_id, limit=1)
            if activities:
                return activities[0].get("created_at")
            return None
        except Exception:
            return None


def ensure_context_cache(project_path: Path, db: Any) -> Dict[str, Any]:
    """
    Convenience function to ensure context cache exists and is fresh.
    
    Called on startup to ensure LLM context is ready.
    """
    cache = ContextCache(project_path, db)
    return cache.generate()
