import logging
from pathlib import Path
from typing import Any, Dict, List
from .base import BaseAnalyzer, CodeNode, Finding
from tree_sitter_languages import get_language, get_parser

# [Cleanup] Stubbed out Zombie Deps
class GraphKernel:
    def ingest_symbol(self, path, name, type, props): return "stub"
    def link(self, s, t, r): pass

class GraphObject: pass

logger = logging.getLogger(__name__)

class PolyglotAnalyzer(BaseAnalyzer):
    """
    Uses tree-sitter for true polyglot AST analysis.
    Supports TS, JS, Go, and Rust.
    """

    QUERIES = {
        "rust": """
            (function_item name: (identifier) @name) @function
            (struct_item name: (type_identifier) @name) @class
            (enum_item name: (type_identifier) @name) @class
            (trait_item name: (type_identifier) @name) @interface
            (impl_item type: (type_identifier) @name) @impl
        """,
        "go": """
            (function_declaration name: (identifier) @name) @function
            (method_declaration name: (field_identifier) @name) @function
            (type_declaration (type_spec name: (type_identifier) @name type: (struct_type))) @class
            (type_declaration (type_spec name: (type_identifier) @name type: (interface_type))) @interface
        """,
        "typescript": """
            (class_declaration name: (type_identifier) @name) @class
            (function_declaration name: (identifier) @name) @function
            (interface_declaration name: (type_identifier) @name) @interface
            (method_definition name: (property_identifier) @name) @function
            (variable_declarator name: (identifier) @name value: (arrow_function)) @function
            (call_expression function: (identifier) @call) @call_node
            (call_expression function: (member_expression property: (property_identifier) @call)) @call_node
        """,
        "tsx": """
            (class_declaration name: (type_identifier) @name) @class
            (function_declaration name: (identifier) @name) @function
            (interface_declaration name: (type_identifier) @name) @interface
            (method_definition name: (property_identifier) @name) @function
            (variable_declarator name: (identifier) @name value: (arrow_function)) @function
        """,
        "javascript": """
            (class_declaration name: (identifier) @name) @class
            (function_declaration name: (identifier) @name) @function
            (method_definition name: (property_identifier) @name) @function
            (variable_declarator name: (identifier) @name value: (arrow_function)) @function
        """
    }

    EXT_MAP = {
        ".ts": "typescript",
        ".tsx": "tsx",
        ".js": "javascript",
        ".jsx": "javascript",
        ".go": "go",
        ".rs": "rust"
    }

    def __init__(self, graph: GraphKernel = None):
        self.parsers = {}
        self.queries = {}
        self.graph = graph or GraphKernel()
        
        for lang_name, query_str in self.QUERIES.items():
            try:
                lang = get_language(lang_name)
                # Test the query before committing
                q = lang.query(query_str)
                self.parsers[lang_name] = get_parser(lang_name)
                self.queries[lang_name] = q
            except Exception as e:
                logger.error(f"Failed to initialize tree-sitter for {lang_name}: {e}")

    async def analyze(self, root: Path, files: list[Path]) -> dict[str, Any]:
        all_nodes = {}
        all_findings = []

        for f in files:
            ext = f.suffix.lower()
            lang_name = self.EXT_MAP.get(ext)
            if not lang_name or lang_name not in self.parsers:
                continue

            try:
                rel_path = str(f.relative_to(root))
                content = f.read_text(encoding="utf-8", errors="replace")
                content_bytes = content.encode("utf-8")
                
                parser = self.parsers[lang_name]
                query = self.queries[lang_name]
                
                tree = parser.parse(content_bytes)
                captures = query.captures(tree.root_node)
                
                # We need to pair @name with their parent nodes
                # tree-sitter query results come as (node, tag)
                last_node_info = {}
                
                for node, tag in captures:
                    if tag == "name":
                        # This name belongs to the PREVIOUS match if it was a symbol tag, 
                        # but tree-sitter query results for multiple captures in one pattern
                        # are interleaved. 
                        # Actually, better to use a dict to hold the 'node' whose name we just found.
                        pass
                    else:
                        # tag is 'function', 'class', 'interface', or 'impl'
                        # The next capture should be the 'name'
                        # Wait, captures are returned in the order they appear in the query/tree.
                        # For '(function_item name: (identifier) @name) @function', 
                        # normally it returns 'function' then 'name' (or depends on query order).
                        pass
                
                # Iterate over matches
                matches = query.matches(tree.root_node)
                dependencies = []
                
                module_node = CodeNode(
                    name=Path(rel_path).name,
                    type="module",
                    file_path=rel_path,
                    start_line=1,
                    end_line=len(content.splitlines()) or 1
                )

                current_node = None
                for match_id, captures in matches:
                    name_node = None
                    symbol_node = None
                    symbol_type = "unknown"
                    call_node = None
                    
                    for tag, node_or_list in captures.items():
                        node = node_or_list[0] if isinstance(node_or_list, list) else node_or_list
                        if tag == "name":
                            name_node = node
                        elif tag == "call":
                            call_node = node
                        elif tag == "dep":
                            dep_name = content_bytes[node.start_byte:node.end_byte].decode("utf-8").strip('"\'')
                            dependencies.append(dep_name)
                        else:
                            symbol_node = node
                            symbol_type = tag
                    
                    if name_node and symbol_node:
                        name = content_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8")
                        node_id = f"symbol:{rel_path}:{name}"
                        
                        properties = {
                            "start_line": symbol_node.start_point[0] + 1,
                            "end_line": symbol_node.end_point[0] + 1,
                            "complexity": len(symbol_node.children)
                        }
                        
                        graph_uid = self.graph.ingest_symbol(rel_path, name, symbol_type, properties)
                        
                        current_node = CodeNode(
                            name=name,
                            type=symbol_type,
                            file_path=rel_path,
                            start_line=properties["start_line"],
                            end_line=properties["end_line"],
                            complexity=properties["complexity"]
                        )
                        all_nodes[node_id] = current_node
                        module_node.definitions.append(node_id)
                    
                    elif call_node and current_node:
                        call_target = content_bytes[call_node.start_byte:call_node.end_byte].decode("utf-8")
                        if call_target not in current_node.dependencies:
                            current_node.dependencies.append(call_target)
                            # Link in Graph
                            target_uid = f"symbol:{rel_path}:{call_target}" # Local call assumption for mvp
                            self.graph.link(f"symbol:{rel_path}:{current_node.name}", target_uid, "calls")

                module_node.dependencies = list(set(dependencies))
                all_nodes[f"module:{rel_path}"] = module_node

            except Exception as e:
                logger.warning(f"Polyglot failed on {f}: {e}")

        return {"code_graph": all_nodes, "findings": all_findings}
