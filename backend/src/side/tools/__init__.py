"""
Side Tools Package - Modular, DRY tool implementations.

This package consolidates all MCP tool handlers into focused modules:
- core.py: Shared utilities and singletons
- definitions.py: Tool definitions (TOOLS list)
- strategy.py: decide, strategy handlers
- planning.py: plan, check handlers
- simulation.py: simulate handler
- audit.py: run_audit handler
- formatting.py: Output formatting utilities
"""

from side.tools.core import (
    get_ai_memory,
    get_audit_log,
    get_billing_ledger,
    get_project_plan,
    get_user_profile,
    get_engine,
)
from side.tools.definitions import TOOLS
from side.tools.router import handle_tool_call

__all__ = [
    "TOOLS",
    "handle_tool_call",
    "get_ai_memory",
    "get_audit_log",
    "get_billing_ledger",
    "get_project_plan",
    "get_user_profile",
    "get_engine",
]
