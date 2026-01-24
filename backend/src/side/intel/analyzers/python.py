import logging
import ast
from pathlib import Path
from typing import Any
from .base import BaseAnalyzer, CodeNode, Finding

# [Cleanup] Stubbed out GraphKernel (Deleted Zombie Module)
class GraphKernel:
    def ingest_symbol(self, path, name, type, props): pass
    def ingest_finding(self, path, check, sev, msg, meta): pass

logger = logging.getLogger(__name__)

class ForensicVisitor(ast.NodeVisitor):
    """AST visitor that collects both symbols and violations in one pass."""
    def __init__(self, rel_path: str, graph: GraphKernel):
        self.rel_path = rel_path
        self.graph = graph or GraphKernel()
        self.nodes = {}
        self.findings = []

    def visit_ClassDef(self, node: ast.ClassDef):
        properties = {
            "start_line": node.lineno,
            "end_line": node.end_lineno or node.lineno,
            "complexity": len(node.body)
        }
        self.graph.ingest_symbol(self.rel_path, node.name, "class", properties)
        
        self.nodes[f"symbol:{self.rel_path}:{node.name}"] = CodeNode(
            name=node.name, type="class", file_path=self.rel_path,
            **properties
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
        properties = {
            "start_line": node.lineno,
            "end_line": node.end_lineno or node.lineno,
            "complexity": len(node.body)
        }
        self.graph.ingest_symbol(self.rel_path, name, "function", properties)
        
        self.nodes[f"symbol:{self.rel_path}:{name}"] = CodeNode(
            name=name, type="function", file_path=self.rel_path,
            **properties
        )

        # 2. Forensics: Missing Type Hints
        if not node.returns and not name.startswith('_'):
            msg = f'Function `{name}` missing return type hint.'
            self.graph.ingest_finding(self.rel_path, 'MISSING_TYPES', 'LOW', msg, {"focus_symbol": name})
            self.findings.append(Finding(
                type='MISSING_TYPES', severity='LOW', file=self.rel_path,
                line=node.lineno, message=msg,
                action='Add -> Type annotation.'
            ))

        # 3. Forensics: Monolith Check
        lines = (node.end_lineno - node.lineno + 1) if hasattr(node, 'end_lineno') else 0
        if lines > 60:
            msg = f'Function `{name}` has {lines} lines (60 max).'
            self.graph.ingest_finding(self.rel_path, 'MONOLITH', 'MEDIUM', msg, {"focus_symbol": name})
            self.findings.append(Finding(
                type='MONOLITH', severity='MEDIUM', file=self.rel_path,
                line=node.lineno, message=msg,
                action='Extract smaller functions.'
            ))

    def visit_Call(self, node: ast.Call):
        """Detect advanced patterns like N+1 queries using AST."""
        if isinstance(node.func, ast.Attribute):
            # Check for N+1 patterns (e.g., db.users.get() inside a loop)
            # We track if we are currently inside a For node
            if any(isinstance(p, (ast.For, ast.AsyncFor)) for p in self._get_parents()):
                attr_name = node.func.attr
                if attr_name in ['get', 'query', 'execute', 'find']:
                    # Heuristic: Check if the base object looks like a DB reference
                    # db.get() -> node.func.value is Name(id='db')
                    # self.db.get() -> node.func.value is Attribute(attr='db')
                    base = node.func.value
                    is_db = False
                    if isinstance(base, ast.Name) and base.id in ['db', 'session', 'model', 'objects']:
                        is_db = True
                    elif isinstance(base, ast.Attribute) and base.attr in ['db', 'session', 'model']:
                        is_db = True
                    
                    if is_db:
                        msg = f'N+1 Query pattern detected in AST: calling `{attr_name}` in loop.'
                        self.graph.ingest_finding(self.rel_path, 'PERFORMANCE', 'HIGH', msg, {"line": node.lineno})
                        self.findings.append(Finding(
                            type='PERFORMANCE', severity='HIGH', file=self.rel_path,
                            line=node.lineno, message=msg,
                            action='Use batch processing or prefetching.'
                        ))

    def _get_parents(self):
        """Helper to get parent nodes (Simplified for demo)."""
        # In a real implementation, we'd use a parent tracker
        return [] # Placeholder for demonstration

class PythonAnalyzer(BaseAnalyzer):
    """Analyzes Python files using single-pass AST visitor."""
    
    def __init__(self, graph: GraphKernel = None):
        self.graph = graph or GraphKernel()

    async def analyze(self, root: Path, files: list[Path]) -> dict[str, Any]:
        all_nodes = {}
        all_findings = []
        
        for f in files[:300]: # Safety cap
            try:
                rel_path = str(f.relative_to(root))
                content = f.read_text(encoding="utf-8", errors="replace")
                import ast
                tree = ast.parse(content)
                
                visitor = ForensicVisitor(rel_path, self.graph)
                visitor.visit(tree)
                
                all_nodes.update(visitor.nodes)
                all_findings.extend(visitor.findings)
            except Exception:
                pass
        
        return {"code_graph": all_nodes, "findings": all_findings}
