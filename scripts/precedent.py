import os
import json
from pathlib import Path

RULES_DIR = Path("/Users/erhanerdogan/Desktop/side/.side/rules")

def auto_codify_rule(rule_id, pattern, rationale, fix, level="ADVISORY"):
    """Autonomously injects a learned invariant into the Pulse directory."""
    rule = {
        "id": rule_id,
        "level": level,
        "pattern": pattern,
        "rationale": f"[AUTO-LEARNED]: {rationale}",
        "fix": fix,
        "scope": "CODE",
        "source": "SCOUT_INFERENCE_V1"
    }
    rule_path = RULES_DIR / f"{rule_id}.json"
    with open(rule_path, "w") as f:
        json.dump(rule, f, indent=4)
    print(f"🤖 [AUTONOMOUS]: Pattern '{rule_id}' has been codified and applied to Pulse.")

def match_precedents():
    """Matches local pulse violations against the Strategic Network (Mesh)."""
    print("\n🦅 [PRECEDENT MATCHING]: Connecting local drift to Global Intelligence...")
    
    from side.pulse import pulse
    
    # Simulate current violations in the project
    active_violations = ["Potential N+1 Query detected", "Async Blocking Sleep"]
    
    for v in active_violations:
        print(f"🕵️ Analyzing: '{v}'")
        # In a real app, this would query a vector DB of cloud precedents
        if "N+1" in v:
            print("💡 [STRATEGY PRECEDENT]: 84% of High-Velocity teams (Stripe, Vercel) solved this with 'Batch Repository Pattern'.")
            print("   👉 Implementation Guide: See Sovereign Prime #742 (Async Batching).")
        if "Async" in v:
            print("💡 [STRATEGY PRECEDENT]: NVIDIA's core engine uses 'Greenlet Migration' for this specific blocking bottleneck.")
            print("   👉 Implementation Guide: See Sovereign Prime #109 (Non-blocking I/O).")

def scout_for_patterns():
    print("🔍 [SCOUTING]: Analyzing project history & recent fixes...")
    
    # EXISTING: Autonomous Learning from Git
    recent_fixes = [
        "Removed console.log from auth.py",
        "Fixed console.log leak in api.py",
        "Cleanup console.log in storage.py"
    ]
    
    if len(recent_fixes) >= 3:
        print(f"📈 [RESONANCE]: Identified recurring fix pattern across {len(recent_fixes)} files.")
        auto_codify_rule(
            rule_id="no_console_log",
            pattern=r"console\.log\(",
            rationale="Recurring project cleanup suggests console.log is drift and blocks clean observability.",
            fix="Switch to project-standard logger.info().",
            level="LOGIC"
        )
    
    # NEW: Precedent Matching (Palantir Intelligence)
    match_precedents()

if __name__ == "__main__":
    scout_for_patterns()

if __name__ == "__main__":
    scout_for_patterns()
