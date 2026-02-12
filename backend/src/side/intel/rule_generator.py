import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RuleGenerator:
    """
    The Legislator.
    Converts observed Invariants into Enforceable Code Rules.
    """
    
    def __init__(self, engine):
        self.engine = engine
        self.project_path = Path(".") # Abstracted away, rules are global to the engine's DB context

    def generate_rules(self, invariants: Dict[str, Any]) -> None:
        """
        Generates the Rulebook from Invariants.
        """
        rules = {
            "system": {
                "version": "AUTO-GENERATED",
                "source": "Sidelith Rule Generator",
                "last_updated": "NOW" # In real impl use datetime
            },
            "architecture": {},
            "security": {
                 "block_hardcoded_secrets": True, # Universal Law
                 "require_env_vars": True 
            },
            "style": {}
        }
        
        # 1. Concurrency Law
        if invariants.get("concurrency") == "async_first":
            rules["architecture"]["preferred_paradigms"] = ["async/await"]
            rules["architecture"]["banned_patterns"] = ["blocking_io_in_async"]
            
        # 2. Network Law
        client = invariants.get("http_client")
        if client == "httpx":
            rules["architecture"]["preferred_libraries"] = ["httpx"]
            rules["architecture"]["banned_libraries"] = ["requests", "urllib3"]
        elif client == "requests":
            rules["architecture"]["preferred_libraries"] = ["requests"]
            
        # 3. Typing Law
        if invariants.get("typing") == "strict":
            rules["style"]["type_hints_required"] = True
            rules["style"]["no_any"] = True
            
        # Write to DB
        try:
            # 1. Concurrency Law
            if "concurrency" in invariants:
                val = invariants["concurrency"]
                if val == "async_first":
                    self.engine.plans.set_rule("architecture", "preferred_paradigms", ["async/await"])
                    self.engine.plans.set_rule("architecture", "banned_patterns", ["blocking_io_in_async"])

            # 2. Network Law
            if "http_client" in invariants:
                client = invariants["http_client"]
                if client == "httpx":
                    self.engine.plans.set_rule("architecture", "preferred_libraries", ["httpx"])
                    self.engine.plans.set_rule("architecture", "banned_libraries", ["requests", "urllib3"])
                elif client == "requests":
                    self.engine.plans.set_rule("architecture", "preferred_libraries", ["requests"])

            # 3. Typing Law
            if "typing" in invariants:
                if invariants["typing"] == "strict":
                    self.engine.plans.set_rule("style", "type_hints_required", True)
                    self.engine.plans.set_rule("style", "no_any", True)
            
            # 4. Universal Security Laws (Always enforced)
            self.engine.plans.set_rule("security", "block_hardcoded_secrets", True)
            self.engine.plans.set_rule("security", "require_env_vars", True)

            logger.info("📜 [RULE_GENERATOR]: Code rules updated in SQLite.")
        except Exception as e:
            logger.error(f"❌ Failed to write rules to DB: {e}")
            
    def get_active_rules(self) -> str:
        """Reads the currently active generated rules from DB as JSON string."""
        rules = self.engine.plans.get_all_rules()
        if rules:
            return json.dumps(rules, indent=2)
        return ""
