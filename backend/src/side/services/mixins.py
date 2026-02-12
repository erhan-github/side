import asyncio
import logging
from typing import Any, Dict, List, Coroutine

logger = logging.getLogger(__name__)

class ServiceLifecycleMixin:
    """
    Mixin to provide standardized lifecycle management for background services.
    Uniformity in task tracking and health monitoring.
    """
    def __init__(self):
        self._tasks: Dict[str, asyncio.Task] = {}
        self._status: Dict[str, Any] = {"services": {}}

    async def launch_service(self, name: str, component_or_func: Any, *args, **kwargs) -> asyncio.Task:
        """Launches a service and tracks its lifecycle."""
        logger.info(f"Launching service: {name}...")
        
        from side.services.base import LifecycleComponent
        
        if isinstance(component_or_func, LifecycleComponent):
            # Lifecycle Pattern
            await component_or_func.setup()
            task = asyncio.create_task(component_or_func.start())
            component_or_func.status = "running"
        elif asyncio.iscoroutine(component_or_func):
            task = asyncio.create_task(component_or_func)
        else:
            task = asyncio.create_task(component_or_func(*args, **kwargs))
            
        self._tasks[name] = task
        self._status["services"][name] = {
            "status": "running",
            "healthy": True,
            "instance": component_or_func if isinstance(component_or_func, LifecycleComponent) else None
        }
        
        return task

    async def kill_service(self, name: str):
        """Standardized service termination."""
        if name in self._tasks:
            task = self._tasks[name]
            if not task.done():
                logger.info(f"Killing service: {name}...")
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            del self._tasks[name]
            if name in self._status["services"]:
                self._status["services"][name]["status"] = "stopped"

    async def kill_all_services(self):
        """Shutdown all tracked services."""
        for name in list(self._tasks.keys()):
            await self.kill_service(name)
