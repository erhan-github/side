"""
System UX Protocol - Abstract Interface for deterministic UIs.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from side.models.core import Finding, Activity

class UXProtocol(ABC):
    """Abstract interface for all user interactions."""

    @abstractmethod
    def display_finding(self, finding: Finding) -> None:
        """Display a audit finding."""
        pass

    @abstractmethod
    def display_activity(self, activity: Activity) -> None:
        """Display a system activity."""
        pass

    @abstractmethod
    def display_status(self, message: str, level: str = "info") -> None:
        """Display a status message (info, warning, error, success)."""
        pass

    @abstractmethod
    def display_header(self, title: str, subtitle: Optional[str] = None) -> None:
        """Display a UI header."""
        pass

    @abstractmethod
    def display_footer(self) -> None:
        """Display a UI footer."""
        pass

    @abstractmethod
    def render_table(self, title: str, columns: List[str], rows: List[List[Any]]) -> None:
        """Render a data table."""
        pass

    @abstractmethod
    def prompt(self, message: str, default: Optional[str] = None) -> str:
        """Get user input."""
        pass

    @abstractmethod
    def confirm(self, message: str, default: bool = False) -> bool:
        """Get user confirmation."""
        pass

    @abstractmethod
    def display_panel(self, content: str, title: Optional[str] = None, style: str = "white") -> None:
        """Display a block of content in a panel/frame."""
        pass
