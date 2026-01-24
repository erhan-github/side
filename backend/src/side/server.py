"""
Side Server - Sidelith Strategic Intelligence.

This module implements the stdio-based MCP server that responds to tool calls
from Cursor and other MCP-compatible clients.
"""

import asyncio
import logging
import os
import time
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server

from side.logging_config import setup_logging
from side.services.service_manager import ServiceManager
from side.env import load_env_file

# Load environment variables before anything else
load_env_file()

# Configure comprehensive logging
log_level = os.getenv("SIDE_LOG_LEVEL", "INFO")
setup_logging(log_level=log_level)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("side-mcp")

# Create MCP server instance
server = Server("side")

# -----------------------------------------------------------------------------
# GLOBAL SERVICE INITIALIZATION
# -----------------------------------------------------------------------------
from side.intel.memory import MemoryPersistence, MemoryManager, MemoryRetrieval, MemoryMaintenance
from side.services.memory_interceptor import MemoryInterceptor
from side.llm.client import LLMClient
from side.tools.forensics_tool import ForensicsTool

# Initialize Memory System Globally
MEMORY_PATH = Path.home() / ".side" / "memory"
_llm_client = LLMClient()
_memory_persistence = MemoryPersistence(MEMORY_PATH)
_memory_manager = MemoryManager(_memory_persistence, _llm_client)
_memory_retrieval = MemoryRetrieval(_memory_persistence, _llm_client)
_memory_interceptor = MemoryInterceptor(_memory_manager)
_memory_maintenance = MemoryMaintenance(_memory_persistence, _llm_client)

# Initialize Forensics
_forensics_tool = ForensicsTool(Path.cwd())

# -----------------------------------------------------------------------------
# MCP COMPONENT REGISTRATION
# -----------------------------------------------------------------------------
from side.prompts import DynamicPromptManager, register_prompt_handlers
from side.resources import ResourceManager, register_resource_handlers
from side.tools_handler import register_tool_handlers

prompt_manager = DynamicPromptManager()
register_prompt_handlers(server, prompt_manager)

resource_manager = ResourceManager()
register_resource_handlers(server, resource_manager)

register_tool_handlers(server, _forensics_tool, _memory_interceptor)

# -----------------------------------------------------------------------------
# SERVER EXECUTION
# -----------------------------------------------------------------------------
async def run_server() -> None:
    """Run the Side MCP server with background services."""
    start_time = time.time()
    logger.info("🧠 Side starting up...")
    
    # Initialize background services
    project_path = Path.cwd()
    service_manager = ServiceManager(project_path)
    
    try:
        # Start the Nervous System (File Watcher, Context Tracker, etc.)
        await service_manager.start()
        
        # [Memory] Schedule Nightly Maintenance (Async)
        from side.storage.simple_db import SimplifiedDatabase
        project_id = SimplifiedDatabase.get_project_id()
        asyncio.create_task(_memory_maintenance.run_nightly_consolidation(project_id))
        
        startup_time = time.time() - start_time
        logger.info("=" * 80)
        logger.info("🚀 Side SERVER IS LIVE")
        logger.info(f"⚡ Startup time: {startup_time:.3f}s")
        logger.info("💡 STRATEGIC TIP: Use 'strategy' tool with specific context for better ROI.")
        logger.info("=" * 80)
        
        async with stdio_server() as (read_stream, write_stream):
            # [Monolith] Evolution at Zero-Hour
            try:
                from side.tools.planning import _generate_monolith_file
                db = SimplifiedDatabase()
                await _generate_monolith_file(db)
                logger.info("🏛️ Monolith Initialized.")
            except Exception as e:
                logger.warning(f"Initial Monolith generation failed: {e}")

            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        # Graceful shutdown of services
        logger.info("🛑 Shutting down nervous system...")
        await service_manager.stop()


def main() -> None:
    """Main entry point for side-mcp command."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Side shutting down...")
    except Exception as err:
        logger.error(f"sideMCP error: {err}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
