import ast
import logging
from pathlib import Path
from typing import Any
from .base import BaseAnalyzer, CodeNode, Finding

logger = logging.getLogger(__name__)

class ForensicVisitor(ast.NodeVisitor):
    """AST visitor that collects both symbols and violations in one pass."""
    def __init__(self, rel_path: str):
        self.rel_path = rel_path
        self.nodes = {}
        self.findings = []

    def visit_ClassDef(self, node: ast.ClassDef):
        self.nodes[f"{self.rel_path}:{node.name}"] = CodeNode(
            name=node.name, type="class", file_path=self.rel_path,
            start_line=node.lineno, end_line=node.end_lineno or node.lineno,
            complexity=len(node.body)
        )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._analyze_callable(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._analyze_callable(node)
        self.generic_visit(node)

    def _analyze_callable(self, node: ast.AST):
        # 1. Intelligence
        name = getattr(node, 'name', 'lambda')
        self.nodes[f"{self.rel_path}:{name}"] = CodeNode(
            name=name, type="function", file_path=self.rel_path,
            start_line=node.lineno, end_line=node.end_lineno or node.lineno,
            complexity=len(node.body)
        )

        # 2. Forensics: Missing Type Hints
        if not node.returns and not name.startswith('_'):
            self.findings.append(Finding(
                type='MISSING_TYPES', severity='LOW', file=self.rel_path,
                line=node.lineno, message=f'Function `{name}` missing return type hint.',
                action='Add -> Type annotation.'
            ))

        # 3. Forensics: Monolith Check
        lines = (node.end_lineno - node.lineno + 1) if hasattr(node, 'end_lineno') else 0
        if lines > 60:
            self.findings.append(Finding(
                type='MONOLITH', severity='MEDIUM', file=self.rel_path,
                line=node.lineno, message=f'Function `{name}` has {lines} lines (60 max).',
                action='Extract smaller functions.'
            ))

    def visit_For(self, node: ast.For):
        self._check_nested_loop(node)
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor):
        self._check_nested_loop(node)
        self.generic_visit(node)

    def _check_nested_loop(self, node: ast.AST):
        # Optimized O(n) check for nested loops in current subtree
        for child in ast.walk(node):
            if child is not node and isinstance(child, (ast.For, ast.AsyncFor)):
                self.findings.append(Finding(
                    type='PERFORMANCE', severity='MEDIUM', file=self.rel_path,
                    line=node.lineno, message='Nested loop detected (O(n^2)).',
                    action='Optimize algorithm or use hash maps.'
                ))
                break

class PythonAnalyzer(BaseAnalyzer):
    """Analyzes Python files using single-pass AST visitor."""

    async def analyze(self, root: Path, files: list[Path]) -> dict[str, Any]:
        all_nodes = {}
        all_findings = []
        
        for f in files[:300]: # Safety cap
            try:
                rel_path = str(f.relative_to(root))
                content = f.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)
                
                visitor = ForensicVisitor(rel_path)
                visitor.visit(tree)
                
                all_nodes.update(visitor.nodes)
                all_findings.extend(visitor.findings)
            except Exception:
                pass
        
        return {"code_graph": all_nodes, "findings": all_findings}
