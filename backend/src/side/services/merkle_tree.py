"""
Merkle Tree Service - System Integrity Authority.
Aggregates all active reasoning chains into a single Project Root Hash.
"""
import hashlib
import logging
from typing import List, Optional
from side.intel.reasoning_timeline import TimelineManager

logger = logging.getLogger(__name__)

class SovereignMerkle:
    """
    [AUTHORITY]: Aggregates all active reasoning chains into a single Project Root Hash.
    This fulfills the 'Merkle Injection' capability.
    """
    
    @staticmethod
    def get_project_root() -> str:
        """
        Calculates the current Merkle Root of the project's reasoning state.
        Root = SHA256(Sorted(HeadHashes))
        """
        # Get all active timelines
        active_ids = TimelineManager.list_active()
        if not active_ids:
            return hashlib.sha256(b"empty").hexdigest()
        
        # Collect HEAD signatures from each timeline
        signatures = []
        for fix_id in active_ids:
            timeline = TimelineManager.get(fix_id)
            if timeline and timeline.chain:
                head = timeline.chain[-1]
                # Assuming node has .signature or .hash attribute. 
                # Checking types.py earlier, reasoning nodes have signatures.
                # If signature is missing, we skip (should not happen in valid nodes)
                if hasattr(head, "signature"):
                    signatures.append(head.signature)
        
        if not signatures:
            return hashlib.sha256(b"empty").hexdigest()
            
        # Sort for deterministic output (Merkle Tree requirement)
        signatures.sort()
        
        # Hash of Hashes
        combined = "".join(signatures).encode("utf-8")
        root_hash = hashlib.sha256(combined).hexdigest()
        
        return root_hash

    @staticmethod
    def get_context_injection() -> str:
        """
        Returns the formatted injection string for AI context.
        """
        root = SovereignMerkle.get_project_root()
        return f"[SYSTEM_INTEGRITY_ROOT]: {root}"

    @staticmethod
    def validate_timeline_inclusion(fix_id: str) -> bool:
        """
        Checks if a specific timeline is currently part of the active merkle set.
        """
        # In a real Merkle Tree this would be a proof, 
        # here we just check presence for now.
        return TimelineManager.get(fix_id) is not None
