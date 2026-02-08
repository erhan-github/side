"""
Ignore Filter Service - File exclusion logic.
"""
import logging
from pathlib import Path
from typing import Set, List
import fnmatch

logger = logging.getLogger(__name__)

class IgnoreFilter:
    """
    Central authority for file exclusion rules.
    Reads from .sovereignignore (legacy) or .sideignore and .gitignore.
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

    # Palantir-level default configuration
    DEFAULT_SIDEIGNORE_CONTENT = """# Sidelith Ignore File
# Defines the boundaries of Sidelith's awareness.
# Format: gitignore-style glob patterns.

# 1. System & SCM
.git/
.DS_Store

# 2. Dependencies & Build Artifacts
node_modules/
venv/
.venv/
__pycache__/
dist/
build/
coverage/
.next/

# 3. Sidelith Internals
.side/
.side-id

# 4. Secrets & Environment
.env*
*.key
*.pem
secrets/
*.log
tmp/

# 5. Editor Configs (Optional - reduce noise)
.vscode/
.idea/
"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ignore_patterns: Set[str] = set(self.DEFAULT_IGNORES)
        self._ensure_config_exists()
        self._load_config()

    def _ensure_config_exists(self):
        """
        Auto-create .sideignore if it doesn't exist.
        This ensures users always have a baseline configuration.
        """
        config_path = self.project_root / ".sideignore"
        if not config_path.exists():
            try:
                config_path.write_text(self.DEFAULT_SIDEIGNORE_CONTENT, encoding="utf-8")
                logger.info(f"Created default .sideignore at {config_path}")
            except Exception as e:
                logger.warning(f"Failed to create default .sideignore: {e}")

    def _load_config(self):
        """
        Load ignore patterns from multiple sources.
        Priority: .sideignore > .sovereignignore > .gitignore > Defaults
        """
        self._load_file(".gitignore")
        self._load_file(".sovereignignore") # Legacy support
        self._load_file(".sideignore")

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
        # 1. Fast check for project root itself (never ignore)
        if path == self.project_root:
            return False

        # 2. Check if ANY parent directory is in the ignore list
        # This is the most robust way to handle nested node_modules, etc.
        parts = path.relative_to(self.project_root).parts
        for part in parts:
            if part in self.ignore_patterns:
                return True
            
        # 3. Check glob patterns against the full relative path
        str_path = str(path.relative_to(self.project_root))
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path.name, pattern):
                return True
            if fnmatch.fnmatch(str_path, pattern):
                return True
            if str_path.startswith(pattern + "/"):
                return True

        return False
