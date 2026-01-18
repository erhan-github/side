"""
CSO.ai Tools Package - Modular, DRY tool implementations.

This package consolidates all MCP tool handlers into focused modules:
- core.py: Shared utilities and singletons
- definitions.py: Tool definitions (TOOLS list)
- strategy.py: decide, strategy handlers
- planning.py: plan, check handlers
- simulation.py: simulate handler
- audit.py: run_audit handler
- formatting.py: Output formatting utilities
"""

from cso_ai.tools.core import (
    get_auto_intel,
    get_database,
    get_market,
)
from cso_ai.tools.definitions import TOOLS
from cso_ai.tools.router import handle_tool_call

__all__ = [
    "TOOLS",
    "handle_tool_call",
    "get_auto_intel",
    "get_database",
    "get_market",
]
