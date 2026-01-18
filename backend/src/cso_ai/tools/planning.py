"""
Planning tool handlers for CSO.ai.

Handles: plan, check
"""

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cso_ai.tools.core import get_auto_intel, get_database
from cso_ai.tools.formatting import format_plan
from cso_ai.utils import handle_tool_errors

logger = logging.getLogger(__name__)


@handle_tool_errors
async def handle_plan(arguments: dict[str, Any]) -> str:
    """
    The Flagship Feature: PROACTIVE Strategic Goal Planning.
    
    - Auto-detects goal completion from git commits
    - Warns about stalled goals
    - Asks proactive questions
    """
    db = get_database()
    auto_intel = get_auto_intel()
    
    goal_text = arguments.get("goal")
    due_date = arguments.get("due")
    
    output = ""
    
    # Proactive: Auto-detect completions from git
    pending_goals = db.list_goals(status="pending")
    if pending_goals:
        detected = await auto_intel.detect_goal_completion(pending_goals)
        for d in detected:
            db.update_goal_status(d["goal_id"], "done")
            output += f"🎉 **DETECTED COMPLETION!**\n"
            output += f"Goal: \"{d['goal_title']}\"\n"
            output += f"Based on commit: `{d['commit_message'][:50]}...`\n"
            output += f"Marking as DONE.\n\n"
    
    # Bi-directional sync: Read changes from PLAN.md
    sync_result = _sync_plan_from_file(db)
    if sync_result.get("updated", 0) > 0:
        output += f"🔄 **SYNCED** {sync_result['updated']} item(s) from `.cso/PLAN.md`\n\n"
    
    # Proactive: Check for due checkpoints
    due_checkpoints = db.get_due_checkpoints()
    if due_checkpoints and not goal_text:
        output += "☀️ **CHECK-IN TIME**\n\n"
        for cp in due_checkpoints[:3]:
            output += f"📍 {cp['goal_title']}: {cp['prompt']}\n"
        output += "\n"
    
    # If a new goal is provided, save it
    if goal_text:
        goal_id = str(uuid.uuid4())[:8]
        
        # Auto-detect plan type from keywords
        goal_lower = goal_text.lower()
        if any(kw in goal_lower for kw in ["objective", "vision", "ultimately", "$100m", "exit", "build a"]):
            plan_type = "objective"
            icon = "🎯"
        elif any(kw in goal_lower for kw in ["milestone", "by end of", "this year", "1000 users", "launch"]):
            plan_type = "milestone"
            icon = "🏁"
        elif any(kw in goal_lower for kw in ["fix", "bug", "implement", "add", "remove", "update"]):
            plan_type = "task"
            icon = "✓"
        else:
            plan_type = "goal"
            icon = "📌"
        
        # Save to plans table
        db.save_plan(
            plan_id=goal_id,
            title=goal_text,
            plan_type=plan_type,
            due_date=due_date,
        )
        
        # Auto-create a check-in prompt for non-task plans
        if plan_type in ["objective", "milestone", "goal"]:
            cp_id = str(uuid.uuid4())[:8]
            db.save_check_in(
                check_in_id=cp_id,
                plan_id=goal_id,
                status="on_track",
                note=f"Created: {goal_text[:50]}",
            )
        
        output += f"{icon} **{plan_type.upper()}** Added!\n\n"
        output += f"**{goal_text}**\n"
        if due_date:
            output += f"📅 Due: {due_date}\n"
        output += f"🆔 ID: `{goal_id}`\n\n"
    
    # Always show the full plan
    all_plans = db.list_plans()
    output += format_plan(all_plans)
    
    # Proactive: Ask about stalled goals
    stalled_plans = [p for p in all_plans if p.get("status") == "active" and p.get("due_date")]
    if stalled_plans and not goal_text:
        output += "\n\n📊 **PROGRESS CHECK**\n"
        for p in stalled_plans[:2]:
            output += f"\n📌 \"{p['title']}\" - How's it going?\n"
            if p.get("due_date"):
                output += f"   Due: {p['due_date']}\n"
            output += f"   → Say \"done\" or \"drop {p['id']}\" to update.\n"
    
    # Generate .cso/PLAN.md file
    plan_file_path = _generate_plan_file(db)
    if plan_file_path:
        output += f"\n\n📄 Plan saved: `.cso/PLAN.md`\n"
    
    return output


@handle_tool_errors
async def handle_check(arguments: dict[str, Any]) -> str:
    """Mark a goal as done or update its status."""
    db = get_database()
    
    goal_query = arguments.get("goal", "")
    new_status = arguments.get("status", "done")
    
    if not goal_query:
        return "❌ Please specify which goal to update (e.g., 'check \"Launch MVP\"')"
    
    # Find matching goal
    all_plans = db.list_plans()
    matching = None
    
    for p in all_plans:
        if goal_query.lower() in p['title'].lower() or goal_query == p.get('id'):
            matching = p
            break
    
    if not matching:
        return f"❌ No goal found matching \"{goal_query}\"\n\nUse `plan` to see your current goals."
    
    # Update status
    db.update_plan_status(matching['id'], new_status)
    
    output = f"✅ **Goal Updated!**\n\n"
    output += f"**{matching['title']}** → `{new_status.upper()}`\n\n"
    
    # Show updated plan
    all_plans = db.list_plans()
    output += format_plan(all_plans)
    
    return output


def _sync_plan_from_file(db) -> dict:
    """Bi-directional sync: Parse PLAN.md to detect checkbox changes."""
    try:
        cso_dir = Path.cwd() / ".cso"
        plan_path = cso_dir / "PLAN.md"
        
        if not plan_path.exists():
            return {"updated": 0}
        
        content = plan_path.read_text()
        updated = 0
        
        # Parse checkboxes
        import re
        for line in content.split("\n"):
            match = re.match(r"- \[([ xX])\] (.+?)(?:\s*\(|$)", line)
            if match:
                is_done = match.group(1).lower() == "x"
                title = match.group(2).strip()
                
                # Find and update matching plan
                plans = db.list_plans()
                for p in plans:
                    if title.lower() in p['title'].lower():
                        current_done = p.get('status') in ['done', 'completed']
                        if is_done != current_done:
                            new_status = 'done' if is_done else 'active'
                            db.update_plan_status(p['id'], new_status)
                            updated += 1
                        break
        
        return {"updated": updated}
        
    except Exception as e:
        logger.warning(f"Failed to sync from PLAN.md: {e}")
        return {"updated": 0}


def _generate_plan_file(db) -> str | None:
    """Generate .cso/PLAN.md file as visual dashboard."""
    try:
        cso_dir = Path.cwd() / ".cso"
        cso_dir.mkdir(exist_ok=True)
        
        plan_path = cso_dir / "PLAN.md"
        
        # Get all data
        all_plans = db.list_plans()
        decisions = db.list_decisions()
        learnings = db.list_learnings()
        
        # Build markdown
        lines = [
            "# Strategic Plan",
            "",
            f"_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_",
            "",
        ]
        
        # Objectives
        objectives = [p for p in all_plans if p.get("type") == "objective"]
        if objectives:
            lines.append("## Objectives (5+ years)")
            for o in objectives:
                status = "x" if o.get("status") == "done" else " "
                lines.append(f"- [{status}] {o['title']}")
            lines.append("")
        
        # Milestones
        milestones = [p for p in all_plans if p.get("type") == "milestone"]
        if milestones:
            lines.append("## Milestones (This Year)")
            for m in milestones:
                status = "x" if m.get("status") == "done" else " "
                due = f" (due: {m['due_date']})" if m.get("due_date") else ""
                lines.append(f"- [{status}] {m['title']}{due}")
            lines.append("")
        
        # Goals
        goals = [p for p in all_plans if p.get("type") == "goal"]
        if goals:
            lines.append("## Goals (This Month)")
            for g in goals:
                status = "x" if g.get("status") in ["done", "completed"] else " "
                due = f" (due: {g['due_date']})" if g.get("due_date") else ""
                lines.append(f"- [{status}] {g['title']}{due}")
            lines.append("")
        
        # Tasks
        tasks = [p for p in all_plans if p.get("type") == "task"]
        if tasks:
            lines.append("## Tasks (This Week)")
            for t in tasks:
                status = "x" if t.get("status") == "done" else " "
                lines.append(f"- [{status}] {t['title']}")
            lines.append("")
        
        # Stats
        total = len([p for p in all_plans if p.get("type") in ["goal", "task"]])
        done = len([p for p in all_plans if p.get("status") in ["done", "completed"] and p.get("type") in ["goal", "task"]])
        progress = int((done / total) * 100) if total > 0 else 0
        
        lines.extend([
            "---",
            "",
            "## Stats",
            f"- Progress: {progress}% ({done}/{total})",
            f"- Decisions made: {len(decisions)}",
            f"- Learnings captured: {len(learnings)}",
        ])
        
        plan_path.write_text("\n".join(lines))
        return str(plan_path)
        
    except Exception as e:
        logger.warning(f"Failed to generate PLAN.md: {e}")
        return None
