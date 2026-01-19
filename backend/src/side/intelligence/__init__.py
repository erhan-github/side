"""
Intelligence module for hierarchical memory and insight generation.

Provides Forensic-level longitudinal analysis with:
- 3-tier memory (Recent/Medium/Long-term)
- Token-optimized LLM prompting
- Quality control and validation
- Zero hallucination guarantees
"""

from .data_aggregator import DataAggregator
from .insight_generator import InsightGenerator
from .quality_control import QualityControl
from .insight_cache import InsightCache
from .insight_engine import InsightEngine

__all__ = [
    'DataAggregator',
    'InsightGenerator',
    'QualityControl',
    'InsightCache',
    'InsightEngine'
]
