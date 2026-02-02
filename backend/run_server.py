import os
import sys
import asyncio
from pathlib import Path
from starlette.requests import Request
from starlette.responses import JSONResponse

# Add src to path for absolute imports
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

# FIXED: Pointing to Sidelith Prime Universal Server
from side.server import mcp

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    # [SILENT PARTNER]: Set polite process priority for background MCP operations
    try:
        if sys.platform != 'win32':
            os.nice(5) # Slightly less nice than the watcher, balance responsiveness vs impact
            print("🍃 [POLITE]: MCP Server priority optimized.")
    except:
        pass
    
    # [Deployment] Railway Detection
    # Force SSE transport on Railway to ensure proper port binding and health checks.
    is_railway = any(os.getenv(k) for k in ["RAILWAY_ENVIRONMENT_NAME", "RAILWAY_STATIC_URL", "RAILWAY_PUBLIC_DOMAIN"])
    
    if transport == "sse" or is_railway:
        print(f"🚀 Starting Sidelith over SSE on port {port}...")
        
        # [Railway Fix] Inject /health endpoint for deployment stability
        # [Railway Fix] Inject /health endpoint via FastMCP custom_route API
        try:
            from datetime import datetime
            
            # Using the official decorator instead of monkey patching
            @mcp.custom_route("/health", methods=["GET"])
            async def health_check(request: Request):
                return JSONResponse({"status": "ok", "timestamp": str(datetime.now())})

            @mcp.custom_route("/", methods=["GET"])
            async def root_health(request: Request):
                return JSONResponse({"status": "ok", "service": "Sidelith Sovereign"})

            print("✅ Injected /health and / endpoints via FastMCP custom_route.")
        except Exception as e:
            print(f"⚠️ Health check injection failed: {e}")

        # Start background services (Governor, Pulse, etc.)
        from side.server import start_background_services
        start_background_services()

        mcp.run(
            transport="sse", 
            # host/port logic handled by Uvicorn from env or internal defaults
        )
    else:
        # Default to stdio for local MCP integration (Cursor/VSCode)
        mcp.run(transport="stdio")
