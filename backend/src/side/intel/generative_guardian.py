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

class GenerativeGuardian:
    def __init__(self, engine: ContextEngine):
        self.engine = engine
        self.llm = LLMClient()
        self.config = LLMConfigs.get_config("guardian")

    async def audit_generation(self, project_id: str, prompt_intent: str, generated_code: str) -> Dict[str, Any]:
        """
        [PHASE 9]: Audits a block of generated code against Sovereign Rules.
        Returns a 'Drift Report'.
        """
        # 1. Retrieve Active Strategic Rules
        # We fetch both patterns and observations for a complete picture
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
                system_prompt=Personas.GENERATIVE_GUARDIAN,
                **self.config
            )
            
            report = extract_json(response)
            if report.get("drift_detected"):
                await self._log_drift_event(project_id, report)
            
            return report
            
        except Exception as e:
            logger.error(f"Generative Audit failed: {e}")
            return {"drift_detected": False, "error": str(e)}

    async def _log_drift_event(self, project_id: str, report: Dict[str, Any]):
        """Logs a drift event and emits a signal to the HUD."""
        self.engine.audit.log_activity(
            project_id=project_id,
            tool="GENERATIVE_GUARDIAN",
            action="DRIFT_DETECTED",
            payload=report,
            tier="enterprise"
        )
        
        # [SILENT OBSERVER]: Emit real-time signal to the Event Bus
        from side.utils.event_optimizer import event_bus, FrictionPoint, EventPriority
        await event_bus.emit(
            friction_point=FrictionPoint.GENERATIVE_ADVISORY,
            payload={
                "type": "ARCHITECTURAL_DRIFT",
                "project_id": project_id,
                "summary": report.get("summary", "Divergence from Sovereign Rules detected."),
                "findings": report.get("findings", [])
            },
            priority=EventPriority.HIGH
        )
        
        logger.warning(f"⚠️ [DRIFT]: Generative Guardian detected divergence from Sovereign Rules.")
