"""
Welcome tool handler - Day 1 Magic.

Sets up Side and creates the Strategic Monolith for a new project.
"""
import os
import logging
from typing import Any
from pathlib import Path

from side.onboarding import run_onboarding, is_side_initialized, detect_project_name, detect_stack
# from side.audit.memory import AuditMemory, AuditSnapshot
from side.tools.planning import _generate_monolith_file
from side.tools.core import get_database
from datetime import datetime

logger = logging.getLogger(__name__)


async def handle_welcome(arguments: dict[str, Any]) -> str:
    """
    Day 1 magic - set up Side and create the Strategic Monolith.
    
    - Detects project name and stack
    - Creates .side/MONOLITH.md (the Sovereign Dashboard)
    - Runs baseline audit
    - Stores initial snapshot
    """
    project_path = arguments.get("project_path", os.getcwd())
    
    # Check if already initialized
    if is_side_initialized(project_path):
        project_name = detect_project_name(Path(project_path))
        stack = detect_stack(Path(project_path))
        
        # Ensure Monolith exists
        db = get_database()
        monolith_path = _generate_monolith_file(db)
        
        # Get latest health
        # memory = AuditMemory(project_path)
        # progress = memory.get_progress()
        progress = {"has_history": False} # Placeholder
        
        if progress.get("has_history"):
            return f"""
## ✅ Side is already set up for {project_name}

**Stack**: {', '.join(stack)}
**Latest Score**: {progress['last_score']}%
**Change**: {progress['message']}

Your **Monolith** is at `.side/MONOLITH.md`

**What would you like to do?**
- Say "Side, audit my code" to check health
- Say "Side, what's my priority?" for strategic focus
- Say "Side, log a goal" to add directives
"""
        else:
            return f"""
## ✅ Side is set up for {project_name}

**Stack**: {', '.join(stack)}

Your **Monolith** is at `.side/MONOLITH.md`

Say "Side, audit my code" to get your first health score!
"""
    
    # Run onboarding
    result = run_onboarding(project_path)
    
    if not result["success"]:
        return "❌ Failed to set up Side. Please try again."
    
    # Create initial snapshot
    # memory = AuditMemory(project_path)
    # snapshot = AuditSnapshot(
        date=datetime.now().strftime("%Y-%m-%d"),
        score=0,  # Will be updated on first audit
        total_checks=0,
        passed_checks=0,
    #     findings=[],
    # )
    # memory.save_snapshot(snapshot)
    
    # Generate the Monolith
    db = get_database()
    monolith_path = _generate_monolith_file(db)
    
    return f"""
## 👋 Welcome to Side!

I've set up your project and created your **Strategic Monolith**:

**📁 Project**: {result['project_name']}
**🔧 Stack**: {', '.join(result['stack'])}
**⬛ Monolith**: `.side/MONOLITH.md`

### The Monolith Paradigm

Your Monolith is a **machine-sovereign dashboard**. It reflects your project's:
- Strategic IQ and Grade
- Active Directives (goals, milestones, tasks)
- Security Matrix
- Transparency Log

> **You cannot edit the Monolith by hand.** To update it, talk to me:
> - "Side, log a goal: Launch by February"
> - "Side, I finished the auth feature"
> - "Side, audit my code"

---
*Your Agency is ready. What's your first directive?*
"""
