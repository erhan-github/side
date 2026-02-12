import os
import time
import json
import logging
import threading
import psutil
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

class TokenBucket:
    """
    Standard Token Bucket algorithm for rate limiting.
    Refills tokens at `rate` per second, up to `capacity`.
    """
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = float(capacity)
        self.tokens = float(capacity)
        self.refill_rate = float(refill_rate)
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_refill
            # Refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

class ResourceLimiter(threading.Thread):
    """
    Polices Memory < 1% CPU, < 500MB RAM.
    Uses Token Bucket to throttle background operations when under load.
    """
    def __init__(self, operational_store=None):
        super().__init__(daemon=True)
        self.max_ram_bytes = 500 * 1024 * 1024 # 500MB
        self.high_cpu_threshold = 5.0 # Strict 5%
        self.project_root = Path.cwd()
        self.pulse_path = self.project_root / ".side" / "pulse.json"
        
        # Token Bucket: Capacity 60s, Refill 1s/s. 
        # Spending 1 token = 1 second of high load allowed.
        self.cpu_budget = TokenBucket(capacity=60, refill_rate=1.0)
        
        self.operational = operational_store
        
        # Fallback if no store provided
        if not self.operational:
             from side.storage.modules.base import ContextEngine
             self.operational = ContextEngine().operational
        
    def run(self):
        process = psutil.Process(os.getpid())
        logger.info(f"👮 [RESOURCE_LIMITER]: Monitoring PID {os.getpid()} with Token Bucket Governance")
        
        while True:
            try:
                # 1. RAM Audit
                mem = process.memory_info().rss
                if mem > 200 * 1024 * 1024:
                    import gc
                    gc.collect() 
                    mem = process.memory_info().rss
                
                if mem > self.max_ram_bytes:
                    logger.critical(f"🚨 [RESOURCE_LIMITER]: RAM Violation ({mem/1024/1024:.1f}MB). Terminating.")
                    os._exit(1) # Hard kill
                
                # 2. CPU Audit (Token Bucket)
                cpu = process.cpu_percent(interval=1.0) # Blocking check 1s
                
                if cpu > self.high_cpu_threshold:
                    # High load consumes budget
                    if not self.cpu_budget.consume(tokens=5): # Cost of being heavy is 5x
                        logger.warning(f"🚨 [RESOURCE_LIMITER]: CPU Budget Exhausted ({cpu}%). Throttling...")
                        time.sleep(2) # Forced Cool Down
                else:
                    # Low load passively refills via time passing
                    pass

                # 3. Pulse Telemetry
                try:
                    self._update_pulse(cpu, mem)
                except Exception:
                    pass
                
            except Exception as e:
                logger.error(f"Resource Limiter Error: {e}")
                time.sleep(5)

    def _update_pulse(self, cpu, mem):
        status = "HEALTHY" if cpu < 5.0 else "BUSY"
        data = {
            "status": status,
            "telemetry": {
                "cpu_percent": round(cpu, 1),
                "ram_mb": round(mem / 1024 / 1024, 1),
                "budget": round(self.cpu_budget.tokens, 1),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        # Atomic write
        tmp = self.pulse_path.with_suffix('.tmp')
        tmp.write_text(json.dumps(data))
        tmp.replace(self.pulse_path)
        
        if self.operational:
            self.operational.set_setting("telemetry_cpu", str(cpu))
            self.operational.set_setting("telemetry_ram", str(mem))
