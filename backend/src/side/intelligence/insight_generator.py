"""
Insight generation layer - Minimal LLM usage with token optimization.

Generates natural language insights from pre-aggregated data.

Forensic-level principles:
- Structured prompts (no ambiguity)
- Minimal tokens (<100 per call)
- Low temperature (factual, not creative)
- Tight limits (force brevity)
"""

from typing import Dict, Optional


class InsightGenerator:
    """
    Generate insights with minimal LLM usage.
    
    Token-optimized prompting with quality guarantees.
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
        
        # Prompt templates (optimized for tokens)
        self.VELOCITY_PROMPT = """Generate a concise insight (max 1 line):

Data:
- Baseline: {baseline} commits/day (Day 1-7)
- Current: {current} commits/day (Last 7 days)
- Change: {delta_pct:+.1f}%
- Trend: {trend}

Format: "You're [X]% [faster/slower] than Day 1 ([trend])"
Example: "You're 81% faster than Day 1 (accelerating)"

Output:"""
        
        self.FOCUS_PROMPT = """Generate a concise insight (max 1 line):

Data:
- Backend: {backend_pct}%
- Frontend: {frontend_pct}%
- Docs: {docs_pct}%

Format: "[X]% backend, [Y]% frontend focus"
Example: "70% backend, 30% frontend focus"

Output:"""
        
        self.COST_PROMPT = """Generate a cost recommendation (max 1 line):

Data:
- Top feature: {top_feature}
- Cost: ${top_feature_cost}
- Percentage: {top_feature_pct}%

Format: "[Feature] costs [X]% of total ([recommendation])"
Example: "Audit costs 52% of total (optimize prompts)"

Output:"""
    
    def generate_velocity_insight(self, aggregated: Dict) -> str:
        """
        Generate velocity insight from aggregated data.
        
        Args:
            aggregated: Pre-aggregated velocity data
            
        Returns:
            1-line insight (e.g., "You're 81% faster than Day 1 (accelerating)")
        """
        try:
            # Format prompt
            prompt = self.VELOCITY_PROMPT.format(**aggregated)
            
            # Generate with optimized parameters
            response = self.llm.generate(
                prompt=prompt,
                max_tokens=30,      # 1 line only
                temperature=0.3,    # Factual, not creative
                top_p=0.9,
                stop=["\n", "."]    # Stop after 1 line
            )
            
            return response.strip()
        except Exception as e:
            # Fallback to template (no LLM)
            return self._template_velocity_insight(aggregated)
    
    def generate_focus_insight(self, aggregated: Dict) -> str:
        """Generate focus insight from aggregated data."""
        try:
            prompt = self.FOCUS_PROMPT.format(**aggregated)
            
            response = self.llm.generate(
                prompt=prompt,
                max_tokens=30,
                temperature=0.3,
                top_p=0.9,
                stop=["\n", "."]
            )
            
            return response.strip()
        except Exception:
            return self._template_focus_insight(aggregated)
    
    def generate_cost_insight(self, aggregated: Dict) -> str:
        """Generate cost insight from aggregated data."""
        try:
            # Add cost to prompt data
            prompt_data = {
                **aggregated,
                'top_feature_cost': aggregated['by_feature'].get(aggregated['top_feature'], 0)
            }
            
            prompt = self.COST_PROMPT.format(**prompt_data)
            
            response = self.llm.generate(
                prompt=prompt,
                max_tokens=40,
                temperature=0.3,
                top_p=0.9,
                stop=["\n", "."]
            )
            
            return response.strip()
        except Exception:
            return self._template_cost_insight(aggregated)
    
    def _template_velocity_insight(self, data: Dict) -> str:
        """Fallback template (no LLM)."""
        if data['delta_pct'] > 0:
            direction = "faster"
        elif data['delta_pct'] < 0:
            direction = "slower"
        else:
            direction = "same speed as"
        
        return f"You're {abs(data['delta_pct']):.0f}% {direction} than Day 1 ({data['trend']})"
    
    def _template_focus_insight(self, data: Dict) -> str:
        """Fallback template (no LLM)."""
        return f"{data['backend_pct']:.0f}% backend, {data['frontend_pct']:.0f}% frontend focus"
    
    def _template_cost_insight(self, data: Dict) -> str:
        """Fallback template (no LLM)."""
        if not data['top_feature']:
            return "No cost data available"
        
        recommendation = "optimize prompts" if data['top_feature_pct'] > 50 else "costs are balanced"
        return f"{data['top_feature']} costs {data['top_feature_pct']:.0f}% of total ({recommendation})"
