"""
Recursive Utility Tools

These tools allow the agent to "program" its interaction with large contexts,
breaking them down rather than trying to swallow them whole.
"""
import re
from typing import List, Generator, Any

def peek(text: str, lines: int = 50) -> str:
    """
    View the first N lines of a text to understand its structure.
    Also returns total line count.
    """
    all_lines = text.splitlines()
    total = len(all_lines)
    header = f"--- PEEK (First {lines} of {total} lines) ---\n"
    content = "\n".join(all_lines[:lines])
    return header + content

def grep(pattern: str, text: str, context: int = 0) -> str:
    """
    Filter lines matching a regex pattern.
    Mimics grep behaviour.
    """
    results = []
    lines = text.splitlines()
    
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error:
        return f"Error: Invalid regex pattern '{pattern}'"

    for i, line in enumerate(lines):
        if regex.search(line):
            # Handle context if needed (simplified here to just the line)
            results.append(f"{i+1}: {line}")
            
    header = f"--- GREP '{pattern}' ({len(results)} matches) ---\n"
    return header + "\n".join(results)

def partition(text: str, chunk_size: int = 5000) -> List[str]:
    """
    Split text into chunks of roughly N characters, respecting line boundaries.
    Used for recursive processing.
    """
    chunks = []
    current_chunk = []
    current_size = 0
    
    for line in text.splitlines(keepends=True):
        if current_size + len(line) > chunk_size and current_chunk:
            chunks.append("".join(current_chunk))
            current_chunk = []
            current_size = 0
        current_chunk.append(line)
        current_size += len(line)
    
    if current_chunk:
        chunks.append("".join(current_chunk))
        
    return chunks

def chunk_list(items: List[Any], size: int) -> List[List[Any]]:
    """
    Split a list into chunks of size N.
    """
    return [items[i:i + size] for i in range(0, len(items), size)]
