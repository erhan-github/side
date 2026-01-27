"""
Sidelith Configuration Engine.

Centralized configuration for the Sidelith Sovereign SDK.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path


PROJECT_NAME = "sidelith"


@dataclass
class SideConfig:
    """Configuration for sideMCP."""

    # Data storage (local fallback)
    data_dir: Path = field(default_factory=lambda: Path.home() / f".{PROJECT_NAME}")
    db_name: str = "data.db"

    # Supabase Configuration (cloud storage with tenant isolation)
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None


    # LLM Configuration - Using Groq for fast, free inference (January 2026)
    llm_provider: str = "groq"
    # Model selection by task (2026 benchmarks):
    # - llama-3.1-8b-instant: Fast scoring (277 tok/s, 140ms TTFT)
    # - llama-3.3-70b-versatile: Strategic reasoning (218 tok/s, 110ms TTFT)
    # - llama3-8b-8192: Lightweight fallback
    llm_fast_model: str = "llama-3.1-8b-instant"
    llm_smart_model: str = "llama-3.3-70b-versatile"
    llm_lite_model: str = "llama3-8b-8192"
    llm_api_key: str | None = None  # Set via GROQ_API_KEY env var


    # Sources
    enabled_sources: list[str] = field(
        default_factory=lambda: ["hackernews", "lobsters", "github"]
    )

    def __post_init__(self) -> None:
        """Initialize after creation."""
        # Get API keys from environment if not set
        if self.llm_api_key is None:
            self.llm_api_key = os.environ.get("GROQ_API_KEY")

        # Supabase configuration from environment
        if self.supabase_url is None:
            self.supabase_url = os.environ.get("SUPABASE_URL")
        if self.supabase_anon_key is None:
            self.supabase_anon_key = os.environ.get("SUPABASE_ANON_KEY")
        if self.supabase_service_role_key is None:
            self.supabase_service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

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

    @property
    def has_supabase(self) -> bool:
        """Check if Supabase is properly configured."""
        return bool(
            self.supabase_url
            and self.supabase_anon_key
            and self.supabase_service_role_key
        )


# Global config instance
config = SideConfig()


# Export Supabase settings for easy access
SUPABASE_URL = config.supabase_url or ""
SUPABASE_ANON_KEY = config.supabase_anon_key or ""
SUPABASE_SERVICE_ROLE_KEY = config.supabase_service_role_key or ""
