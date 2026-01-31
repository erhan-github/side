"""
Sovereign Language Detector - Fingerprinting for Polyglot Analysis.
"""

import logging
from pathlib import Path
from typing import List, Set

logger = logging.getLogger(__name__)

def detect_primary_languages(project_path: Path) -> Set[str]:
    """
    Detects which languages are used in the project based on file patterns.
    Returns a set of normalized language identifiers (e.g., 'python', 'javascript').
    """
    languages = set()
    EXCLUDE_DIRS = {".git", "node_modules", "venv", ".venv", "dist", "build", "target"}
    
    import os
    
    # Efficient walk that prunes excluded directories
    for root, dirs, files in os.walk(project_path):
        # Prune dirs in-place to avoid descending into them
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for name in files:
            if name == "requirements.txt" or name == "setup.py" or name == "pyproject.toml":
                languages.add("python")
            elif name == "package.json":
                languages.add("javascript")
            elif name == "tsconfig.json":
                languages.add("typescript")
            elif name == "go.mod":
                languages.add("go")
            elif name == "Cargo.toml":
                languages.add("rust")
            elif name == "pom.xml" or name == "build.gradle":
                languages.add("java")
                
            ext = os.path.splitext(name)[1]
            if ext == ".py": languages.add("python")
            elif ext == ".js": languages.add("javascript")
            elif ext == ".ts" or ext == ".tsx": languages.add("typescript")
            elif ext == ".go": languages.add("go")
            elif ext == ".rs": languages.add("rust")
            elif ext == ".swift": languages.add("swift")
            elif ext == ".kt" or ext == ".kts": languages.add("kotlin")
            elif ext == ".java": languages.add("java")

    logger.info(f"🔍 [DETECTOR] Detected languages: {list(languages)}")
    return languages
