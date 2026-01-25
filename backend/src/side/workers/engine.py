"""
Side Worker Engine - The Muscle.

Consumes jobs from the Queue and executes them using the Forensic Tools.
Atomic. Resilient.
"""

import time
import asyncio
import traceback
from typing import Dict, Any, Callable
from .queue import JobQueue

class WorkerEngine:
    """
    The background processor.
    """
    
    def __init__(self, queue: JobQueue, handlers: Dict[str, Callable] = None):
        self.queue = queue
        self.handlers = handlers or {}
        self.running = False
        self.poll_interval = 1.0
        
    def register_handler(self, job_type: str, handler: Callable):
        """Register a function to handle a specific job type."""
        self.handlers[job_type] = handler
        
    async def start(self):
        """Start the consumer loop."""
        self.running = True
        print("⚙️  Worker Engine Started. Listening for jobs...")
        
        while self.running:
            try:
                # 1. Claim Job
                job = self.queue.claim_next()
                
                if not job:
                    await asyncio.sleep(self.poll_interval)
                    continue
                    
                # 2. Execute
                await self.process_job(job)
                
            except Exception as e:
                print(f"❌ Loop Error: {e}")
                # traceback.print_exc()

    async def process_job(self, job: Dict):
        """Process a single job (Public for testing)."""
        try:
            print(f"⚙️  Processing Job {job['id']} ({job['type']})...")
            handler = self.handlers.get(job['type'])
            
            if not handler:
                raise ValueError(f"No handler for job type: {job['type']}")
                
            # Execute handler (sync or async)
            payload = job['payload']
            # Determine if async
            if asyncio.iscoroutinefunction(handler):
                result = await handler(payload)
            else:
                result = handler(payload)
                
            # 3. Complete
            self.queue.complete_job(job['id'], result)
            print(f"✅ Job {job['id']} Complete.")
            
        except Exception as e:
            print(f"❌ Job Failed: {e}")
            traceback.print_exc()
            self.queue.fail_job(job['id'], str(e))
            
    def stop(self):
        self.running = False

# --- Standard Handlers ---
from ..common.telemetry import monitor

@monitor("worker_security_scan")
async def handle_security_scan(payload: Dict):
    """Run security probe on target."""
    target = payload.get("target")
    # Mock for v0.1 - In real life calls ForensicAuditRunner
    return {"status": "safe", "scanned": target, "issues": []}

@monitor("worker_complexity")
async def handle_complexity_gauge(payload: Dict):
    """Measure complexity."""
    target = payload.get("target")
    # Mock
    return {"score": 5, "verdict": "clean"}

@monitor("worker_dep_map")
async def handle_dependency_map(payload: Dict):
    """Map imports."""
    target = payload.get("target")
    return {"imports": ["os", "sys"], "depended_by": []}
