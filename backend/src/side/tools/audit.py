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
from side.intel.intelligence_store import IntelligenceStore
from side.storage.simple_db import SimplifiedDatabase

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
    deep_mode = arguments.get('deep', False)
    only_fast = not deep_mode # Default to FAST only unless --deep is passed
    
    # Run Audit
    runner = ForensicAuditRunner(str(project_root))
    
    if dimension:
        # Run specific dimension (Contextual Upsell happens here)
        summary = await runner.run_dimension(dimension, only_fast=only_fast)
        if not summary:
            return f"❌ Unknown dimension: {dimension}. Valid dimensions: security, performance, database, etc."
    else:
        # Run full audit
        summary = await runner.run(only_fast=only_fast)

    # Apply Auto-Fixes if requested
    fixed_count = 0
    if arguments.get('fix'):
        print("🔧 Applying Auto-Fixes...")
        fixed_count = await runner.apply_fixes(summary)
        print(f"✅ Applied {fixed_count} fixes.")

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

    # CONTEXTUAL UPSELL (Premium Feature)
    if summary.upsell_context:
        dim_name = summary.upsell_context.get('dimension', 'Unknown')
        deep_ids = summary.upsell_context.get('deep_probes', [])
        
        lines.append("---")
        lines.append("")
        lines.append(f"## 🚀 Upgrade to Deep {dim_name} Audit")
        lines.append(f"You just ran the Standard (Static) check for {dim_name}.")
        lines.append("To find logical flaws, bypasses, and architectural violations, use Side Intelligence:")
        lines.append("")
        
        for pid in deep_ids:
            if 'security' in pid:
                lines.append(f"- **Deep Security**: `micro_audit.py {pid} <file>`")
            elif 'logic' in pid:
                lines.append(f"- **Deep Logic**: `micro_audit.py {pid} <file>`")
            elif 'arch' in pid:
                lines.append(f"- **Architecture Sentinel**: `micro_audit.py {pid} <file>`")
            elif 'test' in pid:
                lines.append(f"- **Generative QA**: `micro_audit.py {pid} <file>`")
            elif 'intent' in pid:
                lines.append(f"- **Intent Verification**: `micro_audit.py {pid} <file>`")
        
        lines.append("")
        lines.append("> *Tip: Ask the Agent to run these deep checks on critical files.*")
        lines.append("")

    # GAMIFICATION DISPLAY (Serious Fun)
    if summary.gamification_context:
        g = summary.gamification_context
        
        # Level Up Banner
        if g.get("leveled_up"):
            lines.append("🎉" * 20)
            lines.append(f"   LEVEL UP! You are now Level {g['new_level']}   ")
            lines.append("🎉" * 20)
            lines.append("")
        
        # XP Footer
        # XP Footer
        xp = g.get("xp_gained", 0)
        # Legacy streak removed per serious gamification strategy
        
        footer_parts = [f"✨ +{xp} XP"]
            
        # Economy Display
        su_grant = g.get("su_grant", 0)
        # Also check badge bounties? Bounties are returned in 'unlocked_badges' metadata if we updated runner
        # Wait, runner calls unlock_badge which returns badge dict.
        # engine.unlock_badge now returns 'bounty' key.
        bounty_total = sum(b.get("bounty", 0) for b in g.get("unlocked_badges", []))
        total_sus = su_grant + bounty_total
        
        if total_sus > 0:
            footer_parts.append(f"💰 +{total_sus} SUs")
        
        # Badges removed per Serious Intelligence strategy (No streaks/badges)
            
        lines.append(" | ".join(footer_parts))
        lines.append("")

    # Log to DB (Hidden persistence)
    try:
        db = SimplifiedDatabase()
        project_id = db.get_project_id(project_root)
        store = IntelligenceStore(db)
        store.store_audit_summary(project_id, summary)
        
        # Log activity
        db.log_activity(
            project_id=project_id,
            tool="audit",
            action="Executed Forensic Audit",
            cost_tokens=0,
            tier=summary.grade,
            payload={
                "score": summary.score_percentage,
                "failed": summary.failed,
                "warnings": summary.warnings
            }
        )
        # Evolve the Monolith to reflect new findings
        from side.tools.planning import _generate_monolith_file
        await _generate_monolith_file(db)
        
    except Exception as e:
        logger.error(f"Failed to persist audit results: {e}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import asyncio
    import sys
    
    # Simple CLI wrapper
    args = {}
    if len(sys.argv) > 1:
        # Simple simplistic parser
        for arg in sys.argv[1:]:
            if arg == '--fix':
                args['fix'] = True
            elif arg == '--deep':
                args['deep'] = True
            elif arg.startswith('--'):
                pass # ignore other flags
            else:
                args['dimension'] = arg
    
    print("🛡️  Starting Side Forensic Audit...")
    try:
        result = asyncio.run(handle_run_audit(args))
        print("\n" + result)
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        import traceback
        traceback.print_exc()
