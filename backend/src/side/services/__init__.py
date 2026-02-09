"""Services package for background intelligence."""

from side.services.file_watcher import OptimizedFileWatcherService
from side.services.service_manager import ServiceManager

__all__ = [
    "OptimizedFileWatcherService",
    "ServiceManager",
]
