"""
CSO.ai Listener - The observation layer.

The Listener continuously observes:
- Codebase changes (files, commits, PRs)
- Documents (README, docs, notes)
- Database (schema, data patterns)
- Team signals (who, what, when)

It feeds observations to the Understander.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Observation:
    """A single observation from any source."""

    source: str  # codebase, document, database, git, team
    type: str  # file_change, commit, schema_change, etc.
    data: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    importance: float = 0.5  # 0-1 scale

    def to_dict(self) -> dict[str, Any]:
        """Serialize observation."""
        return {
            "source": self.source,
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance,
        }


class Listener:
    """
    The observation layer of CSO.ai.

    Responsibilities:
    - Watch for changes in the codebase
    - Monitor document updates
    - Track database evolution
    - Observe team patterns

    The Listener doesn't interpret - it just observes and records.
    """

    def __init__(self) -> None:
        """Initialize the Listener."""
        self.observations: list[Observation] = []
        self._watched_paths: set[Path] = set()

    async def observe_codebase(self, path: str | Path) -> list[Observation]:
        """
        Observe a codebase and generate observations.

        Args:
            path: Root path of the codebase

        Returns:
            List of observations about the codebase
        """
        root = Path(path).resolve()
        observations = []

        # Observe file structure
        observations.append(
            Observation(
                source="codebase",
                type="structure_scan",
                data={"root": str(root), "scanned_at": datetime.utcnow().isoformat()},
                importance=0.8,
            )
        )

        # TODO: Add more observation types
        # - File type distribution
        # - Dependency files detected
        # - Config files found
        # - Git history signals

        self.observations.extend(observations)
        self._watched_paths.add(root)

        return observations

    async def observe_document(self, path: str | Path) -> Observation | None:
        """
        Observe a specific document.

        Args:
            path: Path to the document

        Returns:
            Observation about the document
        """
        doc_path = Path(path)
        if not doc_path.exists():
            return None

        try:
            content = doc_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None

        observation = Observation(
            source="document",
            type="document_read",
            data={
                "path": str(doc_path),
                "name": doc_path.name,
                "size": len(content),
                "content_preview": content[:1000],
            },
            importance=0.7,
        )

        self.observations.append(observation)
        return observation

    async def observe_git(self, path: str | Path) -> list[Observation]:
        """
        Observe git history and signals.

        Args:
            path: Path to git repository

        Returns:
            List of git-related observations
        """
        git_dir = Path(path) / ".git"
        observations = []

        if git_dir.exists():
            observations.append(
                Observation(
                    source="git",
                    type="repo_detected",
                    data={"path": str(path), "has_git": True},
                    importance=0.6,
                )
            )
            # TODO: Add git history analysis
            # - Recent commits
            # - Branch patterns
            # - Contributor activity
            # - Commit frequency

        self.observations.extend(observations)
        return observations

    def get_recent_observations(
        self,
        limit: int = 50,
        source: str | None = None,
    ) -> list[Observation]:
        """
        Get recent observations, optionally filtered by source.

        Args:
            limit: Maximum observations to return
            source: Filter by source type

        Returns:
            List of recent observations
        """
        filtered = self.observations
        if source:
            filtered = [o for o in filtered if o.source == source]

        # Sort by timestamp descending
        filtered.sort(key=lambda o: o.timestamp, reverse=True)

        return filtered[:limit]

    def clear_observations(self) -> None:
        """Clear all observations."""
        self.observations.clear()
