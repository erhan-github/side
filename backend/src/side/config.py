"""
Sidelith Configuration Engine.

Centralized configuration for the Sidelith SDK.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from side.env import env


PROJECT_NAME = "sidelith"


@dataclass
class SideConfig:
    """Configuration for sideMCP."""

    # Data storage (local fallback)
    data_dir: Path = field(default_factory=lambda: env.get_side_root())
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


    enabled_sources: list[str] = field(
        default_factory=lambda: ["hackernews", "lobsters", "github"]
    )

    # Service Throttling & Synchronization
    service_audit_interval: int = 86400  # 24 hours
    watcher_debounce: float = 2.0        # Seconds
    watcher_high_io_threshold: int = 50  # Events per 10s before circuit break
    buffer_flush_interval: int = 60      # Seconds
    heartbeat_interval: int = 30         # Seconds
    verification_window_hours: int = 1   # Baseline ground truth window

    # Resource Limits (Production Safety)
    max_memory_mb: int = field(default_factory=lambda: int(os.getenv("MAX_MEMORY_MB", "2048")))
    auto_restart_threshold_mb: int = field(default_factory=lambda: int(os.getenv("AUTO_RESTART_THRESHOLD_MB", "3072")))
    memory_warning_threshold_mb: int = field(default_factory=lambda: int(os.getenv("MEMORY_WARNING_THRESHOLD_MB", "1536")))
    max_cache_entries: int = field(default_factory=lambda: int(os.getenv("MAX_CACHE_ENTRIES", "10000")))
    cache_eviction_batch_size: int = field(default_factory=lambda: int(os.getenv("CACHE_EVICTION_BATCH_SIZE", "1000")))
    max_file_watchers: int = field(default_factory=lambda: int(os.getenv("MAX_FILE_WATCHERS", "5")))
    max_pending_changes: int = field(default_factory=lambda: int(os.getenv("MAX_PENDING_CHANGES", "1000")))
    memory_check_interval: int = field(default_factory=lambda: int(os.getenv("MEMORY_CHECK_INTERVAL", "60")))
    
    # Feature Flags
    enable_auto_restart: bool = field(default_factory=lambda: os.getenv("ENABLE_AUTO_RESTART", "false").lower() == "true")
    enable_cache_eviction: bool = field(default_factory=lambda: os.getenv("ENABLE_CACHE_EVICTION", "true").lower() == "true")
    enable_advanced_scavengers: bool = field(default_factory=lambda: os.getenv("ENABLE_ADVANCED_SCAVENGERS", "false").lower() == "true")

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
