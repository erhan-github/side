"""
Sidelith Intelligence Sources.
Adapters for external signals (Cursor, Jira, Linear) into the project context.
"""

from .base import IntentSource
from .antigravity import AntigravitySource
from .cursor import CursorSource
from .jira_linear import JiraSource, LinearSource

__all__ = [
    "IntentSource",
    "AntigravitySource",
    "CursorSource",
    "JiraSource",
    "LinearSource",
]
