
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
from side.instrumentation.engine import InstrumentationEngine
from side.services.billing import BillingService, SystemAction
from side.utils.paths import get_side_dir, get_repo_root
from side.services.hub import generate_hub

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# THE STRATEGIC HUB: Higher-Dimensional Strategic Sovereignty
# ═══════════════════════════════════════════════════════════════════════════
HUB_NAME = "HUB.md"

def _soften_hub(path: Path):
    """Temporarily unlock the Hub for evolution."""
    try:
        if path.exists():
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
    except Exception as e:
        logger.debug(f"Hub softening skipped: {e}")

def _harden_hub(path: Path):
    """Seal the Hub after evolution (Read-only for all)."""
    try:
        if path.exists():
            os.chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    except Exception as e:
        logger.debug(f"Hub hardening skipped: {e}")

@handle_tool_errors
async def handle_check(arguments: dict[str, Any]) -> str:
    """
    Side fulfills a directive and evolves the Strategic Hub.
    The user communicates intent; Side executes and records.
    """
    db = get_database()
    query = arguments.get("goal") or arguments.get("task")
    
    if not query:
        return "❌ Please specify the goal or task to check."
    
    all_plans = db.strategic.list_plans(project_id=db.get_project_id())
    matching = next((p for p in all_plans if query.lower() in p['title'].lower()), None)
    
    if not matching:
        return f"❓ Could not find plan matching: \"{query}\""
    
    db.strategic.update_plan_status(matching['id'], 'done')

    # INSTRUMENTATION: Record Outcome
    ie = InstrumentationEngine(db)
    ie.record_outcome(db.get_project_id(), f"Directive Fulfilled: {matching['title'][:30]}", 2.0)
    
    # BILLING: Charge for Directive Completion (Strategic Sync)
    billing = BillingService(db)
    pk = db.get_project_id()
    try:
        if billing.can_afford(pk, SystemAction.HUB_UPDATE):
            billing.charge(pk, SystemAction.HUB_UPDATE, "check", {"plan_id": matching['id']})
    except Exception as e:
        logger.warning(f"Billing failed for check: {e}")
    
    # LOG COMPLETION
    try:
        profile = db.identity.get_profile(db.get_project_id())
        db.forensic.log_activity(
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
    
    # Evolve the Hub
    from side.services.hub import generate_hub
    await generate_hub(db)
    
    return f"✅ **Directive Fulfilled:** {matching['title']}\nThe Strategic Hub has evolved."


@handle_tool_errors
async def handle_plan(arguments: dict[str, Any]) -> str:
    """
    The Strategic Hub: Sovereign Machine Intelligence.
    """
    db = get_database()
    auto_intel = get_auto_intel()
    
    goal_text = arguments.get("goal")
    due_date = arguments.get("due")
    
    output = ""
    
    # 1. Auto-Detection via Git
    project_id = db.get_project_id()
    pending_goals = db.strategic.list_plans(project_id=project_id, status="active")
    if pending_goals:
        detected = await auto_intel.detect_goal_completion(pending_goals)
        for d in detected:
            db.strategic.update_plan_status(d["goal_id"], "done")
            
            # LOG AUTO-COMPLETION
            try:
                profile = db.identity.get_profile(db.get_project_id())
                db.forensic.log_activity(
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
            
            output += f"🎉 **HUB SYNC: Directive Fulfilled**\n"
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
        
        db.strategic.save_plan(project_id=project_id, plan_id=goal_id, title=goal_text, plan_type=plan_type, due_date=due_date)
        
        # BILLING: Charge for New Directive
        billing = BillingService(db)
        pk = db.get_project_id()
        try:
             if billing.can_afford(pk, SystemAction.HUB_UPDATE):
                 billing.charge(pk, SystemAction.HUB_UPDATE, "plan", {"plan_id": goal_id})
        except Exception as e:
            logger.warning(f"Billing failed for plan: {e}")
        
        # LOG NEW PLAN
        try:
            profile = db.identity.get_profile(db.get_project_id())
            db.forensic.log_activity(
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

    # 3. Evolve and Seal the Hub
    hub_path = await generate_hub(db)
    if hub_path:
        output += f"🏛️ **HUB EVOLVED:** {hub_path}\n"
    
    all_plans = db.strategic.list_plans(project_id=project_id)
    output += format_plan(all_plans)
    
    return output


async def _generate_hub_file(db) -> str | None:
    """Delegated to service."""
    return await generate_hub(db)

async def _generate_ledger_file(db) -> str | None:
    """Legacy alias redirecting to Strategic Hub."""
    return await generate_hub(db)
