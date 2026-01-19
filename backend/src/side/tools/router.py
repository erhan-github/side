"""
Tool router for Side.

Routes incoming tool calls to appropriate handler modules.
"""

import logging
from typing import Any

from side.tools.strategy import handle_decide, handle_strategy
from side.tools.planning import handle_plan, handle_check
from side.tools.simulation import handle_simulate, handle_simulate_users
from side.tools.audit import handle_run_audit
from side.tools.welcome import handle_welcome

logger = logging.getLogger(__name__)


async def handle_tool_call(name: str, arguments: dict[str, Any]) -> str:
    """Route tool calls to appropriate handlers."""
    handlers = {
        "architectural_decision": handle_decide,
        "strategic_review": handle_strategy,
        "plan": handle_plan,
        "check": handle_check,
        "simulate": handle_simulate,
        "simulate_users": handle_simulate_users,
        "run_audit": handle_run_audit,
        "welcome": handle_welcome,
    }


    handler = handlers.get(name)
    if handler is None:
        return f"❌ Unknown tool: {name}"

    try:
        return await handler(arguments)
    except Exception as e:
        logger.exception(f"Tool error in {name}")
        return f"❌ Error: {str(e)}\n\nPlease try again or check your network connection."
