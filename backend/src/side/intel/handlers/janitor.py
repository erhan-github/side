import logging
from side.utils.hashing import sparse_hasher

logger = logging.getLogger(__name__)

class MaintenanceService:
    def __init__(self, strategic, engine):
        self.plans = strategic
        self.engine = engine

    async def autonomous_janitor(self, throttle_hook=None) -> int:
        """
        The 'Cache Decay' Protocol. 
        Prunes obsolete, redundant, or conflicting strategic fragments.
        """
        pruned_count = 0
        
        # 1. PRUNE: Conflict Decay
        rejections = self.plans.list_rejections(limit=100)
        # (Simplified logic from original - placeholder for full implementation)
        
        # 2. PRUNE: Redundancy (SimHash Deduplication)
        patterns = self.plans.list_public_patterns()
        hashes = {} # hash -> id
        
        for w in patterns:
            if throttle_hook: await throttle_hook()
            
            w_hash = w.get('signal_hash')
            if not w_hash: continue
            
            duplicate_found = False
            for existing_hash, existing_id in hashes.items():
                if sparse_hasher.similarity(w_hash, existing_hash) > 0.70:
                    if w.get('is_pinned'):
                        continue
                    low_id = w['id']
                    with self.engine.connection() as conn:
                        conn.execute("DELETE FROM public_patterns WHERE id = ?", (low_id,))
                    pruned_count += 1
                    duplicate_found = True
                    break
            
            if not duplicate_found:
                hashes[w_hash] = w['id']

        # 3. Timeline Decay
        purged_stale = self.plans.purge_stale_rejections(days=180)
        pruned_count += purged_stale

        # 4. Limit Decay
        with self.engine.connection() as conn:
            cursor = conn.execute("DELETE FROM rejections WHERE is_pinned = 0 AND id NOT IN (SELECT id FROM rejections ORDER BY created_at DESC LIMIT 200)")
            pruned_count += cursor.rowcount

        logger.info(f"🧹 [JANITOR]: Cache Decay complete. Purged {pruned_count} strategic fragments.")
        return pruned_count
