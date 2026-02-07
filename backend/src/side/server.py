"""
"""
Sidelith MCP Server - The Official Side SDK Gateway.
Compliance: Model Context Protocol (MCP) standards.
Philosophy: Natural platform integration over custom extensions.

HANDOVER NOTE: Resource URIs use the 'side://' scheme.
"""

from mcp.server.fastmcp import FastMCP
from side.storage.modules.base import ContextEngine
from .storage.modules.identity import IdentityStore
from .storage.modules.chronos import ChronosStore
from .storage.modules.audit import AuditStore
from .storage.modules.transient import OperationalStore
from .intel.auto_intelligence import AutoIntelligence
from starlette.requests import Request
from starlette.responses import JSONResponse
from .intel.log_scavenger import LogScavenger
from .utils.crypto import shield
import json
import asyncio
import time
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Setup
# [Deployment] Allow dynamic port binding (Railway/Heroku/Fly)
port = int(os.getenv("PORT", 8000))
host = "0.0.0.0" # Always bind to all interfaces in production

mcp = FastMCP("Sidelith System", port=port, host=host)
engine = ContextEngine()

# Consolidated Registry: Use engine-provided instances to prevent redundant migrations
identity = engine.identity
strategic = engine.strategic
audit = engine.audit
operational = engine.operational

intel = AutoIntelligence(Path.cwd(), engine=engine)

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# DIMENSION 5: RESOURCE GOVERNOR (Resources)
# ---------------------------------------------------------------------
from .services.resource_limiter import ResourceLimiter

# Background Services Management
def start_background_services():
    """
    Controlled startup of non-blocking background logic.
    Ensures the main server binds to its port first.
    """
    logger.info("📡 [STARTUP]: Launching background services...")
    # Pass the operational store we already have
    governor = ResourceLimiter(operational_store=operational)
    governor.start()
    return governor

# ---------------------------------------------------------------------
# RESOURCES (Read-Only State)
# ---------------------------------------------------------------------

@mcp.resource("side://context/system")
def get_system_context() -> str:
    """
    Core Context: Injects Mandates, Rejections, and Insights.
    This is the 'Golden Record' the Agent sees.
    """
    try:
        # [PERFORMANCE]: Skipping forensic log for high-frequency resource polling
        mandates = strategic.list_decisions(category="mandate")
        rejections = strategic.list_rejections(limit=10)
        
        # 2. Pattern Injection
        # Search for patterns relevant to the current repository DNA
        # Using a default 'global' hash for now, in real use this would be derived from the current focus
        pattern_suggestions = engine.strategic.get_patterns(context_hash="dna:primary")
        
        context = {
            "mandates": [m["answer"] for m in mandates],
            "rejections": [f"Avoid repeating error in {r['file_path']}: {r['rejection_reason']}" for r in rejections],
            "patterns": pattern_suggestions,
            "system_status": "ACTIVE",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        return json.dumps(context, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.resource("side://ledger/recent")
def get_recent_ledger() -> str:
    """Recent Events: Recent 50 system activities."""
    events = audit.get_recent_activities(project_id="global", limit=50)
    return json.dumps(events, indent=2)

@mcp.resource("side://telemetry/pulse")
def get_pulse() -> str:
    """Health Monitor: Real-time signals."""
    path = Path.cwd() / ".side" / "pulse.json"
    if path.exists():
        return path.read_text()
    return json.dumps({"status": "UNKNOWN"})

# ---------------------------------------------------------------------
# TOOLS (Actionable Capabilities)
# ---------------------------------------------------------------------

@mcp.tool()
def check_safety(code: str, filename: str) -> str:
    """
    Guardrail: Check code for secrets, architectural drift, or syntax errors.
    Returns: PASS or VIOLATION.
    """
    # 1. Audit
    audit.log_activity(project_id="global", tool="PULSE", action="check_safety", payload={"file": filename})
    
    from side.pulse import pulse
    ctx = {"target_file": filename, "file_content": code, "PORT": "3000"}
    result = pulse.check_pulse(ctx)
    
    if result.status.value == "SECURE":
        return "PASS"
    else:
        return f"VIOLATION: {', '.join(result.violations)}"

@mcp.tool()
def record_intent(action: str, outcome: str) -> str:
    """
    Commitment: Log a strategic decision or completed task.
    """
    audit.log_activity(project_id="global", tool="AGENT", action=action, payload={"outcome": outcome})
    return "Intent Recorded in System Ledger."

@mcp.tool()
def query_patterns(topic: str) -> str:
    """
    Research: Semantic search over historical patterns.
    """
    # Use the new PatternStore for suggestions
    results = engine.strategic.get_patterns(topic)
    return json.dumps(results, indent=2)

# ---------------------------------------------------------------------
# INFRASTRUCTURE (Deployment & Health)
# ---------------------------------------------------------------------

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    """
    Comprehensive health check with memory diagnostics.
    Returns detailed system status for monitoring and alerting.
    """
    from side.config import config
    from side.utils.memory_diagnostics import MemoryDiagnostics
    
    try:
        # Get memory diagnostics
        diag = MemoryDiagnostics()
        memory = diag.get_current_memory()
        
        # Get cache statistics
        cache_stats = operational.get_cache_stats()
        
        # Determine health status
        status = "healthy"
        warnings = []
        
        if memory["rss_mb"] > config.memory_warning_threshold_mb:
            status = "warning"
            warnings.append(f"Memory usage high: {memory['rss_mb']:.1f}MB / {config.max_memory_mb}MB")
        
        if memory["rss_mb"] > config.auto_restart_threshold_mb:
            status = "critical"
            warnings.append(f"Memory critical: {memory['rss_mb']:.1f}MB > {config.auto_restart_threshold_mb}MB")
        
        if cache_stats["entry_count"] > config.max_cache_entries * 0.9:
            warnings.append(f"Cache near limit: {cache_stats['entry_count']} / {config.max_cache_entries}")
        
        return JSONResponse({
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "memory": {
                "rss_mb": round(memory["rss_mb"], 1),
                "vms_mb": round(memory["vms_mb"], 1),
                "percent": round(memory["percent"], 1),
                "limit_mb": config.max_memory_mb,
                "warning_threshold_mb": config.memory_warning_threshold_mb,
                "auto_restart_threshold_mb": config.auto_restart_threshold_mb
            },
            "cache": {
                "entries": cache_stats["entry_count"],
                "size_mb": round(cache_stats["size_mb"], 2),
                "limit": config.max_cache_entries,
                "eviction_enabled": config.enable_cache_eviction
            },
            "warnings": warnings,
            "mcp_type": "sse"
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, status_code=500)

@mcp.custom_route("/version", methods=["GET"])
async def get_version(request: Request):
    """Returns the current architectural version."""
    return JSONResponse({
        "version": "1.1.0-STABLE",
        "codename": "SystemCore",
        "system_status": "Online"
    })

@mcp.custom_route("/", methods=["GET"])
async def root_health(request: Request):
    """Fallback root endpoint."""
    return JSONResponse({
        "status": "ok",
        "service": "Sidelith System",
        "version": "1.1.0-STABLE"
    })

def main():
    import uvicorn
    # Railway/Production Standards
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    transport = os.getenv("MCP_TRANSPORT", "sse") 
    
    start_background_services()
    
    if transport == "sse":
        logger.info(f"🚀 [SYSTEM]: Starting SSE Server on {host}:{port} (Proxy Hardened)...")
        # Standard production config for behind-proxy Uvicorn
        # Using the correct attribute for FastMCP's starlette app
        uvicorn.run(
            mcp.sse_app, 
            host=host, 
            port=port, 
            proxy_headers=True, 
            forwarded_allow_ips="*",
            access_log=True,
            log_level="info"
        )
    else:
        mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
