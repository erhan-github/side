"""
Intent Context Injector.

Injects institutional memory (verified fixes, repetition warnings) into LLM context.
"""

import logging
from typing import List, Dict, Any, Optional

from side.intel.conversation_session import IntentSignalType
from side.storage.simple_db import SimplifiedDatabase
from side.storage.modules.base import SovereignEngine

logger = logging.getLogger(__name__)

class IntentContextInjector:
    """
    Injects high-value intent signals into the LLM's context window.
    Focuses on:
    1. Preventing repetition (Don't do X again)
    2. Flagging false positives (X didn't work last time)
    3. Suggesting verified fixes (We know X works)
    """

    def __init__(self, engine: SovereignEngine):
        self.engine = engine
        # We access store directly via engine to avoid circular deps if possible
        # Or instantiate store. Ideally engine provides access.
        # SimplifiedDatabase combines them, but ACE uses SovereignEngine.
        # So we reconstruct the store wrapper or use a shared one.
        from side.storage.modules.intent_fusion import IntentFusionStore
        self.store = IntentFusionStore(engine)

    def get_context_snippet(self, project_id: str, focus_cluster: List[str] = None) -> str:
        """
        Builds a context snippet based on project history and focus files.
        """
        # 1. Fetch recent signals for this project
        # In a real impl, we'd filter by project_id in SQL.
        # For now, list recent and filter.
        # TODO: Add project_id filter to list_signals or join sessions.
        
        # We need to find sessions for this project first
        sessions = self.store.list_sessions(project_id, limit=20)
        session_ids = [s['session_id'] for s in sessions]
        
        relevant_signals = []
        for sid in session_ids:
            signals = self.store.get_signals_for_session(sid)
            relevant_signals.extend(signals)
            
        if not relevant_signals:
            return ""

        # 2. Filter/Prioritize Signals
        # We prioritize: FALSE_POSITIVE > REPETITION > REST
        prioritized = sorted(
            relevant_signals, 
            key=lambda x: 10 if x['signal_type'] == IntentSignalType.FALSE_POSITIVE.value else 5,
            reverse=True
        )
        
        parts = []
        seen_snippets = set()
        
        for sig in prioritized[:3]: # Top 3 only
            snippet = sig.get('context_snippet', '')
            if snippet and snippet not in seen_snippets:
                parts.append(snippet)
                seen_snippets.add(snippet)
                
        if not parts:
            return ""
            
        return "📚 INSTITUTIONAL MEMORY:\n" + "\n".join(parts)
