import os
import sys
import asyncio
from pathlib import Path

# Add src to path for absolute imports
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from side.server_fast import mcp

if __name__ == "__main__":
    # Get deployment configuration
    port = int(os.getenv("PORT", 8000))
    transport = os.getenv("MCP_TRANSPORT", "stdio") # DEFAULT to stdio for local use
    
    if transport == "sse" or os.getenv("RAILWAY_PUBLIC_DOMAIN"):
        print(f"🚀 Starting Side Intelligence over SSE on port {port} and binding to 0.0.0.0...")
        mcp.run(transport="sse", port=port, host="0.0.0.0")
    else:
        # Default to stdio for local MCP use
        mcp.run(transport="stdio")
