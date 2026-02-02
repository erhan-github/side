import os
import sys
import asyncio
from pathlib import Path

# Add src to path for absolute imports
src_path = str(Path(__file__).parent.parent / "backend" / "src")
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
        try:
            # Access underlying FastAPI app
            app = getattr(mcp, "_fastapi_app", getattr(mcp, "fastapi_app", None))
            if app:
                from datetime import datetime
                @app.get("/health")
                async def health_check():
                    return {"status": "ok", "timestamp": str(datetime.now())}
                
                @app.get("/")
                async def root_health():
                    return {"status": "ok", "service": "Sidelith Sovereign"}
                print("✅ Injected /health and / endpoints for Railway.")
            else:
                print("⚠️ Could not find underlying FastAPI app to inject health checks.")
        except Exception as e:
            print(f"⚠️ Health check injection failed: {e}")

        mcp.run(
            transport="sse", 
            # port logic handled by Uvicorn from env or internal defaults
        )
    else:
        # Default to stdio for local MCP integration (Cursor/VSCode)
        mcp.run(transport="stdio")
