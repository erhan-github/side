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

from typing import List, Optional
from fastmcp import FastMCP
import json
from pathlib import Path
from datetime import datetime, timezone
from .storage.simple_db import SimplifiedDatabase
from .utils.crypto import shield

# Setup
mcp = FastMCP("Sidelith Sovereign")
db = SimplifiedDatabase()

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
    Self-Policing Unit. Ensures Sidelith never becomes a zombie.
    Policies:
    1. RAM > 500MB -> Terminate (Leak Protection).
    2. CPU > 95% for 60s -> Terminate (Loop Protection).
    """
    def __init__(self):
        super().__init__(daemon=True)
        self.max_ram_bytes = 500 * 1024 * 1024 # 500MB
        self.high_cpu_threshold = 95.0
        self.high_cpu_duration = 0
        
    def run(self):
        process = psutil.Process(os.getpid())
        print(f"👮 [GOVERNOR]: Monitoring PID {os.getpid()} for resource spikes...")
        
        while True:
            try:
                # 1. RAM Check
                mem = process.memory_info().rss
                if mem > self.max_ram_bytes:
                    print(f"🚨 [GOVERNOR]: RAM Violation ({mem/1024/1024:.1f}MB > 500MB). Terminating.")
                    os._exit(1) # Hard kill
                
                # 2. CPU Check
                cpu = process.cpu_percent(interval=1.0)
                if cpu > self.high_cpu_threshold:
                    self.high_cpu_duration += 1
                else:
                    self.high_cpu_duration = 0
                    
                if self.high_cpu_duration > 60: # 60 seconds of max load
                    print(f"🚨 [GOVERNOR]: CPU Violation (>95% for 60s). Terminating.")
                    os._exit(1)
                    
                time.sleep(10) # Low Check Rate (Zero Burden)
                
            except Exception as e:
                print(f"⚠️ Governor Error: {e}")
                time.sleep(10)

# Activate Governor
governor = SovereignGovernor()
governor.start()

# ---------------------------------------------------------------------
# RESOURCES (Read-Only State)
# ---------------------------------------------------------------------

@mcp.resource("side://ledger/recent")
def get_recent_ledger() -> str:
    """Get the latest 50 events from the Sovereign Ledger."""
    try:
        events = db.get_recent_ledger(limit=50)
        return json.dumps(events, indent=2)
    except Exception as e:
        return f"Error reading ledger: {e}"

@mcp.resource("side://profile/status")
def get_profile_status() -> str:
    """Get the high-level Sovereign profile and throughput metrics."""
    try:
        profile = db.get_profile()
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
            db.log_activity(project_id="main", tool="MCP", action="serve_context", cost_tokens=5, payload={"resource": "side://brain/graph"})
        except Exception as e:
            return json.dumps({"error": f"Insufficient SUs for Context Provisioning: {e}"}, indent=2)

        brain_path = Path(".side/sovereign.json")
        if not brain_path.exists():
            return json.dumps({"error": "Brain not initialized. Run 'side feed' first."}, indent=2)
        return shield.unseal_file(brain_path)
    except Exception as e:
        return f"Error reading brain: {e}"

@mcp.resource("side://context/sovereign")
def get_sovereign_context() -> str:
    """
    The 'Golden Record' for Infinite Context.
    Combines Mandates (What to do) with Rejections (What NOT to do).
    Inject this into the prompt footer to stop 'Beautiful Wrong Directions'.
    """
    try:
        # 1. Fetch Mandates (The North Star)
        mandates = db.list_decisions(category="mandate")
        
        # 2. Fetch Rejections (The Anti-Pattern)
        rejections = db.list_rejections(limit=10)
        
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
        db.log_activity(project_id=project_id, tool=type, action="record_intent", cost=cost, payload={"outcome": outcome})
        return f"Sovereign intent recorded: {type} -> {outcome}"
    except Exception as e:
        return f"Failed to record intent: {e}"

@mcp.tool()
def query_ledger(limit: int = 20) -> str:
    """
    Retrieve recent execution history from the Sovereign Ledger.
    """
    try:
        ledger = db.get_recent_ledger(limit=limit)
        return json.dumps(ledger, indent=2)
    except Exception as e:
        return f"Query failure: {e}"

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
    Amnesia Recovery: Force-injects the derived project strategy back into the LLM.
    Use this when the LLM is lost or hallucinating architectural decisions.
    
    Args:
        context_query: The specific problem the LLM is failing to solve due to 'Amnesia'.
    """
    from side.intel.auto_intelligence import AutoIntelligence
    intel = AutoIntelligence(Path.cwd())
    dna = intel.get_condensed_dna() # Real derived DNA
    
    # 1. DEBIT WALLET (Strategic Recovery Cost)
    db.log_activity(project_id="main", tool="AMNESIA_RECOVERY", action="restore_order", cost_tokens=50)
    
    report = [
        "🧠 [AMNESIA RECOVERY ENGAGED]",
        "---------------------------------------------------",
        f"ISSUE: {context_query}",
        "---------------------------------------------------",
        "🦅 [SOVEREIGN DNA INJECTION]:",
        dna,
        "---------------------------------------------------",
        "⚡ [INSTRUCTION]: LLM, you are now re-synced with the CODE Reality.",
        "Stop hallucinating. Trust the DNA over your generic weights.",
        "---------------------------------------------------"
    ]
    return "\n".join(report)

if __name__ == "__main__":
    mcp.run()
