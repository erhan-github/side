"""
CSO.ai Configuration.

Central configuration for the CSO.ai system.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CSOConfig:
    """Configuration for CSO.ai."""

    # Data storage
    data_dir: Path = field(default_factory=lambda: Path.home() / ".cso-ai")
    db_name: str = "data.db"

    # Article fetching
    articles_per_source: int = 50  # How many articles to fetch per source
    fetch_interval_hours: int = 6  # How often to fetch new articles
    keep_articles_days: int = 30  # How long to keep articles

    # LLM Configuration - Using Groq for fast, free inference (January 2026)
    llm_provider: str = "groq"
    # Model selection by task (2026 benchmarks):
    # - llama-3.1-8b-instant: Fast scoring (277 tok/s, 140ms TTFT)
    # - llama-3.3-70b-versatile: Strategic reasoning (218 tok/s, 110ms TTFT)
    # - gemma2-9b-it: Lightweight fallback (814 tok/s, ultra-cheap)
    llm_fast_model: str = "llama-3.1-8b-instant"
    llm_smart_model: str = "llama-3.3-70b-versatile"
    llm_lite_model: str = "gemma2-9b-it"
    llm_api_key: str | None = None  # Set via GROQ_API_KEY env var

    # Scoring
    min_relevance_score: float = 40.0  # Minimum score to consider relevant
    use_llm_for_scoring: bool = True  # Use LLM for scoring (vs heuristics)

    # Sources
    enabled_sources: list[str] = field(
        default_factory=lambda: ["hackernews", "lobsters", "github"]
    )

    def __post_init__(self) -> None:
        """Initialize after creation."""
        # Get API key from environment if not set
        if self.llm_api_key is None:
            self.llm_api_key = os.environ.get("GROQ_API_KEY")

        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

    @property
    def db_path(self) -> Path:
        """Get full database path."""
        return self.data_dir / self.db_name

    @property
    def has_llm(self) -> bool:
        """Check if LLM is available."""
        return self.llm_api_key is not None


# Global config instance
config = CSOConfig()
