import os
from pathlib import Path
from typing import List, Optional, Any

try:
    import pathspec
except ImportError:
    pathspec = None

class FallbackSpec:
    """Safe fallback if pathspec is unavailable."""
    def match_file(self, path: str) -> bool:
        return False
    @staticmethod
    def from_lines(style, patterns):
        return FallbackSpec()

class IgnoreStore:
    """
    Ignore Store [Tier-3]: Handles .gitignore inheritance for Sidelith services.
    Ensures that the Watcher and PulseEngine respect local and global ignore rules.
    """
    
    def __init__(self, root_path: str | Path):
        self.root_path = Path(root_path).resolve()
        self.spec = self._load_all_gitignores()

    def _load_all_gitignores(self) -> Any:
        """Finds and combines all .gitignore files from the root downwards."""
        if pathspec is None:
            return FallbackSpec()

        patterns = []
        # Standard Sidelith ignores
        patterns.extend([
            '.git/', '.side/', '__pycache__/', '*.pyc', 
            '.DS_Store', 'node_modules/', 'dist/', 'build/'
        ])
        
        # Load .gitignore files
        for gitignore in self.root_path.rglob(".gitignore"):
            try:
                with open(gitignore, "r") as f:
                    patterns.extend(f.readlines())
            except Exception:
                continue
                
        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)

    def is_ignored(self, path: str | Path) -> bool:
        """Check if a path should be ignored based on our compiled spec."""
        try:
            path_obj = Path(path).resolve()
            if path_obj.is_relative_to(self.root_path):
                rel_path = path_obj.relative_to(self.root_path)
                return self.spec.match_file(str(rel_path))
            return False
        except Exception:
            return True # Fail-safe to ignored

# Singleton helper (though usually instantiated per project root)
_instances = {}

def get_ignore_store(root: str | Path) -> IgnoreStore:
    root = str(Path(root).resolve())
    if root not in _instances:
        _instances[root] = IgnoreStore(root)
    return _instances[root]
