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

logger = logging.getLogger(__name__)

class ManagedCreditPool:
    """
    Round-robin load balancer for LLM API keys with circuit breaking.
    """
    
    def __init__(self, provider: str = "groq"):
        self.provider = provider
        self.keys = deque()  # Circular buffer for active keys
        self.cooling_keys: Dict[str, float] = {}  # key -> blocked_until_timestamp
        self.default_cool_down = 300  # 5 minutes
        
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
                    
        logger.info(f"ManagedCreditPool: Loaded {len(self.keys)} keys for {self.provider}.")

    def get_next_key(self) -> Optional[str]:
        """
        Get the next available key from the pool.
        Rotates the deque.
        """
        # 1. Check if we have any keys at all
        if not self.keys and not self.cooling_keys:
            return None
            
        # 2. Try to find a healthy key
        attempts = 0
        max_attempts = len(self.keys)
        
        while attempts < max_attempts:
            key = self.keys[0] # Peek
            
            # Check if recently cooled? (Double check, though we move cooled keys out)
            # Actually, we keep cooled keys in 'cooling_keys' dict and remove from 'keys' deque?
            # Or simpler: keep in deque but check status.
            # Design choice: Remove from deque to 'cooling', re-add when healthy.
            
            self.keys.rotate(-1) # Move used key to back
            return key
            
        # If we are here, keys might be empty if all are cooling?
        if not self.keys and self.cooling_keys:
            # Check if any can be recovered
            self._recover_keys()
            if self.keys:
                return self.get_next_key()
            else:
                logger.warning("ManagedCreditPool: All keys are cooling.")
                return None
                
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
            
    @property
    def is_healthy(self) -> bool:
        self._recover_keys()
        return len(self.keys) > 0
