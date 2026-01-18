"""
Context tracker service for monitoring user's work patterns.

Analyzes file changes and git activity to understand what user is working on.
"""

import asyncio
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cso_ai.storage.simple_db import SimplifiedDatabase

logger = logging.getLogger(__name__)


class ContextTracker:
    """
    Tracks user's work context to provide relevant recommendations.

    Analyzes:
    - Recently edited files
    - Git commits
    - Current branch
    - Focus areas (auth, API, frontend, etc.)
    """

    def __init__(self, db: SimplifiedDatabase):
        """
        Initialize context tracker.

        Args:
            db: Database instance
        """
        self.db = db

        # Focus area patterns
        self._focus_patterns = {
            "authentication": ["auth", "login", "signup", "session", "token", "jwt"],
            "api": ["api", "endpoint", "route", "controller", "handler"],
            "frontend": ["component", "ui", "view", "page", "template"],
            "database": ["model", "schema", "migration", "query", "db"],
            "testing": ["test", "spec", "mock", "fixture"],
            "infrastructure": ["docker", "k8s", "deploy", "ci", "cd", "config"],
            "security": ["security", "crypto", "hash", "encrypt", "sanitize"],
            "performance": ["cache", "optimize", "perf", "benchmark"],
        }

    async def update_context(self, project_path: str | Path, changed_files: set[Path]) -> None:
        """
        Update work context based on file changes.

        Args:
            project_path: Path to project
            changed_files: Set of changed file paths
        """
        project_path = Path(project_path).resolve()

        try:
            # Get recent files (relative paths)
            recent_files = [
                str(f.relative_to(project_path))
                for f in list(changed_files)[:10]
                if f.is_relative_to(project_path)
            ]

            # Get recent commits
            recent_commits = self._get_recent_commits(project_path, limit=5)

            # Get current branch
            current_branch = self._get_current_branch(project_path)

            # Detect focus area
            focus_area, confidence = self._detect_focus_area(recent_files, recent_commits)

            # Save to database
            self.db.save_work_context(
                project_path=str(project_path),
                focus_area=focus_area,
                recent_files=recent_files,
                recent_commits=recent_commits,
                current_branch=current_branch,
                confidence=confidence,
            )

            logger.info(
                f"Updated context: {focus_area} (confidence: {confidence:.2f})"
            )

        except Exception as e:
            logger.error(f"Error updating context: {e}", exc_info=True)

    def _get_recent_commits(self, project_path: Path, limit: int = 5) -> list[dict[str, Any]]:
        """Get recent git commits."""
        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    f"-{limit}",
                    "--pretty=format:%H|%an|%s|%ct",
                ],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return []

            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("|")
                if len(parts) == 4:
                    commits.append({
                        "hash": parts[0][:8],
                        "author": parts[1],
                        "message": parts[2],
                        "timestamp": int(parts[3]),
                    })

            return commits

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def _get_current_branch(self, project_path: Path) -> str | None:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=2,
            )

            if result.returncode == 0:
                return result.stdout.strip() or None

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return None

    def _detect_focus_area(
        self,
        recent_files: list[str],
        recent_commits: list[dict[str, Any]],
    ) -> tuple[str, float]:
        """
        Detect current focus area from files and commits.

        Returns:
            Tuple of (focus_area, confidence)
        """
        # Combine files and commit messages for analysis
        text = " ".join(recent_files).lower()
        text += " " + " ".join(c["message"] for c in recent_commits).lower()

        # Score each focus area
        scores = {}
        for area, keywords in self._focus_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[area] = score

        if not scores:
            return "general development", 0.3

        # Get top focus area
        top_area = max(scores, key=scores.get)
        max_score = scores[top_area]

        # Calculate confidence (0-1)
        # Higher if one area dominates, lower if multiple areas
        total_score = sum(scores.values())
        confidence = min(0.95, max_score / total_score if total_score > 0 else 0.3)

        return top_area, confidence

    def get_current_context(self, project_path: str | Path) -> dict[str, Any] | None:
        """
        Get current work context for project.

        Args:
            project_path: Path to project

        Returns:
            Context dict or None if not found
        """
        return self.db.get_latest_work_context(str(Path(project_path).resolve()))
