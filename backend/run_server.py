import os
import sys
import asyncio
from pathlib import Path

# Add src to path for absolute imports
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

# FIXED: Pointing to Sidelith Prime Universal Server
from side.server import mcp

if __name__ == "__main__":
    # Get deployment configuration
    port = int(os.getenv("PORT", 8000))
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    
    # [Deployment] Railway Detection
    # Force SSE transport on Railway to ensure proper port binding and health checks.
    is_railway = any(os.getenv(k) for k in ["RAILWAY_ENVIRONMENT_NAME", "RAILWAY_STATIC_URL", "RAILWAY_PUBLIC_DOMAIN"])
    
    if transport == "sse" or is_railway:
        print(f"🚀 Starting Sidelith over SSE on port {port}...")
        mcp.run(
            transport="sse", 
            port=port, 
            host="0.0.0.0",
            uvicorn_config={"timeout_graceful_shutdown": 30}
        )
    else:
        # Default to stdio for local MCP integration (Cursor/VSCode)
        mcp.run(transport="stdio")
