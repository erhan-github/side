import logging
from pathlib import Path
from typing import Any
from .base import BaseAnalyzer, CodeNode, Finding
from .python import PythonAnalyzer
import re

logger = logging.getLogger(__name__)

class UniversalAnalyzer(BaseAnalyzer):
    """
    A polyglot analyzer that handles multiple languages in a monorepo.
    Produces both CodeNodes (Intel) and Findings (Forensics).
    """

    def __init__(self):
        self.python_analyzer = PythonAnalyzer()
        # Regex-based patterns for symbol detection
        self.patterns = {
            ".ts": r"(?:export\s+)?(?:class|function|interface|const)\s+([a-zA-Z0-9_]+)",
            ".tsx": r"(?:export\s+)?(?:class|function|interface|const)\s+([a-zA-Z0-9_]+)",
            ".js": r"(?:export\s+)?(?:class|function|const)\s+([a-zA-Z0-9_]+)",
            ".jsx": r"(?:export\s+)?(?:class|function|const)\s+([a-zA-Z0-9_]+)",
            ".go": r"(?:func|type|struct)\s+([a-zA-Z0-9_]+)",
            ".rs": r"(?:pub\s+)?(?:fn|struct|enum|trait)\s+([a-zA-Z0-9_]+)"
        }
        
        # Security & Health patterns
        self.secret_pattern = re.compile(r'(api_key|secret|password|token)\s*=\s*["\'][A-Za-z0-9_\-]{8,}["\']', re.IGNORECASE)
        self.todo_pattern = re.compile(r'//\s*(?:TODO|FIXME|XXX)', re.IGNORECASE)

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

        # 2. General Polyglot Pass
        for ext, ext_files in files_by_ext.items():
            if ext in self.patterns and ext != ".py":
                sym_pattern = re.compile(self.patterns[ext])
                for f in ext_files:
                    try:
                        rel_path = str(f.relative_to(root))
                        content = f.read_text(encoding="utf-8", errors="ignore")
                        lines = content.splitlines()
                        
                        # A. Intelligence (Symbols)
                        for match in sym_pattern.finditer(content):
                            name = match.group(1)
                            line_no = content.count("\n", 0, match.start()) + 1
                            node_id = f"{rel_path}:{name}"
                            all_nodes[node_id] = CodeNode(
                                name=name, type="definition", file_path=rel_path,
                                start_line=line_no, end_line=line_no
                            )

                        # B. Forensics (Violations)
                        for i, line in enumerate(lines):
                            # Secret Detection
                            if self.secret_pattern.search(line):
                                all_findings.append(Finding(
                                    type='SECRETS', severity='CRITICAL', file=rel_path, line=i+1,
                                    message='Potential hardcoded secret detected.',
                                    action='Move to environment variables.'
                                ))
                            
                            # TODO/FIXME detection
                            if self.todo_pattern.search(line):
                                all_findings.append(Finding(
                                    type='TODO', severity='LOW', file=rel_path, line=i+1,
                                    message='Leftover TODO/FIXME comment.',
                                    action='Resolve or track in backlog.'
                                ))
                            
                        # File Complexity check
                        if len(lines) > 300:
                            all_findings.append(Finding(
                                type='COMPLEXITY', severity='HIGH', file=rel_path, line=None,
                                message=f'File has {len(lines)} lines (threshold: 300).',
                                action='Refactor into smaller modules.'
                            ))

                    except Exception as e:
                        logger.warning(f"Universal failed on {f}: {e}")

        return {"code_graph": all_nodes, "findings": all_findings}
