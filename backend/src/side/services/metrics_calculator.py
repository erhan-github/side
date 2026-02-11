import asyncio
import logging
from datetime import datetime, timezone
from side.services.data_buffer import DataBuffer
from side.utils.llm_helpers import extract_json
from side.prompts import Personas, ValueEstimationPrompt, LLMConfigs

logger = logging.getLogger(__name__)

class MetricsCalculator:
    """
    Value Estimator Service.
    Estimates the technical and financial impact of resolved issues.
    """
    
    def __init__(self, buffer: DataBuffer):
        self.buffer = buffer
        self.config = LLMConfigs.get_config("value_estimation")

    async def simulate_resolution_impact(self, problem: str, resolution: str):
        """
        Estimates the cost savings of a fix.
        """
        try:
            prompt = ValueEstimationPrompt.format(
                problem=problem,
                resolution=resolution
            )
            from side.llm.client import LLMClient
            client = LLMClient()
            response = await client.complete_async(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=Personas.VALUE_ANALYST,
                **self.config
            )
            
            data = extract_json(response)
            if data:
                
                # Log to Unified Buffer
                await self.buffer.ingest("insights", {
                    "tool": "metrics_calculator",
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
