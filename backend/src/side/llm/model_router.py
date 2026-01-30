"""
Claude 4.5 Model Router - Premium Tiered Intelligence

Routes tasks to the optimal Claude 4.5 model based on complexity:
- Fast: Haiku 4.5 ($1/$5) - Atomic context, quick suggestions
- Balanced: Sonnet 4.5 ($3/$15) - Strategic analysis, general context
- Smart: Opus 4.5 ($5/$25) - Complex reasoning, mesh wisdom
"""

from typing import Literal

ModelTier = Literal["fast", "balanced", "smart"]

# Claude 4.5 Model Registry (2026)
CLAUDE_MODELS = {
    "fast": "claude-haiku-4.5",      # $1/$5 per 1M tokens
    "balanced": "claude-sonnet-4.5",  # $3/$15 per 1M tokens
    "smart": "claude-opus-4.5"        # $5/$25 per 1M tokens
}

# Pricing (per 1M tokens)
CLAUDE_PRICING = {
    "claude-haiku-4.5": {"input": 1.00, "output": 5.00},
    "claude-sonnet-4.5": {"input": 3.00, "output": 15.00},
    "claude-opus-4.5": {"input": 5.00, "output": 25.00}
}

# Task-to-Tier Mapping
TASK_ROUTING = {
    # Fast Tier (40% of intelligent tasks)
    "fast": [
        "atomic_context",
        "proactive_suggestion",
        "context_signature",
        "quick_analysis"
    ],
    
    # Balanced Tier (50% of intelligent tasks)
    "balanced": [
        "semantic_boost",
        "general_context",
        "forensic_analysis",
        "roi_simulation",
        "intent_analysis",
        "code_review"
    ],
    
    # Smart Tier (10% of intelligent tasks)
    "smart": [
        "strategic_planning",
        "mesh_wisdom",
        "architectural_audit",
        "complex_reasoning",
        "cross_project_analysis"
    ]
}

# Free Tasks (0 SU) - Habit-forming, no LLM
FREE_TASKS = {
    "pulse_scan",           # Pre-commit secret detection
    "ast_extraction",       # Symbol extraction
    "forensic_log",         # Activity logging
    "file_watcher",         # File open events
    "git_hook_detection",   # Commit capture
    "intent_correlation"    # Symbol → objective matching (SQL only)
}


def select_claude_model(task_type: str, force_tier: ModelTier | None = None) -> str:
    """
    Select the optimal Claude 4.5 model for a given task.
    
    Args:
        task_type: Type of task (e.g., "semantic_boost", "general_context")
        force_tier: Optional override to force a specific tier
        
    Returns:
        Claude model name (e.g., "claude-sonnet-4.5")
    """
    
    # Check if task is free (no LLM)
    if task_type in FREE_TASKS:
        return None  # No LLM needed
    
    # Force specific tier if requested
    if force_tier:
        return CLAUDE_MODELS[force_tier]
    
    # Auto-route based on task type
    for tier, tasks in TASK_ROUTING.items():
        if task_type in tasks:
            return CLAUDE_MODELS[tier]
    
    # Default to balanced tier if task type unknown
    return CLAUDE_MODELS["balanced"]


def get_model_pricing(model_name: str) -> dict:
    """
    Get pricing for a specific Claude model.
    
    Returns:
        {"input": float, "output": float} per 1M tokens
    """
    return CLAUDE_PRICING.get(model_name, CLAUDE_PRICING["claude-sonnet-4.5"])


def is_free_task(task_type: str) -> bool:
    """
    Check if a task is free (no SU charge).
    
    Free tasks are habit-forming, algorithmic-only operations
    that encourage daily engagement.
    """
    return task_type in FREE_TASKS
