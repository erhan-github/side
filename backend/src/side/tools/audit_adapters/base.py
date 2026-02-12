"""
Audits Adapter Base Class.

Defines the interface for all security tool adapters (Semgrep, Bandit, ESLint, etc.).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


from side.models.core import Finding, Severity


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
        return f"Tool '{self.get_tool_name()}' is not installed."
