"""
Sidelith Intelligence Scavengers.
Specialized components for extracting context from platform-specific environments (Docker, Mobile).
"""

from .docker import DockerScavenger
from .mobile import AndroidScavenger, IOSScavenger

__all__ = [
    "DockerScavenger",
    "AndroidScavenger",
    "IOSScavenger",
]
