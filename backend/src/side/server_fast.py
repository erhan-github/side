"""
Side Server (FastMCP Edition) - "Grammarly for Strategy"

This is the modernized, type-safe implementation of the Side MCP Server.
It runs in parallel with the legacy `mcp_server.py` to allow safe fallback.

To run:
    fastmcp run side.server_fast
"""

from pathlib import Path
from typing import Any, List, Optional
import os
import asyncio
import json


try:
    from fastmcp import FastMCP, Context
except ImportError:
    raise ImportError("FastMCP is not installed. Run `pip install fastmcp`.")

from side.intel.forensic_engine import ForensicEngine
from side.intel.intelligence_store import IntelligenceStore
from side.logging_config import setup_logging
from side.telemetry import telemetry, init_telemetry

# [DATABASE REF: SQLModel Migration]
from side.storage.database import get_session, Project, Activity, Finding
from sqlmodel import select

# Initialize Logging
setup_logging(log_level=os.getenv("SIDE_LOG_LEVEL", "INFO"))

# Initialize Telemetry (Sentry + PostHog)
init_telemetry()

# Initialize FastMCP
mcp = FastMCP("Side Monolith")

# -----------------------------------------------------------------------------
# Core State Initialization
# -----------------------------------------------------------------------------
try:
    project_root = Path.cwd()
    project_root_str = str(project_root)
    
    # Database (SQLModel Session)
    # We use a session factory or create distinct sessions per request?
    # For a simple MCP server, creating a fresh session per resource call is safer for threading.
    # We'll rely on get_session() inside tools/resources.
    
    # Legacy Engine (Keep for IntelligenceStore until fully ported)
    from side.storage.simple_db import SimplifiedDatabase
    simple_db = SimplifiedDatabase(str(project_root / ".side" / "local.db"))
    
    intel_store = IntelligenceStore(simple_db)
    forensic_engine = ForensicEngine(project_root_str)
    
    # Project ID (Still use helper for consistency)
    project_id = SimplifiedDatabase.get_project_id(project_root)
    
except Exception as e:
    print(f"⚠️ Initialization Warning: {e}")
    # Allow partial startup for debugging

# -----------------------------------------------------------------------------
# Tools (Actions)
# -----------------------------------------------------------------------------

@mcp.tool()
@telemetry("get_strategic_alerts")
async def get_strategic_alerts(severity: str = None, rescan: bool = False) -> str:
    """Get active strategic alerts (security gaps, architectural bloat, stale docs)."""
    if rescan:
        findings = await forensic_engine.scan()
        intel_store.store_findings(project_id, findings)
    
    findings = intel_store.get_active_findings(project_id, severity)
    
    if not findings:
        return "✅ No active strategic alerts. Clean!"
    
    output = f"🔍 **Strategic Alerts** ({len(findings)} active)\n\n"
    for f in findings:
        icon = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡'}.get(f['severity'], '⚪')
        output += f"{icon} **{f['type']}** ({f['severity']})\n"
        output += f"   📁 `{f['file']}`\n   💬 {f['message']}\n   🆔 `{f['id']}`\n\n"
    return output


@mcp.tool()
async def get_strategic_iq() -> str:
    """Get the current Strategic IQ score (0-160)."""
    score = intel_store.get_strategic_iq(project_id)
    stats = intel_store.get_finding_stats(project_id)
    percentage = min(100, (score / 160) * 100)
    
    label = "Production Ready" if percentage >= 90 else "Needs Polish"
    output = f"**Strategic IQ: {int(percentage)}%** ({label})\n\n"
    output += f"- 🔴 Critical: {stats['critical']}\n"
    output += f"- 🟠 High: {stats['high']}\n"
    return output


@mcp.tool()
async def resolve_finding(finding_id: str) -> str:
    """Mark a strategic finding as resolved."""
    if intel_store.resolve_finding(finding_id):
        return f"✅ Finding `{finding_id}` resolved"
    return f"❌ Finding `{finding_id}` not found"


@mcp.tool()
@telemetry("scan_project")
async def scan_project() -> str:
    """Run a full forensic scan."""
    findings = await forensic_engine.scan()
    new_count = intel_store.store_findings(project_id, findings)
    return f"✅ Scan complete. Found {len(findings)} issues ({new_count} new)."


@mcp.tool()
async def trigger_sentry_error() -> str:
    """Trigger a deliberate error to verify Sentry reporting."""
    division_by_zero = 1 / 0
    return str(division_by_zero)


# -----------------------------------------------------------------------------
# Resources (Data) via SQLModel
# -----------------------------------------------------------------------------

@mcp.resource("side://monolith")
def get_monolith() -> str:
    """The live Command Center dashboard."""
    path = project_root / ".side" / "MONOLITH.md"
    if path.exists():
        return path.read_text()
    return "# Monolith Not Found\nRun logic not initialized."

@mcp.resource("side://activity")
def get_activity_log() -> str:
    """Recent system actions and costs."""
    # [SQLModel] Clean ORM query
    with get_session() as session:
        statement = select(Activity).where(Activity.project_id == project_id).order_by(Activity.created_at.desc()).limit(20)
        results = session.exec(statement).all()
        # Convert to dicts for JSON
        return str([r.model_dump() for r in results])

@mcp.resource("side://profile")
def get_profile() -> str:
    """Pilot Profile and Gamification Stats."""
    # [SQLModel] Clean ORM query
    with get_session() as session:
        # Assuming Profile ID keying needs alignment, simpler to select by ID or fallback
        # In simple_db we used project_id as ID for profile? 
        # Wait, simple_db.py defines INSERT INTO profile with ID=project_id.
        profile = session.get(Project, project_id)
        if not profile:
             return "{}"
        
        prof_dict = profile.model_dump()
        
        # Add legacy stats if needed (from raw table)
        # We haven't ported 'user_stats' model yet, so keep raw SQL for that one specific join?
        # Or just skip gamification stats in this MVP refactor.
        # Let's keep it simple.
        return str(prof_dict)

@mcp.resource("side://tips")
def get_daily_tip() -> str:
    """Strategic tips and system hacks."""
    import random
    return random.choice([
        "💡 Tip: Run 'quick scan' daily.",
        "💡 Tip: 'Deep Audits' grant 4x more XP.",
        "💡 Hack: Use 'strategy' tool with context."
    ])


# -----------------------------------------------------------------------------
# Prompts (Templates)
# -----------------------------------------------------------------------------

@mcp.prompt()
def brief() -> str:
    """Mission Briefing: Strategic status and today's focus."""
    return f"Side, give me a Strategic Mission Briefing. Analyze my recent context from `side://activity` and tell me what to focus on."

@mcp.prompt()
def consult(question: str) -> str:
    """Strategic Consultation: Get a CTO-level decision."""
    return f"Side, I need a CTO-level decision on: '{question}'. Analyze trade-offs and give a YES/NO verdict."

@mcp.prompt()
def fix_security_critical() -> str:
    """Fix Critical Security Issues."""
    return "Hey Side, list all critical security issues. For each: Explain risk, Propose fix, Apply fix, Verify."

@mcp.prompt()
def fix_performance_critical() -> str:
    """Fix Critical Performance Issues."""
    return "Hey Side, identify N+1 queries and expensive loops. Optimize them and verify speedup."

@mcp.prompt()
def check_truth() -> str:
    """Truth Engine: Verify documentation matches reality."""
    return "Side, compare `README.md` against the actual codebase. Identify 'Hallucinations' (documented but missing features)."


if __name__ == "__main__":
    mcp.run()
