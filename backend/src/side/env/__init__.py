"""
Sidelith Environment Engine.
Deterministic path resolution and high-integrity environment state management.
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("side")

def load_env_file() -> None:
    """Load environment variables from .env file."""
    # Check multiple possible locations (in priority order)
    possible_paths = [
        # Project root (side/.env) - most likely location
        Path(__file__).parent.parent.parent / ".env",
        # Current working directory
        Path.cwd() / ".env",
        # Parent of cwd (if running from src/)
        Path.cwd().parent / ".env",
        # User config directory
        Path.home() / ".side" / ".env",
    ]

    for env_path in possible_paths:
        try:
            env_path = env_path.expanduser().resolve()
            if env_path.exists():
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip().strip("'\"")
                            if key and value and key not in os.environ:
                                os.environ[key] = value
                break  # Use first found .env
        except Exception:
            continue
    
    # [High-Integrity] Scenario 61 Fix: Insecure Env Loading
    # Verify .env permissions (should be 600 or 400)
    dotenv_path = Path(".env")
    if dotenv_path.exists():
        import stat
        mode = dotenv_path.stat().st_mode
        if mode & stat.S_IRGRP or mode & stat.S_IROTH:
            logger.warning("⚠️ SECURITY WARNING: .env file is world-readable (mode %o). Recommend 'chmod 600 .env'.", mode & 0o777)

class EnvironmentEngine:
    """
    Centralized path provider for Sidelith.
    """
    
    _instance: Optional["EnvironmentEngine"] = None
    _root_override: Optional[Path] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def override_root(cls, path: Optional[Path]) -> None:
        """Override the root path."""
        cls._root_override = path
    
    @classmethod
    def get_side_root(cls) -> Path:
        """Get the Sidelith root directory."""
        if cls._root_override is not None:
            return cls._root_override
        
        env_root = os.getenv("SIDE_ROOT")
        if env_root:
            return Path(env_root).resolve()
        
        return Path.home() / ".side"
    
    @classmethod
    def get_db_path(cls, project_id: Optional[str] = None) -> Path:
        """Get the context database path."""
        root = cls.get_side_root()
        if project_id:
            return root / "contexts" / f"{project_id}.db"
        return root / "context.db"
    
    @classmethod
    def get_log_dir(cls) -> Path:
        """Get the log directory."""
        return cls.get_side_root() / "logs"
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist."""
        dirs = [
            cls.get_side_root(),
            cls.get_log_dir(),
        ]
        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def load_env():
        """Expose load_env_file via the engine."""
        load_env_file()

# Singleton instance
env = EnvironmentEngine()
# Auto-load env on import (Standard practice for this system)
load_env_file()

__all__ = [
    "env",
    "EnvironmentEngine",
    "load_env_file",
]
