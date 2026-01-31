"""
Compliance Drill: The Sovereign Shield Stress Test.
Verifies Regex + Entropy Redaction.
"""

import logging
from side.utils.shield import shield

# Setup Logging
logging.basicConfig(level=logging.ERROR)

def run_compliance_drill():
    print("🛡️ [COMPLIANCE DRILL]: Testing Redaction Engines...")
    
    # 1. REGEX TEST (Known Pattern)
    print("\n📝 [TEST 1]: Regex Redaction (OpenAI Key)")
    input_text = "My key is sk-1234567890abcdef1234567890abcdef. Don't share."
    output = shield.scrub(input_text)
    print(f"   Input:  {input_text}")
    print(f"   Output: {output}")
    if "<OPENAI_KEY_REDACTED>" in output and "sk-" not in output:
        print("✅ PASS: Regex caught it.")
    else:
        print("❌ FAIL: Regex missed it.")
        exit(1)

    # 2. ENTROPY TEST (Unknown Secret)
    print("\n🎲 [TEST 2]: Entropy Redaction (Random High-Value String)")
    # A fake high-entropy secret that looks like a JWT or custom token
    secret = "a8f9e2d1c3b4a596874123654789654123654123" 
    input_text = f"Connection string is {secret} for prod db."
    output = shield.scrub(input_text)
    print(f"   Input:  {input_text}")
    print(f"   Output: {output}")
    
    if "<HIGH_ENTROPY_SECRET_REDACTED>" in output and secret not in output:
        print("✅ PASS: Entropy Engine caught the unknown secret.")
    else:
        print(f"❌ FAIL: Entropy Engine missed it. (Entropy: {shield._calculate_entropy(secret):.2f})")
        exit(1)
        
    print("\n🏆 COMPLIANCE DRILL COMPLETE.")

if __name__ == "__main__":
    run_compliance_drill()
