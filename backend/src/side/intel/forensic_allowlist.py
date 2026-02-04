"""
Forensic Allowlist - Eliminates Known False Positives.

This module provides a knowledge base of patterns that are safe by design,
preventing the LLM from flagging legitimate security patterns as vulnerabilities.
"""

from typing import Optional, Dict, List, Tuple
from pathlib import Path
import re


class ForensicAllowlist:
    """
    Maintains a knowledge base of known-safe patterns to eliminate false positives.
    
    Categories:
    1. Defense Patterns: Code that detects/prevents vulnerabilities (not vulnerabilities themselves)
    2. Development Patterns: TODOs, in-memory stores with migration plans
    3. Architectural Patterns: Local-only services, intentional design choices
    """
    
    # File-specific safe patterns
    SAFE_PATTERNS = {
        "utils/shield.py": {
            "PATTERNS dictionary": {
                "reasoning": "These are regex patterns for DETECTING secrets, not actual secrets",
                "line_range": (14, 22),
                "code_markers": ["EMAIL", "OPENAI_KEY", "GITHUB_TOKEN", "STRIPE_KEY"]
            },
            "scrub method": {
                "reasoning": "Security utility that removes secrets from text",
                "function": "scrub"
            }
        },
        "pulse.py": {
            "cloud_payload": {
                "reasoning": "Example patterns for rule synchronization, not production secrets",
                "line_range": (216, 258),
                "code_markers": ["pswd =", "password =", "secret ="]
            },
            "sync_prime_rules": {
                "reasoning": "Demonstration patterns for dynamic rule system",
                "function": "sync_prime_rules"
            }
        },
        "mesh/auth.py": {
            "_USERS dictionary": {
                "reasoning": "In-memory store with explicit TODO for database migration",
                "line_range": (20, 22),
                "acceptable_if": "contains TODO comment or 'replace with database'"
            }
        },
        "llm/client.py": {
            "ALLOWED_KEYS": {
                "reasoning": "List of environment variable NAMES, not actual keys",
                "line_range": (153, 154),
                "code_markers": ["ALLOWED_KEYS", "GROQ_API_KEY", "OPENAI_API_KEY"]
            }
        }
    }
    
    # Global safe patterns (apply to all files)
    GLOBAL_SAFE_PATTERNS = {
        "env_var_usage": {
            "pattern": r'os\.getenv\(["\'][\w_]+["\']\)',
            "reasoning": "Environment variable usage is the CORRECT pattern, not hardcoding"
        },
        "null_checks": {
            "pattern": r'if not \w+:\s*return',
            "reasoning": "Null/empty checks are valid input validation"
        },
        "todo_comments": {
            "pattern": r'#.*TODO|#.*FIXME|replace with database in production',
            "reasoning": "Known technical debt, not a production vulnerability"
        },
        "type_hints": {
            "pattern": r':\s*Optional\[str\]|:\s*str\s*=\s*None',
            "reasoning": "Type hints for optional parameters, not missing validation"
        }
    }
    
    # Architectural context (helps LLM understand deployment model)
    ARCHITECTURAL_CONTEXT = {
        "server.py": "MCP server - runs locally, not a public API",
        "cli.py": "Command-line interface - local execution only",
        "*.py in tools/": "Internal tools - not exposed to network",
        "*.py in utils/": "Utility functions - used internally",
    }
    
    @classmethod
    def check_safe_pattern(cls, file_path: str, line: int, code_snippet: str) -> Optional[Dict]:
        """
        Checks if a code pattern is in the allowlist.
        
        Returns:
            Dict with explanation if safe, None otherwise
        """
        file_name = Path(file_path).name
        
        # Check file-specific patterns
        for pattern_file, patterns in cls.SAFE_PATTERNS.items():
            if pattern_file in file_path:
                for pattern_name, pattern_info in patterns.items():
                    # Check line range if specified
                    if "line_range" in pattern_info:
                        start, end = pattern_info["line_range"]
                        if start <= line <= end:
                            return {
                                "is_safe": True,
                                "reason": pattern_info["reasoning"],
                                "pattern": pattern_name,
                                "file": pattern_file
                            }
                    
                    # Check code markers
                    if "code_markers" in pattern_info:
                        if any(marker in code_snippet for marker in pattern_info["code_markers"]):
                            return {
                                "is_safe": True,
                                "reason": pattern_info["reasoning"],
                                "pattern": pattern_name,
                                "file": pattern_file
                            }
                    
                    # Check acceptable conditions
                    if "acceptable_if" in pattern_info:
                        if pattern_info["acceptable_if"] in code_snippet.lower():
                            return {
                                "is_safe": True,
                                "reason": pattern_info["reasoning"],
                                "pattern": pattern_name,
                                "file": pattern_file
                            }
        
        # Check global patterns
        for pattern_name, pattern_info in cls.GLOBAL_SAFE_PATTERNS.items():
            if re.search(pattern_info["pattern"], code_snippet):
                return {
                    "is_safe": True,
                    "reason": pattern_info["reasoning"],
                    "pattern": pattern_name,
                    "global": True
                }
        
        return None
    
    @classmethod
    def get_architectural_context(cls, file_path: str) -> Optional[str]:
        """
        Returns architectural context for a file to help LLM understand deployment model.
        """
        for pattern, context in cls.ARCHITECTURAL_CONTEXT.items():
            if "*" in pattern:
                # Glob pattern matching
                pattern_re = pattern.replace("*", ".*").replace(".", r"\.")
                if re.search(pattern_re, file_path):
                    return context
            elif pattern in file_path:
                return context
        return None
    
    @classmethod
    def get_context_guidance(cls, file_path: str) -> str:
        """
        Returns contextual guidance for analyzing a specific file.
        """
        guidance = []
        
        # Add architectural context
        arch_context = cls.get_architectural_context(file_path)
        if arch_context:
            guidance.append(f"**Deployment Context**: {arch_context}")
        
        # Add file-specific notes
        for pattern_file, patterns in cls.SAFE_PATTERNS.items():
            if pattern_file in file_path:
                guidance.append(f"**Known Safe Patterns in this file**:")
                for pattern_name, pattern_info in patterns.items():
                    guidance.append(f"- {pattern_name}: {pattern_info['reasoning']}")
        
        return "\n".join(guidance) if guidance else ""


# Singleton instance
allowlist = ForensicAllowlist()

def is_allowed_project(project_path: str) -> bool:
    """
    Checks if a project is allowed for forensic analysis.
    Default: True (Allow all local projects).
    """
    return True
