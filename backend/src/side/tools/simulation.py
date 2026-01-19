"""
Simulation Tool - Virtual User Testing using the superior Simulator engine.

Uses intel/Simulator with 50+ personas and RAP (Retrieval Augmented Personas)
for grounded, brutal feedback.
"""

import logging
from pathlib import Path
from typing import Any

from side.storage.simple_db import SimplifiedDatabase
from side.intel.simulator import Simulator
from side.utils import handle_tool_errors

logger = logging.getLogger(__name__)


@handle_tool_errors
async def handle_simulate_users(arguments: dict[str, Any]) -> str:
    """
    Run a Virtual User Simulation on your feature/idea.
    
    Uses the RAP (Retrieval Augmented Persona) engine with 50+ distinct personas
    grounded in live market signals for brutal, specific feedback.
    
    Args:
        feature: The feature or idea to test
        domain: Product domain for context (e.g., "EdTech", "Developer Tools")
    """
    feature = arguments.get("feature") or arguments.get("content")
    domain = arguments.get("domain") or arguments.get("target_audience", "General Software")
    
    if not feature:
        return "❌ Error: Please provide 'feature' to simulate."
        
    try:
        # Use the superior Simulator with RAP engine
        project_path = Path.cwd()
        simulator = Simulator(project_path=project_path)
        
        result = await simulator.simulate_feedback(feature=feature, domain=domain)
        
        # Log activity
        try:
            from side.tools.core import get_database
            db = get_database()
            project_id = SimplifiedDatabase.get_project_id(project_path)
            profile_data = db.get_profile(project_id)
            tier = profile_data.get('tier', 'free') if profile_data else 'free'
            
            db.log_activity(
                project_id=project_id,
                tool="simulate",
                action=f"RAP Simulation: {domain}",
                cost_tokens=2000,
                tier=tier,
                payload={"feature": feature[:100], "domain": domain}
            )
        except Exception as log_e:
            logger.warning(f"Failed to log simulation activity: {log_e}")
            
        # Trigger ledger update
        try:
            from side.tools.planning import _generate_ledger_file
            _generate_ledger_file(db)
        except Exception:
            pass

        return f"## 🎭 RAP Simulation Results\n\n**Feature:** {feature[:100]}...\n**Domain:** {domain}\n\n{result}"
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        return f"❌ Simulation failed: {str(e)}"


# Alias for backward compatibility
handle_simulate = handle_simulate_users
