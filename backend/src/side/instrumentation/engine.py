import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class InstrumentationEngine:
    """
    Sovereign Telemetry Engine.
    Records strategic outcomes and performance metrics to the local database.
    """
    def __init__(self, db: Any):
        self.db = db

    def record_outcome(self, project_id: str, event: str, value: float):
        """
        Record a strategic outcome (Positive Reward).
        Example: "User completed task X" -> Reward 1.0
        """
        try:
            logger.info(f"📊 [INSTRUMENT] {event}: {value}")
            
            # Log to DB activities table
            # We map 'instrumentation' to a system-level tool log
            self.db.log_activity(
                project_id=project_id,
                tool="instrumentation",
                action=event,
                cost_tokens=0,
                tier="system",
                payload={
                    "event": event,
                    "value": value,
                    "timestamp": time.time(),
                    "type": "outcome"
                }
            )
        except Exception as e:
            logger.warning(f"Failed to record outcome: {e}")

    def capture_metric(self, project_id: str, name: str, value: Any, tags: Dict[str, str] = None):
        """
        Capture a generic metric (e.g. latency, error_rate).
        """
        try:
             # For V1, we log this as detailed activity to be picked up by the report generator
             self.db.log_activity(
                project_id=project_id,
                tool="instrumentation",
                action=f"Metric: {name}",
                cost_tokens=0,
                tier="info",
                payload={
                    "metric_name": name,
                    "value": value,
                    "tags": tags or {},
                    "type": "metric"
                }
            )
        except Exception as e:
             logger.warning(f"Failed to capture metric: {e}")
