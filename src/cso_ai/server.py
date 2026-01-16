"""
CSO.ai MCP Server - Your AI Chief Strategy Officer.

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

from cso_ai.tools import TOOLS, handle_tool_call


def load_env_file() -> None:
    """Load environment variables from .env file."""
    # Check multiple possible locations (in priority order)
    possible_paths = [
        # Project root (cso-ai/.env) - most likely location
        Path(__file__).parent.parent.parent / ".env",
        # Current working directory
        Path.cwd() / ".env",
        # Parent of cwd (if running from src/)
        Path.cwd().parent / ".env",
        # User config directory
        Path.home() / ".cso-ai" / ".env",
    ]

    for env_path in possible_paths:
        env_path = env_path.resolve()
        if env_path.exists():
            try:
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


# Load environment variables before anything else
load_env_file()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("cso-ai")

# Create MCP server instance
server = Server("cso-ai")

# Define prompts - natural ways to invoke CSO.ai
PROMPTS: list[Prompt] = [
    Prompt(
        name="strategy",
        description="Ask CSO.ai for strategic insights - 'What should be our strategy?'",
        arguments=[
            PromptArgument(
                name="focus",
                description="Area to focus on: tech, business, market, growth, risks",
                required=False,
            ),
        ],
    ),
    Prompt(
        name="whats-happening",
        description="Get market intelligence - 'What's happening in our space?'",
        arguments=[],
    ),
    Prompt(
        name="analyze",
        description="Deep codebase analysis - 'CSO, understand our codebase'",
        arguments=[
            PromptArgument(
                name="path",
                description="Path to analyze (defaults to current directory)",
                required=False,
            ),
        ],
    ),
    Prompt(
        name="risks",
        description="Risk assessment - 'Any risks I should know about?'",
        arguments=[],
    ),
    Prompt(
        name="opportunities",
        description="Opportunity scan - 'What opportunities should we pursue?'",
        arguments=[],
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
    """Handle prompt requests - conversation starters for CSO.ai."""
    args = arguments or {}

    prompt_handlers = {
        "strategy": lambda: GetPromptResult(
            description=f"Strategic insights focused on {args.get('focus', 'overall strategy')}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"CSO, what should be our strategy? Focus: {args.get('focus', 'general')}",
                    ),
                ),
            ],
        ),
        "whats-happening": lambda: GetPromptResult(
            description="Market and technology intelligence",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="CSO, what's happening in our space that I should know about?",
                    ),
                ),
            ],
        ),
        "analyze": lambda: GetPromptResult(
            description=f"Codebase analysis for {args.get('path', 'current directory')}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"CSO, analyze the codebase at {args.get('path', '.')} and tell me what you understand.",
                    ),
                ),
            ],
        ),
        "risks": lambda: GetPromptResult(
            description="Risk assessment across all domains",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="CSO, what risks should I be aware of? Technical, business, market, legal - all of it.",
                    ),
                ),
            ],
        ),
        "opportunities": lambda: GetPromptResult(
            description="Opportunity identification",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="CSO, what opportunities should we be pursuing right now?",
                    ),
                ),
            ],
        ),
    }

    handler = prompt_handlers.get(name)
    if handler:
        return handler()

    return GetPromptResult(
        description="CSO.ai - Your Strategic Advisor",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text="Hey CSO, what should I know?"),
            ),
        ],
    )


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """Handle tool calls from the MCP client."""
    logger.info(f"CSO.ai tool invoked: {name} with args: {arguments}")

    try:
        result = await handle_tool_call(name, arguments or {})
        return [TextContent(type="text", text=result)]
    except Exception as err:
        logger.error(f"Error in tool {name}: {err}", exc_info=True)
        return [TextContent(type="text", text=f"CSO.ai Error: {str(err)}")]


async def run_server() -> None:
    """Run the CSO.ai MCP server."""
    logger.info("🧠 CSO.ai starting up...")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """Main entry point for cso-ai command."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("CSO.ai shutting down...")
    except Exception as err:
        logger.error(f"CSO.ai error: {err}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
