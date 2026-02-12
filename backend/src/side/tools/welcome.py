"""
Welcome tool handler - Day 1 Magic.

Sets up Side and creates the Strategic Hub for a new project.
"""
import os
import logging
from typing import Any
from pathlib import Path

from side.onboarding import run_onboarding, is_side_initialized, detect_project_name, detect_stack
from side.tools.core import get_engine
from datetime import datetime

logger = logging.getLogger(__name__)


async def handle_welcome(arguments: dict[str, Any]) -> str:
    """
    Day 1 magic - set up Side and create the Strategic Hub.
    
    - Detects project name and stack
    - Initializes the System Context state
    - Runs baseline audit
    - Stores initial snapshot
    """
    project_path = arguments.get("project_path", os.getcwd())
    
    # Check if already initialized
    if is_side_initialized(project_path):
        project_name = detect_project_name(Path(project_path))
        stack = detect_stack(Path(project_path))
        
        # Database is source of truth
        db = get_engine()
        
        # Get latest health
        # memory = AuditMemory(project_path)
        # progress = memory.get_progress()
        progress = {"has_history": False} # Initial state
        return progress
        
        if progress.get("has_history"):
            return f"""
## ✅ Side is already set up for {project_name}

**Stack**: {', '.join(stack)}
**Latest Score**: {progress['last_score']}%
**Change**: {progress['message']}

**Context Source**: System Context Database (MCP)

**What would you like to do?**
- Say "Side, audit my code" to check health
- Say "Side, what's my priority?" for strategic focus
- Say "Side, log a goal" to add directives
"""
        else:
            return f"""
## ✅ Side is set up for {project_name}

**Stack**: {', '.join(stack)}

**Context Source**: System Context Database (MCP)

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
    
    # Database serves as the Source of Truth
    db = get_engine()
    
    return f"""
## 👋 Welcome to Sidelith.

I've initialized the technical context for this project:

**📁 Project**: {result['project_name']}
**🔧 Stack**: {', '.join(result['stack'])}
**⬛ Context**: System Context Database (Ready)

### How it works:

Sidelith maintains a persistent state in your System Database. It tracks your:
- Codebase health and logic flow
- Active goals and constraints
- Decision history (to prevent regressions)

> **Access context via LLM or MCP tools.** Update it via command:
> - `lith log goal: Launch by February`
> - `lith audit`
> - `lith status`

---
*Your Agency is ready. What's your first directive?*
"""
