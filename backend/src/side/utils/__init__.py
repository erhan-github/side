"""
Sidelith Utility Package.
Shared infrastructure for error handling, performance monitoring, and cryptography.
"""

from .errors import handle_tool_errors, validate_arguments, validate_url
from .performance import PerformanceMonitor, get_monitor
from .retry import ResilientHTTPClient, retry_with_backoff
from .crypto import shield
from .ignore_store import get_ignore_store
from .event_optimizer import event_bus

__all__ = [
    # Error handling
    "handle_tool_errors",
    "validate_url",
    "validate_arguments",
    
    # Retry logic
    "retry_with_backoff",
    "ResilientHTTPClient",
    
    # Performance monitoring
    "PerformanceMonitor",
    "get_monitor",
    
    # Cryptography
    "shield",
    
    # Filesystem Utilities
    "get_ignore_store",
    
    # Event Management
    "event_bus",
]
