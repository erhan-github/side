
"""
Sovereign Ignore Service - The Noise Filter.
"""
import logging
from pathlib import Path
from typing import Set, List
import fnmatch

logger = logging.getLogger(__name__)

class SovereignIgnore:
    """
    Central authority for what Sidelith is allowed to see.
    Reads from .sovereignignore in the project root.
    Falls back to Sane Defaults.
    """
    
    # Defaults: What we ALWAYS ignore unless told otherwise.
    DEFAULT_IGNORES = {
        # SCM / System
        ".git", ".svn", ".hg", ".DS_Store",
        # Dependencies / Build
        "node_modules", "venv", ".venv", "env", "dist", "build", "target",
        "__pycache__", "*.pyc", "*.pyo",
        # Sidelith Internals (Don't eat your own brain)
        ".side", ".side-id",
        # Common huge folders
        "coverage", "tmp", "temp", "logs"
    }

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ignore_patterns: Set[str] = set(self.DEFAULT_IGNORES)
        self._load_config()

    def _load_config(self):
        """
        Load ignore patterns from multiple sources.
        Priority: .sovereignignore > .gitignore > Defaults
        """
        self._load_file(".gitignore")
        self._load_file(".sovereignignore")

    def _load_file(self, filename: str):
        """Helper to parse a gitignore-style file."""
        config_path = self.project_root / filename
        if not config_path.exists():
            return

        try:
            content = config_path.read_text("utf-8")
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Normalize directory patterns (remove trailing slash for checking)
                cleaned = line.rstrip("/")
                self.ignore_patterns.add(cleaned)
        except Exception as e:
            logger.warning(f"Failed to read {filename}: {e}")

    def should_ignore(self, path: Path) -> bool:
        """
        Check if a path should be ignored.
        Checks against all loaded patterns.
        """
        # 1. Check strict name match (fast)
        if path.name in self.ignore_patterns:
            return True

        # 2. Check path relative to root
        try:
            rel_path = path.relative_to(self.project_root)
        except ValueError:
            # Path is not inside project root
            return True

        str_path = str(rel_path)
        
        # 3. Check glob patterns
        for pattern in self.ignore_patterns:
            # Match directly
            if fnmatch.fnmatch(path.name, pattern):
                return True
            # Match full relative path (e.g., "backend/secret/*.key")
            if fnmatch.fnmatch(str_path, pattern):
                return True
            # Match directory prefix (e.g., "dist/" matches "dist/bundle.js")
            if str_path.startswith(pattern + "/"):
                return True

        return False
