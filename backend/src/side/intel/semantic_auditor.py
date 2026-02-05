import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from tree_sitter_languages import get_language, get_parser

logger = logging.getLogger(__name__)

class SemanticAuditor:
    """
    Sovereign Semantic Auditor [Tier-4].
    Uses Tree-sitter for deep AST-level invariants across the Universal Mesh.
    """

    def __init__(self):
        self.parsers = {}

    def _get_parser(self, lang_id: str):
        if lang_id in self.parsers:
            return self.parsers[lang_id]
        
        try:
            # Mapping common extensions/ids to tree-sitter language names
            ts_lang_map = {
                "py": "python",
                "python": "python",
                "js": "javascript",
                "javascript": "javascript",
                "ts": "typescript",
                "typescript": "typescript",
                "rs": "rust",
                "rust": "rust",
                "go": "go",
                "swift": "swift",
                "kt": "kotlin",
                "kotlin": "kotlin"
            }
            
            ts_name = ts_lang_map.get(lang_id, lang_id)
            language = get_language(ts_name)
            parser = get_parser(ts_name)
            self.parsers[lang_id] = (parser, language)
            return self.parsers[lang_id]
        except Exception as e:
            logger.error(f"Failed to load Tree-sitter parser for {lang_id}: {e}")
            return None

    def query_code(self, lang_id: str, code: str, sexp_query: str) -> List[Dict]:
        """Executes a Tree-sitter S-expression query against source code."""
        parser_data = self._get_parser(lang_id)
        if not parser_data:
            return []
        
        parser, language = parser_data
        
        try:
            tree = parser.parse(bytes(code, "utf8"))
            query = language.query(sexp_query)
            captures = query.captures(tree.root_node)
            
            results = []
            for node, name in captures:
                results.append({
                    "capture_name": name,
                    "text": node.text.decode("utf8"),
                    "start_point": node.start_point,
                    "end_point": node.end_point,
                    "type": node.type
                })
            return results
        except Exception as e:
            logger.error(f"Semantic query failed: {e}")
            return []

    def audit_security(self, lang_id: str, code: str) -> List[Dict]:
        """Runs security-focused semantic audits."""
        results = []
        
        # 1. SQL Injection Risk (Raw f-string interpolation into conn.execute)
        if lang_id in ["py", "python"]:
            # Query for conn.execute(f"...") or similar
            # This is a simplified query for demonstration
            query = """
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
            """
            results.extend(self.query_code("python", code, query))
        
        return results

    def audit_architecture(self, lang_id: str, code: str) -> List[Dict]:
        """Runs architecture-focused semantic audits (Clean Arch, DRY)."""
        results = []
        
        # 1. Database Access in UI/Frontend layers
        # (This is better handled via path patterns in PulseEngine, 
        # but semantic queries can check for specific DB-init patterns)
        
        # 2. Unhandled Exception Ghosts
        if lang_id in ["py", "python"]:
            query = """
            (except_clause
              body: (block
                (pass_statement) @swallowed)
            ) @unhandled_ghost
            """
            results.extend(self.query_code("python", code, query))
            
        return results

# Singleton instance
semantic_auditor = SemanticAuditor()
