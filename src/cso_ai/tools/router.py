"""
Tool router for CSO.ai.

Routes incoming tool calls to appropriate handler modules.
"""

import logging
from typing import Any

from cso_ai.tools.strategy import handle_decide, handle_strategy
from cso_ai.tools.planning import handle_plan, handle_check
from cso_ai.tools.simulation import handle_simulate
from cso_ai.tools.audit import handle_run_audit

logger = logging.getLogger(__name__)


async def handle_tool_call(name: str, arguments: dict[str, Any]) -> str:
    """Route tool calls to appropriate handlers."""
    handlers = {
        "architectural_decision": handle_decide,
        "strategic_review": handle_strategy,
        "plan": handle_plan,
        "check": handle_check,
        "simulate": handle_simulate,
        "run_audit": handle_run_audit,
    }

    handler = handlers.get(name)
    if handler is None:
        return f"❌ Unknown tool: {name}"

    try:
        return await handler(arguments)
    except Exception as e:
        logger.exception(f"Tool error in {name}")
        return f"❌ Error: {str(e)}\n\nPlease try again or check your network connection."
