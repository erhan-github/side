"""
Strategic Hub - Database-First Architecture.

[CORE ARCHITECTURE]: Returns data for LLM consumption via MCP directly from Strategic Database.
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


async def get_strategic_hub_data(db: Any) -> Dict[str, Any]:
    """
    [DRY ARCHITECTURE]: Returns strategic hub data directly from database.
    
    No file is created. LLM accesses this via MCP tools.
    
    Returns:
        Dict containing all strategic hub data:
        - project_id: Project identifier
        - objectives: Active strategic objectives
        - friction: Critical/high severity issues
        - milestones: Active milestones
        - completed: Recently completed items
        - activities: Recent activity feed
    """
    project_id = db.get_project_id()
    
    logger.info(f"🏛️ [HUB]: Fetching Strategic Hub data for {project_id}")
    
    # 1. Collect Data from Database (Single Source of Truth)
    plans = db.strategic.list_plans(project_id=project_id)
    activities = db.audit.get_recent_activities(project_id=project_id, limit=5)
    audits = db.audit.get_recent_audits(project_id=project_id, limit=10)
    
    # 2. Process data
    friction = [a for a in audits if a.get('severity') in ['CRITICAL', 'HIGH', 'VIOLATION']]
    objectives = [p for p in plans if p.get('type') == 'objective' and p.get('status') != 'done']
    milestones = [p for p in plans if p.get('type') == 'milestone' and p.get('status') != 'done']
    completed = [p for p in plans if p.get('status') == 'done'][:10]
    
    # 3. Return structured data (not a file)
    hub_data = {
        "project_id": project_id,
        "objectives": objectives,
        "friction": friction,
        "milestones": milestones,
        "completed": completed,
        "activities": activities,
        "summary": {
            "total_objectives": len(objectives),
            "total_friction": len(friction),
            "total_milestones": len(milestones),
            "total_completed": len(completed)
        }
    }
    
    logger.info(f"✨ [HUB]: Project Hub data retrieved. {len(objectives)} objectives, {len(friction)} friction points.")
    
    return hub_data


async def get_strategic_friction(db: Any) -> List[Dict[str, Any]]:
    """
    [DRY ARCHITECTURE]: Returns strategic friction (critical issues) from database.
    
    This provides the "Strategic Friction & Audit Remediation" snapshot for the Hub.
    """
    project_id = db.get_project_id()
    audits = db.audit.get_recent_audits(project_id=project_id, limit=20)
    
    friction = []
    for issue in audits:
        if issue.get('severity') in ['CRITICAL', 'HIGH', 'VIOLATION']:
            friction.append({
                "severity": issue.get('severity'),
                "message": issue.get('message'),
                "file_path": issue.get('file_path', 'Global'),
                "directive": f"Fix the {issue.get('severity')} issue in {issue.get('file_path')}: {issue.get('message')}. Maintain architectural intent."
            })
    
    return friction


# Removed: generate_hub() - All callers must use get_strategic_hub_data()
