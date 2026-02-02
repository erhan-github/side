"""
Sovereign Protocol v3: The Fractal Indexer (Deep Intel Upgrade).
Generates a distributed 'Merkle Tree' of Context with Palantir-level Intelligence.

Changes:
- Added Deep Semantic Parsing (Classes, Functions, Signals).
- Optimized with pre-compiled regex.
- Trust Code over Docs (Active Code Reading).
"""

import os
import json
import hashlib
import re
import logging
from pathlib import Path
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
from side.utils.crypto import shield

# --- PERFORMANCE CONFIG ---
# Pre-compiled regex for micro-second parsing
REGEX_PY_CLASS = re.compile(r'^class\s+(\w+)', re.MULTILINE)
REGEX_PY_DEF = re.compile(r'^def\s+(\w+)', re.MULTILINE)

# Signals to watch for (The 'Shadow Intelligence')
SIGNALS = {
    "FastAPI": re.compile(r'fastapi', re.IGNORECASE),
    "Stripe": re.compile(r'stripe', re.IGNORECASE),
    "Supabase": re.compile(r'supabase', re.IGNORECASE),
    "Alchemy": re.compile(r'alchemy', re.IGNORECASE),
    "NextJS": re.compile(r'next', re.IGNORECASE),
    "Tailwind": re.compile(r'tailwind', re.IGNORECASE),
    "React": re.compile(r'react', re.IGNORECASE),
    "Zustand": re.compile(r'zustand', re.IGNORECASE),
    "Zustand": re.compile(r'zustand', re.IGNORECASE),
}

# --- KARPATHY FILTERING PROTOCOL ---
# "Code is Truth. Docs are Noise."
KARPATHY_DENY_EXTENSIONS = {
    ".md", ".markdown", ".txt", ".rst", ".adoc",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".lock", ".map"
}

# The "Control Plane" Exceptions
KARPATHY_ALLOW_FILES = {
    "task.md",
    "walkthrough.md",
    "implementation_plan.md",
    ".cursorrules",
    ".editorconfig",
    "package.json", 
    "pyproject.toml",
    "Dockerfile",
    "docker-compose.yml",
    "requirements.txt",
    ".gitignore"
}

from side.services.ignore import SovereignIgnore

logger = logging.getLogger(__name__)

def get_file_semantics(path: Path, content: str) -> Dict[str, Any]:
    """Palantir-level semantic extraction from file content."""
    semantics = {
        "classes": [],
        "functions": [],
        "signals": []
    }
    
    # 1. Structural Extraction (Python)
    if path.suffix == ".py":
        semantics["classes"] = REGEX_PY_CLASS.findall(content)
        semantics["functions"] = REGEX_PY_DEF.findall(content)
    
    # 2. Signal Extraction (Cross-Language)
    for signal_name, regex in SIGNALS.items():
        if regex.search(content):
            semantics["signals"].append(signal_name)
            
    return semantics

def get_file_dna(path: Path) -> Dict[str, Any]:
    """Extracts deep DNA from a file (Structure + Semantics)."""
    try:
        content = path.read_text(errors='ignore')
        size = path.stat().st_size
        
        # Build DNA
        dna = {
            "name": path.name,
            "type": path.suffix,
            "size": size,
            "lines": len(content.splitlines()),
            "hash": hashlib.sha256(content.encode()).hexdigest()[:16],
            "semantics": get_file_semantics(path, content)
        }
        
        # [PURGE]: 'Strategic Capture' removed. Files are only indexed for Structure, not Text.
        # if path.name in ["STRATEGY.md", "README.md", "ARCHITECTURE.md"]:
        #     dna["brief"] = content[:1000]
            
        return dna
    except Exception:
        return {"name": path.name, "error": "unreadable"}

def generate_local_index(directory: Path) -> Dict[str, Any]:
    """Generates the V3 Fractal Index for a single directory."""
    files = []
    children_checksums = {}
    aggregated_signals = set()
    total_classes = 0
    total_functions = 0
    
    ignore_service = SovereignIgnore(directory)
    # Finding project root for ignore service
    try:
        project_root_path = directory
        while not (project_root_path / ".git").exists() and project_root_path.parent != project_root_path:
            project_root_path = project_root_path.parent
        ignore_service = SovereignIgnore(project_root_path)
    except:
        ignore_service = SovereignIgnore(directory)

    has_subdirs = False
    
    # [PERFORMANCE SPRINT I] Parallel file scanning
    with ThreadPoolExecutor(max_workers=8) as executor:
        items_to_scan = [item for item in directory.iterdir() if not ignore_service.should_ignore(item)]
        
        file_items = []
        for i in items_to_scan:
            if not i.is_file():
                continue
                
            # [KARPATHY FILTER]: Apply the "Signal Only" logic
            # 1. Allow Exception List explicitly
            if i.name in KARPATHY_ALLOW_FILES:
                file_items.append(i)
                continue
                
            # 2. Deny Noise Extensions
            if i.suffix in KARPATHY_DENY_EXTENSIONS:
                continue
                
            # 3. Default Allow (Code)
            file_items.append(i)

        dna_results = list(executor.map(get_file_dna, file_items))
        
        for dna in dna_results:
            files.append(dna)
            if "semantics" in dna:
                sem = dna["semantics"]
                aggregated_signals.update(sem.get("signals", []))
                total_classes += len(sem.get("classes", []))
                total_functions += len(sem.get("functions", []))

        for item in items_to_scan:
            if item.is_dir() and item.name != ".side":
                has_subdirs = True
                child_index = item / ".side" / "local.json"
                if child_index.exists():
                    try:
                        raw_data = shield.unseal_file(child_index)
                        data = json.loads(raw_data)
                        children_checksums[item.name] = data.get("checksum", "unknown")
                    except:
                        pass
    
    # --- KARPATHY HEURISTIC (Complexity Analysis) ---
    is_complex = (
        len(files) >= 5 or 
        total_classes > 0 or 
        total_functions >= 3 or 
        has_subdirs or 
        len(aggregated_signals) > 0
    )
    
    # Calculate Self Checksum (Merkle-like)
    payload = json.dumps({"files": files, "children": children_checksums}, sort_keys=True)
    checksum = hashlib.sha256(payload.encode()).hexdigest()[:16]
    
    index_data = {
        "protocol": "v3.sparse",
        "path": str(directory),
        "checksum": checksum,
        "is_complex": is_complex,
        "dna": {
            "signals": list(aggregated_signals)
        },
        "context": {
            "files": files,
            "children": children_checksums
        }
    }
    
    return index_data

def run_fractal_scan(root: Path):
    """
    Runs a pruning Top-Down scan to gather directories, 
    then processes them Bottom-Up to ensure Merkle integrity.
    """
    ignore_service = SovereignIgnore(root)
    dirs_to_process = []

    # 1. Top-Down Pruning Pass
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        current_dir = Path(dirpath)
        
        # Modify dirnames in-place to prune the traversal
        dirnames[:] = [d for d in dirnames if not ignore_service.should_ignore(current_dir / d)]
        
        # Don't index .side folders or the root itself (root processed last)
        if current_dir.name == ".side":
            continue
            
        dirs_to_process.append(current_dir)

    # 2. Bottom-Up Processing Pass (Reverse order)
    for current_dir in reversed(dirs_to_process):
        # Skip .git and root is handled explicitly if needed, 
        # but reversed(dirs_to_process) includes root at the end.
        
        print(f"🔮 Deep Indexing: {current_dir}")
        index_data = generate_local_index(current_dir)
        
        # SPARSE WRITE LOGIC
        is_root = current_dir == root
        side_dir = current_dir / ".side"
        
        if index_data["is_complex"] or is_root:
            side_dir.mkdir(exist_ok=True)
            shield.seal_file(side_dir / "local.json", json.dumps(index_data, indent=2))
        else:
            import shutil
            if side_dir.exists():
                shutil.rmtree(side_dir)

def update_branch(root: Path, changed_path: Path):
    """
    Optimized update: Only re-indexes the folders from the changed file up to the root.
    """
    if not changed_path.exists() and not changed_path.parent.exists():
        return

    ignore_service = SovereignIgnore(root)

    # Start from the parent directory of the changed file
    current_dir = changed_path.parent if changed_path.is_file() else changed_path
    
    while True:
        # Stop if we are outside the root
        try:
            current_dir.relative_to(root)
        except ValueError:
            break
            
        # skip ignore dirs
        if ignore_service.should_ignore(current_dir):
            break
            
        print(f"⚡ Fractal Update: {current_dir}")
        index_data = generate_local_index(current_dir)
        
        side_dir = current_dir / ".side"
        is_root = current_dir == root
        
        if index_data["is_complex"] or is_root:
            side_dir.mkdir(exist_ok=True)
            shield.seal_file(side_dir / "local.json", json.dumps(index_data, indent=2))
        else:
            import shutil
            if side_dir.exists():
                shutil.rmtree(side_dir)
        
        if current_dir == root:
            break
        current_dir = current_dir.parent

if __name__ == "__main__":
    import sys
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    print(f"🚀 Starting Deep Fractal Scan on: {target}")
    run_fractal_scan(target)
    print("✨ Deep Intelligence Context Tree Generated.")
