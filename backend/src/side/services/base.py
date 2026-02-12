from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

class LifecycleComponent(ABC):
    """
    Standard interface for all Sidelith background services.
    Ensures predictable boot, run, and shutdown sequences.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.status = "initialized"
        self.healthy = True
        self.metadata: Dict[str, Any] = {}

    @abstractmethod
    async def setup(self) -> None:
        """Performed once before start(). Use for DB connections, etc."""
        pass

    @abstractmethod
    async def start(self) -> None:
        """The main execution loop or entry point of the service."""
        pass

    @abstractmethod
    async def teardown(self) -> None:
        """Graceful cleanup before stopping."""
        pass

    def get_diagnostics(self) -> Dict[str, Any]:
        """Returns health and performance metrics for the HUD."""
        return {
            "name": self.name,
            "status": self.status,
            "healthy": self.healthy,
            **self.metadata
        }
