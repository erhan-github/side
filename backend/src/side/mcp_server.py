"""
Side MCP Server - The Living Bridge.

Part of the Open Context Protocol (OCP).
Exposes the Monolith (SQLite) and Event Clock to external Agents.
"""

from typing import List, Optional
from fastmcp import FastMCP
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from .common.telemetry import monitor

# Setup
mcp = FastMCP("Side Monolith")

# DB Connection Helper
def get_db_path():
    return Path.home() / ".side" / "local.db"

def get_connection():
    return sqlite3.connect(get_db_path())

# ---------------------------------------------------------------------
# RESOURCES (Read-Only State)
# ---------------------------------------------------------------------

@mcp.resource("side://events/recent")
@monitor("mcp_read_events")
def get_recent_events() -> str:
    """Get the last 50 events from the Event Clock."""
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT 50").fetchall()
        events = [dict(row) for row in rows]
        conn.close()
        return json.dumps(events, indent=2)
    except Exception as e:
        return f"Error reading events: {e}"

@mcp.resource("side://findings/active")
def get_active_findings() -> str:
    """Get all unresolved forensic findings."""
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM findings WHERE resolved_at IS NULL ORDER BY severity").fetchall()
        findings = [dict(row) for row in rows]
        conn.close()
        return json.dumps(findings, indent=2)
    except Exception as e:
        return f"Error reading findings: {e}"

@mcp.resource("side://monolith/summary")
def get_monolith_summary() -> str:
    """Get the high-level health summary."""
    # Could read from MONOLITH.md or compute on fly
    # Computing on fly is more 'Live'
    try:
        conn = get_connection()
        total = conn.execute("SELECT COUNT(*) FROM findings WHERE resolved_at IS NULL").fetchone()[0]
        critical = conn.execute("SELECT COUNT(*) FROM findings WHERE resolved_at IS NULL AND severity='CRITICAL'").fetchone()[0]
        
        return f"""# Side Monolith Status
- Active Findings: {total}
- Critical Issues: {critical}
- Last Event: {datetime.now().isoformat()}
"""
    except Exception as e:
        return f"Error: {e}"

# ---------------------------------------------------------------------
# TOOLS (Actionable Capabilities)
# ---------------------------------------------------------------------

@mcp.tool()
def query_context(query: str) -> str:
    """
    Search the context graph for answers.
    Currently supports simple partial matching on finding messages.
    """
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        # Simple LIKE search
        q_str = f"%{query}%"
        rows = conn.execute(
            "SELECT * FROM findings WHERE message LIKE ? OR type LIKE ?", 
            (q_str, q_str)
        ).fetchall()
        results = [dict(row) for row in rows]
        conn.close()
        
        if not results:
            return "No matching context found."
            
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error executing query: {e}"

@mcp.tool()
def log_decision(decision: str, reasoning: str) -> str:
    """
    Explicitly log a strategic decision into the Monolith.
    """
    # This would write to 'decisions' table or 'events'
    # Simplified for V1
    return f"Logged decision: {decision} (Not fully implemented yet)"

# ---------------------------------------------------------------------
# STRATEGY TOOLS (The Trojan Horse)
# ---------------------------------------------------------------------

@mcp.tool()
@monitor("mcp_trigger_strategy")
def trigger_strategy(intent: str, file_context: Optional[str] = None) -> str:
    """
    [Architect Level] Trigger a multi-step background strategy.
    
    Use this when the user asks for a complex task like "Refactor X" or "Audit Project".
    It does not return code immediately. It returns a Strategy ID.
    
    Args:
        intent: The high-level goal (e.g., "Refactor auth.py for simplicity")
        file_context: Optional filename to focus on.
        
    Returns:
        Strategy ID (Batch ID) to track progress.
    """
    try:
        from .storage.simple_db import SimplifiedDatabase
        from .workers.queue import JobQueue
        from .workers.decomposer import TaskDecomposer
        
        db = SimplifiedDatabase() # Connects to global .side/local.db
        queue = JobQueue(db)
        decomposer = TaskDecomposer(queue, db.get_project_id())
        
        context = {}
        if file_context:
            context['file'] = file_context
            
        batch_id = decomposer.decompose_request(intent, context)
        return f"Strategy Started. ID: {batch_id}. Use `get_strategy_status('{batch_id}')` to check progress."
    except Exception as e:
        return f"Error triggering strategy: {e}"

@mcp.tool()
def get_strategy_status(strategy_id: str) -> str:
    """
    Check the progress of a background strategy.
    """
    try:
        # For now, since decomposer just returns a string batch ID and enqueues jobs,
        # we can check the queue for pending jobs.
        # In a real impl, we'd query a 'batches' table. 
        # For V1, we'll just check if there are ANY pending jobs.
        from .storage.simple_db import SimplifiedDatabase
        db = SimplifiedDatabase()
        
        with db._connection() as conn:
            pending = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='pending'").fetchone()[0]
            running = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='running'").fetchone()[0]
            completed = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='completed' LIMIT 5").fetchone()[0]
            
        return f"Strategy Status: {pending} Pending, {running} Running. (Last 5 completed: {completed})"
    except Exception as e:
        return f"Error checking status: {e}"

if __name__ == "__main__":
    mcp.run()
