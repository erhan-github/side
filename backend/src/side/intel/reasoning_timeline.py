"""
[PHASE 7] Reasoning Timeline Service
Manages the immutable audit trail for verified fixes.
"""
import time
import logging
from typing import List, Dict, Any, Optional
from side.intel.types import ReasoningNode, EventType, create_reasoning_node

logger = logging.getLogger(__name__)

class ReasoningTimeline:
    """
    Manages the immutable reasoning chain for a single fix session.
    Each event is linked to its parent, forming a verifiable chain.
    """
    
    def __init__(self, fix_id: str, ledger: Optional[Any] = None, session_id: Optional[str] = None):
        self.fix_id = fix_id
        self.ledger = ledger
        self.session_id = session_id
        self.chain: List[ReasoningNode] = []
        self._head_id: Optional[str] = None

    def record(self, event_type: str, payload: Dict[str, Any]) -> ReasoningNode:
        """
        Records a new event in the reasoning chain and persists it if ledger available.
        
        Args:
            event_type: One of EventType values.
            payload: Event-specific data (e.g., signals_count, file, line).
        
        Returns:
            The created ReasoningNode.
        """
        node = create_reasoning_node(
            event_type=event_type,
            payload=payload,
            parent_id=self._head_id
        )
        
        self.chain.append(node)
        self._head_id = node.event_id
        
        # [CIP]: PALANTIR-LEVEL CAUSAL PERSISTENCE
        if self.ledger:
            try:
                self.ledger.save_reasoning_node(node, session_id=self.session_id)
                logger.info(f"💾 [TIMELINE]: Persisted {event_type} to SQLite.")
            except Exception as e:
                logger.error(f"❌ [TIMELINE]: Persistence failed for {node.event_id}: {e}")
        
        logger.info(f"📝 [TIMELINE]: Recorded {event_type} (chain length: {len(self.chain)})")
        return node

    def record_issue_detected(self, signals: List[Dict], focus_file: str) -> ReasoningNode:
        """Records an ISSUE_DETECTED event."""
        return self.record(EventType.ISSUE_DETECTED.value, {
            "signals_count": len(signals),
            "focus_file": focus_file,
            "sample_errors": [s.get("content", "")[:100] for s in signals[:3]]
        })

    def record_context_injected(self, signals_count: int, token_count: int) -> ReasoningNode:
        """Records a CONTEXT_INJECTED event."""
        return self.record(EventType.CONTEXT_INJECTED.value, {
            "signals_count": signals_count,
            "token_count": token_count
        })

    def record_fix_applied(self, file: str, line: int = None, change_summary: str = None) -> ReasoningNode:
        """Records a FIX_APPLIED event."""
        return self.record(EventType.FIX_APPLIED.value, {
            "file": file,
            "line": line,
            "change_summary": change_summary
        })

    def record_verification_passed(self, remaining_errors: int = 0) -> ReasoningNode:
        """Records a VERIFICATION_PASSED event."""
        return self.record(EventType.VERIFICATION_PASSED.value, {
            "remaining_errors": remaining_errors,
            "verified_at": time.time()
        })

    def record_verification_failed(self, remaining_errors: int, new_errors: int = 0) -> ReasoningNode:
        """Records a VERIFICATION_FAILED event."""
        return self.record(EventType.VERIFICATION_FAILED.value, {
            "remaining_errors": remaining_errors,
            "new_errors": new_errors
        })

    def record_regression(self, new_errors: List[Dict]) -> ReasoningNode:
        """Records a REGRESSION_DETECTED event."""
        return self.record(EventType.REGRESSION_DETECTED.value, {
            "new_error_count": len(new_errors),
            "sample_errors": [e.get("content", "")[:100] for e in new_errors[:3]]
        })

    def get_chain(self) -> List[ReasoningNode]:
        """Returns the full reasoning chain."""
        return self.chain

    def verify_integrity(self) -> bool:
        """
        Verifies the integrity of the entire chain.
        Each node's signature must match its computed signature.
        """
        for node in self.chain:
            if not node.verify():
                logger.error(f"❌ [TIMELINE]: Integrity check failed for {node.event_id}")
                return False
        
        # Verify parent links
        seen_ids = set()
        for node in self.chain:
            if node.parent_id and node.parent_id not in seen_ids:
                logger.error(f"❌ [TIMELINE]: Broken parent link for {node.event_id}")
                return False
            seen_ids.add(node.event_id)
        
        logger.info(f"✅ [TIMELINE]: Integrity verified for {len(self.chain)} nodes.")
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Exports the timeline as a dict for serialization."""
        return {
            "fix_id": self.fix_id,
            "chain": [n.to_dict() for n in self.chain],
            "integrity_verified": self.verify_integrity()
        }

# ---------------------------------------------------------------------
# TIMELINE MANAGER (Global Registry)
# ---------------------------------------------------------------------

class TimelineManager:
    """
    Global registry for all active reasoning timelines.
    """
    _timelines: Dict[str, ReasoningTimeline] = {}

    @classmethod
    def get_or_create(cls, fix_id: str, ledger: Optional[Any] = None, session_id: Optional[str] = None) -> ReasoningTimeline:
        """Gets an existing timeline or creates a new one with optional persistence."""
        if fix_id not in cls._timelines:
            cls._timelines[fix_id] = ReasoningTimeline(fix_id, ledger=ledger, session_id=session_id)
        return cls._timelines[fix_id]

    @classmethod
    def get(cls, fix_id: str) -> Optional[ReasoningTimeline]:
        """Gets an existing timeline."""
        return cls._timelines.get(fix_id)

    @classmethod
    def close(cls, fix_id: str) -> Optional[ReasoningTimeline]:
        """Closes and returns a timeline (removes from active registry)."""
        return cls._timelines.pop(fix_id, None)

    @classmethod
    def list_active(cls) -> List[str]:
        """Lists all active timeline IDs."""
        return list(cls._timelines.keys())

if __name__ == "__main__":
    # Quick Test
    logging.basicConfig(level=logging.INFO)
    
    timeline = ReasoningTimeline("test-fix-001")
    
    timeline.record_issue_detected([{"content": "session.user is None"}], "auth.py")
    timeline.record_context_injected(5, 500)
    timeline.record_fix_applied("session.py", 50, "Added null check")
    timeline.record_verification_passed(0)
    
    print(f"Chain length: {len(timeline.chain)}")
    print(f"Integrity: {timeline.verify_integrity()}")
