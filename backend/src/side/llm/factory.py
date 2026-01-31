"""
[PHASE 4.2] LLMClient Singleton Factory
Eliminates duplicate LLMClient initializations across the codebase.
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Global cache of LLMClient instances by purpose
_client_cache: Dict[str, "LLMClient"] = {}

def get_llm_client(purpose: str = "default", preferred_provider: str = None) -> "LLMClient":
    """
    Returns a cached LLMClient instance for the given purpose.
    
    Args:
        purpose: The purpose of the client (e.g., "reasoning", "intelligence", "analysis").
                 Different purposes may use different model configurations.
        preferred_provider: Optional provider override (e.g., "gemini", "anthropic").
    
    Returns:
        A cached LLMClient instance.
    """
    from side.llm.client import LLMClient
    
    cache_key = f"{purpose}:{preferred_provider or 'auto'}"
    
    if cache_key not in _client_cache:
        logger.info(f"🔧 [LLM Factory]: Creating new client for purpose='{purpose}'")
        _client_cache[cache_key] = LLMClient(
            purpose=purpose,
            preferred_provider=preferred_provider
        )
    
    return _client_cache[cache_key]

def clear_cache():
    """Clears all cached LLMClient instances."""
    global _client_cache
    _client_cache = {}
    logger.info("🧹 [LLM Factory]: Cache cleared.")

def get_reasoning_client() -> "LLMClient":
    """Shortcut for reasoning-purpose client."""
    return get_llm_client(purpose="reasoning")

def get_intelligence_client() -> "LLMClient":
    """Shortcut for intelligence-purpose client."""
    return get_llm_client(purpose="intelligence")

def get_analysis_client() -> "LLMClient":
    """Shortcut for analysis-purpose client."""
    return get_llm_client(purpose="analysis")
