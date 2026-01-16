"""
CSO.ai Intelligence Domains.

Specialized analyzers for different intelligence areas:
- Technical: Code, architecture, dependencies
- Business: Stage, model, priorities
- Market: Trends, competitors, opportunities
- Strategist: LLM-powered strategic advisor
- Embeddings: Vector embeddings for semantic search
"""

from cso_ai.intel.technical import TechnicalAnalyzer
from cso_ai.intel.business import BusinessAnalyzer
from cso_ai.intel.market import MarketAnalyzer
from cso_ai.intel.strategist import Strategist
from cso_ai.intel.embeddings import (
    EmbeddingProvider,
    embed_text,
    embed_article,
    get_embedding_provider,
)

__all__ = [
    "TechnicalAnalyzer",
    "BusinessAnalyzer",
    "MarketAnalyzer",
    "Strategist",
    "EmbeddingProvider",
    "embed_text",
    "embed_article",
    "get_embedding_provider",
]
