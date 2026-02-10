"""
Friction-Point Handlers - The Core Intelligence Layer

These handlers implement Sidelith's unique value at the 5 critical friction points
in the developer-AI workflow.

Each handler is optimized to:
1. Process events quickly (< 100ms for most)
2. Inject context intelligently
3. Learn from patterns
4. Preserve project decisions
"""

import logging
from typing import Dict, Any
from pathlib import Path

from side.utils.event_optimizer import (
    event_bus,
    FrictionPoint,
    EventPriority,
    Event,
    lazy_intelligence
)
from side.storage.modules.transient import SessionCache
from side.storage.modules.audit import AuditService

logger = logging.getLogger(__name__)


# ============================================================================
# Friction Point 1: AI Code Generation
# ============================================================================

@event_bus.on(FrictionPoint.AI_CODE_GENERATION, EventPriority.CRITICAL)
async def handle_ai_code_generation(event: Event):
    """
    Handle AI code generation - inject context and check patterns.
    
    Value:
    - Inject project-specific context to AI
    - Check for anti-patterns
    - Learn from accepted/rejected code
    
    Processing time: < 50ms
    """
    payload = event.payload
    code = payload.get("code", "")
    file_path = payload.get("file_path", "")
    ai_model = payload.get("ai_model", "unknown")
    project_id = payload.get("project_id", "unknown")
    
    logger.info(f"AI code generation detected: {file_path} ({ai_model})")
    
    # Get storage instances (will be injected via dependency injection)
    from side.storage import get_activity_ledger
    ledger = get_activity_ledger()
    
    # Log AI interaction to audit store
    audit.log_activity(
        project_id=project_id,
        tool="ai_assistant",
        action="code_generation",
        payload={
            "file_path": file_path,
            "ai_model": ai_model,
            "code_length": len(code),
            "timestamp": event.timestamp.isoformat(),
            "silent": False  # Important event, not silent
        }
    )
    
    # Check for anti-patterns (basic implementation)
    warnings = []
    
    # Security anti-patterns
    if "eval(" in code or "exec(" in code:
        warnings.append("⚠️ Security: Detected eval/exec usage")
    
    if "password" in code.lower() and ("=" in code or ":" in code):
        warnings.append("⚠️ Security: Potential hardcoded password")
    
    # Performance anti-patterns
    if code.count("for ") > 3 and "for " in code:
        warnings.append("⚠️ Performance: Multiple nested loops detected")
    
    # Log warnings if any
    if warnings:
        for warning in warnings:
            logger.warning(f"{file_path}: {warning}")
            ledger.log_activity(
                project_id=project_id,
                tool="pattern_detector",
                action="anti_pattern_warning",
                payload={
                    "file_path": file_path,
                    "warning": warning,
                    "ai_model": ai_model
                }
            )


# ============================================================================
# Friction Point 2: Git Commit
# ============================================================================

@event_bus.on(FrictionPoint.GIT_COMMIT, EventPriority.HIGH)
async def handle_git_commit(event: Event):
    """
    Handle git commit - log commit goal.
    
    Value:
    - Capture the "why" behind changes
    - Build decision history
    - Enable history auditing
    
    Processing time: < 100ms
    """
    payload = event.payload
    message = payload.get("message", "")
    files = payload.get("files", [])
    author = payload.get("author", "")
    project_id = payload.get("project_id", "unknown")
    commit_hash = payload.get("commit_hash", "")
    
    logger.info(f"Git commit detected: {message[:50]}... ({len(files)} files)")
    
    from side.storage import get_activity_ledger
    ledger = get_activity_ledger()
    
    # Extract commit goal from commit message
    intent_type = "feature"  # Default
    if any(keyword in message.lower() for keyword in ["fix", "bug", "error"]):
        intent_type = "bugfix"
    elif any(keyword in message.lower() for keyword in ["refactor", "cleanup", "improve"]):
        intent_type = "refactoring"
    elif any(keyword in message.lower() for keyword in ["test", "spec"]):
        intent_type = "testing"
    elif any(keyword in message.lower() for keyword in ["doc", "readme", "comment"]):
        intent_type = "documentation"
    
    # Log to ledger store with goal context
    ledger.log_activity(
        project_id=project_id,
        tool="git",
        action="commit",
        payload={
            "message": message,
            "files": files,
            "author": author,
            "commit_hash": commit_hash,
            "intent_type": intent_type,
            "file_count": len(files),
            "timestamp": event.timestamp.isoformat(),
            "silent": False  # Critical decisions are never silent
        }
    )


# ============================================================================
# Friction Point 3: AI Context Request
# ============================================================================

@event_bus.on(FrictionPoint.AI_CONTEXT_REQUEST, EventPriority.HIGH)
async def handle_ai_context_request(event: Event):
    """
    Handle AI context request - provide system knowledge.
    
    Value:
    - Inject project-specific context
    - Provide architectural knowledge
    - Share decision history
    
    Processing time: < 200ms (may load intelligence)
    """
    payload = event.payload
    query = payload.get("query", "")
    context_type = payload.get("context_type", "general")
    
    logger.info(f"AI context request: {context_type} - {query[:50]}...")
    
    if context_type == "architecture":
        # Strategy: Query CoreIndexer for real project graph
        try:
            from side.intel.handlers.topology import CoreIndexer
            from side.config import config
            
            indexer = CoreIndexer(
                project_path=config.PROJECT_ROOT,
                engine=engine,
                brain_path=config.BRAIN_PATH
            )
            project_graph = await indexer.get_topology()
            logger.info(f"AI: Injected DNA Context: {project_graph[:50]}...")
            # Real implementation: Append DNA to AI context payload
            payload["architectural_dna"] = project_graph
        except Exception as e:
            logger.error(f"Failed to inject DNA Context: {e}")
            
    elif context_type == "patterns":
        # Strategy: Load high-fidelity code patterns from WisdomStore
        logger.info("Injecting pattern context")
        
    elif context_type == "industry":
        # Strategy: Real-time intelligence capture via OperationalStore
        from side.storage.modules.transient import SessionCache
        cache = SessionCache(engine)
        intel_signals = ops.get_setting("external_intel_cache")
        logger.info(f"AI: Injected External Intel: {len(intel_signals or '')} chars")
        payload["external_intelligence"] = intel_signals


# ============================================================================
# Friction Point 4: Developer Debug
# ============================================================================

@event_bus.on(FrictionPoint.DEVELOPER_DEBUG, EventPriority.HIGH)
async def handle_developer_debug(event: Event):
    """
    Handle developer debug session - enable activity history.
    
    Value:
    - Show what happened before error
    - Link to related decisions
    - Suggest similar past fixes
    
    Processing time: < 300ms (history query)
    """
    payload = event.payload
    error_message = payload.get("error_message", "")
    file_path = payload.get("file_path", "")
    line_number = payload.get("line_number", 0)
    
    logger.info(f"Debug session started: {file_path}:{line_number}")
    
    from side.storage import get_activity_ledger
    ledger = get_activity_ledger()

    # Forensic time-travel
    # Query forensic store for file history
    history = audit.get_recent_activities(project_id, limit=5)
    
    # Suggest fixes (Placeholder for V1)
    # in V2 this would query a vector DB
    ledger.log_activity(
        project_id=project_id,
        tool="debugger",
        action="context_injection",
        payload={
            "file_path": file_path,
            "related_history_count": len(history),
            "suggestion": "Check recent commits for regressions."
        }
    )


# ============================================================================
# Friction Point 5: AI Mistake Repeat
# ============================================================================

@event_bus.on(FrictionPoint.AI_MISTAKE_REPEAT, EventPriority.CRITICAL)
async def handle_ai_mistake_repeat(event: Event):
    """
    Handle AI repeating a rejected pattern - inject rejection context.
    
    Value:
    - Prevent AI from repeating mistakes
    - Learn from rejections
    - Build anti-pattern database
    
    Processing time: < 50ms
    """
    payload = event.payload
    pattern = payload.get("pattern", "")
    previous_rejection = payload.get("previous_rejection", {})
    
    logger.warning(f"AI repeating rejected pattern: {pattern}")
    
    from side.storage import get_activity_ledger
    ledger = get_activity_ledger()

    # Inject rejection context
    ledger.log_activity(
        project_id="global",
        tool="pattern_detector",
        action="rejection_context_injected",
        payload={
            "pattern": pattern,
            "reason": previous_rejection.get("reason", "Unknown"),
            "advice": "Avoid this pattern based on previous rejection."
        }
    )
    
    # Learn from pattern
    # Add to anti-pattern database (Mock for V1)
    logger.info(f"Anti-pattern weight increased for: {pattern}")


# ============================================================================
# Friction Point 6: File Structure Change
# ============================================================================

@event_bus.on(FrictionPoint.FILE_STRUCTURE_CHANGE, EventPriority.NORMAL)
async def handle_file_structure_change(event: Event):
    """
    Handle file structure change - update project context.
    
    Value:
    - Keep project structure up-to-date
    - Detect architectural changes
    - Update AI context
    
    Processing time: < 50ms
    """
    payload = event.payload
    path = payload.get("path", "")
    event_type = payload.get("event_type", "")
    project_id = payload.get("project_id", "unknown")
    file_type = payload.get("file_type", "")
    
    logger.debug(f"File structure change: {event_type} - {path}")
    
    # Only log significant changes (not every file save)
    if event_type in {"created", "deleted"}:
        logger.info(f"Significant structure change: {event_type} - {path}")
        
        from side.storage import get_activity_ledger, get_transient_cache
        ledger = get_activity_ledger()
        cache = get_transient_cache()
        
        # Log structural change
        ledger.log_activity(
            project_id=project_id,
            tool="file_watcher",
            action=f"file_{event_type}",
            payload={
                "path": path,
                "file_type": file_type,
                "event_type": event_type,
                "timestamp": event.timestamp.isoformat(),
                "silent": True  # Structural changes are logged but silent
            }
        )
        
        # Invalidate relevant caches (project structure cache)
        # This would be implemented when we have cache invalidation logic


# ============================================================================
# Friction Point 7: Error Occurred
# ============================================================================

@event_bus.on(FrictionPoint.ERROR_OCCURRED, EventPriority.CRITICAL)
async def handle_error(event: Event):
    """
    Handle error - always log for forensics.
    
    Value:
    - Build error history
    - Detect patterns
    - Enable debugging
    
    Processing time: < 20ms
    """
    payload = event.payload
    error = payload.get("error", "")
    context = payload.get("context", {})
    project_id = payload.get("project_id", "unknown")
    file_path = payload.get("file_path", "")
    
    logger.error(f"Error occurred: {error}")
    
    from side.storage import get_audit_store
    audit = get_audit_store()
    
    # Always log errors to audit store (CRITICAL priority)
    audit.log_activity(
        project_id=project_id,
        tool="error_tracker",
        action="error_occurred",
        payload={
            "error": error,
            "file_path": file_path,
            "context": context,
            "timestamp": event.timestamp.isoformat(),
            "silent": False  # Errors are never silent
        }
    )
    
    # Check if this is a repeated error (simple pattern detection)
    recent_errors = audit.get_recent_activities(project_id, limit=10)
    error_count = sum(1 for act in recent_errors 
                     if act.action == "error_occurred" and error in str(act.payload))
    
    if error_count > 2:
        logger.warning(f"⚠️ Repeated error detected ({error_count} times): {error[:50]}...")
        audit.log_activity(
            project_id=project_id,
            tool="pattern_detector",
            action="repeated_error",
            payload={
                "error": error,
                "occurrence_count": error_count,
                "file_path": file_path
            }
        )


# ============================================================================
# Statistics and Monitoring
# ============================================================================

def get_handler_stats() -> Dict[str, Any]:
    """Get statistics for all friction-point handlers."""
    return {
        "event_bus_stats": event_bus.get_stats(),
        "lazy_intelligence_stats": lazy_intelligence.get_stats()
    }
