"""
LLM Helpers for Sidelith.
Provides robust parsing and utility functions for LLM interactions.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

def extract_json(text: str) -> Any:
    """
    Robustly extracts JSON from LLM response text.
    Handles markdown code blocks, multiple blocks, and potential escaping issues.
    """
    if not text:
        return None

    # 1. Try to find markdown code blocks
    code_block_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if code_block_match:
        json_str = code_block_match.group(1)
    else:
        # 2. Try to find the first '{' or '[' and last '}' or ']'
        start_curly = text.find('{')
        start_bracket = text.find('[')
        
        # Determine start index (first of either)
        if start_curly != -1 and (start_bracket == -1 or start_curly < start_bracket):
            start_idx = start_curly
            end_idx = text.rfind('}') + 1
        elif start_bracket != -1:
            start_idx = start_bracket
            end_idx = text.rfind(']') + 1
        else:
            # No JSON-like delimiters found
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return None
        
        if end_idx > start_idx:
            json_str = text[start_idx:end_idx]
        else:
            json_str = text

    # 3. Clean and Parse
    try:
        # Basic cleanup: remove potential trailing commas (common LLM error)
        # This is a bit risky but often helpful for single-level JSON
        # json_str = re.sub(r",\s*([\]}])", r"\1", json_str)
        
        # Handle some escaping edge cases
        # (Though most modern models handle this well)
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse extracted JSON: {e}\nRaw extracted: {json_str[:100]}...")
        # Last resort: try literal eval or similar if we really wanted to, 
        # but for now just return None and log it.
        return None

def clean_code_block(text: str) -> str:
    """Strips markdown code blocks and returns raw code."""
    match = re.search(r"```(?:\w+)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()
