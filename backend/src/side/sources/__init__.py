"""
Side Content Sources.

External sources for market intelligence:
- Hacker News
- Lobste.rs
- GitHub Trending
- ArXiv (future)
"""

from side.sources.hackernews import HackerNewsSource
from side.sources.lobsters import LobstersSource
from side.sources.github import GitHubSource

__all__ = ["HackerNewsSource", "LobstersSource", "GitHubSource"]
