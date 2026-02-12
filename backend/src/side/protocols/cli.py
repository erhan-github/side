"""
System CLI Protocol - Rich Terminal Implementation of UXProtocol.
"""

import sys
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.theme import Theme
from rich.live import Live
from rich.status import Status
from side.models.core import Finding, Activity
from .ux import UXProtocol

# [DESIGN]: System Theme - Minimalist & High-Fidelity
SYSTEM_THEME = Theme({
    "info": "white",
    "warning": "yellow",
    "error": "red bold",
    "success": "cyan bold",
    "finding": "cyan",
    "activity": "bright_black",
    "header": "white bold",
    "footer": "grey37 italic",
})

class CLIProtocol(UXProtocol):
    """CLI implementation using the rich library."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console(theme=SYSTEM_THEME)

    def display_finding(self, finding: Finding) -> None:
        """Display an audit finding with minimalist structure."""
        severity_map = {
            "critical": "red bold",
            "warning": "yellow",
            "low": "white",
            "info": "white dim"
        }
        color = severity_map.get(finding.severity.lower(), "white")
        
        # Vertical Rule Style
        self.console.print(f"\n[bold {color}]| {finding.title.upper()}[/bold {color}]")
        self.console.print(f"| [italic]{finding.description}[/italic]")
        
        if finding.file_path:
            location = f"{finding.file_path}"
            if finding.line_number:
                location += f":{finding.line_number}"
            self.console.print(f"| [dim]Location: {location}[/dim]")

    def display_activity(self, activity: Activity) -> None:
        """Display system activity with subtle tracing."""
        self.console.print(f" [activity]→[/activity] {activity.action} [dim]({activity.tool})[/dim]")

    def display_status(self, message: str, level: str = "info") -> None:
        """Display a status message with consistent markers."""
        prefix = {
            "info": "  ",
            "warning": "! ",
            "error": "✕ ",
            "success": "✓ "
        }.get(level, "  ")
        self.console.print(f"{prefix}[{level}]{message}[/{level}]")

    def display_header(self, title: str, subtitle: Optional[str] = None) -> None:
        """Display a clean UI header."""
        self.console.print("\n")
        self.console.print(f"[header]{title.upper()}[/header]")
        if subtitle:
            self.console.print(f"[dim]{subtitle}[/dim]")
        self.console.print("")

    def display_footer(self) -> None:
        """Display System Footer."""
        self.console.print(f"[footer]SIDELITH SYSTEM CORE[/footer]\n")

    def render_table(self, title: str, columns: List[str], rows: List[List[Any]]) -> None:
        """Render a data table."""
        table = Table(title=title, show_header=True, header_style="bold cyan")
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*[str(item) for item in row])
        self.console.print(table)

    def prompt(self, message: str, default: Optional[str] = None) -> str:
        """Get user input."""
        return Prompt.ask(message, default=default, console=self.console)

    def confirm(self, message: str, default: bool = False) -> bool:
        """Get user confirmation."""
        return Confirm.ask(message, default=default, console=self.console)

    def display_panel(self, content: str, title: Optional[str] = None, style: str = "white") -> None:
        """Display a block of content in a panel."""
        self.console.print(Panel(content, title=title, border_style=style))
