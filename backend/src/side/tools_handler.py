"""
Tool handling for Side MCP.
"""

import asyncio
import logging
import os
import time
import traceback
from typing import Any

from mcp.types import TextContent

from side.storage.simple_db import SimplifiedDatabase
from side.services.billing import BillingService, SystemAction
from side.tools import handle_tool_call

logger = logging.getLogger("side-mcp")

async def call_tool_handler(server, name: str, arguments: dict[str, Any] | None, 
                          _forensics_tool, _memory_interceptor) -> list[TextContent]:
    """
    Handle tool calls with Extreme Fuzz-Resistance & Environment Isolation.
    """
    # [Extreme God Mode] Forensic 13: Subprocess Environment Isolation
    # Ensure sensitive keys are NEVER leaked to shell subprocesses spawned here.
    SENSITIVE_KEYS = ["GROQ_API_KEY", "SUPABASE_SERVICE_ROLE_KEY", "LEMONSQUEEZY_API_KEY"]
    for key in SENSITIVE_KEYS:
        os.environ.pop(key, None) # Remove from current process env before any potential shell spawn
    
    # [Extreme God Mode] Forensic 8: Fuzz-Resistance
    # Reject insane payloads immediately.
    MAX_ARG_SIZE = 1000000 # 1MB limit for arguments
    arg_str = str(arguments)
    if len(arg_str) > MAX_ARG_SIZE:
        return [TextContent(type="text", text=f"❌ **Fuzzing Detected**: Payload size {len(arg_str)} exceeds limit.")]

    start_time = time.time()
    logger.info(f"🔧 [GOD MODE EXECUTING] {name}")
    
    # [Billing] Calculate Cost
    TOOL_COST_MAP = {
        "architectural_decision": SystemAction.STRATEGY_CHAT,
        "strategic_review": SystemAction.SCAN_DEEP,
        "simulate": SystemAction.SCAN_DEEP,
        "audit_deep": SystemAction.SCAN_DEEP,
    }
    
    project_id = SimplifiedDatabase.get_project_id()
    billing = BillingService(SimplifiedDatabase()) # Lightweight init
    action = TOOL_COST_MAP.get(name)

    if action:
        # [Traffic Cop] Rate Limiting (Leaky Bucket)
        # Prevent runaway scripts from draining user balance in seconds.
        # Limit: 1 request per 2 seconds for expensive tools.
        if not hasattr(server, "_last_action_time"):
            server._last_action_time = 0
            
        now = time.time()
        if now - server._last_action_time < 2.0:
            return [TextContent(type="text", text="⏳ **Traffic Cop**: Slow down! Strategic analysis takes time. (Rate Limit: 1 req/2s)")]
        
        server._last_action_time = now

        if not billing.can_afford(project_id, action):
             cost = billing.get_cost(action)
             balance = billing.db.get_token_balance(project_id)
             return [TextContent(type="text", text=f"❌ **Insufficient Strategic Units**: '{name}' costs {cost} SUs. You have {balance['balance']}. Upgrade to Pro for more.")]

    try:
        # Re-load env locally for internal logic ONLY if needed, 
        # but keep it out of the global process env to prevent shell leaks.
        if name == "purge_project":
            db = SimplifiedDatabase()
            success = db.purge_project_data(project_id, confirm=True) # Explicit confirm enforced
            result = f"🛡️ **Kill Switch Triggered**: Purged project `{project_id}`." if success else "❌ Purge failed."
        elif name == "audit_deep":
             # Execute global forensics tool
             query = arguments.get("query", "general audit") if arguments else "general audit"
             report = await _forensics_tool.scan_codebase(query)
             result = report
        else:
            result = await handle_tool_call(name, arguments or {})
        
        # [Memory] Intercept and Memorize (Fire-and-Forget)
        try:
             # Use the global interceptor initialized at module level
             asyncio.create_task(_memory_interceptor.intercept(name, arguments, project_id, result))
        except Exception as mem_err:
             logger.warning(f"Memory Intercept Failed: {mem_err}")

        # [Billing] Charge if successful
        if action:
            new_balance = billing.charge(project_id, action, name, arguments)
            logger.info(f"💰 Charged {billing.get_cost(action)} SUs. New Balance: {new_balance}")

        elapsed = time.time() - start_time
        logger.info(f"✅ {name} SUCCESS ({elapsed:.3f}s)")
        
        # [The Live Wire]
        # Notify Client that Monolith and Activity Log have changed.
        try:
             if hasattr(server, "request_context"):
                 await server.request_context.session.send_resource_updated("side://monolith")
                 await server.request_context.session.send_resource_updated("side://activity")
                 await server.request_context.session.send_resource_updated("side://profile")
        except Exception:
            pass # Fail silently if notifications not supported yet

        return [TextContent(type="text", text=result)]
    except Exception as err:
        logger.error(f"❌ {name} ERROR: {str(err)}\n{traceback.format_exc()}")
        return [TextContent(type="text", text=f"Side Forensic Error: {str(err)}")]

def register_tool_handlers(server, _forensics_tool, _memory_interceptor):
    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
        return await call_tool_handler(server, name, arguments, _forensics_tool, _memory_interceptor)
