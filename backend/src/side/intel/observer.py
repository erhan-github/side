"""
[LAYER 4] Activity Distiller - The Activity Log Compiler.
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

logger = logging.getLogger(__name__)

class StrategicObserver:
    def __init__(self, ledger: AuditService):
        self.audit = audit
        self.llm = LLMClient()

    async def distill_observations(self, project_id: str, limit: int = 20) -> int:
        """
        Scans recent activity logs and extracts new "Invariant Facts".
        """
        activities = self.audit.get_recent_activities(project_id, limit=limit)
        if not activities:
            return 0
            
        # Compile Context for LLM
        stream_text = "\n".join([
            f"[{a['created_at']}] {a['tool']}:{a['action']} -> {json.dumps(a['payload'])}"
            for a in activities
        ])
        
        prompt = f"""
Analyze the provided activity stream and extract INVARIANT FACTS.
        
RULES:
1. Ignore transient noise (file reads, minor edits).
2. Focus on ARCHITECTURAL DECISIONS (e.g., "User added Tailwind", "Auth is via Supabase").
3. Extract User Preferences (e.g., "User prefers Pydantic V2").
4. Output strictly a JSON list of objects.

Stream:
{stream_text}

Format:
[
    {{
        "content": "Fact description",
        "tags": ["tag1", "tag2"],
        "confidence": 0.9
    }}
]
"""
        
        try:
            response = await self.llm.complete_async(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are a Fact Extraction Engine. Output strictly JSON.",
                temperature=0.1
            )
            
            facts = extract_json(response)
            if not facts or not isinstance(facts, list):
                 return 0
            count = 0
            for fact in facts:
                if self._store_observation(fact):
                    count += 1
            
            if count > 0:
                logger.info(f"👁️ [DISTILLER]: Extracted {count} new facts from the activity log.")
            return count
            
        except Exception as e:
            logger.error(f"Observation failed: {e}")
            return 0

    def _store_observation(self, fact: Dict[str, Any]) -> bool:
        """Store a verified observation."""
        # Simple deduplication check could go here
        try:
            with self.audit.engine.connection() as conn:
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

    def _parse_json(self, text: str) -> List[Dict[str, Any]]:
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text)
        except:
            return []
