from enum import Enum
from typing import Any
import logging
from side.storage.modules.base import InsufficientTokensError

logger = logging.getLogger(__name__)

from side.models.pricing import ActionCost

class SystemAction(Enum):
    HUB_UPDATE = "hub_update"
    PLAN_UPDATE = "plan_update"
    
# Cost Table (Primary Source of Economy)
ACTION_COSTS = {
    SystemAction.HUB_UPDATE: ActionCost.HUB_EVOLVE,
    SystemAction.PLAN_UPDATE: ActionCost.HUB_EVOLVE # Simplified
}

class BillingService:
    """
    Sovereign Billing Service.
    Enforces token economy for high-value strategic actions.
    """
    def __init__(self, db: Any):
        self.db = db

    def can_afford(self, project_id: str, action: SystemAction) -> bool:
        """Check if profile has enough tokens for the action."""
        try:
            balance_data = self.db.identity.get_token_balance(project_id)
            current = balance_data.get("balance", 0)
            cost = ACTION_COSTS.get(action, 0)
            
            if current >= cost:
                return True
            
            logger.warning(f"Insufficient funds for {action}: Has {current}, Need {cost}")
            return False
            
        except Exception as e:
            logger.error(f"Billing check failed: {e}")
            # Fail closed for safety, or open for UX? 
            # Sovereign principle: If local DB fails, don't block work.
            return True

    def charge(self, project_id: str, action: SystemAction, tool_name: str, payload: dict) -> bool:
        """Deduct tokens and track premium usage."""
        try:
            cost = ACTION_COSTS.get(action, 0)
            
            # [CURSOR TRACKING]: If it's a strategic action, increment premium count
            if cost > 0:
                self.db.identity.increment_premium_count(project_id)

            # Deduct (negative update)
            self.db.identity.update_token_balance(project_id, -cost)
            
            logger.info(f"💰 Charged {cost} SUs for {action.value}")
            return True
            
        except InsufficientTokensError:
            logger.error(f"Charge failed: Insufficient SUs.")
            return False
        except Exception as e:
            logger.error(f"Charge failed: {e}")
            return False

    def get_summary(self, project_id: str) -> dict[str, Any]:
        """Exposes the Cursor-level usage breakdown."""
        return self.db.identity.get_cursor_usage_summary(project_id)

    def claim_trial(self, project_path: Any):
        """One-time trial grant."""
        pass 
