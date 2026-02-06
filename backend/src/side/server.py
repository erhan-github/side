"""
Sidelith MCP Server - The Official Sovereign SDK Gateway.
Compliance: Model Context Protocol (MCP) standards.
Philosophy: Natural platform integration over custom extensions.

HANDOVER NOTE: Resource URIs use the 'side://' scheme.
"""

from mcp.server.fastmcp import FastMCP
from side.storage.modules.base import ContextEngine
from .storage.modules.identity import IdentityStore
from .storage.modules.strategic import StrategicStore
from .storage.modules.forensic import ForensicStore
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
import threading
import os
import sys
import psutil
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Setup
# [Deployment] Allow dynamic port binding (Railway/Heroku/Fly)
port = int(os.getenv("PORT", 8000))
host = "0.0.0.0" # Always bind to all interfaces in production

mcp = FastMCP("Sidelith Sovereign", port=port, host=host)
engine = ContextEngine()

# Consolidated Registry: Use engine-provided instances to prevent redundant migrations
identity = engine.identity
strategic = engine.strategic
forensic = engine.forensic
operational = engine.operational

intel = AutoIntelligence(Path.cwd(), engine=engine)

# ---------------------------------------------------------------------
# DIMENSION 5: THE SOVEREIGN GOVERNOR (Resources)
# ---------------------------------------------------------------------
class SovereignGovernor(threading.Thread):
    """
    Polices Dimension 5: Memory < 1% CPU, < 500MB RAM.
    If we violate physics, we terminate to protect the user's flow.
    """
    def __init__(self):
        super().__init__(daemon=True)
        self.max_ram_bytes = 500 * 1024 * 1024 # 500MB
        self.high_cpu_threshold = 5.0 # Strict 5% (was 95%) - We must be invisible.
        self.high_cpu_duration = 0
        self.project_root = Path.cwd()
        self.pulse_path = self.project_root / ".side" / "pulse.json"
        self.last_pulse_time = 0
        self.last_status = None
        
    def run(self):
        process = psutil.Process(os.getpid())
        logger.info(f"👮 [GOVERNOR]: Monitoring PID {os.getpid()} -- Strict Mode")
        
        while True:
            try:
                # 1. RAM Audit
                mem = process.memory_info().rss
                if mem > 200 * 1024 * 1024:
                    import gc
                    gc.collect() # Proactive hygiene
                    mem = process.memory_info().rss
                
                if mem > self.max_ram_bytes:
                    logger.critical(f"🚨 [GOVERNOR]: RAM Violation ({mem/1024/1024:.1f}MB). Terminating.")
                    os._exit(1) # Hard kill
                
                # 2. CPU Audit (Non-blocking measurement)
                cpu = process.cpu_percent(interval=None)
                if cpu > self.high_cpu_threshold:
                    self.high_cpu_duration += 1
                else:
                    self.high_cpu_duration = 0
                    
                if self.high_cpu_duration > 60: # 60s of sustained >5% usage
                    logger.warning(f"🚨 [GOVERNOR]: Sustained CPU usage ({cpu}%). Throttling...")
                    time.sleep(1) # Self-throttle
                    
                # 3. Pulse Telemetry (IO Optimized: Write only on change or every 10s)
                now = time.time()
                status = "HEALTHY" if cpu < 5.0 else "BUSY"
                if status != self.last_status or (now - self.last_pulse_time) > 10:
                    self._update_pulse(cpu, mem, status)
                    self.last_pulse_time = now
                    self.last_status = status
                
            except Exception as e:
                logger.error(f"Governor Error: {e}")
                time.sleep(5)

    def _update_pulse(self, cpu, mem, status):
        try:
            data = {
                "status": status,
                "telemetry": {
                    "cpu_percent": round(cpu, 1),
                    "ram_mb": round(mem / 1024 / 1024, 1),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            # Atomic write
            tmp = self.pulse_path.with_suffix('.tmp')
            tmp.write_text(json.dumps(data))
            tmp.replace(self.pulse_path)
            
            # Upsert partials to Operational DB (Transient)
            operational.set_setting("telemetry_cpu", str(cpu))
            operational.set_setting("telemetry_ram", str(mem))
            
        except Exception:
            pass

# Background Services Management
def start_background_services():
    """
    Controlled startup of non-blocking background logic.
    Ensures the main server binds to its port first.
    """
    logger.info("📡 [STARTUP]: Launching Sovereign background services...")
    governor = SovereignGovernor()
    governor.start()
    return governor

# ---------------------------------------------------------------------
# RESOURCES (Read-Only State)
# ---------------------------------------------------------------------

@mcp.resource("side://context/sovereign")
def get_sovereign_context() -> str:
    """
    [The Brain]: Injects Mandates, Rejections, and Insights.
    This is the 'Golden Record' the Agent sees.
    """
    try:
        # [PERFORMANCE]: Skipping forensic log for high-frequency resource polling
        mandates = strategic.list_decisions(category="mandate")
        rejections = strategic.list_rejections(limit=10)
        
        # 2. Wisdom Injection (Phase 6)
        # Search for wisdom relevant to the current repository DNA
        # Using a default 'global' hash for now, in real use this would be derived from the current focus
        wisdom_suggestions = engine.wisdom.get_patterns(context_hash="dna:primary")
        
        context = {
            "mandates": [m["answer"] for m in mandates],
            "rejections": [f"Avoid repeating error in {r['file_path']}: {r['rejection_reason']}" for r in rejections],
            "wisdom": wisdom_suggestions,
            "sovereign_status": "ACTIVE",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        return json.dumps(context, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.resource("side://ledger/recent")
def get_recent_ledger() -> str:
    """[Episodic Memory]: Recent 50 events."""
    events = forensic.get_recent_activities(project_id="global", limit=50)
    return json.dumps(events, indent=2)

@mcp.resource("side://telemetry/pulse")
def get_pulse() -> str:
    """[Health Monitor]: Real-time signals."""
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
    [The Guardrail]: Check code for secrets, architectural drift, or syntax errors.
    Returns: PASS or VIOLATION.
    """
    # 1. Forensic Audit
    forensic.log_activity(project_id="global", tool="PULSE", action="check_safety", payload={"file": filename})
    
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
    [The Commitment]: Log a strategic decision or completed task.
    """
    forensic.log_activity(project_id="global", tool="AGENT", action=action, payload={"outcome": outcome})
    return "Intent Recorded in Sovereign Ledger."

@mcp.tool()
def query_wisdom(topic: str) -> str:
    """
    [The Research]: Semantic search over historical wisdom (Patterns & Anti-patterns).
    """
    # Use the new PatternStore for suggestions
    results = engine.wisdom.get_patterns(topic)
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
        "version": "1.1.0-REFINED",
        "codename": "WisdomDistiller",
        "mesh_status": "Sovereign"
    })

@mcp.custom_route("/", methods=["GET"])
async def root_health(request: Request):
    """Fallback root endpoint."""
    return JSONResponse({
        "status": "ok",
        "service": "Sidelith Sovereign",
        "version": "1.1.0-REFINED"
    })

def main():
    import uvicorn
    # Railway/Production Standards
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    transport = os.getenv("MCP_TRANSPORT", "sse") 
    
    start_background_services()
    
    if transport == "sse":
        logger.info(f"🚀 [SOVEREIGN]: Starting SSE Server on {host}:{port} (Proxy Hardened)...")
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
