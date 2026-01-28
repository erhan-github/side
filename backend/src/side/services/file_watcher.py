"""
File watcher for monitoring codebase changes.

Watches for file changes, git commits, and triggers knowledge sync.
"""

import asyncio
import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Set

logger = logging.getLogger(__name__)


class FileWatcher:
    """
    Monitors codebase for changes and triggers updates.

    Features:
    - Watches file system for changes
    - Detects git commits
    - Debounces rapid changes
    - Triggers callbacks on change events
    """

    def __init__(
        self,
        project_path: str | Path,
        on_change: Callable[[Set[Path]], None] | None = None,
        debounce_seconds: float = 2.0,
    ):
        """
        Initialize file watcher.

        Args:
            project_path: Path to project to watch
            on_change: Callback when files change (receives set of changed paths)
            debounce_seconds: Wait time before triggering callback (default 2s)
        """
        self.project_path = Path(project_path).resolve()
        self.on_change = on_change
        self.debounce_seconds = debounce_seconds

        self._running = False
        self._task: asyncio.Task | None = None
        self._changed_files: Set[Path] = set()
        self._last_commit_hash: str | None = None
        self._debounce_task: asyncio.Task | None = None

        self._last_commit_hash: str | None = None
        self._debounce_task: asyncio.Task | None = None
        
        # Use Sovereign Ignore Service
        from side.services.ignore import SovereignIgnore
        self._ignore_service = SovereignIgnore(Path(root_path))


    async def start(self) -> None:
        """Start watching for changes."""
        if self._running:
            logger.warning("File watcher already running")
            return

        self._running = True
        self._last_commit_hash = self._get_current_commit()

        # Start monitoring task
        self._task = asyncio.create_task(self._watch_loop())

        logger.info(f"File watcher started for {self.project_path}")

    async def stop(self) -> None:
        """Stop watching."""
        if not self._running:
            return

        self._running = False

        # Cancel tasks
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        if self._debounce_task:
            self._debounce_task.cancel()
            try:
                await self._debounce_task
            except asyncio.CancelledError:
                pass

        logger.info("File watcher stopped")

    async def _watch_loop(self) -> None:
        """Main watching loop."""
        last_scan = {}  # path -> (mtime, size)

        while self._running:
            try:
                # Check for git commits
                current_commit = self._get_current_commit()
                if current_commit and current_commit != self._last_commit_hash:
                    logger.info(f"New commit detected: {current_commit[:8]}")
                    self._last_commit_hash = current_commit
                    # Trigger full rescan on commit
                    await self._trigger_change(set([self.project_path]))

                # Scan for file changes
                current_scan = {}
                for file_path in self._walk_files():
                    try:
                        stat = file_path.stat()
                        current_scan[file_path] = (stat.st_mtime, stat.st_size)
                    except (OSError, PermissionError):
                        continue

                # Detect changes
                changed = set()
                for path, (mtime, size) in current_scan.items():
                    if path not in last_scan:
                        # New file
                        changed.add(path)
                    elif last_scan[path] != (mtime, size):
                        # Modified file
                        changed.add(path)

                # Detect deletions
                for path in last_scan:
                    if path not in current_scan:
                        changed.add(path)

                if changed:
                    logger.debug(f"Detected {len(changed)} changed files")
                    self._changed_files.update(changed)
                    await self._schedule_debounce()

                last_scan = current_scan

                # Wait before next scan
                await asyncio.sleep(1.0)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in watch loop: {e}", exc_info=True)
                await asyncio.sleep(5.0)

    def _walk_files(self) -> list[Path]:
        """Walk project files, respecting ignore patterns."""
        files = []

        for root, dirs, filenames in os.walk(self.project_path):
            root_path = Path(root)
            
            # Filter out ignored directories
            # We must modify dirs in-place to prune valid subtrees
            dirs[:] = [d for d in dirs if not self._ignore_service.should_ignore(root_path / d)]

            for filename in filenames:
                file_path = root_path / filename
                
                # Check if file should be ignored
                if self._ignore_service.should_ignore(file_path):
                    continue

                # Skip hidden files
                if filename.startswith(".") and filename != ".env":
                    continue

                files.append(file_path)

        return files

    def _get_current_commit(self) -> str | None:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    async def _schedule_debounce(self) -> None:
        """Schedule debounced callback."""
        # Cancel existing debounce
        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()

        # Schedule new debounce
        self._debounce_task = asyncio.create_task(self._debounce_wait())

    async def _debounce_wait(self) -> None:
        """Wait for debounce period, then trigger callback."""
        try:
            await asyncio.sleep(self.debounce_seconds)

            # Trigger callback with accumulated changes
            if self._changed_files and self.on_change:
                changed = self._changed_files.copy()
                self._changed_files.clear()

                logger.info(f"Triggering change callback for {len(changed)} files")
                try:
                    # Call callback (may be sync or async)
                    result = self.on_change(changed)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as e:
                    logger.error(f"Error in change callback: {e}", exc_info=True)

        except asyncio.CancelledError:
            pass

    async def _trigger_change(self, paths: Set[Path]) -> None:
        """Immediately trigger change callback."""
        if self.on_change:
            try:
                result = self.on_change(paths)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Error in change callback: {e}", exc_info=True)
