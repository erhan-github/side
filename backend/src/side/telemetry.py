import os
import time
import functools
from typing import Any, Callable
from side.logging_config import get_logger
import sentry_sdk

logger = get_logger(__name__)

# Mock Posthog if not configured
class MockPosthog:
    def capture(self, *args, **kwargs):
        pass
    def identify(self, *args, **kwargs):
        pass

ph_client = MockPosthog()

def init_telemetry():
    """
    Initialize all telemetry providers (Sentry + PostHog).
    Should be called at server startup.
    """
    # 1. Initialize Sentry
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        try:
            sentry_sdk.init(
                dsn=sentry_dsn,
                # Set traces_sample_rate to 1.0 to capture 100%
                # of transactions for performance monitoring.
                traces_sample_rate=1.0,
                # Set profiles_sample_rate to 1.0 to profile 100%
                # of sampled transactions.
                # We recommend adjusting this value in production.
                profiles_sample_rate=1.0,
                environment=os.getenv("RAILWAY_ENVIRONMENT_NAME", "local"),
            )
            logger.info(f"✅ Sentry initialized (env: {os.getenv('RAILWAY_ENVIRONMENT_NAME', 'local')})")
        except Exception as e:
            logger.error(f"❌ Sentry initialization failed: {e}")
    else:
        logger.warning("⚠️ SENTRY_DSN not set. Error tracking disabled.")

    # 2. Initialize PostHog
    global ph_client
    try:
        from posthog import Posthog
        api_key = os.getenv("POSTHOG_API_KEY")
        host = os.getenv("POSTHOG_HOST", "https://app.posthog.com")
        if api_key:
            ph_client = Posthog(api_key, host=host)
            logger.info("✅ PostHog initialized")
        else:
             logger.warning("⚠️ POSTHOG_API_KEY not set. Analytics disabled.")
    except ImportError:
        logger.warning("⚠️ PostHog library not installed.")
    except Exception as e:
        logger.error(f"❌ PostHog initialization failed: {e}")


def telemetry(event_name: str):
    """
    Decorator to track tool execution time, success/failure, AND errors in Sentry.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            # Try to extract project_id or user_id for context
            context_id = os.getenv("SIDE_PROJECT_ID", "anonymous")
            
            # Start Sentry Transaction for this tool
            with sentry_sdk.start_transaction(op="tool", name=event_name):
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    ph_client.capture(
                        context_id,
                        f"side_tool_{event_name}_success",
                        {
                            "app": "sidelith",
                            "duration_sec": duration,
                            "tool": func.__name__,
                            "status": "success"
                        }
                    )
                    return result

                except Exception as e:
                    duration = time.time() - start_time
                    
                    # 1. Log to PostHog
                    ph_client.capture(
                        context_id,
                        f"side_tool_{event_name}_failure",
                        {
                            "app": "sidelith",
                            "duration_sec": duration,
                            "tool": func.__name__,
                            "status": "failure",
                            "error": str(e)
                        }
                    )

                    # 2. Capture in Sentry
                    sentry_sdk.capture_exception(e)
                    
                    # 3. Log locally
                    logger.error(f"Tool {event_name} failed: {e}")

                    # Re-raise so the MCP client gets the error
                    raise e
        return wrapper
    return decorator
