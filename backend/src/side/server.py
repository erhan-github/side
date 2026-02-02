"""
Sidelith MCP Server - The Official Sovereign SDK Gateway.
Compliance: Model Context Protocol (MCP) standards.
Philosophy: Natural platform integration over custom extensions.

HANDOVER NOTE: Resource URIs use the 'side://' scheme.
"""

from mcp.server.fastmcp import FastMCP
from .storage.modules.base import SovereignEngine
from .storage.modules.identity import IdentityStore
from .storage.modules.strategic import StrategicStore
from .storage.modules.forensic import ForensicStore
from .storage.modules.transient import OperationalStore
from .intel.auto_intelligence import AutoIntelligence
from .intel.log_scavenger import LogScavenger
from .services.watcher_service import WatcherService
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
engine = SovereignEngine()

# Consolidated Registry: Use engine-provided instances to prevent redundant migrations
identity = engine.identity
strategic = engine.strategic
forensic = engine.forensic
operational = engine.operational

intel = AutoIntelligence(Path.cwd())

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
                
                # 2. CPU Audit
                cpu = process.cpu_percent(interval=1.0)
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

# Start Governor
governor = SovereignGovernor()
governor.start()

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
        # 1. Forensic Audit (Did we fetch context?)
        forensic.log_activity(project_id="global", tool="MCP", action="serve_context", cost_tokens=1)
        
        mandates = strategic.list_decisions(category="mandate")
        rejections = strategic.list_rejections(limit=10)
        
        context = {
            "mandates": [m["answer"] for m in mandates],
            "rejections": [f"Avoid repeating error in {r['file_path']}: {r['rejection_reason']}" for r in rejections],
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
    [The Research]: Semantic search over historical context.
    """
    results = operational.search_mesh_wisdom(topic)
    return json.dumps(results, indent=2)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
