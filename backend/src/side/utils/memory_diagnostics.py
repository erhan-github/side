"""
Memory Diagnostics Utility

Provides centralized memory tracking and diagnostics for the language server.
Tracks process memory usage, detects leaks, and formats reports.
"""

import logging
import os
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Deque, Optional

try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger(__name__)


@dataclass
class MemorySample:
    """Single memory measurement."""
    timestamp: float
    rss_bytes: int  # Resident Set Size
    vms_bytes: int  # Virtual Memory Size
    percent: float  # Memory usage as percentage of total


class MemoryDiagnostics:
    """
    Tracks memory usage over time and detects potential leaks.
    
    Features:
    - Process memory tracking (RSS, VMS, percent)
    - Rolling window of samples
    - Growth rate calculation
    - Leak detection
    - Human-readable reporting
    """
    
    def __init__(self, window_size: int = 100, leak_threshold_mb_per_hour: float = 10.0):
        """
        Initialize memory diagnostics.
        
        Args:
            window_size: Number of samples to keep in rolling window
            leak_threshold_mb_per_hour: MB/hour growth rate to trigger leak warning
        """
        self.window_size = window_size
        self.leak_threshold = leak_threshold_mb_per_hour
        self.samples: Deque[MemorySample] = deque(maxlen=window_size)
        self.process = psutil.Process(os.getpid()) if psutil else None
        
        if not psutil:
            logger.warning("psutil not available - memory diagnostics disabled")
    
    def sample(self) -> Optional[MemorySample]:
        """Take a memory sample."""
        if not self.process:
            return None
        
        try:
            mem_info = self.process.memory_info()
            mem_percent = self.process.memory_percent()
            
            sample = MemorySample(
                timestamp=time.time(),
                rss_bytes=mem_info.rss,
                vms_bytes=mem_info.vms,
                percent=mem_percent
            )
            
            self.samples.append(sample)
            return sample
            
        except Exception as e:
            logger.error(f"Failed to sample memory: {e}")
            return None
    
    def get_current_memory(self) -> dict:
        """Get current memory usage."""
        sample = self.sample()
        if not sample:
            return {}
        
        return {
            "rss_mb": sample.rss_bytes / (1024 * 1024),
            "vms_mb": sample.vms_bytes / (1024 * 1024),
            "percent": sample.percent,
            "rss_human": self._format_bytes(sample.rss_bytes),
            "vms_human": self._format_bytes(sample.vms_bytes)
        }
    
    def get_growth_rate(self) -> Optional[float]:
        """
        Calculate memory growth rate in MB/hour.
        
        Returns:
            Growth rate in MB/hour, or None if insufficient data
        """
        if len(self.samples) < 2:
            return None
        
        first = self.samples[0]
        last = self.samples[-1]
        
        time_delta_hours = (last.timestamp - first.timestamp) / 3600
        if time_delta_hours < 0.01:  # Less than 36 seconds
            return None
        
        memory_delta_mb = (last.rss_bytes - first.rss_bytes) / (1024 * 1024)
        growth_rate = memory_delta_mb / time_delta_hours
        
        return growth_rate
    
    def detect_leak(self) -> tuple[bool, Optional[float]]:
        """
        Detect potential memory leak.
        
        Returns:
            (is_leaking, growth_rate_mb_per_hour)
        """
        growth_rate = self.get_growth_rate()
        if growth_rate is None:
            return False, None
        
        is_leaking = growth_rate > self.leak_threshold
        return is_leaking, growth_rate
    
    def get_report(self) -> str:
        """Generate human-readable memory report."""
        if not self.samples:
            return "[MEMORY DIAGNOSTICS] No data available"
        
        current = self.get_current_memory()
        growth_rate = self.get_growth_rate()
        is_leaking, _ = self.detect_leak()
        
        lines = [
            "[MEMORY DIAGNOSTICS]",
            f"  Process Memory: {current['rss_human']} (RSS), {current['vms_human']} (VMS)",
            f"  Memory Percent: {current['percent']:.1f}%"
        ]
        
        if growth_rate is not None:
            lines.append(f"  Memory Growth: {growth_rate:+.1f} MB/hour")
        
        if is_leaking:
            lines.append(f"  ⚠️  WARNING: Potential memory leak detected!")
        else:
            lines.append(f"  Status: ✅ HEALTHY")
        
        lines.append(f"  Samples: {len(self.samples)}/{self.window_size}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_bytes(bytes_value: int) -> str:
        """Format bytes as human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"


# Global instance for easy access
_global_diagnostics: Optional[MemoryDiagnostics] = None


def get_diagnostics() -> MemoryDiagnostics:
    """Get global memory diagnostics instance."""
    global _global_diagnostics
    if _global_diagnostics is None:
        _global_diagnostics = MemoryDiagnostics()
    return _global_diagnostics


def log_memory_report():
    """Log current memory report."""
    diag = get_diagnostics()
    report = diag.get_report()
    logger.info(report)
