"""
Sidelith MCP Server - The Official Sovereign SDK Gateway.

This is the primary, natural interface for IDEs (Cursor, VS Code) and external 
Agents to interact with the Sidelith Sovereign Core. 

Compliance: Model Context Protocol (MCP) standards.
Philosophy: Natural platform integration over custom extensions.
"""

from typing import List, Optional
from fastmcp import FastMCP
import json
from pathlib import Path
from datetime import datetime, timezone
from .storage.simple_db import SimplifiedDatabase

# Setup
mcp = FastMCP("Sidelith Sovereign")
db = SimplifiedDatabase()

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

# ---------------------------------------------------------------------
# TOOLS (Actionable Capabilities)
# ---------------------------------------------------------------------

@mcp.tool()
def record_strategic_intent(project_id: str, type: str, outcome: str = "PASS", cost: int = 5) -> str:
    """
    Record a strategic intent or action into the Sovereign Ledger.
    
    Args:
        project_id: The ID of the current project.
        type: The type of event (e.g. 'DOC_REFINE', 'AUTH_SHIFT').
        outcome: The outcome status ('PASS', 'VIOLATION', 'DRIFT').
        cost: The SU cost for this action.
    """
    try:
        db.log_activity(project_id=project_id, type=type, cost=cost, outcome=outcome)
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

if __name__ == "__main__":
    mcp.run()
