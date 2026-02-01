"""
Conversation Session Data Models

Palantir-Grade ontology for LLM-User exchange tracking.
[MIGRATED]: See backend/src/side/models/intent.py
"""

from side.models.intent import (
    IntentCategory,
    ClaimedOutcome,
    VerifiedOutcome,
    IntentSignalType,
    ConversationSession,
    IntentSignal
)

# Backward Compatibility Export
__all__ = [
    "IntentCategory",
    "ClaimedOutcome",
    "VerifiedOutcome",
    "IntentSignalType", 
    "ConversationSession",
    "IntentSignal"
]
