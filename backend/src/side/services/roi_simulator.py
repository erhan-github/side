import asyncio
import logging
from datetime import datetime, timezone
from side.services.unified_buffer import UnifiedBuffer
from side.utils.llm_helpers import extract_json

logger = logging.getLogger(__name__)

class ROISimulatorService:
    """
    Value Estimator Service.
    Estimates the technical and financial impact of resolved issues.
    """
    
    def __init__(self, buffer: UnifiedBuffer):
        self.buffer = buffer

    async def simulate_resolution_impact(self, problem: str, resolution: str):
        """
        Estimates the cost savings of a fix.
        """
        try:
            prompt = f"""
A developer just fixed this problem: "{problem}"
The resolution was: "{resolution}"
            
TASK:
Estimate the value of this fix. If this problem reached production:
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
                
                # Log to Unified Buffer
                await self.buffer.ingest("insights", {
                    "tool": "roi_simulator",
                    "action": "value_estimation",
                    "payload": {
                        "problem": problem,
                        "simulated_impact": data,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                })
                logger.info(f"💰 Value Estimate: ${data.get('cost_saved', 0)} saved.")

        except Exception as e:
            logger.warning(f"ROI Estimation failed: {e}")
