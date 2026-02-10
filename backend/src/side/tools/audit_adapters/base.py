"""
Forensics Adapter Base Class.

Defines the interface for all security tool adapters (Semgrep, Bandit, ESLint, etc.).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Normalized severity levels across all tools."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class Finding:
    """
    Normalized finding structure across all security tools.
    
    This is the common format that all adapters must produce.
    """
    tool: str                    # e.g., "semgrep", "bandit"
    rule_id: str                 # Tool-specific rule identifier
    file_path: str               # Relative path to file
    line: int                    # Line number (1-indexed)
    column: Optional[int]        # Column number (1-indexed)
    severity: Severity           # Normalized severity
    message: str                 # Human-readable description
    code_snippet: Optional[str]  # Affected code
    cwe_id: Optional[str]        # CWE identifier if available
    owasp_category: Optional[str] # OWASP Top 10 mapping
    confidence: Optional[str]    # HIGH, MEDIUM, LOW
    explanation: Optional[str] = None # LLM-generated explanation
    suggested_fix: Optional[str] = None # LLM-generated fix
    metadata: Dict[str, Any] = None    # Tool-specific metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "tool": self.tool,
            "rule_id": self.rule_id,
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "severity": self.severity.value,
            "message": self.message,
            "code_snippet": self.code_snippet,
            "cwe_id": self.cwe_id,
            "owasp_category": self.owasp_category,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "suggested_fix": self.suggested_fix,
            "metadata": self.metadata
        }


class AuditAdapter(ABC):
    """
    Abstract base class for security tool adapters.
    
    Each adapter wraps a specific tool (Semgrep, Bandit, etc.) and
    provides a unified interface for running scans and parsing results.
    """
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the tool is installed and available.
        
        Returns:
            True if tool can be executed, False otherwise
        """
        pass
    
    @abstractmethod
    def get_tool_name(self) -> str:
        """
        Get the name of the security tool.
        
        Returns:
            Tool name (e.g., "semgrep", "bandit")
        """
        pass
    
    @abstractmethod
    async def scan(self, target_paths: Optional[List[Path]] = None) -> List[Finding]:
        """
        Run the security tool and return normalized findings.
        
        Args:
            target_paths: Optional list of specific files/dirs to scan.
                         If None, scans entire project.
        
        Returns:
            List of Finding objects
        """
        pass
    
    @abstractmethod
    def parse_output(self, raw_output: str) -> List[Finding]:
        """
        Parse tool-specific output into normalized Finding objects.
        
        Args:
            raw_output: Raw JSON/text output from the tool
        
        Returns:
            List of Finding objects
        """
        pass
    
    @abstractmethod
    def install(self) -> bool:
        """
        Attempt to install the tool automatically.
        
        Returns:
            True if installation succeeded, False otherwise
        """
        pass

    def get_install_instructions(self) -> str:
        """
        Get installation instructions for this tool.
        
        Returns:
            Installation command/instructions
        """
        return f"Tool '{self.get_tool_name()}' is not installed."
