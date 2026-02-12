"""
Goal Validator - The Objective Auditor.
Compares Human Intent (Artifacts) with Generative State (Code).
"""

import logging
import json
from typing import Dict, Any, List
from side.storage.modules.base import ContextEngine
from side.llm.client import LLMClient
from side.utils.llm_helpers import extract_json
from side.prompts import Personas, IntentAuditPrompt, LLMConfigs

logger = logging.getLogger(__name__)

class GoalValidator:
    def __init__(self, engine: ContextEngine):
        self.engine = engine
        self.llm = LLMClient()
        self.config = LLMConfigs.get_config("intent_verifier")

    async def verify_goal_alignment(self, project_id: str) -> Dict[str, Any]:
        """
        [GOAL VALIDATION]: Verifies if generated code matches the 'Stated Goals' (Artifacts + Git).
        """
        # 1. Fetch Goals from Multi-Source Ontology
        objective = self.engine.schema.get_concept("current_objective")
        git_intent = self.engine.schema.get_concept("git_intent")
        
        # [UNIVERSAL INGESTION]: Load all supporting strategic artifacts
        artifacts = self.engine.schema.list_concepts_by_category("strategic_artifact")
        
        goal_signals = []
        if objective: goal_signals.append(f"### PRIMARY GOAL (from task.md)\n{objective.get('content')}")
        if git_intent: goal_signals.append(f"### RECENT COMMIT (Git State)\n{git_intent.get('content')}")
        
        artifact_signals = []
        for art in artifacts:
            # Avoid duplicating task.md if it's already primary
            if art.get("topic") == "artifact_task": continue
            # Limit individual artifact contribution to prevent prompt bloating
            content = art.get('content', '')[:1000] 
            artifact_signals.append(f"#### {art.get('topic')}\n{content}")

        goal_context = "\n\n".join(goal_signals) if goal_signals else "No explicit primary goals found."
        supporting_context = "\n\n".join(artifact_signals) if artifact_signals else "No supporting artifacts found."

        # 2. Fetch Recent Activities (Representing code generations)
        activities = self.engine.audits.get_recent_activities(project_id, limit=5)
        code_snippets = []
        for activity in activities:
            if activity.tool in ["EDITOR", "GENERATOR", "LLM_ENGINE"]:
                # [SIGNAL FIDELITY]: Use diffs for structural state
                code_snippets.append(f"File: {activity.payload.get('file', 'unknown')}\n{activity.payload.get('diff', 'no diff available')}")

        code_context = "\n\n".join(code_snippets)

        # 3. Semantic Alignment Audit
        prompt = IntentAuditPrompt.format(
            intent_context=goal_context,
            supporting_context=supporting_context,
            code_context=code_context
        )

        try:
            response = await self.llm.complete_async(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=Personas.INTENT_VERIFIER,
                **self.config
            )
            
            report = extract_json(response)
            if report.get("mission_drift_detected") or report.get("goal_drift_detected"):
                await self._log_goal_drift(project_id, report)
            
            return report

        except Exception as e:
            logger.error(f"Goal Validation failed: {e}")
            return {"alignment_score": 0.0, "error": str(e)}

    async def _log_goal_drift(self, project_id: str, report: Dict[str, Any]):
        """Logs a goal drift event and emits a HUD signal."""
        self.engine.audits.log_activity(
            project_id=project_id,
            tool="GOAL_VALIDATOR",
            action="GOAL_DRIFT_DETECTED",
            payload=report,
            tier="enterprise"
        )
        
        # [SILENT OBSERVER]: Emit real-time signal to the Event Bus
        from side.utils.event_optimizer import event_bus, FrictionPoint, EventPriority
        await event_bus.emit(
            friction_point=FrictionPoint.GENERATIVE_ADVISORY,
            payload={
                "type": "GOAL_DRIFT",
                "project_id": project_id,
                "score": report.get("alignment_score"),
                "summary": report.get("summary", report.get("strategic_summary", "Goal Drift detected.")),
                "findings": report.get("findings", [])
            },
            priority=EventPriority.CRITICAL
        )
        
        logger.info(f"🎯 [GOAL_VALIDATOR]: Goal Drift detected. Alignment: {report.get('alignment_score')}")
