"""
Architecture Advisor - LLM-powered code refactoring suggestions.

Uses Groq for fast, intelligent code analysis:
- Semantic similarity validation for duplicate patterns
- Refactoring suggestions with naming conventions
- File structure recommendations
"""

import os
import logging
import httpx
import asyncio
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


from side.llm.client import LLMClient

class ArchitectureAdvisor:
    """
    LLM-powered architecture intelligence advisor.
    
    Uses LLMClient for unified code analysis and refactoring suggestions.
    """
    
    def __init__(self):
        self.llm = LLMClient()
        self.is_available = self.llm.is_available()
    
    def analyze_duplicate_patterns(self, code_snippets: list[dict]) -> Optional[str]:
        """
        Analyze code snippets for semantic similarity and suggest unification.
        
        Args:
            code_snippets: List of {file, line, preview} dicts
            
        Returns:
            Clean, single-line suggestion string or None if LLM unavailable
        """
        if not self.is_available or len(code_snippets) < 2:
            return None
        
        # Build prompt
        snippet_text = "\n\n".join([
            f"### File: {s['file']}:{s['line']}\n```\n{s.get('preview', 'N/A')[:200]}\n```"
            for s in code_snippets[:5]  # Limit to 5 for token economy
        ])
        
        system_prompt = "You are a code architecture expert."
        user_prompt = f"""Analyze these similar code patterns:

{snippet_text}

TASK:
1. Are these patterns doing the same thing semantically? (YES/NO)
2. If YES, suggest a unified helper function name and signature.
3. Keep your response under 50 words.

Format: 
DUPLICATE: YES/NO
SUGGESTION: [helper_name(args)] - [brief description]"""

        try:
            raw_response = self.llm.complete(
                messages=[{"role": "user", "content": user_prompt}],
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=150
            )
            return self._parse_suggestion(raw_response)
        except Exception as e:
            logger.debug(f"ArchitectureAdvisor: LLM call failed: {e}")
            return None
    
    def _parse_suggestion(self, raw_response: str) -> Optional[str]:
        """Parse LLM response to extract a clean, user-friendly suggestion."""
        try:
            lines = raw_response.strip().split('\n')
            
            # Look for SUGGESTION line
            for line in lines:
                if line.strip().startswith('SUGGESTION:'):
                    suggestion = line.replace('SUGGESTION:', '').strip()
                    # Clean up common formatting issues
                    suggestion = suggestion.strip('[]').strip()
                    if suggestion:
                        return f"Extract to {suggestion}"
            
            # If no SUGGESTION found, check if it says YES and extract any function mention
            if 'YES' in raw_response.upper():
                # Try to find anything that looks like a function name
                import re
                func_match = re.search(r'(\w+)\s*\([^)]*\)', raw_response)
                if func_match:
                    return f"Extract to {func_match.group(0)}"
            
            return None
        except Exception:
            return None
    
    def suggest_file_split(self, file_path: str, function_groups: dict) -> Optional[str]:
        """
        Suggest how to split a large file based on function groupings.
        """
        if not self.is_available:
            return None
        
        groups_text = "\n".join([
            f"- {prefix}*: {', '.join(funcs[:5])}"
            for prefix, funcs in list(function_groups.items())[:6]
        ])
        
        system_prompt = "You are a Python architecture expert."
        user_prompt = f"""This file needs splitting:

File: {Path(file_path).name}
Function groups detected:
{groups_text}

Suggest 2-3 new file names that follow Python conventions.
Keep response under 30 words.

Format: Split into: file1.py, file2.py, file3.py"""

        try:
            return self.llm.complete(
                messages=[{"role": "user", "content": user_prompt}],
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=150
            )
        except Exception:
            return None
    
    def suggest_helper_name(self, pattern_type: str, example_context: str) -> Optional[str]:
        """
        Suggest a good helper function name for an extracted pattern.
        """
        if not self.is_available:
            return None
        
        system_prompt = "You are a Python naming expert."
        user_prompt = f"""Suggest a helper function name for this pattern:

Pattern type: {pattern_type}
Example: {example_context[:150]}

Requirements:
- Follow Python naming conventions (snake_case)
- Be descriptive but concise
- Include suggested module location

Format: utils/[module].py::[function_name]"""

        try:
            return self.llm.complete(
                messages=[{"role": "user", "content": user_prompt}],
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=150
            )
        except Exception:
            return None



# Singleton instance
_advisor: Optional[ArchitectureAdvisor] = None

def get_architecture_advisor() -> ArchitectureAdvisor:
    """Get the singleton ArchitectureAdvisor instance."""
    global _advisor
    if _advisor is None:
        _advisor = ArchitectureAdvisor()
    return _advisor
