"""
Insight caching layer - Avoid redundant LLM calls.

Caches insights to minimize cost and latency.

Forensic-level principles:
- Hash-based caching (content-addressable)
- Automatic invalidation (when data changes)
- 90%+ hit rate target
- Zero stale data
"""

from typing import Optional, Dict
import hashlib
import json
from datetime import datetime, timedelta, timezone


class InsightCache:
    """
    Cache LLM-generated insights to avoid redundant calls.
    
    90% cache hit rate = 10x cost reduction.
    """
    
    def __init__(self, db):
        self.db = db
        self.ttl_hours = 24  # Cache for 24 hours
    
    def get(self, data: Dict, insight_type: str) -> Optional[str]:
        """
        Get cached insight if available and fresh.
        
        Args:
            data: Aggregated data (used for cache key)
            insight_type: 'velocity', 'focus', or 'cost'
            
        Returns:
            Cached insight or None
        """
        try:
            # Generate cache key
            cache_key = self._generate_key(data, insight_type)
            
            # Check database
            cached = self.db.get_cached_insight(cache_key)
            
            if not cached:
                return None
            
            # Check if expired
            cached_time = datetime.fromisoformat(cached['created_at'])
            age = datetime.now(timezone.utc) - cached_time
            
            if age > timedelta(hours=self.ttl_hours):
                # Expired - delete and return None
                self.db.delete_cached_insight(cache_key)
                return None
            
            # Fresh cache hit
            return cached['insight']
        except Exception:
            return None
    
    def set(self, data: Dict, insight_type: str, insight: str):
        """
        Store insight in cache.
        
        Args:
            data: Aggregated data (used for cache key)
            insight_type: 'velocity', 'focus', or 'cost'
            insight: Generated insight
        """
        try:
            cache_key = self._generate_key(data, insight_type)
            
            self.db.store_cached_insight(
                cache_key=cache_key,
                insight=insight,
                created_at=datetime.now(timezone.utc).isoformat()
            )
        except Exception:
            pass  # Silent failure - caching is optional
    
    def _generate_key(self, data: Dict, insight_type: str) -> str:
        """
        Generate cache key from data.
        
        Uses content hash for cache invalidation when data changes.
        """
        try:
            # Create deterministic string from data
            data_str = json.dumps(data, sort_keys=True)
            combined = f"{insight_type}:{data_str}"
            
            # Hash it
            return hashlib.sha256(combined.encode()).hexdigest()[:16]
        except Exception:
            # Fallback to simple key
            return f"{insight_type}:{hash(str(data))}"
