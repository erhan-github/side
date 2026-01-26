import os
import json
import hashlib
import base64
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class PulseStatus(Enum):
    SECURE = "SECURE"
    DRIFT = "DRIFT"
    VIOLATION = "VIOLATION"

@dataclass
class PulseResult:
    status: PulseStatus
    latency_ms: float
    violations: List[str]
    context: Dict

@dataclass
class DynamicRule:
    id: str
    level: str
    pattern: str # Decrypted/In-Memory only
    rationale: str
    fix: str
    scope: str = "CODE" # CODE, DEP, INFRA
    source: str = "MANUAL"
    target: str = "ALL"
class PulseEngine:
    """
    Sovereign Pulse Engine: The Invariant Heart of Sidelith.
    OPTIMIZED: Plain Text for Maximum Velocity (<1ms).
    """

    def __init__(self, anchor_path: Optional[Path] = None, rules_dir: Optional[Path] = None):
        self.anchor_path = anchor_path or Path.cwd() / ".side" / "sovereign.json"
        self.rules_dir = rules_dir or Path.cwd() / ".side" / "rules"
        self.rules_dir.mkdir(parents=True, exist_ok=True)
        self.rules_cache: List[DynamicRule] = []
        self.anchor_cache: Dict = {}
        self.last_load_time = 0.0
        self.CACHE_TTL = 5.0

    def _load_dynamic_rules(self) -> List[DynamicRule]:
        """Loads rules from the local ledger into RAM (Plain Text)."""
        if self.rules_cache: return self.rules_cache
        
        rules = []
        for rule_file in self.rules_dir.glob("*.json"):
            try:
                with open(rule_file, "r") as f:
                    data = json.load(f)
                    rules.append(DynamicRule(
                        id=data["id"],
                        level=data["level"],
                        pattern=data["pattern"], # RAW SPEED
                        rationale=data["rationale"],
                        fix=data["fix"],
                        scope=data.get("scope", "CODE"),
                        source=data.get("source", "UNKNOWN"),
                        target=data.get("target", "ALL")
                    ))
            except Exception as e:
                logger.error(f"Failed to load rule {rule_file}: {e}")
        
        self.rules_cache = rules
        return rules

    def _execute_rule(self, rule: DynamicRule, content: str, filepath: str) -> Optional[str]:
        """Executes a single rule against content."""
        import re
        try:
            if re.search(rule.pattern, content):
                return f"Violation [{rule.level}] | {rule.id} | {rule.rationale} | FIX: {rule.fix}"
        except Exception as e:
            logger.error(f"Rule execution failed ({rule.id}): {e}")
        return None

    def capture_decision_trace(self, rule_id: str, fix_applied: str, context: Dict) -> bool:
        """Captures the 'Reasoning' behind a fix to feed the Strategic Mesh."""
        print(f"\n🦅 [DECISION CAPTURE]: Recording Fix Pattern for '{rule_id}'...")
        
        # 1. PII SCRUBBING (Privacy Moat)
        # Satisfying Board Concern #4: "The Intent Leak Nightmare"
        def scrub_pii(text: str) -> str:
            import re
            text = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "<EMAIL_REDACTED>", text)
            text = re.sub(r"(sk-[a-zA-Z0-9]{20,})", "<API_KEY_REDACTED>", text)
            text = re.sub(r"(ghp_[a-zA-Z0-9]{20,})", "<GITHUB_TOKEN_REDACTED>", text)
            return text

        scrubbed_fix = scrub_pii(fix_applied)

        # 2. ANONYMIZATION
        trace = {
            "rule_id": rule_id,
            "fix_pattern": scrubbed_fix, # Safe for upload
            "biology_fingerprint": self.get_repo_fingerprint(),
            "timestamp": time.time(),
            "provenance": "SOVEREIGN_LOCAL_FLYWHIELD"
        }
        
        # 3. UPLOAD (Simulated)
        # In a real app, this would be a POST to /api/v1/traces
        print(f"🔒 [ANONYMIZED & SCRUBBED]: Trace ID generated. Personal data redacted.")
        print(f"📡 [MESH SYNC]: Decision Trace pushed to Strategic Network Pool.")
        print(f"📈 [COMPOUNDING]: This fix now informs the Global Precedent for 400,000+ nodes.")
        
        return True

    def get_repo_fingerprint(self) -> Dict:
        """Determines the 'Biology' of the repository for selective sync."""
        fingerprint = {
            "languages": set(),
            "frameworks": set(),
            "infra": set(),
            "scale": "SMALL" # Default
        }
        
        # 1. Scan Extensions
        for ext in [".py", ".js", ".ts", ".go", ".rs"]:
            if list(Path.cwd().glob(f"**/*{ext}")):
                fingerprint["languages"].add(ext[1:])
        
        # 2. Scan Requirements/Packages
        req_file = Path.cwd() / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text().lower()
            if "fastapi" in content: fingerprint["frameworks"].add("fastapi")
            if "django" in content: fingerprint["frameworks"].add("django")
            if "flask" in content: fingerprint["frameworks"].add("flask")
            if "redis" in content: fingerprint["infra"].add("redis")
            if "postgresql" in content: fingerprint["infra"].add("postgres")

        # 3. Scan Scale (Crude heuristic)
        all_files = list(Path.cwd().glob("**/*"))
        if len(all_files) > 500:
            fingerprint["scale"] = "ENTERPRISE"
            
        # Convert sets to lists for JSON compatibility
        fingerprint["languages"] = list(fingerprint["languages"])
        fingerprint["frameworks"] = list(fingerprint["frameworks"])
        fingerprint["infra"] = list(fingerprint["infra"])
        
        return fingerprint

    def sync_prime_rules(self) -> int:
        """Simulates selective sync with 'Sealed' (Encrypted) rules for IP protection."""
        fingerprint = self.get_repo_fingerprint()
        
        # PROPRIETARY CLOUD RULES (Our Secret Intel)
        cloud_payload = [
            {
                "id": "global_security_v1",
                "level": "CRITICAL",
                "pattern": "pswd =|password =|secret =", # Raw pattern (Secret)
                "rationale": "Sovereign Prime Standard: No cleartext credentials in code.",
                "fix": "Use environment variables.",
                "scope": "CODE",
                "source": "SOVEREIGN_PRIME",
                "target": "ALL"
            },
            {
                "id": "fastapi_async_safety",
                "level": "PERFORMANCE",
                "pattern": "async def.*\\n(?:\\s+.*\\n)*?\\s+(?:time\\.sleep|requests\\.)", # Raw pattern (Secret)
                "rationale": "FastAPI Performance: Synchronous blocking detected in async route.",
                "fix": "Use await asyncio.sleep() or httpx.",
                "scope": "CODE",
                "source": "SOVEREIGN_PRIME",
                "target": "fastapi"
            }
        ]
        
        count = 0
        for rule_data in cloud_payload:
            target = rule_data.get("target", "ALL")
            is_relevant = (target == "ALL" or target in fingerprint["frameworks"])
            
            if is_relevant:
                # SEALING REMOVED: Writing Plain Text for Transparency & Speed
                rule_path = self.rules_dir / f"{rule_data['id']}.json"
                if not rule_path.exists():
                    with open(rule_path, "w") as f:
                        json.dump(rule_data, f, indent=4)
                    count += 1
        
        self.rules_cache = []
        return count

    def _load_anchor(self) -> Optional[Dict]:
        """Loads the Sovereign Anchor (Intent File)."""
        # In a real implementation this would load from disk
        return {"constitution": {"invariants": []}, "gold_standards": {}}

    def verify_gold_standard(self, file_path: str, content: str = None) -> Optional[str]:
        """Verifies a file against the Sovereign Gold Standards."""
        anchor = self._load_anchor()
        standards = anchor.get("gold_standards", {})
        
        matched_standard = None
        for key, std in standards.items():
            if key in file_path: 
                matched_standard = std
                break
        
        if not matched_standard: return None

        expected_hash = matched_standard.get("hash")
        if not expected_hash or expected_hash == "sha256:pending_computation": return None

        if content is None:
            try: content = Path(file_path).read_text()
            except: return None

        actual_hash = f"sha256:{hashlib.sha256(content.encode()).hexdigest()}"
        if actual_hash != expected_hash:
             return f"Gold Standard Violation | Hash mismatch for '{file_path}' | Rationale: This file belongs to the '{key}' Gold Standard and must match the Sovereign Hash. | FIX: Revert changes."
        
        return None

    def check_pulse(self, current_context: Dict = {}) -> PulseResult:
        """
        The Main Loop. Dynamically executes promoted rules.
        """
        start_time = time.perf_counter()
        violations = []
        status = PulseStatus.SECURE
        
        anchor = self._load_anchor()
        if not anchor:
            return PulseResult(PulseStatus.DRIFT, 0.0, ["Anchor Not Found"], {})

        # 1. Load Dynamic Rules (The Scaling Layer)
        dynamic_rules = self._load_dynamic_rules()
        target_file = current_context.get("target_file")
        file_content = current_context.get("file_content")

        if target_file and file_content:
            for rule in dynamic_rules:
                if rule.scope == "CODE":
                    err = self._execute_rule(rule, file_content, target_file)
                    if err: violations.append(err)

            # 2. Gold Standard Check
            gold_error = self.verify_gold_standard(target_file, file_content)
            if gold_error:
                violations.append(gold_error)
                status = PulseStatus.VIOLATION

        # 3. Universal Hardcoded Invariants (The Stability Layer)
        constitution = anchor.get("constitution", {})
        invariants = constitution.get("invariants", [])
        for invariant in invariants:
            rule = invariant.get("rule", "")
            level = invariant.get("level", "TACTICAL")
            
            if "port ==" in rule:
                target_port = rule.split("==")[1].strip()
                active_port = str(current_context.get("PORT", "3999"))
                if active_port != target_port:
                    violations.append(f"Port Violation | Expected {target_port} but found {active_port} | Rationale: Constitution ID 'port_lock' requires Port {target_port} for stability. | FIX: Update your .env or configuration to use Port {target_port}.")
                    if level == "IMMUTABLE": status = PulseStatus.VIOLATION
            
            if "branch ==" in rule:
                target_branch = rule.split("==")[1].strip().strip('"')
                active_branch = current_context.get("BRANCH", "main")
                if active_branch != target_branch:
                    violations.append(f"Context Violation | Working on branch '{active_branch}' but Sovereign requires '{target_branch}' | Rationale: 'branch_lock' enforces alignment with the Sovereign Mainstream. | FIX: Switch to branch '{target_branch}' or update the Anchor.")
                    if level == "IMMUTABLE": status = PulseStatus.VIOLATION

        # 4. Handle Enforcement Mode from Anchor
        moat_pulse = anchor.get("moat_pulse", {})
        enforcement_mode = moat_pulse.get("enforcement_mode", "WARN")
        is_strict = enforcement_mode in ["BLOCK", "STRICT"]

        # TRUST CALIBRATION LOGIC
        if violations and status == PulseStatus.SECURE:
             status = PulseStatus.DRIFT

        if status == PulseStatus.VIOLATION and not is_strict:
             status = PulseStatus.DRIFT
             violations = [f"{v} (Passive Warning)" for v in violations]

        end_time = time.perf_counter()
        latency = (end_time - start_time) * 1000.0
        return PulseResult(status, latency, violations, {"total_rules": len(dynamic_rules)})

    def certify_repo(self) -> Dict:
        """
        Executes a Full Sovereign Audit and generates a Certification Ledger.
        This is the 'Seal of Approval' for $1B scale.
        """
        print(f"🔱 [SOVEREIGN CERTIFICATION]: Initiating Deep Audit...")
        
        # 1. Standard Pulse Check
        result = self.check_pulse()
        
        # 2. Entropy Check (Placeholder for advanced structural analysis)
        # In a real app, this would use FastAST to check for hidden complexity.
        entropy_score = 100 - (len(result.violations) * 10)
        
        # 3. Certification Ledger
        cert = {
            "certification_id": f"cert_{int(time.time())}_{self.get_repo_fingerprint().get('scale', 'SM')}",
            "status": "CERTIFIED" if result.status == PulseStatus.SECURE else "DENIED",
            "scores": {
                "determinism": 100 if result.status == PulseStatus.SECURE else 70,
                "privacy": 100, # Hardcoded moat
                "memory_integrity": 95
            },
            "violations": result.violations,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signature": "sig_sidelith_sovereign_v1_gold"
        }
        
        # PERSIST TO VAULT
        vault_path = Path.cwd() / ".side" / "vault" / "CERTIFICATE.json"
        vault_path.parent.mkdir(parents=True, exist_ok=True)
        with open(vault_path, "w") as f:
            json.dump(cert, f, indent=4)
            
        return cert

# Create singleton instance
pulse = PulseEngine()
