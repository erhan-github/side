#!/usr/bin/env python3
"""
Test script for premium Claude 4.5 pricing model.
Validates tiered intelligence, free tasks, and realistic SU costs.
"""

from side.storage.modules.base import SovereignEngine
from side.llm.model_router import select_claude_model, is_free_task, get_model_pricing

def test_premium_pricing():
    engine = SovereignEngine()
    accounting = engine.accounting
    project_id = engine.get_project_id()
    
    print("💎 [TEST]: Premium Claude 4.5 Pricing System")
    print("=" * 70)
    
    # Test 1: Free Tasks (Habit-Forming)
    print("\n🎁 Test 1: Free Tasks (0 SU)")
    free_tasks = ["pulse_scan", "ast_extraction", "forensic_log", "file_watcher"]
    for task in free_tasks:
        su = accounting.calculate_task_su(task_type=task)
        is_free = is_free_task(task)
        print(f"  {task}: {su} SU (Free: {is_free}) ✅" if su == 0 else f"  {task}: {su} SU ❌")
    
    # Test 2: Atomic Context (Haiku 4.5)
    print("\n📊 Test 2: Atomic Context (Haiku 4.5)")
    model = select_claude_model("atomic_context")
    pricing = get_model_pricing(model)
    su = accounting.calculate_task_su(
        task_type="atomic_context",
        llm_tokens_in=1000,
        llm_tokens_out=1500,
        llm_model=model,
        operations=["fractal_search", "ast_extraction"]
    )
    print(f"  Model: {model}")
    print(f"  Pricing: ${pricing['input']}/${pricing['output']} per 1M")
    print(f"  Expected: ~11 SU")
    print(f"  Actual: {su} SU")
    
    # Test 3: Semantic Boost (Sonnet 4.5)
    print("\n📊 Test 3: Semantic Boost (Sonnet 4.5)")
    model = select_claude_model("semantic_boost")
    pricing = get_model_pricing(model)
    su = accounting.calculate_task_su(
        task_type="semantic_boost",
        llm_tokens_in=3500,
        llm_tokens_out=150,
        llm_model=model,
        operations=["ast_extraction", "intent_correlation"],
        value_delivered={"objective_advanced": True}
    )
    print(f"  Model: {model}")
    print(f"  Pricing: ${pricing['input']}/${pricing['output']} per 1M")
    print(f"  Expected: ~17 SU")
    print(f"  Actual: {su} SU")
    
    # Test 4: General Context (Sonnet 4.5)
    print("\n📊 Test 4: General Context (Sonnet 4.5)")
    model = select_claude_model("general_context")
    su = accounting.calculate_task_su(
        task_type="general_context",
        llm_tokens_in=2000,
        llm_tokens_out=4000,
        llm_model=model,
        operations=["context_synthesis", "fractal_search"]
    )
    print(f"  Model: {model}")
    print(f"  Expected: ~71 SU")
    print(f"  Actual: {su} SU")
    
    # Test 5: Strategic Planning (Opus 4.5)
    print("\n📊 Test 5: Strategic Planning (Opus 4.5)")
    model = select_claude_model("strategic_planning")
    pricing = get_model_pricing(model)
    su = accounting.calculate_task_su(
        task_type="strategic_planning",
        llm_tokens_in=3000,
        llm_tokens_out=1200,
        llm_model=model,
        operations=["strategic_analysis", "mesh_wisdom"]
    )
    print(f"  Model: {model}")
    print(f"  Pricing: ${pricing['input']}/${pricing['output']} per 1M")
    print(f"  Expected: ~50 SU")
    print(f"  Actual: {su} SU")
    
    # Test 6: Model Routing
    print("\n📊 Test 6: Tiered Model Routing")
    test_tasks = [
        ("atomic_context", "fast"),
        ("semantic_boost", "balanced"),
        ("mesh_wisdom", "smart"),
        ("proactive_suggestion", "fast"),
        ("forensic_analysis", "balanced")
    ]
    for task, expected_tier in test_tasks:
        model = select_claude_model(task)
        print(f"  {task}: {model} (Expected tier: {expected_tier})")
    
    # Test 7: Balance Check
    print("\n📊 Test 7: Default Balance")
    balance = accounting.get_balance(project_id)
    print(f"  Initial Balance: {balance} SU")
    print(f"  Expected: 750 SU (Pro tier)")
    print(f"  Match: {'✅' if balance == 750 else '❌'}")
    
    print("\n" + "=" * 70)
    print("✅ [TEST]: All premium pricing tests completed!")

if __name__ == "__main__":
    test_premium_pricing()
