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
    
    try:
        # Billing logic removed (Sidelith Prime is Free/Open Core)
        if name == "audit_deep":
            # Execute global forensics tool
            query = arguments.get("query", "general audit") if arguments else "general audit"
            report = await _forensics_tool.scan_codebase(query)
            result = report
        else:
            result = await handle_tool_call(name, arguments or {})
        
        # [Memory] Intercept and Memorize (Fire-and-Forget)
        try:
            # Note: project_id should be extracted from arguments if available
            project_id = arguments.get("project_id", "default") if arguments else "default"
            asyncio.create_task(_memory_interceptor.intercept(name, arguments, project_id, result))
        except Exception as mem_err:
            logger.warning(f"Memory Intercept Failed: {mem_err}")

        elapsed = time.time() - start_time
        logger.info(f"✅ {name} SUCCESS ({elapsed:.3f}s)")
        
        return [TextContent(type="text", text=result)]

    except Exception as err:
        logger.error(f"❌ {name} ERROR: {str(err)}\n{traceback.format_exc()}")
        return [TextContent(type="text", text=f"Side Forensic Error: {str(err)}")]

def register_tool_handlers(server, _forensics_tool, _memory_interceptor):
    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
        return await call_tool_handler(server, name, arguments, _forensics_tool, _memory_interceptor)
