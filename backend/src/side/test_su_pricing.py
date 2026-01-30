#!/usr/bin/env python3
"""
Test script for dynamic SU pricing system.
Validates task-based SU calculation with various scenarios.
"""

from side.storage.modules.base import SovereignEngine

def test_dynamic_su_pricing():
    engine = SovereignEngine()
    accounting = engine.accounting
    project_id = engine.get_project_id()
    
    print("🏦 [TEST]: Dynamic SU Pricing System")
    print("=" * 60)
    
    # Test 1: Atomic Context (no LLM, pure algorithmic)
    print("\n📊 Test 1: Atomic Context")
    su1 = accounting.calculate_task_su(
        task_type="atomic_context",
        operations=["fractal_search", "ast_extraction", "intent_correlation"]
    )
    print(f"  Expected: ~6-7 SU (2.0 + 1.5 + 3.0)")
    print(f"  Actual: {su1} SU")
    
    # Test 2: Semantic Boost with LLM
    print("\n📊 Test 2: Semantic Boost (Groq Llama)")
    su2 = accounting.calculate_task_su(
        task_type="semantic_boost",
        llm_tokens_in=3000,
        llm_tokens_out=600,
        llm_model="groq-llama-70b",
        operations=["ast_extraction", "intent_correlation"],
        value_delivered={"objective_advanced": True}
    )
    print(f"  Expected: ~8-10 SU (LLM ~1 + Algo 4.5 + Value 2)")
    print(f"  Actual: {su2} SU")
    
    # Test 3: General Context with Claude (expensive)
    print("\n📊 Test 3: General Context (Claude 3.5)")
    su3 = accounting.calculate_task_su(
        task_type="general_context",
        llm_tokens_in=5000,
        llm_tokens_out=1200,
        llm_model="claude-3.5-sonnet",
        operations=["context_synthesis", "fractal_search"]
    )
    print(f"  Expected: ~35-40 SU (LLM ~33 + Algo 4.5)")
    print(f"  Actual: {su3} SU")
    
    # Test 4: Pulse Scan (zero LLM, minimal algo)
    print("\n📊 Test 4: Pulse Scan (Pre-commit)")
    su4 = accounting.calculate_task_su(
        task_type="pulse_scan",
        operations=["pulse_scan"]
    )
    print(f"  Expected: 1 SU (minimum)")
    print(f"  Actual: {su4} SU")
    
    # Test 5: Averted Disaster (high value)
    print("\n📊 Test 5: Averted Disaster ($125k)")
    su5 = accounting.calculate_task_su(
        task_type="shield_fix",
        operations=["shield_fix", "forensic_log"],
        value_delivered={"disaster_averted_usd": 125000}
    )
    print(f"  Expected: ~22-25 SU (Algo 1.8 + Value 20 capped)")
    print(f"  Actual: {su5} SU")
    
    # Test 6: Deduct using new API
    print("\n📊 Test 6: Deduct Task SU")
    initial_balance = accounting.get_balance(project_id)
    print(f"  Initial Balance: {initial_balance} SU")
    
    success = accounting.deduct_task_su(
        project_id=project_id,
        task_type="atomic_context",
        operations=["fractal_search"],
        value_delivered={"time_saved_hours": 0.5}
    )
    
    final_balance = accounting.get_balance(project_id)
    print(f"  Deduction Success: {success}")
    print(f"  Final Balance: {final_balance} SU")
    print(f"  Cost: {initial_balance - final_balance} SU")
    
    print("\n" + "=" * 60)
    print("✅ [TEST]: All tests completed!")

if __name__ == "__main__":
    test_dynamic_su_pricing()
