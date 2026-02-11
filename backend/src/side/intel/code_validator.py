"""
Phase 9: Generative Advisory - The Software 2.0 Observer.
Monitors LLM-generated code for structural and semantic drift,
acting as an expert partner to provide high-fidelity advisory signals.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from side.storage.modules.base import ContextEngine
from side.llm.client import LLMClient
from side.utils.llm_helpers import extract_json
from side.prompts import Personas, GuardianPrompt, LLMConfigs

logger = logging.getLogger(__name__)

class CodeValidator:
    def __init__(self, engine: ContextEngine):
        self.engine = engine
        self.llm = LLMClient()
        self.config = LLMConfigs.get_config("guardian")

    async def audit_generation(self, project_id: str, prompt_intent: str, generated_code: str) -> Dict[str, Any]:
        """
        [CODE VALIDATION]: Audits a block of generated code against Project Rules.
        Returns a 'Pattern Violation' report.
        """
        # 1. Retrieve Active Code Rules
        rules = self.engine.wisdom.get_patterns(limit=10)
        observations = []
        with self.engine.connection() as conn:
            obs_rows = conn.execute("SELECT content FROM observations ORDER BY confidence DESC LIMIT 10").fetchall()
            observations = [row[0] for row in obs_rows]

        rule_context = "\n".join([f"- {r['intent']}" for r in rules])
        obs_context = "\n".join([f"- {o}" for o in observations])
        
        # 2. Perform Semantic Verification
        prompt = GuardianPrompt.format(
            prompt_intent=prompt_intent,
            rule_context=rule_context,
            obs_context=obs_context,
            generated_code=generated_code
        )
        
        try:
            response = await self.llm.complete_async(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=Personas.CODE_VALIDATOR,
                **self.config
            )
            
            report = extract_json(response)
            if report.get("drift_detected") or report.get("violation_detected"):
                await self._log_violation_event(project_id, report)
            
            return report
            
        except Exception as e:
            logger.error(f"Code Validation failed: {e}")
            return {"violation_detected": False, "error": str(e)}

    async def _log_violation_event(self, project_id: str, report: Dict[str, Any]):
        """Logs a pattern violation and emits a signal to the HUD."""
        self.engine.audit.log_activity(
            project_id=project_id,
            tool="CODE_VALIDATOR",
            action="VIOLATION_DETECTED",
            payload=report,
            tier="enterprise"
        )
        
        # [SILENT OBSERVER]: Emit real-time signal to the Event Bus
        from side.utils.event_optimizer import event_bus, FrictionPoint, EventPriority
        await event_bus.emit(
            friction_point=FrictionPoint.GENERATIVE_ADVISORY,
            payload={
                "type": "PATTERN_VIOLATION",
                "project_id": project_id,
                "summary": report.get("summary", "Divergence from Code Rules detected."),
                "findings": report.get("findings", [])
            },
            priority=EventPriority.HIGH
        )
        
        logger.warning(f"⚠️ [VIOLATION]: Code Validator detected divergence from Code Rules.")
