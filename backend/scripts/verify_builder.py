import os
import sys
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from side.audit.experts.engineer import SeniorEngineer
from side.audit.experts.base import ExpertContext
from side.audit.core import AuditStatus
from side.server import load_env_file

# Setup
logging.basicConfig(level=logging.ERROR)
load_env_file()

def verify_builder():
    print("🚀 Initializing Builder (Senior Engineer)...")
    expert = SeniorEngineer()
    
    # 1. Test Case: Magic Numbers and Poor Logic
    bad_code = """
def calculate_discount(price, user_type):
    if user_type == 1: # What is 1?
        return price * 0.9
    elif user_type == 2: # ???
        return price * 0.85
    elif user_type == 3:
        if price > 100:
            if price < 500:
                return price * 0.8
            else:
                if price > 1000:
                    return price * 0.7
    return price
"""
    
    print("\n👷 Analyzing 'Magic Numbers' Snippet...")
    ctx_bad = ExpertContext(
        check_id="ENG-001",
        file_path="src/billing/discount.py",
        content_snippet=bad_code,
        language="python"
    )
    
    result_bad = expert.review(ctx_bad)
    
    print(f"\n[RESULT] Status: {result_bad.status}")
    print(f"[RESULT] Notes: {result_bad.notes}")
    
    if result_bad.status in [AuditStatus.FAIL, AuditStatus.WARNING]:
        print("✅ SUCCESS: Builder flagged the magic numbers and nested logic.")
    else:
        print(f"❌ FAILURE: Builder missed the issues. Status: {result_bad.status}")

    # 2. Test Case: Clean Code with Enums and Clear Logic
    clean_code = """
from enum import Enum
from dataclasses import dataclass

class UserTier(Enum):
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

DISCOUNT_RATES = {
    UserTier.STANDARD: 0.0,
    UserTier.PREMIUM: 0.10,
    UserTier.ENTERPRISE: 0.20,
}

def calculate_discount(price: float, tier: UserTier) -> float:
    \"\"\"Calculate discounted price based on user tier.\"\"\"
    discount = DISCOUNT_RATES.get(tier, 0.0)
    return price * (1 - discount)
"""
    
    print("\n👷 Analyzing 'Clean Code' Snippet...")
    ctx_good = ExpertContext(
        check_id="ENG-002",
        file_path="src/billing/discount.py",
        content_snippet=clean_code,
        language="python"
    )
    
    result_good = expert.review(ctx_good)
    
    print(f"\n[RESULT] Status: {result_good.status}")
    print(f"[RESULT] Notes: {result_good.notes}")
    
    if result_good.status == AuditStatus.PASS:
        print("✅ SUCCESS: Builder approved the clean design.")
    else:
        print(f"❌ FAILURE: Builder complained about clean code: {result_good.status}")

if __name__ == "__main__":
    verify_builder()
