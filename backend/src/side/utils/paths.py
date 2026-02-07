
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
    """
    Get the standardized .side directory.
    
    DEPRECATION NOTE: This function now delegates to EnvironmentEngine
    for consistent path resolution across the entire codebase.
    The `current_path` parameter is ignored for backwards compatibility.
    
    Returns:
        Path to the global Sidelith data directory (~/.side-mcp by default).
    """
    from side.env import env
    root = env.get_side_root()
    root.mkdir(parents=True, exist_ok=True)
    return root

def mask_path(absolute_path: str | Path | None, human: bool = False) -> str:
    """
    Mask absolute system paths for privacy.
    - if human=True: /Users/.../side -> ./ (Root)
    - if human=False: /Users/.../side -> @.
    """
    is_root = absolute_path is None or str(absolute_path).lower() in ["project", "project root", ".", "./"]
    
    if is_root:
        return "./ (Root)" if human else "@."
        
    path_obj = Path(absolute_path)
    if not path_obj.is_absolute():
        return f"@{absolute_path}" if not human else str(absolute_path)
        
    try:
        repo_root = get_repo_root()
        if path_obj.is_relative_to(repo_root):
            rel = str(path_obj.relative_to(repo_root))
            return f"@{rel}" if not human else rel
            
        # Fallback: Just return the filename if it's outside repo
        return f"@{path_obj.name}" if not human else path_obj.name
    except Exception:
        name = str(path_obj.name)
        return f"@{name}" if not human else name
