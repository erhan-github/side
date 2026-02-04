import asyncio
import logging
from datetime import datetime, timezone
from side.services.unified_buffer import UnifiedBuffer
from side.utils.llm_helpers import extract_json

logger = logging.getLogger(__name__)

class ROISimulatorService:
    """
    [COUNTERFACTUAL_SIMULATOR]: Calculates the 'Value of Averted Disaster'.
    Whenever a Causal Resolution is detected, this service simulates the 
    'World Without Sidelith' to quantify technical and financial ROI.
    """
    
    def __init__(self, buffer: UnifiedBuffer):
        self.buffer = buffer

    async def simulate_resolution_impact(self, problem: str, resolution: str):
        """
        Simulates the counterfactual cost of a bug.
        """
        try:
            # TIER 2: Strategic Simulation (Gated Call)
            prompt = f"""
A developer just fixed this problem: "{problem}"
The resolution was: "{resolution}"
            
TASK:
Simulate the "World Without This Fix". If this problem reached production:
1. How many ENGINEERING HOURS would it take to find and fix?
2. What is the RISK (None, Low, Medium, High, Critical)?
3. What is the ESTIMATED COST (in USD, assuming $150/hr)?
            
Output strictly JSON:
{{
    "hours_saved": float,
    "risk_level": "string",
    "cost_saved": float,
    "why": "one sentence explanation"
}}
"""
            from side.llm.client import LLMClient
            client = LLMClient()
            response = await client.complete_async(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are a value-analyst. Output JSON only.",
                temperature=0.1
            )
            
            data = extract_json(response)
            if data:
                
                # [IMPACT_LOG] Commit to the Unified Buffer
                await self.buffer.ingest("insights", {
                    "tool": "roi_simulator",
                    "action": "averted_disaster_log",
                    "payload": {
                        "problem": problem,
                        "simulated_impact": data,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                })
                logger.info(f"💰 [ROI]: Simulated ${data.get('cost_saved', 0)} in averted disaster costs.")

        except Exception as e:
            logger.warning(f"ROI Simulation failed: {e}")
