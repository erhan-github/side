"""
Rate limiting for Side.

Capacity-based model. All users get the same features, just different volumes.
Hybrid Model: Daily Baseline (System Readiness) + Monthly Allowance.
"""
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class CapacityBudget:
    """Capacity budget for a user."""
    monthly_allowance: int = 1_000   # Default free tier (Starter)
    burst_per_minute: int = 100     # Burst protection


# Capacity costs (approximations of system effort)
CAPACITY_COSTS = {
    "audit": 500,       # One audit run
    "plan": 100,        # Create/update plan
    "simulate": 300,    # Run simulation
    "decide": 200,      # Strategic decision
}


class CapacityLimiter:
    """
    Capacity-based rate limiter.
    
    Consumption Hierarchy:
    1. Monthly Allowance (Used first)
    2. Add-on CP (Used second - never expires)
    """
    
    def __init__(self):
        # user_id -> {month_key: monthly_used}
        self._monthly_usage: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        # user_id -> balance
        self._addon_balance: Dict[str, int] = defaultdict(int) 
        # user_id -> list of {timestamp, operation, cost, balance_after}
        self._ledger: Dict[str, list] = defaultdict(list)
        self._budgets: Dict[str, CapacityBudget] = {}  # Custom budgets per user
        
    def _get_month_key(self) -> str:
        return time.strftime("%Y%m")
        
    def get_budget(self, user_id: str) -> CapacityBudget:
        """Get the capacity budget for a user."""
        return self._budgets.get(user_id, CapacityBudget())
        
    def set_budget(self, user_id: str, budget: CapacityBudget) -> None:
        """Set custom budget for a user (e.g., after upgrade)."""
        self._budgets[user_id] = budget

    def add_capacity(self, user_id: str, amount: int) -> None:
        """Add one-time 'Add-on' capacity (never expires)."""
        self._addon_balance[user_id] += amount
        
    def get_usage(self, user_id: str) -> dict:
        """Get current usage stats."""
        month_key = self._get_month_key()
        budget = self.get_budget(user_id)
        
        monthly_used = self._monthly_usage[user_id].get(month_key, 0)
        addon_balance = self._addon_balance.get(user_id, 0)
        
        monthly_remaining = max(0, budget.monthly_allowance - monthly_used)
        
        return {
            "monthly_allowance_used": monthly_used,
            "monthly_allowance_limit": budget.monthly_allowance,
            "monthly_allowance_remaining": monthly_remaining,
            "addon_balance": addon_balance,
            "total_remaining": monthly_remaining + addon_balance,
            "month": month_key,
        }

    def get_ledger(self, user_id: str, limit: int = 50) -> list:
        """Get the forensic ledger for a user."""
        # Return last N transactions, newest first
        return sorted(self._ledger[user_id], key=lambda x: x['timestamp'], reverse=True)[:limit]
        
    def check_limit(self, user_id: str, operation: str) -> Tuple[bool, str]:
        """
        Check if user can perform an operation.
        
        Returns: (allowed, reason)
        """
        cost = CAPACITY_COSTS.get(operation, 100)
        usage = self.get_usage(user_id)
        
        if usage["total_remaining"] < cost:
            return False, f"Capacity limit reached. You have {usage['total_remaining']} CP remaining. Upgrades/Boosts at sidelith.com/pricing"
            
        return True, "OK"
        
    def record_usage(self, user_id: str, operation: str) -> None:
        """
        Record capacity usage for an operation.
        Hierarchy: Monthly -> Add-on.
        """
        cost = CAPACITY_COSTS.get(operation, 100)
        month_key = self._get_month_key()
        budget = self.get_budget(user_id)
        
        remaining_to_charge = cost

        # 1. Consume Monthly Allowance
        monthly_used = self._monthly_usage[user_id][month_key]
        monthly_available = max(0, budget.monthly_allowance - monthly_used)
        if monthly_available > 0:
            charge = min(remaining_to_charge, monthly_available)
            self._monthly_usage[user_id][month_key] += charge
            remaining_to_charge -= charge

        # 2. Consume Add-on Balance
        if remaining_to_charge > 0:
            # We assume check_limit was called, so balance should be sufficient
            self._addon_balance[user_id] -= remaining_to_charge

        # 4. Update Ledger
        self._ledger[user_id].append({
            "timestamp": time.time(),
            "operation": operation,
            "start_balance": "N/A", # Simplified for now
            "cost": cost,
            "model": "groq-llama-3-70b" if cost < 300 else "claude-3-5-sonnet" # inferred
        })
            
    def reset_usage(self, user_id: str) -> None:
        """Reset usage (for testing or admin)."""
        self._monthly_usage[user_id] = defaultdict(int)
        self._addon_balance[user_id] = 0
        self._ledger[user_id] = []


# Global instance
limiter = CapacityLimiter()
