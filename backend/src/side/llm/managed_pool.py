"""
Managed Credit Pool - High-Velocity Key Rotation.

This component enables Side to scale beyond single-key rate limits by 
aggregating multiple enterprise keys into a single virtual pool.
"""

import os
import time
import logging
from typing import List, Dict, Optional
from collections import deque
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CircuitBreakerMetrics:
    """Metrics for monitoring circuit breaker health."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    keys_currently_cooling: int = 0
    keys_total: int = 0
    avg_rotation_per_minute: float = 0
    last_failure_time: float = 0
    circuit_trips: int = 0  # Number of times all keys exhausted
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests
    
    @property
    def health_score(self) -> int:
        """0-100 health score."""
        if self.keys_total == 0:
            return 0
        healthy_ratio = (self.keys_total - self.keys_currently_cooling) / self.keys_total
        return int(healthy_ratio * self.success_rate * 100)


class ManagedCreditPool:
    """
    Round-robin load balancer for LLM API keys with circuit breaking.
    """
    
    def __init__(self, provider: str = "groq"):
        self.provider = provider
        self.keys = deque()  # Circular buffer for active keys
        self.cooling_keys: Dict[str, float] = {}  # key -> blocked_until_timestamp
        self.default_cool_down = 300  # 5 minutes
        
        # Circuit Breaker Metrics
        self._metrics = CircuitBreakerMetrics()
        self._rotation_timestamps: List[float] = []
        
        self._load_pool()
        
    def _load_pool(self):
        """Load keys from environment variables."""
        # 1. Primary Key (Legacy/Single)
        primary_key = os.getenv("GROQ_API_KEY") if self.provider == "groq" else os.getenv("OPENAI_API_KEY")
        if primary_key:
            self.keys.append(primary_key)
            
        # 2. Pool Keys (SIDE_POOL_KEYS="key1,key2,key3")
        pool = os.getenv("SIDE_POOL_KEYS", "")
        if pool:
            extra_keys = [k.strip() for k in pool.split(",") if k.strip()]
            for k in extra_keys:
                if k not in self.keys:
                    self.keys.append(k)
        
        self._metrics.keys_total = len(self.keys)
        logger.info(f"ManagedCreditPool: Loaded {len(self.keys)} keys for {self.provider}.")

    def get_next_key(self) -> Optional[str]:
        """
        Get the next available key from the pool.
        Rotates the deque.
        """
        self._metrics.total_requests += 1
        
        # 1. Check if we have any keys at all
        if not self.keys and not self.cooling_keys:
            self._metrics.failed_requests += 1
            return None
            
        # 2. Try to find a healthy key
        attempts = 0
        max_attempts = len(self.keys)
        
        while attempts < max_attempts:
            key = self.keys[0] # Peek
            
            # Track rotation rate
            now = time.time()
            self._rotation_timestamps.append(now)
            # Keep only last minute
            self._rotation_timestamps = [t for t in self._rotation_timestamps if now - t < 60]
            self._metrics.avg_rotation_per_minute = len(self._rotation_timestamps)
            
            self.keys.rotate(-1) # Move used key to back
            self._metrics.successful_requests += 1
            
            if len(self.keys) > 1:
                logger.info(f"🔄 [STRATEGIC ROTATION]: Key rotated for {self.provider.upper()} pool. Active: {len(self.keys)}")
                
            return key
            
        # If we are here, keys might be empty if all are cooling?
        if not self.keys and self.cooling_keys:
            # Check if any can be recovered
            self._recover_keys()
            if self.keys:
                return self.get_next_key()
            else:
                logger.warning("ManagedCreditPool: All keys are cooling.")
                self._metrics.circuit_trips += 1
                self._metrics.failed_requests += 1
                return None
                
        self._metrics.failed_requests += 1
        return None

    def mark_as_cooling(self, key: str, duration: int = None):
        """
        Circuit Breaker: Temporarily disable a key (e.g. on 429).
        """
        if not key: return
        
        if duration is None:
            duration = self.default_cool_down
            
        expiry = time.time() + duration
        self.cooling_keys[key] = expiry
        self._metrics.last_failure_time = time.time()
        self._metrics.keys_currently_cooling = len(self.cooling_keys)
        
        # Remove from active rotation if present
        if key in self.keys:
            self.keys.remove(key)
            
        logger.warning(f"ManagedCreditPool: Key ...{key[-4:]} cooling for {duration}s.")

    def _recover_keys(self):
        """Check cooling keys and restore them if expired."""
        now = time.time()
        to_recover = []
        
        for key, expiry in list(self.cooling_keys.items()):
            if now >= expiry:
                to_recover.append(key)
        
        for key in to_recover:
            del self.cooling_keys[key]
            self.keys.append(key)
            logger.info(f"ManagedCreditPool: Key ...{key[-4:]} recovered.")
        
        self._metrics.keys_currently_cooling = len(self.cooling_keys)
            
    @property
    def is_healthy(self) -> bool:
        self._recover_keys()
        return len(self.keys) > 0
    
    def get_metrics(self) -> CircuitBreakerMetrics:
        """Get current circuit breaker metrics for monitoring."""
        self._recover_keys()
        self._metrics.keys_currently_cooling = len(self.cooling_keys)
        return self._metrics
    
    def get_status(self) -> Dict[str, any]:
        """Get detailed status for dashboards."""
        metrics = self.get_metrics()
        return {
            "provider": self.provider,
            "health_score": metrics.health_score,
            "active_keys": len(self.keys),
            "cooling_keys": metrics.keys_currently_cooling,
            "total_keys": metrics.keys_total,
            "success_rate": f"{metrics.success_rate * 100:.1f}%",
            "circuit_trips": metrics.circuit_trips,
            "rotations_per_minute": metrics.avg_rotation_per_minute
        }

