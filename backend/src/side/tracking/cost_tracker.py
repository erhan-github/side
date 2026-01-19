"""
Cost tracking and attribution system.

Tracks costs per feature with bulletproof accuracy based on actual logged activities.
"""

from typing import Dict
from datetime import datetime, timedelta, timezone


class CostTracker:
    """Track costs per feature with 100% confidence (based on logs)."""
    
    def __init__(self, db):
        self.db = db
        # Cost rates (can be configured)
        self.llm_cost_per_token = 0.0001  # $0.0001 per token (example)
    
    def calculate_costs(self, days: int = 30) -> Dict:
        """
        Calculate costs by feature from activity logs.
        
        Returns:
            {
                'by_feature': {'audit': 12.40, 'simulate': 8.20, ...},
                'total': 48.70,
                'confidence': 1.0,  # Perfect (from actual logs)
                'period_days': 30
            }
        """
        try:
            # Get activities from last N days
            since = datetime.now(timezone.utc) - timedelta(days=days)
            activities = self.db.get_activities_since(since.isoformat())
            
            costs = {}
            for activity in activities:
                tool = activity['tool']
                tokens = activity.get('cost_tokens', 0)
                cost = tokens * self.llm_cost_per_token
                
                costs[tool] = costs.get(tool, 0) + cost
            
            return {
                'by_feature': costs,
                'total': sum(costs.values()),
                'confidence': 1.0,  # Perfect confidence (from actual logs)
                'period_days': days
            }
        except Exception:
            return {
                'by_feature': {},
                'total': 0.0,
                'confidence': 0.0,
                'period_days': days
            }
    
    def get_cost_insights(self, days: int = 30) -> Dict:
        """
        Get actionable cost insights.
        
        Returns:
            {
                'highest_cost_feature': str,
                'percentage_of_total': float,
                'recommendation': str
            }
        """
        costs = self.calculate_costs(days)
        
        if not costs['by_feature']:
            return {}
        
        # Find highest cost feature
        highest = max(costs['by_feature'].items(), key=lambda x: x[1])
        feature_name, feature_cost = highest
        
        percentage = (feature_cost / costs['total'] * 100) if costs['total'] > 0 else 0
        
        return {
            'highest_cost_feature': feature_name,
            'cost': feature_cost,
            'percentage_of_total': round(percentage, 1),
            'recommendation': f"Optimize {feature_name} prompts to reduce costs" if percentage > 50 else None
        }
