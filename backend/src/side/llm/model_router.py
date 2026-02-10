"""
Model Router - Pragmatic Strategy

Phase 1 (Months 1-2): Groq Llama 70B for everything (MVP)
Phase 2 (Month 3+): Migrate to Gemini 3 Flash when validated

Philosophy: Same intelligence for all users, charge based on usage.
"""

from typing import Literal

# Phase selection (switch to "gemini" when ready to migrate)
CURRENT_PHASE = "groq"  # Options: "groq" or "gemini"

# Model configuration per phase
MODELS = {
    "groq": {
        "default": "llama-3.1-70b-versatile",
        "pricing": {"input": 0.20, "output": 0.30}  # per 1M tokens
    },
    "gemini": {
        "default": "gemini-3-flash-thinking",
        "pricing": {"input": 0.50, "output": 3.00}  # per 1M tokens
    }
}

# Free tasks (habit-forming, no SU charge)
FREE_TASKS = {
    "pulse_scan",
    "ast_extraction",
    "audit_log",
    "file_watcher",
    "git_hook_detection",
    "intent_correlation"
}


def select_model(task_type: str) -> str | None:
    """
    Select the appropriate model for a given task.
    
    MVP Strategy (Groq):
    - Single model for all intelligent tasks
    - Free tasks return None (no LLM)
    
    Production Strategy (Gemini):
    - Single model for all intelligent tasks
    - Free tasks return None (no LLM)
    
    Args:
        task_type: Type of task (e.g., "semantic_boost", "general_context")
        
    Returns:
        Model name or None if free task
    """
    # Check if task is free (no LLM)
    if task_type in FREE_TASKS:
        return None
    
    # Return current phase model
    return MODELS[CURRENT_PHASE]["default"]


def get_model_pricing(model_name: str | None = None) -> dict:
    """
    Get pricing for the current or specified model.
    
    Returns:
        {"input": float, "output": float} per 1M tokens
    """
    if model_name is None:
        return MODELS[CURRENT_PHASE]["pricing"]
    
    # Check all phases for the model
    for phase, config in MODELS.items():
        if config["default"] == model_name:
            return config["pricing"]
    
    # Default to current phase pricing
    return MODELS[CURRENT_PHASE]["pricing"]


def is_free_task(task_type: str) -> bool:
    """
    Check if a task is free (no SU charge).
    
    Free tasks are habit-forming, algorithmic-only operations
    that encourage daily engagement.
    """
    return task_type in FREE_TASKS
