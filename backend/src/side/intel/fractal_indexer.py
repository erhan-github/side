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
from pathlib import Path
from typing import Dict, Any, List
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
            "hash": hashlib.md5(content.encode()).hexdigest()[:8],
            "semantics": get_file_semantics(path, content)
        }
        
        # Strategic Capture: Capture first few lines of main files
        if path.name in ["STRATEGY.md", "README.md", "ARCHITECTURE.md"]:
            dna["brief"] = content[:1000]
            
        return dna
    except Exception:
        return {"name": path.name, "error": "unreadable"}

def generate_local_index(directory: Path) -> Dict[str, Any]:
    """Generates the V3 Fractal Index for a single directory."""
    files = []
    children_checksums = {}
    aggregated_signals = set()
    
    ignore_service = SovereignIgnore(directory) # In a real implementation this should be passed in or single-instanced
    # But for a script run, we instantiate based on the directory root (assuming project root above)
    # To resolve properly, we try to find the project root.
    try:
        project_root = SimplifiedDatabase.get_project_id() # Logic to get root is implicit in CLI usually
        # Fallback for script usage:
        project_root_path = directory
        while not (project_root_path / ".git").exists() and project_root_path.parent != project_root_path:
            project_root_path = project_root_path.parent
        ignore_service = SovereignIgnore(project_root_path)
    except:
        ignore_service = SovereignIgnore(directory) # Fallback

    for item in directory.iterdir():
        if ignore_service.should_ignore(item):
            continue
            
        if item.is_file():
            dna = get_file_dna(item)
            files.append(dna)
            if "semantics" in dna:
                aggregated_signals.update(dna["semantics"].get("signals", []))
        elif item.is_dir():
            child_index = item / ".side" / "local.json"
            if child_index.exists():
                try:
                    # USE SHIELD TO DECRYPT CHILD INDEX
                    raw_data = shield.unseal_file(child_index)
                    data = json.loads(raw_data)
                    children_checksums[item.name] = data.get("checksum", "unknown")
                except:
                    pass
    
    # Calculate Self Checksum (Merkle-like)
    payload = json.dumps({"files": files, "children": children_checksums}, sort_keys=True)
    checksum = hashlib.sha256(payload.encode()).hexdigest()[:16]
    
    index_data = {
        "protocol": "v3.fractal",
        "path": str(directory),
        "checksum": checksum,
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
    Runs a Bottom-Up scan to ensure child checksums are ready for parents.
    """
    ignore_service = SovereignIgnore(root)

    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        current_dir = Path(dirpath)
        
        # Prune ignored directories (modify dirnames in place for efficiency if topdown=True, 
        # but since we are topdown=False, we just check current_dir)
        if ignore_service.should_ignore(current_dir):
            continue
            
        # skip .side folders themselves
        if ".side" in current_dir.parts:
            continue

        print(f"🔮 Deep Indexing: {current_dir}")
        index_data = generate_local_index(current_dir)
        
        # Write .side/local.json
        side_dir = current_dir / ".side"
        side_dir.mkdir(exist_ok=True)
        shield.seal_file(side_dir / "local.json", json.dumps(index_data, indent=2))

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
        
        # Write .side/local.json
        side_dir = current_dir / ".side"
        side_dir.mkdir(exist_ok=True)
        shield.seal_file(side_dir / "local.json", json.dumps(index_data, indent=2))
        
        if current_dir == root:
            break
        current_dir = current_dir.parent

if __name__ == "__main__":
    import sys
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    print(f"🚀 Starting Deep Fractal Scan on: {target}")
    run_fractal_scan(target)
    print("✨ Deep Intelligence Context Tree Generated.")
