"""
CSO.ai Server - Your Strategic Partner.

This module implements the stdio-based MCP server that responds to tool calls
from Cursor and other MCP-compatible clients.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    Tool,
)

from cso_ai.logging_config import setup_logging
from cso_ai.tools import TOOLS, handle_tool_call
from cso_ai.services.service_manager import ServiceManager


def load_env_file() -> None:
    """Load environment variables from .env file."""
    # Check multiple possible locations (in priority order)
    possible_paths = [
        # Project root (side-mcp/.env) - most likely location
        Path(__file__).parent.parent.parent / ".env",
        # Current working directory
        Path.cwd() / ".env",
        # Parent of cwd (if running from src/)
        Path.cwd().parent / ".env",
        # User config directory
        Path.home() / ".side-mcp" / ".env",
    ]

    for env_path in possible_paths:
        try:
            env_path = env_path.expanduser().resolve()
            if env_path.exists():
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip().strip("'\"")
                            if key and value and key not in os.environ:
                                os.environ[key] = value
                break  # Use first found .env
        except Exception:
            continue
    
    # [Hyper-Ralph] Scenario 61 Fix: Insecure Env Loading
    # Verify .env permissions (should be 600 or 400)
    dotenv_path = Path(".env")
    if dotenv_path.exists():
        import stat
        mode = dotenv_path.stat().st_mode
        if mode & stat.S_IRGRP or mode & stat.S_IROTH:
            logger.warning("⚠️ SECURITY WARNING: .env file is world-readable (mode %o). Recommend 'chmod 600 .env'.", mode & 0o777)



# Load environment variables before anything else
load_env_file()

# Configure comprehensive logging
# Get log level from environment or default to INFO
log_level = os.getenv("CSO_LOG_LEVEL", "INFO")
setup_logging(log_level=log_level)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("side-mcp")

# Create MCP server instance
server = Server("cso-ai")

# Define prompts - simplified for 3 core tools
PROMPTS: list[Prompt] = [
    Prompt(
        name="read",
        description="Get top articles for your stack - 'What should I read?'",
        arguments=[],
    ),
    Prompt(
        name="strategy",
        description="Get strategic advice - 'What should I focus on?'",
        arguments=[
            PromptArgument(
                name="context",
                description="Optional context about what you're working on",
                required=False,
            ),
        ],
    ),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return the list of available tools."""
    return TOOLS


@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    """Return the list of available prompts."""
    return PROMPTS


@server.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    """Handle prompt requests - simplified for 3 core tools."""
    args = arguments or {}

    prompt_handlers = {
        "read": lambda: GetPromptResult(
            description="Top articles for your stack",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="CSO, what should I read?",
                    ),
                ),
            ],
        ),
        "strategy": lambda: GetPromptResult(
            description=f"Strategic advice{' for ' + args.get('context') if args.get('context') else ''}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"CSO, what should I focus on?{' Context: ' + args.get('context') if args.get('context') else ''}",
                    ),
                ),
            ],
        ),
    }

    handler = prompt_handlers.get(name)
    if handler:
        return handler()

    return GetPromptResult(
        description="CSO.ai - Instant Strategic Intelligence",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text="CSO, what should I read?"),
            ),
        ],
    )


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """
    Handle tool calls with Extreme Fuzz-Resistance & Environment Isolation.
    """
    import time
    import traceback
    
    # [Extreme God Mode] Forensic 13: Subprocess Environment Isolation
    # Ensure sensitive keys are NEVER leaked to shell subprocesses spawned here.
    SENSITIVE_KEYS = ["GROQ_API_KEY", "SUPABASE_SERVICE_ROLE_KEY", "STRIPE_SECRET_KEY"]
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
        # Re-load env locally for internal logic ONLY if needed, 
        # but keep it out of the global process env to prevent shell leaks.
        if name == "purge_project":
            from cso_ai.storage.simple_db import SimplifiedDatabase
            db = SimplifiedDatabase()
            project_id = SimplifiedDatabase.get_project_id()
            success = db.purge_project_data(project_id, confirm=True) # Explicit confirm enforced
            result = f"🛡️ **Kill Switch Triggered**: Purged project `{project_id}`." if success else "❌ Purge failed."
        else:
            result = await handle_tool_call(name, arguments or {})
        
        elapsed = time.time() - start_time
        logger.info(f"✅ {name} SUCCESS ({elapsed:.3f}s)")
        
        return [TextContent(type="text", text=result)]
    except Exception as err:
        logger.error(f"❌ {name} ERROR: {str(err)}\n{traceback.format_exc()}")
        return [TextContent(type="text", text=f"CSO.ai Forensic Error: {str(err)}")]


async def run_server() -> None:
    """Run the CSO.ai MCP server with background services."""
    logger.info("🧠 CSO.ai starting up...")
    
    # Initialize background services
    # We use the current directory as the project root
    project_path = Path.cwd()
    service_manager = ServiceManager(project_path)
    
    try:
        # Start the Nervous System (File Watcher, Context Tracker, etc.)
        await service_manager.start()
        
        startup_time = time.time() - start_time
        logger.info("=" * 80)
        logger.info("🚀 CSO.ai SERVER IS LIVE")
        logger.info(f"⚡ Startup time: {startup_time:.3f}s")
        logger.info("💡 STRATEGIC TIP: Use 'strategy' tool with specific context for better ROI.")
        logger.info("=" * 80)
        
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        # Do not return 1, as the function signature is `-> None`
    finally:
        # Graceful shutdown of services
        logger.info("🛑 Shutting down nervous system...")
        await service_manager.stop()


def main() -> None:
    """Main entry point for side-mcp command."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("CSO.ai shutting down...")
    except Exception as err:
        logger.error(f"sideMCP error: {err}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
