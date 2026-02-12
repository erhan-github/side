"""
Sidelith Communication Protocols.
Standardized interfaces for cross-platform data exchange (MCP, CLI, UX).
"""

from .cli import CLIProtocol
from .ux import UXProtocol

__all__ = [
    "CLIProtocol",
    "UXProtocol",
]
