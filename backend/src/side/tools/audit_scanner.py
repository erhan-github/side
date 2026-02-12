import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from side.utils.fast_ast import get_ast

logger = logging.getLogger(__name__)

class DebtScanner:
    """
    Programmatic Technical Debt & Marker Auditor.
    Uses AST parsing and pattern matching to rank code rot.
    """
    
    MARKERS = ["TODO", "FIXME", "HACK", "BUG", "XXX", "TEMP"]
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.results = {
            "critical": [],
            "technical_debt": [],
            "placeholders": [],
            "scanned_at": datetime.now().isoformat()
        }

    def scan(self) -> Dict[str, Any]:
        """Performs a full lexical and structural scan."""
        logger.info(f"Initiating Debt Scan on {self.project_path}")
        
        # We focus on source directories
        src_dirs = ["backend/src", "web/lib", "web/app", "scripts"]
        
        for sdir in src_dirs:
            full_path = self.project_path / sdir
            if not full_path.exists():
                continue
                
            for path in full_path.rglob("*"):
                if path.is_file() and path.suffix in [".py", ".ts", ".tsx", ".js"]:
                    self._audit_file(path)
                    
        return self.results

    def _audit_file(self, path: Path):
        """Audits a single file for debt markers and structural placeholders."""
        try:
            content = path.read_text(errors='ignore')
            lines = content.splitlines()
            
            # 1. Lexical Scan (Markers)
            for i, line in enumerate(lines):
                for marker in self.MARKERS:
                    if marker in line:
                        severity = "technical_debt"
                        if marker in ["BUG", "FIXME"]: severity = "critical"
                        
                        self.results[severity].append({
                            "file": str(path.relative_to(self.project_path)),
                            "line": i + 1,
                            "type": marker,
                            "snippet": line.strip()[:100]
                        })

            # 2. Structural Scan (Python only for now)
            if path.suffix == ".py":
                self._audit_python_ast(content, path)
                
        except Exception as e:
            logger.debug(f"Scanner: Skip {path}: {e}")

    def _audit_python_ast(self, content: str, path: Path):
        """Uses AST to find empty try/except pass or NotImplementedError."""
        import ast
        try:
            tree = get_ast(str(path))
            for node in ast.walk(tree):
                # Detect 'except: pass'
                if isinstance(node, ast.ExceptHandler):
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        self.results["critical"].append({
                            "file": str(path.relative_to(self.project_path)),
                            "line": node.lineno,
                            "type": "SILENT_FAILURE",
                            "snippet": "except: pass (Swallowed exception)"
                        })
                # Detect 'NotImplementedError'
                if isinstance(node, ast.Raise):
                    if isinstance(node.exc, ast.Call) and getattr(node.exc.func, 'id', '') == 'NotImplementedError':
                         self.results["placeholders"].append({
                            "file": str(path.relative_to(self.project_path)),
                            "line": node.lineno,
                            "type": "NOT_IMPLEMENTED",
                            "snippet": "raise NotImplementedError()"
                        })
            
            # 3. Semantic (Tree-sitter) Audits
            self._audit_semantics("python", content, path)
                
        except SyntaxError:
            pass

    def _audit_semantics(self, lang_id: str, content: str, path: Path):
        """Advanced Semantic Audits using Tree-sitter (migrated from CodeAuditor)."""
        try:
            from tree_sitter_languages import get_language, get_parser
            
            # Map common extensions/ids to tree-sitter language names
            ts_lang_map = {"py": "python", "python": "python", "js": "javascript", "ts": "typescript"}
            ts_name = ts_lang_map.get(lang_id, lang_id)
            
            language = get_language(ts_name)
            parser = get_parser(ts_name)
            tree = parser.parse(bytes(content, "utf8"))
            
            # Define Semantic Rules
            rules = []
            if ts_name == "python":
                rules = [
                    {
                        "id": "SQL_INJECTION_RISK",
                        "query": """
                        (call
                          function: (attribute
                            object: (identifier) @obj
                            attribute: (identifier) @method)
                          arguments: (argument_list
                            (string
                              (string_content) @str_content))
                          (#match? @method "execute|query")
                          (#match? @str_content "{.*}")
                        ) @sqli_risk
                        """,
                        "severity": "critical"
                    }
                ]
            
            for rule in rules:
                ts_query = language.query(rule["query"])
                captures = ts_query.captures(tree.root_node)
                for node, _ in captures:
                    self.results[rule["severity"]].append({
                        "file": str(path.relative_to(self.project_path)),
                        "line": node.start_point[0] + 1,
                        "type": rule["id"],
                        "snippet": node.text.decode("utf8")[:100]
                    })
        except ImportError:
            pass # Tree-sitter not available
        except Exception as e:
            logger.debug(f"Semantic audit failed for {path}: {e}")

    def export_report(self, output_path: Path):
        """Exports the findings to a structured JSON for the HUD."""
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Debt Report exported to {output_path}")

if __name__ == "__main__":
    import sys
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    scanner = DebtScanner(root)
    report = scanner.scan()
    print(json.dumps(report, indent=2))
