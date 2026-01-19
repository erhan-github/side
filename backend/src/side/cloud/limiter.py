"""
Rate limiting for Side.

Token-based model. All users get the same features, just different volumes.
Like Manus - full product, upgrade when you need more.
"""
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict


@dataclass
class TokenBudget:
    """Token budget for a user."""
    tokens_per_month: int = 10_000  # Default free tier
    tokens_per_minute: int = 100  # Burst protection


# Simple token costs (approximations)
TOKEN_COSTS = {
    "audit": 500,       # One audit run
    "plan": 100,        # Create/update plan
    "simulate": 300,    # Run simulation
    "decide": 200,      # Strategic decision
}


class TokenLimiter:
    """
    Token-based rate limiter.
    
    All users get the same features.
    Difference is only in volume (tokens/month).
    """
    
    def __init__(self):
        # user_id -> {month_key: tokens_used}
        self._usage: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._budgets: Dict[str, TokenBudget] = {}  # Custom budgets per user
        
    def _get_month_key(self) -> str:
        return time.strftime("%Y%m")
        
    def get_budget(self, user_id: str) -> TokenBudget:
        """Get the token budget for a user."""
        return self._budgets.get(user_id, TokenBudget())
        
    def set_budget(self, user_id: str, budget: TokenBudget) -> None:
        """Set custom budget for a user (e.g., after upgrade)."""
        self._budgets[user_id] = budget
        
    def get_usage(self, user_id: str) -> dict:
        """Get current usage stats."""
        month_key = self._get_month_key()
        budget = self.get_budget(user_id)
        used = self._usage[user_id].get(month_key, 0)
        return {
            "used": used,
            "limit": budget.tokens_per_month,
            "remaining": max(0, budget.tokens_per_month - used),
            "month": month_key,
        }
        
    def check_limit(self, user_id: str, operation: str) -> tuple[bool, str]:
        """
        Check if user can perform an operation.
        
        Returns: (allowed, reason)
        """
        cost = TOKEN_COSTS.get(operation, 100)
        usage = self.get_usage(user_id)
        
        if usage["remaining"] < cost:
            return False, f"Token limit reached. Used {usage['used']}/{usage['limit']} this month. Upgrade at side.ai/upgrade"
            
        return True, "OK"
        
    def record_usage(self, user_id: str, operation: str) -> None:
        """Record token usage for an operation."""
        cost = TOKEN_COSTS.get(operation, 100)
        month_key = self._get_month_key()
        self._usage[user_id][month_key] += cost
        
    def reset_usage(self, user_id: str) -> None:
        """Reset usage (for testing or admin)."""
        self._usage[user_id] = defaultdict(int)


# Global instance
limiter = TokenLimiter()
