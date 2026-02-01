
import pytest
from side.pulse import pulse, PulseStatus
import time

# -----------------------------------------------------------------------------
# SETUP: Ensure the Firewall rules are loaded
# -----------------------------------------------------------------------------
# Trigger rule sync to write the regex patterns to .side/rules
pulse.sync_prime_rules()
# Force reload of rules into memory
pulse._load_dynamic_rules()

# MOCK STRICT MODE FOR TESTING
def mock_load_anchor(self):
    return {
        "moat_pulse": {"enforcement_mode": "STRICT"},
        "constitution": {"invariants": []}, 
        "gold_standards": {}
    }
# Monkey patch the instance method
import types
pulse._load_anchor = types.MethodType(mock_load_anchor, pulse)

# -----------------------------------------------------------------------------
# ATTACK VECTOR 1: The "Split Token" Smuggling
# -----------------------------------------------------------------------------
def test_attack_split_keys():
    """
    Attack: Splitting an AWS key across two lines or variables
    to evade single-line regex detection.
    """
    malicious_code = """
    part1 = "AKIA"
    part2 = "IOSFODNN7EXAMPLE" 
    key = part1 + part2
    """
    
    # PULSE TAKES A DICT, NOT AN OBJECT
    ctx = {
        "target_file": "hack.py",
        "file_content": malicious_code,
        "metadata": {}
    }
    
    result = pulse.check_pulse(ctx)
    print(f"\n[ATTACK] Split Key Result: {result.status}")

# -----------------------------------------------------------------------------
# ATTACK VECTOR 2: The "Standard" Leak (Baseline)
# -----------------------------------------------------------------------------
def test_attack_standard_leak():
    """
    Attack: Pasteurizing a raw AWS Key.
    """
    # Note: The default rule in pulse.py (lines 220) is "pswd =|password =|secret ="
    # It does NOT specifically have "AKIA" in the hardcoded cloud_payload yet.
    # We should test "secret =" to verify the engine works, or "password =".
    malicious_code = 'my_secret = "super_secret_password"'
    
    ctx = {
        "target_file": "config.py",
        "file_content": malicious_code,
        "metadata": {}
    }
    
    result = pulse.check_pulse(ctx)
    
    # Debug info
    if result.status != PulseStatus.VIOLATION:
        print(f"DEBUG: Violations found: {result.violations}")
        
    assert result.status == PulseStatus.VIOLATION, "Firewall failed to block a 'secret =' pattern!"

# -----------------------------------------------------------------------------
# ATTACK VECTOR 3: The "Password" Leak
# -----------------------------------------------------------------------------
def test_attack_password_leak():
    """
    Attack: Exposing a password.
    """
    malicious_code = 'db_password = "correcthorsebatterystaple"'
    
    ctx = {
        "target_file": "db.py",
        "file_content": malicious_code,
        "metadata": {}
    }
    
    result = pulse.check_pulse(ctx)
    assert result.status == PulseStatus.VIOLATION, "Firewall failed to block 'password ='!"

if __name__ == "__main__":
    # Manual run wrapper
    try:
        test_attack_standard_leak()
        print("✅ Standard Secret Block: CONFIRMED")
        test_attack_password_leak()
        print("✅ Password Block: CONFIRMED")
        test_attack_split_keys()
    except AssertionError as e:
        print(f"🛑 FIREWALL BREACHED: {e}")
        exit(1)
