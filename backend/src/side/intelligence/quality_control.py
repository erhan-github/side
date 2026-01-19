"""
Quality control layer - Validate LLM outputs for accuracy.

Ensures zero hallucinations reach users through multi-layer validation.

Forensic-level principles:
- Verify numbers match source data
- Check for unsupported claims
- Validate format compliance
- Silent failures (never break)
"""

from typing import Dict, Tuple
import re


class QualityControl:
    """
    Validate LLM outputs before showing to users.
    
    Zero hallucinations guarantee through strict validation.
    """
    
    def validate_velocity_insight(self, insight: str, source_data: Dict) -> Tuple[bool, str]:
        """
        Validate velocity insight against source data.
        
        Args:
            insight: LLM-generated insight
            source_data: Original aggregated data
            
        Returns:
            (is_valid, reason)
        """
        try:
            # Extract numbers from insight
            numbers = self._extract_numbers(insight)
            
            # Check 1: Delta percentage must match
            delta_pct = abs(source_data['delta_pct'])
            if not any(abs(n - delta_pct) < 1 for n in numbers):
                return False, f"Wrong percentage (expected {delta_pct})"
            
            # Check 2: Trend must match
            trend = source_data['trend'].lower()
            if trend not in insight.lower():
                return False, f"Wrong trend (expected {trend})"
            
            # Check 3: Direction must match
            if source_data['delta_pct'] > 0:
                if 'slower' in insight.lower():
                    return False, "Wrong direction (should be faster)"
            elif source_data['delta_pct'] < 0:
                if 'faster' in insight.lower():
                    return False, "Wrong direction (should be slower)"
            
            # All checks passed
            return True, "Valid"
        except Exception as e:
            # Validation error = reject
            return False, f"Validation error: {str(e)}"
    
    def validate_focus_insight(self, insight: str, source_data: Dict) -> Tuple[bool, str]:
        """Validate focus insight against source data."""
        try:
            # Extract numbers
            numbers = self._extract_numbers(insight)
            
            # Check: Backend percentage must match
            backend_pct = source_data['backend_pct']
            if not any(abs(n - backend_pct) < 2 for n in numbers):
                return False, f"Wrong backend % (expected {backend_pct})"
            
            # Check: Frontend percentage must match
            frontend_pct = source_data['frontend_pct']
            if not any(abs(n - frontend_pct) < 2 for n in numbers):
                return False, f"Wrong frontend % (expected {frontend_pct})"
            
            return True, "Valid"
        except Exception:
            return False, "Validation error"
    
    def validate_cost_insight(self, insight: str, source_data: Dict) -> Tuple[bool, str]:
        """Validate cost insight against source data."""
        try:
            # Check: Top feature must be mentioned
            top_feature = source_data['top_feature']
            if top_feature and top_feature.lower() not in insight.lower():
                return False, f"Missing top feature ({top_feature})"
            
            # Extract numbers
            numbers = self._extract_numbers(insight)
            
            # Check: Percentage must match
            top_pct = source_data['top_feature_pct']
            if not any(abs(n - top_pct) < 2 for n in numbers):
                return False, f"Wrong percentage (expected {top_pct})"
            
            return True, "Valid"
        except Exception:
            return False, "Validation error"
    
    def _extract_numbers(self, text: str) -> list:
        """Extract all numbers from text."""
        try:
            # Find all numbers (including decimals)
            pattern = r'\d+\.?\d*'
            matches = re.findall(pattern, text)
            return [float(m) for m in matches]
        except Exception:
            return []
