"""
Environment configuration for Side.
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger("side-mcp")

def load_env_file() -> None:
    """Load environment variables from .env file."""
    # Check multiple possible locations (in priority order)
    possible_paths = [
        # Project root (side-mcp/.env) - most likely location
        Path(__file__).parent.parent.parent / ".env",
        # Current working directory
        Path.cwd() / ".env",
        # Parent of cwd (if running from src/)
        Path.cwd().parent / ".env",
        # User config directory
        Path.home() / ".side-mcp" / ".env",
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
    
    # [Hyper-Ralph] Scenario 61 Fix: Insecure Env Loading
    # Verify .env permissions (should be 600 or 400)
    dotenv_path = Path(".env")
    if dotenv_path.exists():
        import stat
        mode = dotenv_path.stat().st_mode
        if mode & stat.S_IRGRP or mode & stat.S_IROTH:
            logger.warning("⚠️ SECURITY WARNING: .env file is world-readable (mode %o). Recommend 'chmod 600 .env'.", mode & 0o777)
