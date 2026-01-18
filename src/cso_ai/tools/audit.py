"""
Audit tool handler for CSO.ai.

Handles: run_audit

Implements Killer Features UX Strategy with curiosity gap pattern.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cso_ai.tools.core import get_database
from cso_ai.tools.formatting import format_audit_summary, format_audit_finding
from cso_ai.utils import handle_tool_errors

logger = logging.getLogger(__name__)


@handle_tool_errors
async def handle_run_audit(arguments: dict[str, Any]) -> str:
    """
    Run forensic audit on the codebase.
    
    Uses curiosity gap pattern: show magnitude, let user explore details.
    """
    start_time = datetime.now(timezone.utc)
    
    # Get project root
    project_root = Path.cwd()
    
    # Run forensic scan using the new DRY ForensicEngine
    from cso_ai.intel.forensic_engine import ForensicEngine
    from cso_ai.intel.intelligence_store import IntelligenceStore
    from cso_ai.storage.simple_db import SimplifiedDatabase
    
    engine = ForensicEngine(str(project_root))
    findings = engine.scan()
    
    # Store findings
    db = get_database()
    store = IntelligenceStore(db)
    project_id = SimplifiedDatabase.get_project_id(project_root)
    new_count = store.store_findings(project_id, findings)
    
    # Get Strategic IQ
    strategic_iq = store.get_strategic_iq(project_id)
    stats = store.get_finding_stats(project_id)
    
    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    # Determine top issue
    if findings:
        top_finding = findings[0]  # Already sorted by severity
        top_issue = f"{top_finding.type} in {Path(top_finding.file).name}"
    else:
        top_issue = "No issues detected"
    
    # Use curiosity gap pattern: show summary, let user explore
    output = format_audit_summary(
        critical=stats['critical'],
        high=stats['high'],
        medium=stats['medium'],
        top_issue=top_issue,
        follow_ups=[
            "Show all findings?",
            "Fix critical issues first?",
            "Export to plan.md?"
        ]
    )
    
    # Add timing and IQ footer
    output += "\n\n"
    
    # Strategic IQ card
    if strategic_iq >= 140:
        grade = "🏆 Genius-Tier"
    elif strategic_iq >= 120:
        grade = "💎 Excellent"
    elif strategic_iq >= 100:
        grade = "✅ Good"
    elif strategic_iq >= 80:
        grade = "⚠️ Needs Attention"
    else:
        grade = "🔴 Critical"
    
    output += f"Strategic IQ: {strategic_iq}/160 {grade}\n"
    output += f"⚡ Scanned in {elapsed:.1f}s"
    
    # If user wants more detail, they can ask follow-up questions
    # This is handled by the LLM conversation context
    
    return output
