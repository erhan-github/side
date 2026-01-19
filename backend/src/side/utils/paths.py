
import os
from pathlib import Path

def get_repo_root(current_path: Path | str | None = None) -> Path:
    """
    Find the repository root by looking for .git or .side marker.
    Defaults to current directory if not found.
    """
    if current_path is None:
        current_path = Path.cwd()
    
    current_path = Path(current_path).resolve()
    
    # Preferred: Find the nearest directory with a .git marker
    for parent in [current_path] + list(current_path.parents):
        if (parent / ".git").exists():
            return parent
            
    # Fallback: Find the nearest .side dir (excluding the Global home one)
    for parent in [current_path] + list(current_path.parents):
        if (parent / ".side").exists() and parent != Path.home():
            return parent
            
    return current_path

def get_side_dir(current_path: Path | str | None = None) -> Path:
    """Get the standardized .side directory at repository root."""
    root = get_repo_root(current_path)
    side_dir = root / ".side"
    side_dir.mkdir(exist_ok=True)
    return side_dir
