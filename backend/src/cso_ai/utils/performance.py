"""
Performance monitoring utilities for CSO.ai.

Tracks timing, LLM usage, and cache performance.
"""

import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Generator

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for a single operation."""

    operation: str
    start_time: float
    end_time: float | None = None
    duration_ms: float | None = None
    cache_hit: bool = False
    llm_calls: int = 0
    http_requests: int = 0
    errors: list[str] = field(default_factory=list)

    def finish(self) -> None:
        """Mark operation as finished and calculate duration."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation": self.operation,
            "duration_ms": self.duration_ms,
            "cache_hit": self.cache_hit,
            "llm_calls": self.llm_calls,
            "http_requests": self.http_requests,
            "errors": self.errors,
            "timestamp": datetime.fromtimestamp(self.start_time, tz=timezone.utc).isoformat(),
        }


class PerformanceMonitor:
    """
    Monitor performance across operations.

    Usage:
        monitor = PerformanceMonitor()

        with monitor.track("fetch_articles") as metrics:
            # Do work
            metrics.http_requests += 1
            metrics.cache_hit = True
    """

    def __init__(self):
        """Initialize performance monitor."""
        self._metrics: list[PerformanceMetrics] = []
        self._current_operation: PerformanceMetrics | None = None

    @contextmanager
    def track(self, operation: str) -> Generator[PerformanceMetrics, None, None]:
        """
        Track performance of an operation.

        Args:
            operation: Name of the operation

        Yields:
            PerformanceMetrics object to update during operation
        """
        metrics = PerformanceMetrics(
            operation=operation,
            start_time=time.time(),
        )

        self._current_operation = metrics

        try:
            yield metrics
        except Exception as e:
            metrics.errors.append(str(e))
            raise
        finally:
            metrics.finish()
            self._metrics.append(metrics)
            self._current_operation = None

            # Log performance
            if metrics.duration_ms:
                logger.info(
                    f"{operation}: {metrics.duration_ms:.1f}ms "
                    f"(cache_hit={metrics.cache_hit}, "
                    f"llm_calls={metrics.llm_calls}, "
                    f"http_requests={metrics.http_requests})"
                )

    def get_metrics(self, operation: str | None = None) -> list[PerformanceMetrics]:
        """
        Get recorded metrics.

        Args:
            operation: Filter by operation name (optional)

        Returns:
            List of performance metrics
        """
        if operation:
            return [m for m in self._metrics if m.operation == operation]
        return self._metrics.copy()

    def get_summary(self) -> dict[str, Any]:
        """
        Get performance summary.

        Returns:
            Summary statistics
        """
        if not self._metrics:
            return {
                "total_operations": 0,
                "total_duration_ms": 0,
                "avg_duration_ms": 0,
                "cache_hit_rate": 0,
                "total_llm_calls": 0,
                "total_http_requests": 0,
                "total_errors": 0,
            }

        total_duration = sum(m.duration_ms or 0 for m in self._metrics)
        cache_hits = sum(1 for m in self._metrics if m.cache_hit)
        total_llm = sum(m.llm_calls for m in self._metrics)
        total_http = sum(m.http_requests for m in self._metrics)
        total_errors = sum(len(m.errors) for m in self._metrics)

        return {
            "total_operations": len(self._metrics),
            "total_duration_ms": total_duration,
            "avg_duration_ms": total_duration / len(self._metrics),
            "cache_hit_rate": cache_hits / len(self._metrics) if self._metrics else 0,
            "total_llm_calls": total_llm,
            "total_http_requests": total_http,
            "total_errors": total_errors,
        }

    def reset(self) -> None:
        """Clear all metrics."""
        self._metrics.clear()
        self._current_operation = None


# Global performance monitor
_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get the global performance monitor."""
    return _monitor
