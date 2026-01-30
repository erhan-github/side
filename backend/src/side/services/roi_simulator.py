import asyncio
import logging
from datetime import datetime, timezone
from side.services.unified_buffer import UnifiedBuffer

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
            prompt = f"""You are a Senior Project Manager & Financial Analyst.
            
            A developer just fixed this problem: "{problem}"
            The resolution was: "{resolution}"
            
            TASK:
            Simulate the "World Without This Fix". If this problem reached production:
            1. How many ENGINEERING HOURS would it take to find and fix?
            2. What is the RISK (None, Low, Medium, High, Critical)?
            3. What is the ESTIMATED COST (in USD, assuming $150/hr)?
            
            OUTPUT JSON:
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
            
            import json
            # Heuristic JSON parsing
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end != -1:
                data = json.loads(response[start:end])
                
                # [ROI_LEDGER] Commit to the Unified Buffer
                await self.buffer.ingest("wisdom", {
                    "tool": "roi_simulator",
                    "action": "averted_disaster_ledger",
                    "payload": {
                        "problem": problem,
                        "simulated_impact": data,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                })
                logger.info(f"💰 [ROI]: Simulated ${data.get('cost_saved', 0)} in averted disaster costs.")

        except Exception as e:
            logger.warning(f"ROI Simulation failed: {e}")
