
import logging
import uuid
import os
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from side.tools.core import get_ai_memory, get_engine
from side.tools.formatting import format_plan
from side.utils.errors import handle_tool_errors
from side.services.billing import BillingService, SystemAction
from side.utils.paths import get_side_dir, get_repo_root

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# THE STRATEGIC HUB: System Strategy Center
# ═══════════════════════════════════════════════════════════════════════════
# Removed: HUB_NAME - The Hub is now database-first.

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
    db = get_engine()
    query = arguments.get("goal") or arguments.get("task")
    
    if not query:
        return "❌ Please specify the goal or task to check."
    
    all_plans = db.plans.list_plans(project_id=db.get_project_id())
    matching = next((p for p in all_plans if query.lower() in p['title'].lower()), None)
    
    if not matching:
        return f"❓ Could not find plan matching: \"{query}\""
    
    db.plans.update_plan_status(matching['id'], 'done')

    # STRATEGIC OUTCOME: Record Directive Fulfillment
    try:
        db.audits.log_activity(
            project_id=db.get_project_id(),
            tool="instrumentation",
            action=f"Directive Fulfilled: {matching['title'][:30]}",
            cost_tokens=0,
            tier="system",
            payload={
                "event": f"Directive Fulfilled: {matching['title'][:30]}",
                "value": 2.0,
                "timestamp": datetime.now(timezone.utc).timestamp(),
                "type": "outcome"
            }
        )
    except Exception as ie_err:
        logger.warning(f"Strategy instrumentation failed: {ie_err}")
    
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
        profile = db.profile.get_user_profile(db.get_project_id())
        db.audits.log_activity(
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
    
    return f"✅ [STRATEGIC VECTORING]: Directive fulfilled. The Strategic Hub data updated."


@handle_tool_errors
async def handle_plan(arguments: dict[str, Any]) -> str:
    """
    STRATEGIC VECTORING (Planning).
    The Strategic Hub: System Machine Intelligence.
    """
    db = get_engine()
    auto_intel = get_ai_memory()
    
    goal_text = arguments.get("goal")
    due_date = arguments.get("due")
    
    output = ""
    
    # 1. Auto-Detection via Git DNA
    project_id = db.get_project_id()
    pending_goals = db.plans.list_plans(project_id=project_id, status="active")
    if pending_goals:
        detected = await auto_intel.detect_goal_completion(pending_goals)
        for d in detected:
            db.plans.update_plan_status(d["goal_id"], "done")
            
            # LOG AUTO-COMPLETION
            try:
                profile = db.profile.get_user_profile(db.get_project_id())
                db.audits.log_activity(
                    project_id=db.get_project_id(),
                    tool="plan",
                    action=f"Auto-alignment: {d['goal_title'][:40]}{'...' if len(d['goal_title']) > 40 else ''}",
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
            
            output += f"🎉 [HUB SYNC]: Directive Fulfilled via Git DNA\n"
            output += f"Ref: \"{d['goal_title']}\"\n"
            output += f"Evidence: `{d['commit_message'][:50]}...`\n\n"
    
    # 2. Add new directive (Intention Capture)
    if goal_text:
        goal_id = str(uuid.uuid4())[:8]
        goal_lower = goal_text.lower()
        if any(kw in goal_lower for kw in ["objective", "vision", "ultimately", "$100m", "exit"]): plan_type = "objective"
        elif any(kw in goal_lower for kw in ["milestone", "launch", "year"]): plan_type = "milestone"
        elif any(kw in goal_lower for kw in ["fix", "add", "remove"]): plan_type = "task"
        else: plan_type = "goal"
        
        db.plans.save_plan(project_id=project_id, plan_id=goal_id, title=goal_text, plan_type=plan_type, due_date=due_date)
        
        # LOG NEW PLAN
        try:
            profile = db.profile.get_user_profile(db.get_project_id())
            db.audits.log_activity(
                project_id=db.get_project_id(),
                tool="plan",
                action=f"INTENTION CAPTURE: {goal_text[:50]}{'...' if len(goal_text) > 50 else ''}",
                cost_tokens=0,
                tier=profile.get('tier', 'free') if profile else 'free',
                payload={
                    "plan_id": goal_id,
                    "plan_type": plan_type,
                    "title": goal_text
                }
            )
        except Exception as e:
            logger.error(f"Failed to log plan activity: {e}")
        
        output += f"📎 [INTENTION CAPTURED]: [{plan_type.upper()}] {goal_text}\n"

    all_plans = db.plans.list_plans(project_id=project_id)
    output += format_plan(all_plans)
    
    return output


# Removed: _generate_hub_file and _generate_ledger_file - All callers must use get_strategic_hub_data()
