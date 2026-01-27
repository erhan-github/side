"""
Tool router for Side.

Routes incoming tool calls to appropriate handler modules.
"""

import logging
from typing import Any

from side.tools.strategy import handle_decide, handle_strategy
from side.tools.planning import handle_plan, handle_check
from side.tools.audit import handle_run_audit
from side.tools.welcome import handle_welcome
from side.storage.simple_db import SimplifiedDatabase, InsufficientTokensError
from side.tools.core import get_database

logger = logging.getLogger(__name__)

# Costs for different tool types
TOOL_COSTS = {
    "architectural_decision": 1,
    "strategic_review": 1,
    "plan": 1,
    "check": 1,
    "run_audit": 1,
    "welcome": 0,
}


async def handle_tool_call(name: str, arguments: dict[str, Any]) -> str:
    """Route tool calls to appropriate handlers."""
    handlers = {
        "architectural_decision": handle_decide,
        "strategic_review": handle_strategy,
        "plan": handle_plan,
        "check": handle_check,
        "run_audit": handle_run_audit,
        "welcome": handle_welcome,
    }

    if name == "verify_fix":
        from side.tools.verification import VerificationTool
        tool = VerificationTool()
        result = await tool.run(arguments)
        return result.content
        
    if name == "generate_repro":
        from side.tools.verification import VerificationTool
        tool = VerificationTool()
        result = await tool.generate_repro(arguments)
        return result.content


    handler = handlers.get(name)
    if handler is None:
        return f"❌ Unknown tool: {name}"

    # CURSOR-STYLE ENFORCEMENT
    # 1. Get project ID and DB
    db = get_database()
    project_id = db.get_project_id()
    
    # 2. Check cost
    cost = TOOL_COSTS.get(name, 100) # Default to 100 if unknown
    
    # 3. Verify balance before execution
    if cost > 0:
        balance_info = db.get_token_balance(project_id)
        if balance_info["balance"] < cost:
            return f"""
⚠️ **Insufficient Strategic Units (SUs)**

Sidelith service has paused for this project. 
Current Balance: `{balance_info['balance']} SUs`
Required for `{name}`: `{cost} SUs`

**How to resume:**
1. Open your [Sidelith Dashboard](https://sidelith.com/dashboard)
2. Provision additional infrastructure (SUs)
3. Relaunch the terminal or IDE

*Note: Sidelith stops execution to prevent architectural regressions when intelligence throughput is low.*
"""

    try:
        # Run the tool
        result = await handler(arguments)
        
        # 4. Deduct cost on success (No-bullshit logic)
        if cost > 0:
            try:
                db.update_token_balance(project_id, -cost)
                db.log_activity(project_id, name, "execution", cost)
            except InsufficientTokensError:
                pass # Atomic check already passed, this is a safety fallback
                
        return result
    except Exception as e:
        logger.exception(f"Tool error in {name}")
        return f"❌ Error: {str(e)}\n\nPlease try again or check your network connection."
