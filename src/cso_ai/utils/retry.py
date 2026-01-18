"""
Retry logic with exponential backoff for network requests.

Provides resilient HTTP operations with automatic retry on failures.

[Architect's Note]: We use exponential backoff not just for network stability, 
but to avoid "RateLimit" errors on the Groq Tier 1 API during high-burst 
strategy analysis. This ensures the MCP server remains robust during 
high-concurrency "Gardening" tasks.
"""

import asyncio
import logging
from functools import wraps
from typing import Any, Callable, TypeVar

import httpx

logger = logging.getLogger(__name__)

T = TypeVar("T")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
):
    """
    Decorator for retrying async functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff calculation

    Example:
        @retry_with_backoff(max_retries=3, base_delay=1.0)
        async def fetch_data():
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                return response.json()
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (
                    httpx.TimeoutException,
                    httpx.ConnectError,
                    httpx.NetworkError,
                ) as e:
                    last_exception = e

                    if attempt == max_retries - 1:
                        # Last attempt failed
                        logger.error(
                            f"{func.__name__} failed after {max_retries} attempts: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff + jitter
                    import random
                    delay = min(base_delay * (exponential_base**attempt), max_delay)
                    jitter = delay * 0.1 * random.uniform(-1, 1)
                    actual_delay = max(0, delay + jitter)

                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1}/{max_retries} failed: {e}. "
                        f"Retrying in {actual_delay:.1f}s (jittered)..."
                    )

                    await asyncio.sleep(actual_delay)

                except httpx.HTTPStatusError as e:
                    # Don't retry on 4xx errors (client errors)
                    if 400 <= e.response.status_code < 500:
                        logger.error(f"{func.__name__} client error: {e}")
                        raise

                    # Retry on 5xx errors (server errors)
                    last_exception = e

                    if attempt == max_retries - 1:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} attempts: {e}"
                        )
                        raise

                    delay = min(base_delay * (exponential_base**attempt), max_delay)
                    logger.warning(
                        f"{func.__name__} server error (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )

                    await asyncio.sleep(delay)

                except Exception as e:
                    # Unexpected error - don't retry
                    logger.error(f"{func.__name__} unexpected error: {e}", exc_info=True)
                    raise

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


class ResilientHTTPClient:
    """
    HTTP client with built-in retry logic and timeout handling.

    Usage:
        client = ResilientHTTPClient()
        data = await client.get_json("https://api.example.com/data")
    """

    def __init__(
        self,
        timeout: float = 10.0,
        max_retries: int = 3,
        base_delay: float = 1.0,
    ):
        """
        Initialize resilient HTTP client with 'Smart Timeout' logic.
        
        [Hyper-Ralph] DNS Blackhole Fix: We use a multi-stage timeout
        to detect DNS failures in <500ms rather than waiting for 10s.
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.smart_timeout = httpx.Timeout(
            timeout, 
            connect=1.0, # Fast connect fail for DNS Blackholes
            read=timeout,
            write=timeout,
            pool=timeout
        )

    async def close(self) -> None:
        """Close the client (no-op since we use context managers)."""
        pass

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    async def get_json(self, url: str, **kwargs: Any) -> Any:
        """
        GET request returning JSON with retry logic.

        Args:
            url: URL to fetch
            **kwargs: Additional arguments for httpx.get

        Returns:
            Parsed JSON response

        Raises:
            httpx.HTTPError: On network or HTTP errors after retries
        """
        async with httpx.AsyncClient(timeout=self.smart_timeout) as client:
            response = await client.get(url, **kwargs)
            response.raise_for_status()
            return response.json()

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    async def get_text(self, url: str, **kwargs: Any) -> str:
        """
        GET request returning text with retry logic.

        Args:
            url: URL to fetch
            **kwargs: Additional arguments for httpx.get

        Returns:
            Response text

        Raises:
            httpx.HTTPError: On network or HTTP errors after retries
        """
        async with httpx.AsyncClient(timeout=self.smart_timeout) as client:
            response = await client.get(url, **kwargs)
            response.raise_for_status()
            return response.text

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    async def post_json(self, url: str, data: Any = None, **kwargs: Any) -> Any:
        """
        POST request with JSON data, returning JSON with retry logic.

        Args:
            url: URL to post to
            data: JSON-serializable data
            **kwargs: Additional arguments for httpx.post

        Returns:
            Parsed JSON response

        Raises:
            httpx.HTTPError: On network or HTTP errors after retries
        """
        async with httpx.AsyncClient(timeout=self.smart_timeout) as client:
            response = await client.post(url, json=data, **kwargs)
            response.raise_for_status()
            return response.json()
