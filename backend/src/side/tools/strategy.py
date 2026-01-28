from typing import Any
from pathlib import Path
from side.llm.client import LLMClient
from side.intel.auto_intelligence import AutoIntelligence

# Helper to find project root (Assume we are running inside backend/src)
# In real prod, this is passed via args or env
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent

async def handle_decide(args: dict[str, Any]) -> str:
    """Handle architectural_decision tool."""
    question = args.get("question")
    base_context = args.get("context", "")
    
    # Auto-Inject Sovereign Context
    intel = AutoIntelligence(PROJECT_ROOT)
    sovereign_context = intel.gather_context(topic=question)
    
    llm = LLMClient()
    prompt = f"Question: {question}\nUser Context: {base_context}\n\nProvide a strategic architectural decision."
    
    system_prompt = intel.enrich_system_prompt(
        "You are a Principal Software Architect.", 
        sovereign_context
    )
    
    try:
        return await llm.complete_async(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=system_prompt,
            temperature=0.3
        )
    except Exception as e:
        return f"🚫 Architectural decision failed due to neural outage: {e}"

async def handle_strategy(args: dict[str, Any]) -> str:
    """Handle strategic_review tool."""
    base_context = args.get("context", "")
    
    intel = AutoIntelligence(PROJECT_ROOT)
    sovereign_context = intel.gather_context(topic=base_context)
    
    llm = LLMClient()
    prompt = f"User Context: {base_context}\n\nConduct a strategic review of the current direction."
    
    system_prompt = intel.enrich_system_prompt(
        "You are a Strategic Advisor.", 
        sovereign_context
    )
    
    try:
        return await llm.complete_async(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=system_prompt,
            temperature=0.3
        )
    except Exception as e:
        return f"🚫 Strategic review unavailable: {e}"
