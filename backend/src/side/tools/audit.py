"""
Audit tool handler for Side.

Handles: run_audit

Implements Forensic-level audit with Safety First protocol.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Note: get_database unused for now, but kept for future DB logging
from side.utils import handle_tool_errors
from side.forensic_audit.runner import ForensicAuditRunner
from side.forensic_audit.core import AuditFixRisk, Severity, AuditStatus
from side.tools.formatting import ToolResult

logger = logging.getLogger(__name__)


@handle_tool_errors
async def handle_run_audit(arguments: dict[str, Any]) -> str:
    """
    Run Side Forensic Audit on the codebase.
    
    Arguments:
        dimension (Optional[str]): Specific dimension to audit (e.g., 'security')
        format (str): Output format ('summary', 'full', 'json')
        show_passed (bool): Whether to show passed checks
    """
    start_time = datetime.now(timezone.utc)
    
    # Auto-detect workspace root (if running from backend/frontend subdirs)
    cwd = Path.cwd()
    project_root = cwd
    if (cwd / ".." / "web").exists() and (cwd / ".." / "backend").exists():
        project_root = cwd.parent
        print(f"📍 Detected workspace root: {project_root}")
    elif (cwd / ".git").exists():
        project_root = cwd
        
    
    # Extract arguments
    dimension = arguments.get('dimension')
    fmt = arguments.get('format', 'summary')
    
    # Run Audit
    runner = ForensicAuditRunner(str(project_root))
    
    if dimension:
        # Run specific dimension
        summary = runner.run_dimension(dimension)
        if not summary:
            return f"❌ Unknown dimension: {dimension}. Valid dimensions: security, performance, database, etc."
    else:
        # Run full audit
        summary = runner.run()

    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    # Format Output based on Safety First Protocol
    lines = []
    
    # header
    lines.append(f"🛡️ **Side Forensic Audit Results** ({elapsed:.1f}s)")
    lines.append(f"Grade: **{summary.grade}** ({summary.grade_label})")
    lines.append("")
    
    # CRITICAL / SAFETY FIRST (Actionable)
    critical_issues = []
    safe_fixes = []
    
    all_results = []
    for dim_results in summary.results_by_dimension.values():
        all_results.extend(dim_results)
        
    for res in all_results:
        if res.status.value in ['fail', 'warn']:
            if res.severity == Severity.CRITICAL:
                critical_issues.append(res)
            if res.fix_risk == AuditFixRisk.SAFE:
                safe_fixes.append(res)
                
    if critical_issues:
        lines.append("### 🔴 Critical Issues (Fix Immediately)")
        for i, issue in enumerate(critical_issues[:5], 1):
             lines.append(f"{i}. **{issue.check_name}** ({issue.check_id})")
             lines.append(f"   - Risk: {issue.fix_risk.value.upper()}")
             lines.append(f"   - Recommendation: {issue.recommendation}")
             if issue.evidence:
                 lines.append(f"   - Location: `{issue.evidence[0].file_path}:{issue.evidence[0].line_number}`")
        lines.append("")

    # SAFE FIXES (Quick Wins)
    if safe_fixes:
        lines.append(f"### 🟢 Safe Fixes Available ({len(safe_fixes)})")
        lines.append("These issues are 100% deterministic and safe to auto-fix.")
        for issue in safe_fixes[:3]:
            lines.append(f"- {issue.check_name} ({len(issue.evidence)} instances)")
        lines.append("   ➡️ *Ready to auto-fix*")
        lines.append("")

    # WARNINGS (Backlog) - only in full mode
    if summary.warnings > 0 and fmt != 'summary':
        lines.append(f"### ⚠️ Warnings ({summary.warnings})")
        lines.append("Run with `format='full'` to see details.")
        lines.append("")

    # READINESS / MOCK STATUS
    readiness_results = [r for r in all_results if r.dimension == "Product Readiness" and r.status.value in ['warn', 'info', 'fail']]
    if readiness_results:
        lines.append(f"### 🚧 Work In Progress (Mock/Todo)")
        for check in readiness_results:
            lines.append(f"- **{check.check_name}**: {check.notes}")
            if check.evidence:
                lines.append(f"  > Found {len(check.evidence)} instances (e.g. `{check.evidence[0].context}`)")
        lines.append("")
    
    # ARCHITECTURE OPPORTUNITIES (new!)
    arch_check_ids = ['CQ-010', 'CQ-011', 'CQ-012', 'CQ-013']
    arch_results = [r for r in all_results if r.check_id in arch_check_ids and r.status.value in ['warn', 'info']]
    if arch_results:
        lines.append("### 🔧 Architecture Opportunities")
        for check in arch_results:
            lines.append(f"- **{check.check_name}**: {check.notes}")
            if check.evidence and check.evidence[0].context:
                lines.append(f"  > {check.evidence[0].context}")
            if check.evidence and check.evidence[0].suggested_fix:
                lines.append(f"  > 💡 {check.evidence[0].suggested_fix}")
        lines.append("")
        
    # LIVE SYSTEM FAILURES
    live_results = [r for r in all_results if r.dimension == "Live System" and r.status.value in ['fail', 'warn']]
    if live_results:
        lines.append(f"### 🚨 Live System Issues")
        for check in live_results:
             lines.append(f"- **{check.check_name}**: {check.notes}")
             for ev in check.evidence[:3]:
                 lines.append(f"  > {ev.description} at `{ev.context}`")
        lines.append("")

    # SKIPPED CHECKS
    skipped_checks = [r for r in all_results if r.status == AuditStatus.SKIP]
    if skipped_checks:
        lines.append(f"### ⏭️ Skipped Checks ({len(skipped_checks)})")
        for check in skipped_checks:
            lines.append(f"- **{check.check_name}**: {check.notes}")
            if check.recommendation:
                 lines.append(f"  > Tip: {check.recommendation}")
        lines.append("")

    # PERFECT SCORES
    perfect_dims = [d for d, res in summary.results_by_dimension.items() 
                   if all(r.status.value == 'pass' for r in res) and res]
    
    if perfect_dims:
        lines.append(f"### ✅ Perfect Scores")
        lines.append(f"{', '.join(perfect_dims)}")
        lines.append("")

    # Footer
    lines.append(f"Run full report: `@side audit report`")
    
    # Log to DB (Hidden)
    # TODO: Implement DB logging
    
    return "\n".join(lines)


if __name__ == "__main__":
    import asyncio
    import sys
    
    # Simple CLI wrapper
    args = {}
    if len(sys.argv) > 1:
        args['dimension'] = sys.argv[1]
    
    print("🛡️  Starting Side Forensic Audit...")
    try:
        result = asyncio.run(handle_run_audit(args))
        print("\n" + result)
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        import traceback
        traceback.print_exc()
