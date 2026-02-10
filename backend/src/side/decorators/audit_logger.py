"""
ForensicLogger: Enterprise-grade telemetry decorator for MCP tools.

Captures:
- Execution duration
- Success/failure status
- Token consumption
- Error details with stack traces

Reports to:
- Structured JSON logs (Railway)
- Sentry (Exception tracking)
- PostHog (Product analytics)
"""

import functools
import time
import traceback
import os
from typing import Any, Callable, Optional
from side.logging_config import get_logger

logger = get_logger("audit")

# Import telemetry clients
try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

try:
    from posthog import Posthog
    ph_api_key = os.getenv("POSTHOG_API_KEY")
    ph_host = os.getenv("POSTHOG_HOST", "https://app.posthog.com")
    ph_client = Posthog(ph_api_key, host=ph_host) if ph_api_key else None
except ImportError:
    ph_client = None


def audit_log(
    event_name: str,
    capture_tokens: bool = False,
    critical: bool = False
):
    """
    Decorator for comprehensive audit logging of MCP tools. calls.
    
    Args:
        event_name: Unique identifier for this operation (e.g., "scan_project", "audit_file")
        capture_tokens: If True, attempts to extract token count from result
        critical: If True, logs at ERROR level on failure and triggers Sentry alert
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            trace_id = os.getenv("SIDE_TRACE_ID", "no-trace")
            user_id = os.getenv("SIDE_USER_ID", "anonymous")
            project_id = os.getenv("SIDE_PROJECT_ID", "unknown")
            
            # Pre-execution breadcrumb
            log_context = {
                "event": f"tool.{event_name}.start",
                "trace_id": trace_id,
                "user_id": user_id,
                "project_id": project_id,
                "tool": func.__name__,
            }
            logger.info(f"[{event_name}] Starting...", extra={"data": log_context})
            
            if SENTRY_AVAILABLE:
                sentry_sdk.add_breadcrumb(
                    category="tool",
                    message=f"Starting {event_name}",
                    level="info",
                    data=log_context
                )
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Extract tokens if applicable
                tokens_used = 0
                if capture_tokens and isinstance(result, dict):
                    tokens_used = result.get("tokens_used", 0)
                
                # Success log
                success_context = {
                    **log_context,
                    "event": f"tool.{event_name}.success",
                    "duration_ms": duration_ms,
                    "tokens_used": tokens_used,
                    "status": "success"
                }
                logger.info(f"[{event_name}] Completed ({duration_ms}ms)", extra={"data": success_context})
                
                # PostHog analytics
                if ph_client:
                    ph_client.capture(
                        user_id,
                        f"side_tool_{event_name}_success",
                        {
                            "app": "sidelith",
                            "duration_ms": duration_ms,
                            "tokens_used": tokens_used,
                            "tool": func.__name__,
                            "project_id": project_id,
                        }
                    )
                
                return result
                
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                error_details = {
                    "name": type(e).__name__,
                    "message": str(e),
                    "stack": traceback.format_exc()
                }
                
                # Error log
                error_context = {
                    **log_context,
                    "event": f"tool.{event_name}.failure",
                    "duration_ms": duration_ms,
                    "status": "failure",
                    "error": error_details
                }
                
                log_level = logger.error if critical else logger.warning
                log_level(f"[{event_name}] Failed: {e}", extra={"data": error_context})
                
                # Sentry exception capture
                if SENTRY_AVAILABLE:
                    sentry_sdk.set_context("audit", error_context)
                    sentry_sdk.capture_exception(e)
                
                # PostHog failure event
                if ph_client:
                    ph_client.capture(
                        user_id,
                        f"side_tool_{event_name}_failure",
                        {
                            "app": "sidelith",
                            "duration_ms": duration_ms,
                            "tool": func.__name__,
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                        }
                    )
                
                raise
                
        return wrapper
    return decorator
