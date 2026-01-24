import logging
from pathlib import Path
from typing import Any
from .base import BaseAnalyzer, CodeNode, Finding
from .python import PythonAnalyzer
from .polyglot import PolyglotAnalyzer
from .python import PythonAnalyzer
from .polyglot import PolyglotAnalyzer

# [Cleanup] Stubbed out Zombie Deps
class GraphKernel:
    def ingest_symbol(self, path, name, type, props): return "stub"
    def ingest_finding(self, path, check, sev, msg, meta): pass
    def ingest_intent(self, id, text, props): pass
import re
import hashlib

logger = logging.getLogger(__name__)

class UniversalAnalyzer(BaseAnalyzer):
    """
    A polyglot analyzer that handles multiple languages in a monorepo.
    Produces both CodeNodes (Intel) and Findings (Forensics).
    """

    def __init__(self, graph: GraphKernel = None):
        self.graph = graph or GraphKernel()
        self.python_analyzer = PythonAnalyzer(graph=self.graph)
        self.polyglot_analyzer = PolyglotAnalyzer(graph=self.graph)
        
        # Security & Health patterns
        self.secret_pattern = re.compile(r'(api_key|secret|password|token)\s*=\s*["\'][A-Za-z0-9_\-]{8,}["\']', re.IGNORECASE)
        self.todo_pattern = re.compile(r'(?://|#)\s*(?:TODO|FIXME|XXX)', re.IGNORECASE)
        
        # Strategic Intent Patterns (Intelligent Discovery)
        # Looks for: "because", "due to", "reason", "logic", "law", "requirement", "decision"
        self.strategic_pattern = re.compile(r'(?://|#)\s*.*(?:because|due to|reason|logic|law|requirement|decision|policy|constraint|strategy).*', re.IGNORECASE)

    async def analyze(self, root: Path, files: list[Path]) -> dict[str, Any]:
        """Perform unified polyglot analysis."""
        all_nodes = {}
        all_findings = []
        
        # Group files by extension
        files_by_ext: dict[str, list[Path]] = {}
        for f in files:
            ext = f.suffix.lower()
            if ext not in files_by_ext:
                files_by_ext[ext] = []
            files_by_ext[ext].append(f)

        # 1. Delegate Python to AST Analyzer
        if ".py" in files_by_ext:
            py_res = await self.python_analyzer.analyze(root, files_by_ext[".py"])
            all_nodes.update(py_res.get("code_graph", {}))
            all_findings.extend(py_res.get("findings", []))

        # 2. Delegate other languages to Polyglot Analyzer (Tree-Sitter)
        poly_files = []
        for ext, ext_files in files_by_ext.items():
            if ext in self.polyglot_analyzer.EXT_MAP:
                poly_files.extend(ext_files)
        
        if poly_files:
            poly_res = await self.polyglot_analyzer.analyze(root, poly_files)
            all_nodes.update(poly_res.get("code_graph", {}))
            all_findings.extend(poly_res.get("findings", []))

        # 3. General Forensics Pass (Non-AST based)
        for ext, ext_files in files_by_ext.items():
            for f in ext_files:
                try:
                    rel_path = str(f.relative_to(root))
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    lines = content.splitlines()
                    
                    # Forensics (Violations)
                    for i, line in enumerate(lines):
                        # Secret Detection
                        if self.secret_pattern.search(line):
                            msg = 'Potential hardcoded secret detected.'
                            self.graph.ingest_finding(rel_path, 'SECRETS', 'CRITICAL', msg, {"line": i+1})
                            all_findings.append(Finding(
                                type='SECRETS', severity='CRITICAL', file=rel_path, line=i+1,
                                message=msg,
                                action='Move to environment variables.'
                            ))
                        
                        # TODO/FIXME detection
                        if self.todo_pattern.search(line):
                            msg = 'Leftover TODO/FIXME comment.'
                            self.graph.ingest_finding(rel_path, 'TODO', 'LOW', msg, {"line": i+1})
                            all_findings.append(Finding(
                                type='TODO', severity='LOW', file=rel_path, line=i+1,
                                message=msg,
                                action='Resolve or track in backlog.'
                            ))
                        
                        # --- NEW: Strategic Intent Discovery ---
                        if self.strategic_pattern.search(line) and not self.todo_pattern.search(line):
                            # Clean the comment text
                            intent_text = re.sub(r'^[#/\s*]+', '', line).strip()
                            if len(intent_text) > 15: # Ignore trivial comments
                                # PALANTIR-LEVEL: Use content hash for deterministic, duplicate-proof IDs
                                content_hash = hashlib.md5(intent_text.encode()).hexdigest()[:12]
                                intent_id = f"discovered_{content_hash}"
                                
                                # Find nearest symbol for linking
                                nearest_symbol = None
                                min_dist = 9999
                                for node_uid, node in all_nodes.items():
                                    # node is a CodeNode object
                                    if node.file_path == rel_path:
                                        node_line = node.start_line
                                        dist = abs((i+1) - node_line)
                                        if dist < min_dist:
                                            min_dist = dist
                                            nearest_symbol = node_uid
                                
                                props = {
                                    "source": "comment_discovery", 
                                    "line": i+1,
                                    "file_path": rel_path
                                }
                                if nearest_symbol:
                                    props["focus_symbol"] = nearest_symbol
                                    
                                self.graph.ingest_intent(intent_id, intent_text, props)
                                logger.info(f"Comment Miner: Discovered strategic intent at {rel_path}:{i+1} -> {nearest_symbol}")

                    # File Complexity check
                    if len(lines) > 300:
                        msg = f'File has {len(lines)} lines (threshold: 300).'
                        self.graph.ingest_finding(rel_path, 'COMPLEXITY', 'HIGH', msg, {})
                        all_findings.append(Finding(
                            type='COMPLEXITY', severity='HIGH', file=rel_path, line=None,
                            message=msg,
                            action='Refactor into smaller modules.'
                        ))

                except Exception as e:
                    logger.warning(f"Forensics failed on {f}: {e}")

        return {"code_graph": all_nodes, "findings": all_findings}
