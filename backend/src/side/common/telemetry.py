"""
Side Telemetry - The Nervous System.

Provides universal error handling, performance tracking, and event logging
written directly to the Monolith (local.db).
"""

import time
import functools
import traceback
import logging
from typing import Optional, Any
from datetime import datetime
import asyncio

# Configure standard logging fallback
from pathlib import Path
log_file = Path.home() / ".side" / "side.log"
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
    filename=str(log_file), # Silence terminal
    filemode='a'
)
logger = logging.getLogger("Side")

class TelemetryClient:
    """
    Centralized point for recording organism state.
    """
    _instance = None
    
    def __init__(self, project_id: str = "global"):
        self.project_id = project_id
        self.store = None
        self._init_store()
        
    def _init_store(self):
        # Lazy load to avoid circular imports during startup
        from ..storage.simple_db import SimplifiedDatabase
        from ..intel.intelligence_store import IntelligenceStore
        try:
            db = SimplifiedDatabase()
            self.store = IntelligenceStore(db)
        except Exception as e:
            logger.error(f"Failed to init IntelligenceStore: {e}")

    def log_event(self, event_type: str, context: dict, outcome: Optional[str] = None):
        """
        Record an event to the Monolith.
        Safely fails open if DB is unreachable.
        """
        try:
            if self.store:
                self.store.record_event(
                    project_id=self.project_id,
                    event_type=event_type,
                    context=context,
                    outcome=outcome
                )
            else:
                # Fallback to stderr if DB dead
                logger.info(f"[{event_type}] {outcome} | {context}")
        except Exception as e:
            logger.error(f"Telemetry Failure: {e}")

def monitor(operation: str):
    """
    Decorator: Universal Performance & Error Tracking.
    Wraps any function (sync or async) with telemetry.
    """
    def decorator(func):
        # Handle Async Functions
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start = time.time()
                telemetry = TelemetryClient()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start
                    telemetry.log_event(
                        event_type="OP_SUCCESS",
                        context={"op": operation, "duration_ms": int(duration*1000)},
                        outcome="OK"
                    )
                    return result
                except Exception as e:
                    duration = time.time() - start
                    error_trace = traceback.format_exc()
                    telemetry.log_event(
                        event_type="OP_ERROR",
                        context={
                            "op": operation, 
                            "duration_ms": int(duration*1000),
                            "error": str(e),
                            "trace": error_trace
                        },
                        outcome="FAIL"
                    )
                    logger.error(f"Operation '{operation}' Failed: {e}")
                    raise # Re-raise to let caller handle if needed
            return async_wrapper
            
        # Handle Sync Functions
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.time()
                telemetry = TelemetryClient()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start
                    telemetry.log_event(
                        event_type="OP_SUCCESS",
                        context={"op": operation, "duration_ms": int(duration*1000)},
                        outcome="OK"
                    )
                    return result
                except Exception as e:
                    duration = time.time() - start
                    error_trace = traceback.format_exc()
                    telemetry.log_event(
                        event_type="OP_ERROR",
                        context={
                            "op": operation, 
                            "duration_ms": int(duration*1000),
                            "error": str(e),
                            "trace": error_trace
                        },
                        outcome="FAIL"
                    )
                    logger.error(f"Operation '{operation}' Failed: {e}")
                    raise
            return sync_wrapper
    return decorator
