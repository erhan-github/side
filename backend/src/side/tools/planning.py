
import logging
import uuid
import os
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from side.tools.core import get_auto_intel, get_database
from side.tools.formatting import format_plan
from side.utils.errors import handle_tool_errors
from side.intel.evaluator import StrategicEvaluator
from side.utils.paths import get_side_dir, get_repo_root

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# THE MONOLITH PARADIGM: Higher-Dimensional Strategic Sovereignty
# ═══════════════════════════════════════════════════════════════════════════
MONOLITH_NAME = "MONOLITH.md"

def _soften_monolith(path: Path):
    """Temporarily unlock the Monolith for evolution."""
    try:
        if path.exists():
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
    except Exception as e:
        logger.debug(f"Monolith softening skipped: {e}")

def _harden_monolith(path: Path):
    """Seal the Monolith after evolution (Read-only for all)."""
    try:
        if path.exists():
            os.chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    except Exception as e:
        logger.debug(f"Monolith hardening skipped: {e}")

@handle_tool_errors
async def handle_check(arguments: dict[str, Any]) -> str:
    """
    Side fulfills a directive and evolves the Monolith.
    The user communicates intent; Side executes and records.
    """
    db = get_database()
    query = arguments.get("goal") or arguments.get("task")
    
    if not query:
        return "❌ Please specify the goal or task to check."
    
    all_plans = db.list_plans()
    matching = next((p for p in all_plans if query.lower() in p['title'].lower()), None)
    
    if not matching:
        return f"❓ Could not find plan matching: \"{query}\""
    
    db.update_plan_status(matching['id'], 'done')
    
    # LOG COMPLETION
    try:
        profile = db.get_profile(db.get_project_id())
        db.log_activity(
            project_id=db.get_project_id(),
            tool="check",
            action=f"Completed: {matching['title'][:50]}{'...' if len(matching['title']) > 50 else ''}",
            cost_tokens=0,  # Free
            tier=profile.get('tier', 'free') if profile else 'free',
            payload={
                "plan_id": matching['id'],
                "title": matching['title'],
                "plan_type": matching.get('type', 'task')
            }
        )
    except Exception as e:
        logger.error(f"Failed to log check activity: {e}")
    
    # Evolve the Monolith
    _generate_monolith_file(db)
    
    return f"✅ **Directive Fulfilled:** {matching['title']}\nThe Monolith has evolved."


@handle_tool_errors
async def handle_plan(arguments: dict[str, Any]) -> str:
    """
    The Strategic Monolith: Sovereign Machine Intelligence.
    """
    db = get_database()
    auto_intel = get_auto_intel()
    
    goal_text = arguments.get("goal")
    due_date = arguments.get("due")
    
    output = ""
    
    # 1. Auto-Detection via Git
    pending_goals = db.list_plans(status="active")
    if pending_goals:
        detected = await auto_intel.detect_goal_completion(pending_goals)
        for d in detected:
            db.update_plan_status(d["goal_id"], "done")
            
            # LOG AUTO-COMPLETION
            try:
                profile = db.get_profile(db.get_project_id())
                db.log_activity(
                    project_id=db.get_project_id(),
                    tool="plan",
                    action=f"Auto-completed: {d['goal_title'][:40]}{'...' if len(d['goal_title']) > 40 else ''}",
                    cost_tokens=0,
                    tier=profile.get('tier', 'free') if profile else 'free',
                    payload={
                        "plan_id": d["goal_id"],
                        "commit_message": d["commit_message"],
                        "auto_detected": True
                    }
                )
            except Exception as e:
                logger.error(f"Failed to log auto-completion: {e}")
            
            output += f"🎉 **MONOLITH SYNC: Directive Fulfilled**\n"
            output += f"Ref: \"{d['goal_title']}\"\n"
            output += f"Evidence: `{d['commit_message'][:50]}...`\n\n"
    
    # 2. Add new directive (Agency Command)
    if goal_text:
        goal_id = str(uuid.uuid4())[:8]
        goal_lower = goal_text.lower()
        if any(kw in goal_lower for kw in ["objective", "vision", "ultimately", "$100m", "exit"]): plan_type = "objective"
        elif any(kw in goal_lower for kw in ["milestone", "launch", "year"]): plan_type = "milestone"
        elif any(kw in goal_lower for kw in ["fix", "add", "remove"]): plan_type = "task"
        else: plan_type = "goal"
        
        db.save_plan(plan_id=goal_id, title=goal_text, plan_type=plan_type, due_date=due_date)
        
        # LOG NEW PLAN
        try:
            profile = db.get_profile(db.get_project_id())
            db.log_activity(
                project_id=db.get_project_id(),
                tool="plan",
                action=f"Added {plan_type}: {goal_text[:50]}{'...' if len(goal_text) > 50 else ''}",
                cost_tokens=0,  # Free for now
                tier=profile.get('tier', 'free') if profile else 'free',
                payload={
                    "plan_id": goal_id,
                    "plan_type": plan_type,
                    "title": goal_text
                }
            )
        except Exception as e:
            logger.error(f"Failed to log plan activity: {e}")
        
        output += f"📎 **DIRECTIVE LOGGED:** [{plan_type.upper()}] {goal_text}\n"

    # 3. Evolve and Seal the Monolith
    monolith_path = _generate_monolith_file(db)
    if monolith_path:
        output += f"🏛️ **MONOLITH EVOLVED:** {monolith_path}\n"
    
    all_plans = db.list_plans()
    output += format_plan(all_plans)
    
    return output


def _generate_monolith_file(db) -> str | None:
    """Generate and seal the .side/MONOLITH.md as the definitive strategic anchor."""
    try:
        side_dir = get_side_dir()
        monolith_path = side_dir / MONOLITH_NAME
        repo_root = get_repo_root()
        
        # 1. Unlock for Evolution
        _soften_monolith(monolith_path)
        
        # 2. Gather Intelligence
        all_plans = db.list_plans()
        project_id = db.get_project_id(repo_root)
        profile = db.get_profile(project_id) or {}
        audit_summary = db.get_audit_summary(project_id)
        activities = db.get_recent_activities(project_id, limit=100)
        
        eval_result = StrategicEvaluator.calculate_iq(
            profile, all_plans, audit_summary, 
            project_root=repo_root, 
            activities=activities
        )
        
        # 3. Render Dashboard
        lines = [
            "<!-- 🔐 MONOLITH LOCK: This is a machine-sovereign asset. Hand-editing is prohibited. -->",
            "",
            "# ⬛ THE MONOLITH",
            "> *Strategic Sovereignty // ALPHA-0 [IMMUTABLE]*",
            "",
            f"**Temporal Sync**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            f"**Project Signature**: `{project_id}`",
            "---",
            "",
            "## ⬛ STRATEGIC PULSE",
            f"- **Sovereignty Grade**: {eval_result['grade']} ({eval_result['label']})",
            f"- **Strategic IQ**: {eval_result['score']}/{eval_result.get('max_score', 400)}",
            f"- **Prime Directive**: {eval_result['top_focus']}",
            "",
            "### Dimensional Analysis",
        ]
        
        for k, v in eval_result['dimensions'].items():
            status = "✅" if v >= 32 else "💡" if v >= 28 else "⚠️"
            lines.append(f"- {status} {k:12}: {v}/40")
        lines.append("")

        # Directives (Roadmap)
        lines.append("## 🎯 ACTIVE DIRECTIVES")
        for ptype in ["objective", "milestone", "goal", "task"]:
            items = [p for p in all_plans if p.get("type") == ptype]
            if items:
                lines.append(f"### {ptype.title()}s")
                for i in items:
                    status = "x" if i.get("status") in ["done", "completed"] else " "
                    due = f" (due: {i['due_date']})" if i.get("due_date") else ""
                    lines.append(f"- [{status}] {i['title']}{due}")
                lines.append("")

        # Forensic Snapshot
        if audit_summary:
            lines.append("## 🔬 SECURITY MATRIX")
            colors = {"CRITICAL": "🔴", "WARNING": "🟡", "INFO": "🔵"}
            for sev, count in audit_summary.items():
                if count > 0:
                    lines.append(f"- {colors.get(sev, '⚪')} {sev}: {count}")
            
            recent = db.get_recent_audits(project_id, limit=3)
            if recent:
                lines.append("\n### Anomaly Feed")
                for r in recent:
                    lines.append(f"- **[{r['severity']}]** {r['finding'][:65]}...")
            lines.append("")

        # Machine Context
        lines.extend([
            "---",
            "## 🧠 NEURAL INTERFACE",
            "```yaml",
            "type: side-monolith",
            f"signature: {project_id}",
            f"grade: {eval_result['grade']}",
            f"iq: {eval_result['score']}",
            f"stack: {list(profile.get('languages', {}).keys())}",
            f"sync_at: {datetime.now(timezone.utc).isoformat()}",
            "```",
            "",
            "---",
            "**Transparency Log**",
        ])
        
        activities = db.get_recent_activities(project_id, limit=5)
        for a in activities:
            lines.append(f"- `[{a['created_at'][11:16]}]` **{a['tool'].upper()}** (-{a['cost_tokens']} tokens)")
            
        monolith_path.write_text("\n".join(lines))
        
        # 4. Seal the Monolith
        _harden_monolith(monolith_path)
        
        return str(monolith_path)
        
    except Exception as e:
        logger.warning(f"Monolith Evolution Failed: {e}")
        return None

def _generate_ledger_file(db) -> str | None:
    """Legacy alias redirecting to Monolith."""
    return _generate_monolith_file(db)
