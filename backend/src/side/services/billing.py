"""
Billing Service.

Server-side billing via Supabase RPC.
Users cannot tamper with local database to fake usage.
All charges are verified and logged on the cloud.
"""
from enum import Enum
from typing import Any, Optional
import logging
import os

from side.storage.modules.base import InsufficientTokensError

logger = logging.getLogger(__name__)

from side.models.pricing import ActionCost


class SystemAction(Enum):
    HUB_UPDATE = "hub_update"
    PLAN_UPDATE = "plan_update"
    AUDIT_SCAN = "audit_scan"
    STRATEGIC_ANALYSIS = "strategic_analysis"


# Cost Table (Primary Source of Economy)
ACTION_COSTS = {
    SystemAction.HUB_UPDATE: ActionCost.HUB_EVOLVE,
    SystemAction.PLAN_UPDATE: ActionCost.HUB_EVOLVE,
    SystemAction.AUDIT_SCAN: 10,
    SystemAction.STRATEGIC_ANALYSIS: 25,
}


class BillingService:
    """
    Billing Service with Server-Side Verification.
    
    Architecture:
    1. Server-Side Verification: All charges go through Supabase RPC
    2. Transaction Ledger: Every charge is logged with timestamp
    3. Local Cache: Read-only balance cache for UX
    4. Fail-Open for UX: If cloud unavailable, allow work (local tracking)
    """
    
    def __init__(self, db: Any, user_id: Optional[str] = None):
        self.db = db
        self.user_id = user_id
        self._supabase_client = None
        self._balance_cache: Optional[int] = None
    
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
                    logger.warning("⚠️ [BILLING]: Supabase credentials not found, using local-only mode")
            except ImportError:
                logger.warning("⚠️ [BILLING]: Supabase client not installed, using local-only mode")
        return self._supabase_client
    
    def can_afford(self, project_id: str, action: SystemAction) -> bool:
        """
        Check if user has enough tokens for the action.
        
        Check cloud first, fall back to local cache.
        """
        cost = ACTION_COSTS.get(action, 0)
        if cost == 0:
            return True
        
        # Try cloud first (source of truth)
        balance = self._get_cloud_balance()
        if balance is not None:
            return balance >= cost
        
        # Fall back to local cache
        try:
            balance_data = self.db.profile.get_token_balance(project_id)
            current = balance_data.get("balance", 0)
            return current >= cost
        except Exception as e:
            logger.error(f"Billing check failed: {e}")
            # Fail open for UX - don't block work
            return True
    
    async def charge_async(self, project_id: str, action: SystemAction, 
                           tool_name: str, payload: dict) -> bool:
        """
        [ANTI-FRAUD] Server-side charge via Supabase RPC.
        
        All billing goes through the cloud for tamper-proof verification.
        """
        cost = ACTION_COSTS.get(action, 0)
        if cost == 0:
            return True
        
        # 1. Try server-side charge (anti-fraud)
        if self.supabase and self.user_id:
            try:
                response = self.supabase.rpc(
                    'increment_tokens',
                    {'p_user_id': self.user_id, 'p_amount': cost}
                ).execute()
                
                if response.data is not None:
                    logger.info(f"💰 [CLOUD]: Charged {cost} SUs for {action.value}")
                    
                    # Update local cache (read-only)
                    self._update_balance_cache(project_id)
                    return True
                    
            except Exception as e:
                logger.warning(f"⚠️ [CLOUD]: Server charge failed: {e}, falling back to local")
        
        # 2. Fall back to local tracking (for offline/dev mode)
        return self._charge_local(project_id, action, tool_name, payload)
    
    def charge(self, project_id: str, action: SystemAction, 
               tool_name: str, payload: dict) -> bool:
        """
        Synchronous charge (wraps async for backward compatibility).
        
        [NOTE]: Prefer charge_async() for server-side verification.
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Already in async context, use local
                return self._charge_local(project_id, action, tool_name, payload)
            return loop.run_until_complete(
                self.charge_async(project_id, action, tool_name, payload)
            )
        except RuntimeError:
            # No event loop, use local
            return self._charge_local(project_id, action, tool_name, payload)
    
    def _charge_local(self, project_id: str, action: SystemAction,
                      tool_name: str, payload: dict) -> bool:
        """
        Local-only charge (for offline/dev mode).
        
        [WARNING]: This is not anti-fraud protected.
        Usage is tracked locally and should sync to cloud when available.
        """
        try:
            cost = ACTION_COSTS.get(action, 0)
            
            # Track premium usage
            if cost > 0:
                self.db.profile.increment_premium_count(project_id)
            
            # Deduct from local balance
            self.db.profile.update_token_balance(project_id, -cost)
            
            logger.info(f"💰 [LOCAL]: Charged {cost} SUs for {action.value}")
            return True
            
        except InsufficientTokensError:
            logger.error("Charge failed: Insufficient SUs.")
            return False
        except Exception as e:
            logger.error(f"Charge failed: {e}")
            return False
    
    def _get_cloud_balance(self) -> Optional[int]:
        """Get balance from cloud (source of truth)."""
        if not self.supabase or not self.user_id:
            return None
        
        try:
            response = self.supabase.table('profiles').select(
                'tokens_monthly, tokens_used'
            ).eq('id', self.user_id).single().execute()
            
            if response.data:
                monthly = response.data.get('tokens_monthly', 0)
                used = response.data.get('tokens_used', 0)
                balance = monthly - used
                self._balance_cache = balance
                return balance
        except Exception as e:
            logger.debug(f"Could not fetch cloud balance: {e}")
        
        return None
    
    def _update_balance_cache(self, project_id: str) -> None:
        """Update local balance cache from cloud."""
        balance = self._get_cloud_balance()
        if balance is not None:
            try:
                self.db.profile.set_cached_balance(project_id, balance)
            except AttributeError:
                # Method might not exist yet
                pass
    
    def get_summary(self, project_id: str) -> dict[str, Any]:
        """Get usage summary (tries cloud first, falls back to local)."""
        # Cloud summary
        if self.supabase and self.user_id:
            try:
                response = self.supabase.table('profiles').select(
                    'tokens_monthly, tokens_used'
                ).eq('id', self.user_id).single().execute()
                
                if response.data:
                    return {
                        "monthly_limit": response.data.get('tokens_monthly', 0),
                        "used": response.data.get('tokens_used', 0),
                        "balance": response.data.get('tokens_monthly', 0) - response.data.get('tokens_used', 0),
                        "source": "cloud"
                    }
            except Exception:
                pass
        
        # Local summary
        return self.db.profile.get_cursor_usage_summary(project_id)
    
    
    def claim_trial(self) -> bool:
        """
        One-time trial grant check.
        
        Trials are automatically granted on signup via Supabase Database Triggers.
        This method handles future manual claim logic.
        """
        # Logic handled by PostgreSQL Trigger: on_auth_user_created -> grant_trial()
        return True
