#!/usr/bin/env python3
"""
Test script for Groq-first MVP pricing model.
Validates simple single-model strategy with free tasks.
"""

from side.storage.modules.base import SovereignEngine
from side.llm.model_router import select_model, is_free_task, get_model_pricing

def test_groq_mvp_pricing():
    engine = SovereignEngine()
    accounting = engine.accounting
    project_id = engine.get_project_id()
    
    print("🚀 [TEST]: Groq MVP Pricing System")
    print("=" * 70)
    
    # Test 1: Free Tasks
    print("\n🎁 Test 1: Free Tasks (0 SU)")
    free_tasks = ["pulse_scan", "ast_extraction", "forensic_log"]
    for task in free_tasks:
        su = accounting.calculate_task_su(task_type=task)
        is_free = is_free_task(task)
        model = select_model(task)
        print(f"  {task}: {su} SU (Free: {is_free}, Model: {model}) {'✅' if su == 0 else '❌'}")
    
    # Test 2: Model Selection
    print("\n📊 Test 2: Model Selection (Same for All)")
    test_tasks = ["atomic_context", "semantic_boost", "general_context", "strategic_planning"]
    models = set()
    for task in test_tasks:
        model = select_model(task)
        models.add(model)
        print(f"  {task}: {model}")
    
    print(f"\n  Unique models used: {len(models)} (should be 1)")
    print(f"  All use same model: {'✅' if len(models) == 1 else '❌'}")
    
    # Test 3: Pricing
    print("\n📊 Test 3: Groq Pricing")
    pricing = get_model_pricing()
    print(f"  Model: {select_model('atomic_context')}")
    print(f"  Input: ${pricing['input']}/1M tokens")
    print(f"  Output: ${pricing['output']}/1M tokens")
    print(f"  Expected: $0.20/$0.30")
    
    # Test 4: SU Costs (Groq)
    print("\n📊 Test 4: SU Costs with Groq")
    
    tasks = [
        ("atomic_context", 1000, 1500),
        ("semantic_boost", 3500, 150),
        ("general_context", 2000, 4000)
    ]
    
    for task_type, tokens_in, tokens_out in tasks:
        su = accounting.calculate_task_su(
            task_type=task_type,
            llm_tokens_in=tokens_in,
            llm_tokens_out=tokens_out,
            operations=["ast_extraction"]
        )
        llm_cost = (tokens_in * 0.20 + tokens_out * 0.30) / 1_000_000
        print(f"  {task_type}: {su} SU (LLM cost: ${llm_cost:.4f})")
    
    # Test 5: Balance
    print("\n📊 Test 5: Default Balance")
    balance = accounting.get_balance(project_id)
    print(f"  Balance: {balance} SU")
    print(f"  Expected: 750 SU (Pro tier)")
    
    # Test 6: Deduction
    print("\n📊 Test 6: Free Task Deduction")
    initial = accounting.get_balance(project_id)
    success = accounting.deduct_task_su(
        project_id=project_id,
        task_type="pulse_scan",  # Free task
        operations=["pulse_scan"]
    )
    final = accounting.get_balance(project_id)
    print(f"  Initial: {initial} SU")
    print(f"  Deducted: {initial - final} SU")
    print(f"  Final: {final} SU")
    print(f"  Free task worked: {'✅' if initial == final else '❌'}")
    
    print("\n" + "=" * 70)
    print("✅ [TEST]: Groq MVP pricing tests completed!")
    print("\n💡 Migration Tip: Change CURRENT_PHASE in model_router.py to 'gemini' when ready")

if __name__ == "__main__":
    test_groq_mvp_pricing()
