"""
[LAYER 5] Reflection Engine - The Judge.
Calculates "Surprise" to determine the strategic value of an event.
Implements the Hybrid "Safe & Smart" tagging methodology.
"""

import logging
import json
from typing import Dict, Any, Tuple
from side.llm.client import LLMClient

logger = logging.getLogger(__name__)

class ReflectionEngine:
    def __init__(self):
        self.llm = LLMClient()

    async def reflect_on_outcome(self, tool: str, intent: str, outcome: str) -> Tuple[str, float]:
        """
        [THE SURPRISE METRIC]:
        Compares Intent (Expectation) vs. Outcome (Reality).
        Returns: (Tag, Surprise_Score)
        """
        # Fast path for obvious routine tasks
        if tool in ["read_file", "list_dir"] and "error" not in outcome.lower():
            return "ROUTINE", 0.1

        prompt = f"""
        Analyze this Action/Outcome pair. Calculate the SURPRISE SCORE (0.0 - 1.0).
        
        Intent: {intent}
        Tool: {tool}
        Actual Outcome: {outcome}
        
        Ontology:
        - CRITICAL (>0.8): Failed expectations, bugs, architectural pivots.
        - STRATEGIC (0.4-0.8): User preferences, new features, non-standard success.
        - ROUTINE (<0.4): Expected success, standard operations.
        
        Output JSON:
        {{
            "tag": "CRITICAL" | "STRATEGIC" | "ROUTINE",
            "score": float,
            "reason": "Why?"
        }}
        """
        
        try:
            response = await self.llm.complete_async(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are the Reflection Engine. Be critical.",
                temperature=0.0
            )
            
            data = self._parse_json(response)
            return data.get("tag", "ROUTINE"), data.get("score", 0.1)
            
        except Exception as e:
            logger.warning(f"Reflection failed: {e}")
            return "ROUTINE", 0.0

    def _parse_json(self, text: str) -> Dict[str, Any]:
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text)
        except:
            return {}
