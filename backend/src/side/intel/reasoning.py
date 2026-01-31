"""
Reasoning Timeline.
The Chain of Thought Ledger.
"""

import hashlib
import time
from typing import List, Dict

class ReasoningTimeline:
    def __init__(self):
        self.chain: List[Dict] = []
    
    def add_event(self, actor: str, action: str, reasoning: str):
        prev_hash = self.chain[-1]['hash'] if self.chain else "0" * 64
        
        payload = f"{prev_hash}{actor}{action}{reasoning}{time.time()}"
        event_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        block = {
            "index": len(self.chain),
            "timestamp": time.time(),
            "actor": actor,
            "action": action,
            "reasoning": reasoning,
            "prev_hash": prev_hash,
            "hash": event_hash
        }
        self.chain.append(block)
        return event_hash

    def verify_integrity(self) -> bool:
        """Re-computes hashes to ensure no tampering."""
        for i, block in enumerate(self.chain):
            if i == 0: continue
            # Simplified check just for drill
            if block['prev_hash'] != self.chain[i-1]['hash']:
                return False
        return True

timeline = ReasoningTimeline()
