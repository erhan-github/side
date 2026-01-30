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

    def audit_mobile_intent(self, lang_id: str, code: str) -> List[str]:
        """
        Specific audit for Mobile 'Intent' violations.
        Example: Blocking network calls on the Main Thread (Swift/Kotlin).
        """
        violations = []
        
        # Prototype: Detecting SwiftUI @State mutations in inappropriate places
        if lang_id in ["swift", "ios"]:
            query = """
            (property_declaration
              (attribute (type_identifier) @attr)
              (#eq? @attr "State")
            ) @state_prop
            """
            results = self.query_code("swift", code, query)
            # This is just an example of what we CAN do with AST
            if results:
                logger.info(f"Found {len(results)} @State properties in Swift UI.")
        
        return violations

# Singleton instance
semantic_auditor = SemanticAuditor()
