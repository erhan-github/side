"""
Error handling utilities for CSO.ai.

Provides consistent error handling across all tools.
"""

import logging
from functools import wraps
from typing import Any, Callable

import httpx

logger = logging.getLogger(__name__)


def handle_tool_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for handling errors in tool handlers.

    Provides user-friendly error messages for common failure scenarios.

    Usage:
        @handle_tool_errors
        async def _handle_read(arguments: dict[str, Any]) -> str:
            # Tool implementation
            pass
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> str:
        try:
            return await func(*args, **kwargs)

        except httpx.TimeoutException:
            logger.error(f"{func.__name__} timed out", exc_info=True)
            return (
                "⏱️ **Request Timed Out**\n\n"
                "The request took too long to complete. This usually means:\n"
                "• Network is slow or unavailable\n"
                "• External service is down\n\n"
                "**What to try:**\n"
                "• Check your internet connection\n"
                "• Try again in a few moments\n"
                "• Use cached results if available"
            )

        except (httpx.ConnectError, httpx.NetworkError) as e:
            logger.error(f"{func.__name__} network error: {e}", exc_info=True)
            return (
                "🌐 **Network Error**\n\n"
                f"Could not connect to external services: {str(e)}\n\n"
                "**What to try:**\n"
                "• Check your internet connection\n"
                "• Verify firewall/proxy settings\n"
                "• Try again in a few moments"
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"{func.__name__} HTTP error: {e}", exc_info=True)
            status = e.response.status_code

            if status == 429:
                return (
                    "🚦 **Rate Limited**\n\n"
                    "Too many requests to external services.\n\n"
                    "**What to try:**\n"
                    "• Wait a few minutes and try again\n"
                    "• Use cached results if available"
                )
            elif 500 <= status < 600:
                return (
                    "🔧 **Service Unavailable**\n\n"
                    f"External service returned error {status}.\n\n"
                    "**What to try:**\n"
                    "• Try again in a few moments\n"
                    "• The service may be experiencing issues"
                )
            else:
                return (
                    f"❌ **HTTP Error {status}**\n\n"
                    f"Request failed: {str(e)}\n\n"
                    "Please try again or check the URL."
                )

        except ValueError as e:
            logger.error(f"{func.__name__} validation error: {e}", exc_info=True)
            return (
                "⚠️ **Invalid Input**\n\n"
                f"{str(e)}\n\n"
                "Please check your input and try again."
            )

        except KeyError as e:
            logger.error(f"{func.__name__} missing data: {e}", exc_info=True)
            return (
                "❌ **Missing Data**\n\n"
                f"Required data not found: {str(e)}\n\n"
                "This might be a temporary issue. Please try again."
            )

        except Exception as e:
            # Log with full traceback for debugging
            import traceback
            logger.error(
                f"{func.__name__} unexpected error: {e}\\n"
                f"Traceback:\\n{traceback.format_exc()}",
                exc_info=True
            )
            return (
                "❌ **Unexpected Error**\\n\\n"
                f"Something went wrong: {str(e)}\\n\\n"
                "**What to try:**\\n"
                "• Try again\\n"
                "• Check the logs for details\\n"
                "• Report this issue if it persists"
            )

    return wrapper


def validate_url(url: str) -> str:
    """
    Validate and normalize a URL.

    Args:
        url: URL to validate

    Returns:
        Normalized URL

    Raises:
        ValueError: If URL is invalid
    """
    if not url:
        raise ValueError("URL cannot be empty")

    url = url.strip()

    # Add https:// if no scheme
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    # Basic validation
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid URL scheme: {url}")

    if len(url) > 2048:
        raise ValueError("URL is too long (max 2048 characters)")

    # Check for common issues
    if " " in url:
        raise ValueError("URL contains spaces")

    return url


def validate_arguments(
    arguments: dict[str, Any],
    required: list[str] | None = None,
    optional: list[str] | None = None,
) -> None:
    """
    Validate tool arguments.

    Args:
        arguments: Arguments to validate
        required: List of required argument names
        optional: List of optional argument names

    Raises:
        ValueError: If validation fails
    """
    required = required or []
    optional = optional or []

    # Check required arguments
    for arg in required:
        if arg not in arguments or arguments[arg] is None:
            raise ValueError(f"Missing required argument: {arg}")

    # Check for unknown arguments
    all_args = set(required + optional)
    for arg in arguments:
        if arg not in all_args:
            logger.warning(f"Unknown argument: {arg}")
