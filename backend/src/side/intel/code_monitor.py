"""
 Activity Distiller - The Activity Log Compiler.
Distills raw transaction streams into high-fidelity "Observations" (Facts).
"""
import logging
import json
import uuid
from typing import List, Dict, Any
from datetime import datetime, timezone
from side.storage.modules.audit import AuditService
from side.llm.client import LLMClient
from side.utils.llm_helpers import extract_json
from side.prompts import Personas, FactExtractionPrompt, LLMConfigs

logger = logging.getLogger(__name__)

class CodeMonitor:
    def __init__(self, ledger: AuditService):
        self.audits = ledger
        self.llm = LLMClient()
        self.config = LLMConfigs.get_config("fact_extraction")

    async def distill_observations(self, project_id: str, limit: int = 20) -> int:
        """
        Scans recent activity logs and extracts new "Invariant Facts".
        """
        activities = self.audits.get_recent_activities(project_id, limit=limit)
        if not activities:
            return 0
            
        # Compile Context for LLM
        stream_text = "\n".join([
            f"[{a['created_at']}] {a['tool']}:{a['action']} -> {json.dumps(a['payload'])}"
            for a in activities
        ])
        
        prompt = FactExtractionPrompt.format(stream_text=stream_text)
        
        try:
            response = await self.llm.complete_async(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=Personas.FACT_ENGINE,
                **self.config
            )
            
            facts = extract_json(response)
            if not facts or not isinstance(facts, list):
                 return 0
            count = 0
            for fact in facts:
                if self._store_observation(fact):
                    count += 1
            
            if count > 0:
                logger.info(f"👁️ [MONITOR]: Extracted {count} new facts from the activity log.")
            return count
            
        except Exception as e:
            logger.error(f"Observation failed: {e}")
            return 0

    def _store_observation(self, fact: Dict[str, Any]) -> bool:
        """Store a verified observation."""
        # Simple deduplication check could go here
        try:
            with self.audits.engine.connection() as conn:
                conn.execute("""
                    INSERT INTO observations (id, content, context_tags, confidence, last_verified_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    fact['content'],
                    json.dumps(fact.get('tags', [])),
                    fact.get('confidence', 0.8),
                    datetime.now(timezone.utc)
                ))
            return True
        except Exception as e:
            logger.warning(f"Failed to store observation: {e}")
            return False
