"""
"""
System Protocol v4: Distributed Indexing.
Implements Sparse Context Retrieval with O(1) Local Update Latency.

Architectural Principles:
1. Structural Truth: Extract method signatures and signal heuristics.
2. Sparse State: Only persist 'Complex' nodes to minimize disk I/O.
3. Zero-Trust Localism: All telemetry remains within the Merkle root.
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
REGEX_STRUCTURAL = {
    "python": {
        "class": re.compile(r'^class\s+(\w+)', re.MULTILINE),
        "def": re.compile(r'^def\s+(\w+)', re.MULTILINE)
    },
    "javascript": {
        "class": re.compile(r'\bclass\s+(\w+)', re.MULTILINE),
        "def": re.compile(r'\bfunction\s+(\w+)', re.MULTILINE)
    },
    "ruby": {
        "class": re.compile(r'^class\s+(\w+)', re.MULTILINE),
        "def": re.compile(r'^def\s+(\w+)', re.MULTILINE)
    },
    "php": {
        "class": re.compile(r'\bclass\s+(\w+)', re.MULTILINE),
        "def": re.compile(r'\bfunction\s+(\w+)', re.MULTILINE)
    },
    "go": {
        "class": re.compile(r'^type\s+(\w+)\s+struct', re.MULTILINE),
        "def": re.compile(r'^func\s+(?:\([^)]*\)\s+)?(\w+)', re.MULTILINE)
    },
    "dotnet": {
        "class": re.compile(r'\b(?:class|struct|interface)\s+(\w+)', re.MULTILINE),
        "def": re.compile(r'\b(?:public|private|protected|internal|static)?\s+(?:\w+)\s+(\w+)\s*\([^)]*\)\s*{', re.MULTILINE)
    },
    "swift": {
        "class": re.compile(r'\b(?:class|struct|enum|protocol)\s+(\w+)', re.MULTILINE),
        "def": re.compile(r'\bfunc\s+(\w+)', re.MULTILINE)
    },
    "kotlin": {
        "class": re.compile(r'\b(?:class|interface|object)\s+(\w+)', re.MULTILINE),
        "def": re.compile(r'\bfun\s+(\w+)', re.MULTILINE)
    }
}

# Signals to watch for (Technology Detection)
# These allow the indexer to 'smell' the architecture of a file without deep parsing.
SIGNALS = {
    # Web & UI (The Visual Surface)
    "NextJS": re.compile(r'next/navigation|next/link', re.IGNORECASE),
    "React": re.compile(r'react', re.IGNORECASE),
    "Vue": re.compile(r'vue', re.IGNORECASE),
    "Svelte": re.compile(r'svelte', re.IGNORECASE),
    "Tailwind": re.compile(r'tailwind', re.IGNORECASE),
    "Zustand": re.compile(r'zustand', re.IGNORECASE),
    "TanStack": re.compile(r'tanstack|react-query', re.IGNORECASE),
    
    # Backend & Frameworks (The Logic Core)
    "FastAPI": re.compile(r'fastapi', re.IGNORECASE),
    "Django": re.compile(r'django', re.IGNORECASE),
    "Flask": re.compile(r'flask', re.IGNORECASE),
    "Laravel": re.compile(r'laravel|illuminate', re.IGNORECASE),
    "Rails": re.compile(r'rails|active_record', re.IGNORECASE),
    "Spring": re.compile(r'springframework', re.IGNORECASE),
    "DotNetCore": re.compile(r'Microsoft\.AspNetCore', re.IGNORECASE),
    "GoGin": re.compile(r'gin-gonic', re.IGNORECASE),
    
    # Infrastructure & Persistence (The Foundation)
    "Stripe": re.compile(r'stripe', re.IGNORECASE),
    "Supabase": re.compile(r'supabase', re.IGNORECASE),
    "Firebase": re.compile(r'firebase', re.IGNORECASE),
    "Alchemy": re.compile(r'alchemy', re.IGNORECASE),
    "Redlock": re.compile(r'redlock|redis', re.IGNORECASE),
    "Prisma": re.compile(r'prisma', re.IGNORECASE),
    "TypeORM": re.compile(r'typeorm', re.IGNORECASE),
    "EntityFramework": re.compile(r'EntityFramework', re.IGNORECASE),
    
    # Security & Auth (The Security Shield)
    "Auth0": re.compile(r'auth0', re.IGNORECASE),
    "Clerk": re.compile(r'clerk', re.IGNORECASE),
    "OAuth2": re.compile(r'oauth2|oidc', re.IGNORECASE),
}

# --- CONTEXT FILTERING ---
# "Code is Truth. Docs are Noise."
# We exclude artifacts that increase Context Entropy while preserving 'Strategic Anchor' files.
DENIED_EXTENSIONS = {
    ".md", ".markdown", ".txt", ".rst", ".adoc",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".lock", ".map", ".tmp", ".log"
}

ALLOWED_FILES = {
    "task.md", "README.md", "SYSTEM_ANCHOR.md", 
    "walkthrough.md", "implementation_plan.md",
    ".cursorrules", ".editorconfig", "package.json", 
    "pyproject.toml", "Dockerfile", "go.mod", "Gemfile", "composer.json"
}

try:
    from tree_sitter_languages import get_language, get_parser
    TS_AVAILABLE = True
except ImportError:
    TS_AVAILABLE = False

from side.services.ignore import ProjectIgnore

logger = logging.getLogger(__name__)

def get_file_semantics(path: Path, content: str) -> Dict[str, Any]:
    """Semantic extraction from file content."""
    semantics = {
        "classes": [],
        "functions": [],
        "signals": [],
        "entities": [],      # For OntologyStore
        "relationships": [] # For OntologyStore
    }
    
    # 1. Structural Extraction (Universal)
    ext_to_lang = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".rb": "ruby",
        ".php": "php",
        ".go": "go",
        ".cs": "c_sharp",
        ".swift": "swift",
        ".kt": "kotlin",
        ".java": "java"
    }
    
    lang_id = ext_to_lang.get(path.suffix)
    # print(f"🔍 [SEMANTICS]: {path.name} -> {lang_id}")
    
    # --- TREE-SITTER DEEP SCAN (IF AVAILABLE) ---
    if TS_AVAILABLE and lang_id:
        try:
            parser = get_parser(lang_id)
            language = get_language(lang_id)
            tree = parser.parse(bytes(content, "utf8"))
            
            # Simple queries for classes and functions
            query_str = ""
            if lang_id == "python":
                query_str = """
                (class_definition name: (identifier) @class.name)
                (function_definition name: (identifier) @func.name)
                (call function: (identifier) @call.name)
                (call function: (attribute attribute: (identifier) @call.method))
                """
            elif lang_id in ["javascript", "typescript"]:
                query_str = """
                (class_declaration name: (identifier) @class.name)
                (function_declaration name: (identifier) @func.name)
                (call_expression function: (identifier) @call.name)
                (call_expression function: (member_expression property: (property_identifier) @call.method))
                """
            
            if query_str:
                query = language.query(query_str)
                captures = query.captures(tree.root_node)
                
                for node, tag in captures:
                    name = node.text.decode("utf8")
                    if "class.name" in tag:
                        semantics["classes"].append(name)
                        semantics["entities"].append({"name": name, "type": "class"})
                    elif "func.name" in tag:
                        semantics["functions"].append(name)
                        semantics["entities"].append({"name": name, "type": "function"})
                    elif "call.name" in tag or "call.method" in tag:
                        # Relationship candidates
                        semantics["relationships"].append({"target": name, "type": "calls"})
                
                # If we have AST results, we can skip regex
                if semantics["classes"] or semantics["functions"]:
                    return semantics
        except Exception as e:
            logger.debug(f"Tree-sitter scan failed for {path}: {e}")

    # --- REGEX FALLBACK ---
    lang = lang_id # Normalize for REGEX_STRUCTURAL mapping if needed
    if lang == "c_sharp": lang = "dotnet"
    
    if lang and lang in REGEX_STRUCTURAL:
        semantics["classes"] = REGEX_STRUCTURAL[lang]["class"].findall(content)
        semantics["functions"] = REGEX_STRUCTURAL[lang]["def"].findall(content)
    
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

def generate_local_index(directory: Path, ontology_store=None) -> Dict[str, Any]:
    """Generates the Context Index for a single directory."""
    files = []
    children_checksums = {}
    aggregated_signals = set()
    total_classes = 0
    total_functions = 0
    
    project_id = ontology_store.engine.get_project_id() if ontology_store else "default"
    
    ignore_service = ProjectIgnore(directory)
    # Finding project root for ignore service
    try:
        project_root_path = directory
        while not (project_root_path / ".git").exists() and project_root_path.parent != project_root_path:
            project_root_path = project_root_path.parent
        ignore_service = ProjectIgnore(project_root_path)
    except:
        ignore_service = ProjectIgnore(directory)

    has_subdirs = False
    
    # [PERFORMANCE SPRINT I] Parallel file scanning
    with ThreadPoolExecutor(max_workers=8) as executor:
        items_to_scan = [item for item in directory.iterdir() if not ignore_service.should_ignore(item)]
        
        file_items = []
        for i in items_to_scan:
            if not i.is_file():
                continue
                
            # [CONTEXT FILTER]: Apply the "Signal Only" logic
            # 1. Allow Exception List explicitly
            if i.name in ALLOWED_FILES:
                file_items.append(i)
                continue
                
            # 2. Deny Noise Extensions
            if i.suffix in DENIED_EXTENSIONS:
                continue
                
            file_items.append(i)

        dna_results = list(executor.map(get_file_dna, file_items))
        
        for dna in dna_results:
            files.append(dna)
            if "semantics" in dna:
                sem = dna["semantics"]
                aggregated_signals.update(sem.get("signals", []))
                total_classes += len(sem.get("classes", []))
                total_functions += len(sem.get("functions", []))

                # 🧬 ONTOLOGY PERSISTENCE
                if ontology_store:
                    file_rel_path = str(dna["name"])
                    entities_to_save = []
                    for ent in sem.get("entities", []):
                        ent_id = hashlib.sha256(f"{project_id}:{ent['name']}:{ent['type']}".encode()).hexdigest()[:16]
                        entities_to_save.append({
                            "id": ent_id,
                            "project_id": project_id,
                            "name": ent["name"],
                            "entity_type": ent["type"],
                            "file_path": file_rel_path
                        })
                    if entities_to_save:
                        ontology_store.save_entities_batch(entities_to_save)
                    
                    # Relationships (Simplified logic: entities in same file 'reference' each other)
                    # Future: Use Tree-sitter 'calls' for high-precision
                    relationships_to_save = []
                    for rel in sem.get("relationships", []):
                        # Find target entity ID (if already indexed or known)
                        target_id = hashlib.sha256(f"{project_id}:{rel['target']}:function".encode()).hexdigest()[:16]
                        # Source ID would be the current function/class if we tracked the traversal
                        # For now, we link the FILE to the entity
                        file_id = hashlib.sha256(f"{project_id}:{file_rel_path}:file".encode()).hexdigest()[:16]
                        relationships_to_save.append({
                            "id": hashlib.sha256(f"{file_id}:{target_id}:{rel['type']}".encode()).hexdigest()[:16],
                            "project_id": project_id,
                            "source_id": file_id,
                            "target_id": target_id,
                            "relation_type": rel["type"]
                        })
                    if relationships_to_save:
                        ontology_store.save_relationships_batch(relationships_to_save)

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
    
    # --- HEURISTIC (Complexity Analysis) ---
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

def run_context_scan(root: Path, ontology_store=None):
    """
    Runs a pruning Top-Down scan to gather directories, 
    then processes them Bottom-Up to ensure Merkle integrity.
    """
    ignore_service = ProjectIgnore(root)
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
        index_data = generate_local_index(current_dir, ontology_store=ontology_store)
        
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

def update_branch(root: Path, changed_path: Path, ontology_store=None):
    """
    Optimized update: Only re-indexes the folders from the changed file up to the root.
    """
    if not changed_path.exists() and not changed_path.parent.exists():
        return

    ignore_service = ProjectIgnore(root)

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
            
        print(f"⚡ Context Update: {current_dir}")
        index_data = generate_local_index(current_dir, ontology_store=ontology_store)
        
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
    print(f"🚀 Starting Deep Context Scan on: {target}")
    run_context_scan(target)
    print("✨ Deep Intelligence Context Tree Generated.")
