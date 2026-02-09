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

# [DESIGN]: System Theme
SYSTEM_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green bold",
    "finding": "magenta",
    "activity": "blue",
    "header": "gold1 bold",
    "footer": "grey50 italic",
})

class CLIProtocol(UXProtocol):
    """CLI implementation using the rich library."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console(theme=SYSTEM_THEME)

    def display_finding(self, finding: Finding) -> None:
        """Display a forensic finding in a structured panel."""
        severity_map = {
            "critical": "red bold",
            "warning": "yellow",
            "low": "blue",
            "info": "cyan"
        }
        color = severity_map.get(finding.severity.lower(), "white")
        
        content = f"[bold]{finding.title}[/bold]\n"
        content += f"[italic]{finding.description}[/italic]\n"
        if finding.file_path:
            content += f"\n[dim]File: {finding.file_path}"
            if finding.line_number:
                content += f":{finding.line_number}"
            # Add line range if available (simulated here)
            content += "[/dim]"
        
        title = f"Finding: {finding.category.upper()}"
        self.console.print(Panel(content, title=f"[{color}]{title}[/{color}]", border_style=color.split()[0]))

    def display_activity(self, activity: Activity) -> None:
        """Display a system activity."""
        self.console.print(f"🧬 [activity]{activity.tool}[/activity]: {activity.action} [dim]({activity.cost_tokens} SUs)[/dim]")

    def display_status(self, message: str, level: str = "info") -> None:
        """Display a status message."""
        prefix = {
            "info": "ℹ️ ",
            "warning": "⚠️ ",
            "error": "❌ ",
            "success": "✅ "
        }.get(level, "")
        self.console.print(f"{prefix}[{level}]{message}[/{level}]")

    def display_header(self, title: str, subtitle: Optional[str] = None) -> None:
        """Display a UI header with ASCII art or styling."""
        self.console.print("\n")
        self.console.print(f"[header]{'=' * 60}[/header]")
        self.console.print(f"[header]  {title.upper()}[/header]")
        if subtitle:
            self.console.print(f"  [dim]{subtitle}[/dim]")
        self.console.print(f"[header]{'=' * 60}[/header]")

    def display_footer(self) -> None:
        """Display the System Footer."""
        self.console.print(f"[footer]{'-' * 60}[/footer]")
        self.console.print("[footer]  SIDELITH | Detective AI | System Core[/footer]\n")

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
