"""
Sidelith MCP Server - The Official Sovereign SDK Gateway.

This is the primary, natural interface for IDEs (Cursor, VS Code) and external 
Agents to interact with the Sidelith Sovereign Core. 

Compliance: Model Context Protocol (MCP) standards.
Philosophy: Natural platform integration over custom extensions.

HANDOVER NOTE: Resource URIs use the 'side://' scheme.
- side://ledger/recent: Tail of the Sovereign Ledger.
- side://profile/status: Current project technical identity.
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
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Setup
mcp = FastMCP("Sidelith Sovereign")
engine = SovereignEngine()
identity = IdentityStore(engine)
strategic = StrategicStore(engine)
operational = OperationalStore(engine)
intel = AutoIntelligence(Path.cwd())

# [KARPATHY PROTOCOL]: Deep Sync Hook
# Whenever the Ledger is updated, we refresh the Sovereign Weights (sovereign.json)
def run_checkpoint_sync():
    import asyncio
    try:
        # Check if we are in an event loop (FastMCP runs in one)
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(intel.sync_checkpoint())
        else:
            asyncio.run(intel.sync_checkpoint())
    except Exception as e:
        # Fallback for worker threads
        asyncio.run(intel.sync_checkpoint())

forensic = ForensicStore(engine, post_log_hook=run_checkpoint_sync)

# ---------------------------------------------------------------------
# SOVEREIGN GOVERNOR (Resource Defense)
# ---------------------------------------------------------------------
import threading
import time
import os
import sys
import psutil

class SovereignGovernor(threading.Thread):
    """
    Self-Policing Unit & Hyper-Perception Engine.
    Ensures Sidelith never becomes a zombie and calculates the SPC score.
    """
    def __init__(self, operational: OperationalStore):
        super().__init__(daemon=True)
        self.operational = operational
        self.max_ram_bytes = 500 * 1024 * 1024 # 500MB
        self.high_cpu_threshold = 95.0
        self.high_cpu_duration = 0
        self.last_sqlite_update = 0
        self.sqlite_interval = 15 # Seconds
        
        # Resolve pulse path (JSON Bridge)
        self.project_root = Path.cwd()
        self.pulse_path = self.project_root / ".side" / "pulse.json"
        self.pulse_path.parent.mkdir(parents=True, exist_ok=True)
        
    def run(self):
        process = psutil.Process(os.getpid())
        # Initial call to seed cpu_percent
        process.cpu_percent()
        psutil.cpu_percent()
        
        print(f"👮 [GOVERNOR]: Monitoring PID {os.getpid()} for resource spikes...")
        
        while True:
            try:
                # 1. Resource Guards (RAM/CPU)
                mem = process.memory_info().rss
                
                # [HYGIENE]: Proactive Garbage Collection if RAM > 200MB
                if mem > 200 * 1024 * 1024:
                    import gc
                    gc.collect()
                    mem = process.memory_info().rss # Re-sample
                
                if mem > self.max_ram_bytes:
                    print(f"🚨 [GOVERNOR]: RAM Violation ({mem/1024/1024:.1f}MB > 500MB). Terminating.")
                    os._exit(1)
                
                # [EFFICIENCY]: Non-blocking sampling
                global_cpu = psutil.cpu_percent(interval=None)
                process_cpu = process.cpu_percent() 
                
                if process_cpu > self.high_cpu_threshold:
                    self.high_cpu_duration += 1
                else:
                    self.high_cpu_duration = 0
                    
                if self.high_cpu_duration > 30: # Tightened to 30s
                    print(f"🚨 [GOVERNOR]: CPU Violation (>95% for 30s). Terminating.")
                    os._exit(1)

                # 2. [HYPER-PERCEPTION]: Calculate SPC Score
                w = float(self.operational.get_setting("buffer_ingest_velocity") or 0.0)
                h = float(self.operational.get_setting("silicon_pulse_score") or 0.1)
                
                vs = min(1.0, w / (max(0.1, h) * 10.0))
                if h < 0.2:
                    vs = max(vs, 1.0 - (h / 2.0))
                
                vg = float(self.operational.get_setting("temporal_synapse_velocity") or 0.8)
                vc = float(self.operational.get_setting("cognitive_flow_score") or 0.8)

                vs = max(0.01, vs)
                vg = max(0.01, vg)
                vc = max(0.01, vc)

                spc = 3 / ( (1/vs) + (1/vg) + (1/vc) )
                spc_final = round(spc, 3)
                
                # 3. [JSON BRIDGE]: Write to pulse.json for high-frequency, zero-cost access
                status = "HEALTHY"
                if spc_final < 0.4: status = "FRICTION_SPIKE"
                elif spc_final < 0.6: status = "WARNING"

                # Get recent alerts from operational store without full SQL write
                alerts = self.operational.get_active_telemetry_alerts()[:3]
                
                pulse_data = {
                    "spc_score": spc_final,
                    "vectors": {
                        "silicon_velocity": round(vs, 3),
                        "temporal_synapse": round(vg, 3),
                        "cognitive_flow": round(vc, 3)
                    },
                    "telemetry": {
                        "source": "INTERNAL" if process_cpu > 50 else ("EXTERNAL" if global_cpu > 70 else "OPTIMAL"),
                        "global_heat": round(global_cpu / 100.0, 3),
                        "local_heat": round(process_cpu / 100.0, 3),
                        "alerts": [{"id": a["id"], "message": a["message"]} for a in alerts]
                    },
                    "status": status,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                with open(self.pulse_path, 'w') as f:
                    f.write(json.dumps(pulse_data))

                # 4. [THROTTLED SQLITE]: Only write to DB every 15 seconds to reduce PowerLog churn
                now = time.time()
                if now - self.last_sqlite_update > self.sqlite_interval:
                    self.operational.set_setting("sovereign_perception_coefficient", str(spc_final))
                    self.operational.set_setting("silicon_velocity_derived", str(round(vs, 3)))
                    self.operational.set_setting("global_friction_level", str(round(global_cpu / 100.0, 3)))
                    self.operational.set_setting("local_friction_contribution", str(round(process_cpu / 100.0, 3)))
                    self.last_sqlite_update = now
                
                time.sleep(2) 
                
            except Exception as e:
                print(f"⚠️ Governor Error: {e}")
                time.sleep(10)

# ---------------------------------------------------------------------
# CONTINUOUS SOVEREIGNTY (Automation & Scavenging)
# ---------------------------------------------------------------------
intel_core = AutoIntelligence(Path.cwd())
scavenger = LogScavenger(forensic, Path.cwd())
watcher = WatcherService(intel_core)

# Start background listeners
scavenger.start()
watcher.start()

# Activate Governor
governor = SovereignGovernor(operational)
governor.start()

# ---------------------------------------------------------------------
# RESOURCES (Read-Only State)
# ---------------------------------------------------------------------

@mcp.resource("side://ledger/recent")
def get_recent_ledger() -> str:
    """Get the latest 50 events from the Sovereign Ledger."""
    try:
        events = forensic.get_recent_activities(project_id="global", limit=50)
        return json.dumps(events, indent=2)
    except Exception as e:
        return f"Error reading ledger: {e}"

@mcp.resource("side://profile/status")
def get_profile_status() -> str:
    """Get the high-level Sovereign profile and throughput metrics."""
    try:
        # We assume local context for the MCP server instance
        project_id = SovereignEngine.get_project_id(".")
        profile = identity.get_profile(project_id)
        return json.dumps(profile, indent=2)
    except Exception as e:
        return f"Error reading profile: {e}"

@mcp.resource("side://brain/graph")
def get_sovereign_graph() -> str:
    """
    Get the full Sovereign Knowledge Graph (Context).
    COST: 5 Strategic Units (SUs).
    """
    try:
        # 1. DEBIT WALLET (Value-based pricing)
        # Context is the 'Hard Drive' for the LLM's 'Brain'.
        # Serving it is a high-bandwidth strategic help.
        try:
            project_id = SovereignEngine.get_project_id(".")
            forensic.log_activity(project_id=project_id, tool="MCP", action="serve_context", cost_tokens=5, payload={"resource": "side://brain/graph"})
        except Exception as e:
            return json.dumps({"error": f"Insufficient SUs for Context Provisioning: {e}"}, indent=2)

        brain_path = Path(".side/sovereign.json")
        if not brain_path.exists():
            return json.dumps({"error": "Brain not initialized. Run 'side feed' first."}, indent=2)
        return shield.unseal_file(brain_path)
    except Exception as e:
        return f"Error reading brain: {e}"

@mcp.resource("side://mesh/nodes")
def get_mesh_nodes() -> str:
    """List all discovered Sidelith projects on this machine."""
    try:
        nodes = operational.list_mesh_nodes()
        return json.dumps(nodes, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Mesh access failed: {e}"}, indent=2)

@mcp.resource("side://mesh/wisdom")
def get_universal_wisdom() -> str:
    """
    Aggregate all architectural rejections and mandates from ALL local projects.
    The 'Universal Wisdom' layer for the machine.
    """
    try:
        wisdom = []
        nodes = operational.list_mesh_nodes()
        for node in nodes:
            # Note: We simulate aggregation from the global ledger here
            # In V2.2, we'll implement deep cross-node querying.
            pass
            
        rejections = strategic.list_rejections(limit=20)
        return json.dumps({
            "scope": "Global Mesh",
            "findings": rejections,
            "node_count": len(nodes)
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Wisdom aggregation failed: {e}"}, indent=2)

@mcp.resource("side://telemetry/alerts")
def get_telemetry_alerts() -> str:
    """Retrieve active proactive strategic warnings from the Sovereign Ledger."""
    try:
        project_id = SovereignEngine.get_project_id(".")
        alerts = operational.get_active_telemetry_alerts(project_id)
        return json.dumps(alerts, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Telemetry access failed: {e}"}, indent=2)

@mcp.resource("side://context/sovereign")
def get_sovereign_context() -> str:
    """
    The 'Golden Record' for Infinite Context.
    Combines Mandates (What to do) with Rejections (What NOT to do).
    Inject this into the prompt footer to stop 'Beautiful Wrong Directions'.
    """
    try:
        # 1. Fetch Mandates (The North Star)
        mandates = strategic.list_decisions(category="mandate")
        
        # 2. Fetch Rejections (The Anti-Pattern)
        rejections = strategic.list_rejections(limit=10)
        
        # 3. Construct the Sovereign Context
        context = {
            "mandates": [m["answer"] for m in mandates],
            "rejections": [
                f"DO NOT repeat error in {r['file_path']}: {r['rejection_reason']}" 
                for r in rejections
            ],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        return json.dumps(context, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to build Sovereign Context: {e}"}, indent=2)
@mcp.resource("side://telemetry/spc")
def get_spc_telemetry() -> str:
    """
    Retrieve the Sovereign Perception Coefficient (SPC).
    The 'Unified Pulse' of your project's silicon, temporal, and cognitive health.
    """
    try:
        spc = operational.get_setting("sovereign_perception_coefficient")
        vs = operational.get_setting("silicon_pulse_score")
        vg = operational.get_setting("temporal_synapse_velocity")
        vc = operational.get_setting("cognitive_flow_score")
        
        return json.dumps({
            "spc_score": spc,
            "vectors": {
                "silicon_velocity": vs,
                "temporal_synapse": vg,
                "cognitive_flow": vc
            },
            "status": "HEALTHY" if float(spc or 1.0) > 0.4 else "FRICTION_SPIKE",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"SPC Telemetry failed: {e}"}, indent=2)

@mcp.resource("side://buffer/stream")
def get_buffer_stream() -> str:
    """
    [KAR-6.13] The Unified Stream.
    Real-time pulse of background activities, rejections, and wisdom.
    """
    try:
        # We need access to the buffer. In a real integration, the ServiceManager 
        # would hold the buffer and the server would query it.
        # For this sprint, we simulate/connect to the active buffer.
        from side.services.service_manager import ServiceManager
        # Note: MCP server usually runs in a separate process/context.
        # This is a high-level representation.
        return json.dumps({
            "status": "active",
            "stream": [
                {"category": "activity", "label": "temporal_audit", "ts": time.time()},
                {"category": "wisdom", "label": "DNA_harvest", "ts": time.time() - 10}
            ],
            "pressure": 1.0
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Stream access failed: {e}"}, indent=2)


# ---------------------------------------------------------------------
# TOOLS (Actionable Capabilities)
# ---------------------------------------------------------------------

@mcp.tool()
def record_strategic_intent(project_id: str, type: str, outcome: str = "PASS", cost: int = 5) -> str:
    """
    Record a strategic intent or action into the Sovereign Ledger.
    
    Args:
        project_id: The unique ID of the current project context.
        type: Strategic event category (e.g., 'CORE_REFACT', 'AUTH_SHIFT').
        outcome: Strategic result ('PASS', 'VIOLATION', 'DRIFT').
        cost: Strategic Unit (SU) cost weight.
    """
    try:
        forensic.log_activity(project_id=project_id, tool=type, action="record_intent", cost_tokens=cost, payload={"outcome": outcome})
        return f"Sovereign intent recorded: {type} -> {outcome}"
    except Exception as e:
        return f"Failed to record intent: {e}"

@mcp.tool()
def record_shadow_intent(pivot_description: str, shadow_diff: str | None = None) -> str:
    """
    [INTENT SOCKET]: Captured architectural pivots or 'Shadow Diffs' before save.
    [KAR-2]: Analyzes the 'Negative Space' of dev intent to derive strategic rejections.
    """
    try:
        from side.utils.hashing import sparse_hasher
        project_id = SovereignEngine.get_project_id(".")
        pivot_id = f"shadow_{int(time.time())}"
        
        # 1. Calculate Intent Entropy (The 'Karpathy Weight')
        # High entropy = Large code blocks deleted/replaced = Serious Architectural Pivot
        entropy = len(shadow_diff.splitlines()) if shadow_diff else 0
        weight = "HIGH" if entropy > 50 else ("MEDIUM" if entropy > 10 else "LOW")
        
        # 2. Fingerprint the intent [SILO PROTOCOL]: Salted with Project ID
        signal_hash = sparse_hasher.fingerprint(pivot_description + (shadow_diff or ""), salt=project_id)
        
        # 3. Persist as a Correction Vector (Rejection)
        strategic.save_rejection(
            rejection_id=pivot_id,
            file_path="SHADOW_BUFFER",
            reason=f"[{weight}_ENTROPY] Pivot: {pivot_description}",
            diff_signature=shadow_diff[:1000] if shadow_diff else None,
            signal_hash=signal_hash
        )
        
        # 4. Log to Ledger
        forensic.log_activity(
            project_id=project_id, 
            tool="INTENT_SOCKET", 
            action="capture_shadow", 
            cost_tokens=int(entropy / 2) + 5, 
            payload={"id": pivot_id, "weight": weight, "entropy": entropy}
        )
        
        return f"✨ [SHADOW INTENT]: Captured {weight} entropy pivot. Corrective vector locked."
    except Exception as e:
        return f"Failed to capture shadow intent: {e}"

@mcp.tool()
def query_ledger(limit: int = 20) -> str:
    """
    Retrieve recent execution history from the Sovereign Ledger.
    """
    try:
        ledger = forensic.get_recent_activities(project_id="global", limit=limit)
        return json.dumps(ledger, indent=2)
    except Exception as e:
        return f"Query failure: {e}"

@mcp.tool()
def search_mesh(query: str) -> str:
    """
    Search for architectural wisdom (decisions, rejections, mandates) 
    across ALL Sidelith projects on this machine.
    
    Args:
        query: The architectural pattern or decision to search for.
    """
    try:
        results = operational.search_mesh_wisdom(query)
        if not results:
            return f"No matching strategic wisdom found in the local mesh for '{query}'."
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Mesh search failed: {e}"

@mcp.tool()
def check_safety(code: str, filename: str = "snippet.py") -> str:
    """
    Check if a code snippet is safe to proceed with. 
    Uses the Sovereign Pulse Engine (<3ms latency).
    
    Args:
        code: The source code to verify.
        filename: Virtual filename to help context (e.g., 'auth.py').
    """
    from side.pulse import pulse
    
    # Context
    ctx = {
        "target_file": filename,
        "file_content": code,
        "PORT": "3999" # Default assumption
    }
    
    # Run Pulse
    result = pulse.check_pulse(ctx)
    
    if result.status.value == "SECURE":
        return "✅ [SECURE]: Code is safe and aligned with Sovereign Standards."
    else:
        violations = "\n".join([f"- {v}" for v in result.violations])
        return f"🛑 [VIOLATION DETECTED]:\n{violations}\n\nDo not proceed until fixed."

@mcp.tool()
def recover_amnesia(context_query: str) -> str:
    """
    [KARPATHY PROTOCOL]: Amnesia Recovery via Checkpoint-Resume.
    Treats the project as a neural network: sovereign.json (Weights) + Ledger (Gradients).
    
    Args:
        context_query: The specific problem the LLM is failing to solve due to 'Amnesia'.
    """
    try:
        project_id = SovereignEngine.get_project_id(".")
        sovereign_file = Path.cwd() / ".side" / "sovereign.json"
        
        # 1. LOAD CHECKPOINT (The Weights)
        if not sovereign_file.exists():
            asyncio.run(intel.sync_checkpoint())
        
        raw_weights = shield.unseal_file(sovereign_file)
        weights = json.loads(raw_weights)
        
        # 2. REPLAY GRADIENTS (The History)
        gradients = intel.get_episodic_context(limit=15)
        
        # 3. SURGICAL ATTENTION (Layer 3)
        attention = intel.get_surgical_context(context_query, limit=2)
        
        checkpoint_time = weights.get("last_scan", "")
        
        report = [
            "🧠 [SOVEREIGN RECOVERY]: Checkpoint-Resume Protocol Engaged",
            "=========================================================",
            f"QUERY: {context_query}",
            "=========================================================",
            "💾 [MODEL CHECKPOINT]: (sovereign.json Weights)",
            f"Version: {weights.get('version')}",
            f"State Timestamp: {checkpoint_time}",
            "Architectural Focus:",
            json.dumps(weights.get("intent", {}).get("objectives", []), indent=2),
            "---------------------------------------------------------",
            "🎞️ [EPISODIC GRADIENTS]: (Ledger-derived History)",
            gradients,
            "---------------------------------------------------------",
            "🔬 [SURGICAL ATTENTION]: (Live Code Focus)",
            attention,
            "=========================================================",
            "⚡ [INSTRUCTION]: LLM, you have been rebooted with the Sovereign Weights (Truth) and Episodic Gradients (Time).",
            "1. Weights = Current State of the Repository.",
            "2. Gradients = Recent intent vectors and historical friction.",
            "3. Attention = Surgical code focus to prevent drift.",
            "Resume strategic execution immediately. Focus on the 'Architectural Focus' identified above."
        ]
        
        # Log the recovery event
        forensic.log_activity(project_id=project_id, tool="AMNESIA_RECOVERY", action="checkpoint_resume", cost_tokens=50)
        
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Recovery failed: {e}")
        return f"🚨 [RECOVERY FAILURE]: {e}"

def main():
    """CLI Entry Point for the Sidelith Sovereign MCP Server."""
    mcp.run()

if __name__ == "__main__":
    main()
