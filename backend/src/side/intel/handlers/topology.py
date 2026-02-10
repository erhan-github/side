import logging
import uuid
import json
from pathlib import Path
from typing import Optional
from side.utils.crypto import shield
from side.common.constants import Origin
from side.utils.hashing import sparse_hasher

logger = logging.getLogger(__name__)

class CodeIndexer:
    def __init__(self, project_path: Path, engine, brain_path: Path, buffer=None):
        self.project_path = project_path
        self.engine = engine
        self.brain_path = brain_path
        self.buffer = buffer

    def get_condensed_dna(self) -> str:
        """Extract a high-level architectural summary from the Index."""
        root_index = self.project_path / ".side" / "local.json"
        if not root_index.exists():
            return "DNA Not Found. Run 'side feed' to initialize."
            
        try:
            raw_data = shield.unseal_file(root_index)
            data = json.loads(raw_data)
            signals = data.get("dna", {}).get("signals", [])
            summary = f"Architectural DNA: {', '.join(signals)}\n"
            summary += f"Context Path: {data.get('path', 'root')}\n"
            # Add top-level folder digests
            folders = [k for k,v in data.get("children", {}).items()]
            summary += f"Derived Modules: {', '.join(folders)}"
            return summary
        except Exception as e:
            return f"Strategic DNA extraction failed: {e}"

    def _walk_context_tree(self, path: Path, prefix: str = "") -> str:
        """
        Recursively walks the distributed Context Index to build a tree view.
        """
        tree_out = ""
        index_path = path / ".side" / "local.json"
        
        if not index_path.exists():
            return tree_out
            
        try:
            raw = shield.unseal_file(index_path)
            data = json.loads(raw)
            files = sorted(data.get("context", {}).get("files", []), key=lambda x: x['name'])
            children = sorted(data.get("context", {}).get("children", {}).items())
            
            # 1. Render Files
            for i, f in enumerate(files):
                is_last_item = (i == len(files) - 1) and not children
                connector = "└── " if is_last_item else "├── "
                f_hash = f.get('hash', 'no_hash')[:8]
                tree_out += f"{prefix}{connector}{f['name']} [{f_hash}]\n"
                
            # 2. Render Children (Sub-directories)
            for i, (name, checksum) in enumerate(children):
                is_last_child = (i == len(children) - 1)
                connector = "└── " if is_last_child else "├── "
                tree_out += f"{prefix}{connector}{name}/ [Hash: {checksum[:8]}]\n"
                
                # Recursive Step - FIXED recursion call
                new_prefix = prefix + ("    " if is_last_child else "│   ")
                tree_out += self._walk_context_tree(path / name, new_prefix)
                
            return tree_out
        except Exception as e:
            return f"{prefix}└── [ERROR: {e}]\n"

    async def _harvest_documentation_dna(self):
        """
        Scans walkthroughs and notes to extract key patterns.
        """
        # 1. SCAN LOCATIONS
        doc_paths = [
            self.project_path / "README.md",
            self.brain_path,
        ]
        
        for path in doc_paths:
            if not path.exists():
                continue
            
            files = [path] if path.is_file() else list(path.glob("*.md"))
            
            for f in files:
                try:
                    content = f.read_text()
                    # Segment by headers
                    sections = content.split("\n#")
                    for section in sections:
                        if len(section.strip()) < 50:
                            continue
                            
                        # Generate Signal Hash
                        project_id = self.engine.get_project_id()
                        sig_hash = sparse_hasher.fingerprint(section, salt=project_id)
                        
                        # Store as public_patterns
                        # We use a UUID based on the file and hash to avoid duplicates
                        fragment_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{f.name}:{sig_hash}"))
                        
                        if self.buffer:
                            await self.buffer.ingest("wisdom", {
                                "id": fragment_id,
                                "origin": "local",
                                "category": "documentation",
                                "pattern": f.name,
                                "signal_hash": sig_hash,
                                "text": section[:1000].strip(),
                                "source_type": "documentation",
                                "source_file": str(f),
                                "confidence": 8
                            })
                        else:
                            with self.engine.connection() as conn:
                                conn.execute("""
                                    INSERT OR REPLACE INTO public_patterns (
                                        id, origin_node, category, signal_pattern, 
                                        signal_hash, wisdom_text, source_type, source_file, confidence
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    fragment_id, Origin.LOCAL, "documentation", f.name,
                                    sig_hash, section[:1000].strip(), "documentation", str(f), 8
                                ))
                            
                except Exception as e:
                    logger.warning(f"Failed to harvest DNA from {f}: {e}")

    async def _extract_documentation_patterns(self, file_path: Path):
        """Extracts patterns from a single markdown file."""
        try:
            content = file_path.read_text()
            sections = content.split("\n#")
            project_id = self.engine.get_project_id()
            
            for section in sections:
                if len(section.strip()) < 50: continue
                sig_hash = sparse_hasher.fingerprint(section, salt=project_id)
                fragment_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{file_path.name}:{sig_hash}"))
                
                with self.engine.connection() as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO public_patterns (
                            id, origin_node, category, signal_pattern, 
                            signal_hash, pattern_text, source_type, source_file, confidence
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (fragment_id, "local", "documentation", file_path.name,
                          sig_hash, section[:1000].strip(), "documentation", str(file_path), 9))
            logger.info(f"Extracted fragments from {file_path.name}")
        except Exception as e:
            logger.warning(f"Failed to harvest {file_path.name}: {e}")

    async def scan_single(self, path: Path):
        """Scan a single file for DNA updates."""
        # Placeholder for incremental update
        pass
        self.project_path = project_path
        self.engine = engine
        self.brain_path = brain_path
        self.buffer = buffer

    def get_condensed_dna(self) -> str:
        """Extract a high-level architectural summary from the Fractal Index."""
        root_index = self.project_path / ".side" / "local.json"
        if not root_index.exists():
            return "DNA Not Found. Run 'side feed' to initialize."
            
        try:
            raw_data = shield.unseal_file(root_index)
            data = json.loads(raw_data)
            signals = data.get("dna", {}).get("signals", [])
            summary = f"Architectural DNA: {', '.join(signals)}\n"
            summary += f"Context Path: {data.get('path', 'root')}\n"
            # Add top-level folder digests
            folders = [k for k,v in data.get("children", {}).items()]
            summary += f"Derived Modules: {', '.join(folders)}"
            return summary
        except Exception as e:
            return f"Strategic DNA extraction failed: {e}"

    def _walk_context_tree(self, path: Path, prefix: str = "") -> str:
        """
        Recursively walks the distributed Context Index to build a Merkle Tree.
        """
        tree_out = ""
        index_path = path / ".side" / "local.json"
        
        if not index_path.exists():
            return tree_out
            
        try:
            raw = shield.unseal_file(index_path)
            data = json.loads(raw)
            files = sorted(data.get("context", {}).get("files", []), key=lambda x: x['name'])
            children = sorted(data.get("context", {}).get("children", {}).items())
            
            # 1. Render Files
            for i, f in enumerate(files):
                is_last_item = (i == len(files) - 1) and not children
                connector = "└── " if is_last_item else "├── "
                f_hash = f.get('hash', 'no_hash')[:8]
                tree_out += f"{prefix}{connector}{f['name']} [{f_hash}]\n"
                
            # 2. Render Children (Sub-directories)
            for i, (name, checksum) in enumerate(children):
                is_last_child = (i == len(children) - 1)
                connector = "└── " if is_last_child else "├── "
                tree_out += f"{prefix}{connector}{name}/ [Merkle: {checksum[:8]}]\n"
                
                # Recursive Step
                new_prefix = prefix + ("    " if is_last_child else "│   ")
                tree_out += self._walk_fractal_tree(path / name, new_prefix)
                
            return tree_out
        except Exception as e:
            return f"{prefix}└── [ERROR: {e}]\n"

    async def _harvest_documentation_dna(self):
        """
        [KAR-4] Universal Strategic Memory.
        Scans walkthroughs and notes to extract 'Documentation DNA'.
        """
        # 1. SCAN LOCATIONS
        doc_paths = [
            self.project_path / "README.md",
            self.brain_path,
        ]
        
        for path in doc_paths:
            if not path.exists():
                continue
            
            files = [path] if path.is_file() else list(path.glob("*.md"))
            
            for f in files:
                try:
                    content = f.read_text()
                    # Segment by headers
                    sections = content.split("\n#")
                    for section in sections:
                        if len(section.strip()) < 50:
                            continue
                            
                        # Generate Signal Hash [SILO PROTOCOL]: Salted with Project ID
                        project_id = self.engine.get_project_id()
                        sig_hash = sparse_hasher.fingerprint(section, salt=project_id)
                        
                        # Store as public_patterns (Documentation-Sourced)
                        # We use a UUID based on the file and hash to avoid duplicates
                        fragment_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{f.name}:{sig_hash}"))
                        
                        if self.buffer:
                            await self.buffer.ingest("wisdom", {
                                "id": fragment_id,
                                "origin": "local",
                                "category": "documentation",
                                "pattern": f.name,
                                "signal_hash": sig_hash,
                                "text": section[:1000].strip(),
                                "source_type": "documentation",
                                "source_file": str(f),
                                "confidence": 8
                            })
                        else:
                            with self.engine.connection() as conn:
                                conn.execute("""
                                    INSERT OR REPLACE INTO public_patterns (
                                        id, origin_node, category, signal_pattern, 
                                        signal_hash, wisdom_text, source_type, source_file, confidence
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    fragment_id, Origin.LOCAL, "documentation", f.name,
                                    sig_hash, section[:1000].strip(), "documentation", str(f), 8
                                ))
                            
                except Exception as e:
                    logger.warning(f"Failed to harvest DNA from {f}: {e}")

    async def _extract_documentation_patterns(self, file_path: Path):
        """Extracts technical patterns from a single markdown file."""
        try:
            content = file_path.read_text()
            sections = content.split("\n#")
            project_id = self.engine.get_project_id()
            
            for section in sections:
                if len(section.strip()) < 50: continue
                sig_hash = sparse_hasher.fingerprint(section, salt=project_id)
                fragment_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{file_path.name}:{sig_hash}"))
                
                with self.engine.connection() as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO public_patterns (
                            id, origin_node, category, signal_pattern, 
                            signal_hash, pattern_text, source_type, source_file, confidence
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (fragment_id, "local", "documentation", file_path.name,
                          sig_hash, section[:1000].strip(), "documentation", str(file_path), 9))
            logger.info(f"📁 [PATTERNS]: Extracted fragments from {file_path.name}")
        except Exception as e:
            logger.warning(f"Failed to harvest {file_path.name}: {e}")
