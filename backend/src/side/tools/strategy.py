from typing import Any
from pathlib import Path
from side.llm.client import LLMClient
from side.intel.auto_intelligence import ContextService
from side.storage.modules.base import ContextEngine

from side.utils.paths import get_repo_root

from side.prompts import Personas, LLMConfigs

# Centralized root resolution
PROJECT_ROOT = get_repo_root()

async def handle_decide(args: dict[str, Any]) -> str:
    """Handle architectural_decision tool."""
    question = args.get("question")
    base_context = args.get("context", "")
    
    # [ECONOMY]: Charge for Strategic Decision (50 SUs)
    from side.tools.core import get_engine, get_ai_memory
    db = get_engine()
    project_id = db.get_project_id()
    
    if not db.identity.charge_action(project_id, "STRATEGIC_ALIGN"):
        return "🚫 [INSUFFICIENT FUNDS]: Strategic Alignment requires 50 SUs. Run 'side login' or upgrade."
    
    # Auto-Inject Strategic Context
    intel = get_ai_memory()
    # We pass the question as topic and the base_context as active_file if it looks like a path
    active_file = base_context if "/" in base_context or "." in base_context else None
    project_context = intel.gather_context(topic=question, active_file=active_file)
    
    llm = LLMClient()
    prompt = f"🎯 Strategic Question: {question}\n🛠️ Operational Context: {base_context}\n\nProvide a high-density architectural decision anchored in technical reality."
    
    system_prompt = intel.enrich_system_prompt(
        Personas.STRATEGIC_ARCHITECT, 
        project_context
    )
    
    config = LLMConfigs.get_config("decision_making")
    
    try:
        response = await llm.complete_async(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=system_prompt,
            **config
        )
        return response
    except Exception as e:
        return f"🚫 Architectural decision failed due to system outage: {e}"

async def handle_strategy(args: dict[str, Any]) -> str:
    """Handle strategic_review tool."""
    base_context = args.get("context", "")
    
    from side.tools.core import get_engine, get_ai_memory
    db = get_engine()
    project_id = db.get_project_id()
    
    if not db.identity.charge_action(project_id, "STRATEGIC_ALIGN"):
        return "🚫 [INSUFFICIENT FUNDS]: Strategic Alignment requires 50 SUs. Run 'side login' or upgrade."
    
    intel = get_ai_memory()
    active_file = base_context if "/" in base_context or "." in base_context else None
    project_context = intel.gather_context(topic="strategic review", active_file=active_file)
    
    llm = LLMClient()
    prompt = f"🔍 Review Context: {base_context}\n\nConduct a high-density Strategic Review of the current project state. Identify potential project-drift or architectural bottlenecks."
    
    system_prompt = intel.enrich_system_prompt(
        Personas.STRATEGIC_REVIEWER, 
        project_context
    )
    
    config = LLMConfigs.get_config("strategic_review")
    
    try:
        response = await llm.complete_async(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=system_prompt,
            **config
        )
        return response
    except Exception as e:
        return f"🚫 Strategic review unavailable: {e}"
