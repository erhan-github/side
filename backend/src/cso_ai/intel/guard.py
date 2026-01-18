"""
CSO.ai Guard - Proactive Guardianship.

Detects conflicts between current user intent and past strategic decisions.
Zero storage, pure logic. Uses existing 'decisions' table.

Usage:
    guard = Guard()
    conflict = await guard.check_conflict(query, decisions)
    if conflict:
        print(f"⚠️ Conflict: {conflict.reason}")
"""

import logging
from typing import Any, Optional
from dataclasses import dataclass

from cso_ai.intel.strategist import Strategist

logger = logging.getLogger("cso_ai.intel.guard")

@dataclass
class Conflict:
    detected: bool
    reason: str
    decision_id: str

class Guard:
    """
    The Guardian of Strategy.
    Checks for semantic conflicts using a fast LLM model.
    """
    
    CONFLICT_PROMPT = """
    You are a Strategic Guardian for an elite engineering team. Your job is to detect CRITICAL CONFLICTS between a user's new request and their past established strategic decisions.
    
    PAST DECISIONS:
    {decisions_text}
    
    USER REQUEST:
    "{query}"
    
    TASK:
    Identify if the user is making a "Dangerous Architectural Move" that contradicts a previous standard.
    
    CRITICAL CONFLICT EXAMPLES:
    - Decided on "PostgreSQL" -> User asks "How to setup MongoDB" (CONFLICT)
    - Decided on "Supabase" -> User asks "Integrate Firebase auth" (CONFLICT)
    - Decided on "Monolith" -> User asks "Create a new microservice" (CONFLICT)
    - Decided on "Local-First" -> User asks "Move all data to purely cloud-only storage" (CONFLICT)
    
    INSTRUCTIONS:
    - If a DIRECT CONTRADICTION is found, flag it.
    - If the user is just exploring or asking for info without intent to change, say "NO_CONFLICT".
    - Ignore minor formatting or styling queries.
    
    RESPONSE FORMAT:
    NO_CONFLICT
    OR
    CONFLICT: [Decision ID]: [Explanation of why this contradicts the previous decision. Be concise but firm.]
    """

    def __init__(self):
        self.strategist = Strategist()

    async def check_conflict(
        self, query: str, decisions: list[dict[str, Any]]
    ) -> Optional[Conflict]:
        """
        Check if query contradicts past decisions.
        Returns Conflict object or None.
        """
        if not decisions:
            return None
            
        # Format decisions for prompt
        decisions_text = ""
        for d in decisions:
            decisions_text += f"- [{d['id']}] {d['question']} -> {d['answer']}\n"
            
        prompt = self.CONFLICT_PROMPT.format(
            decisions_text=decisions_text,
            query=query
        )
        
        # Use Fast/Lite model for speed
        response = await self.strategist._call_groq(
            prompt,
            model=self.strategist.LITE_MODEL,
            max_tokens=100,
            temperature=0.1
        )
        
        if not response:
            return None
            
        if "NO_CONFLICT" in response.upper():
            return None
            
        # Parse conflict
        # Expected: "CONFLICT: d123: You decided to use X..."
        try:
            parts = response.split(":", 2)
            if len(parts) >= 3 and "CONFLICT" in parts[0].upper():
                return Conflict(
                    detected=True,
                    decision_id=parts[1].strip(),
                    reason=parts[2].strip()
                )
        except Exception as e:
            logger.warning(f"Failed to parse guard response: {e}")
            
        return None
