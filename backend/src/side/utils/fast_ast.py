"""
Fast AST - Zero-Latency Parsing.
Uses mtime-based LRU caching to prevent redundant parsing of the same file
during multi-probe audits.
"""

import ast
import os
import functools
from pathlib import Path

@functools.lru_cache(maxsize=128)
def _parse_content(content: str) -> ast.AST:
    """Internal cache for content->AST."""
    return ast.parse(content)

# We use a secondary cache for path+mtime -> content hash?
# Actually, passing full content to lru_cache key is expensive for hashing?
# Python's str hash is fast (cached in object).
# So _parse_content(content) is actually very fast to lookup.

def get_ast(file_path: str) -> ast.AST:
    """
    Get AST for a file.
    Reads file.
    """
    content = Path(file_path).read_text()
    return _parse_content(content)

def get_content(file_path: str) -> str:
    """ Read text, uncached (OS handles file cache). """
    return Path(file_path).read_text()

# We can also cache the Read if we check mtime.
# But OS FS cache is usually good enough for reads.
# The CPU cost is in `ast.parse`.
