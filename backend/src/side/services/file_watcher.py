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
        buffer=None,
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
        self.buffer = buffer

        self._running = False
        self._task: asyncio.Task | None = None
        self._changed_files: Set[Path] = set()
        self._last_commit_hash: str | None = None
        self._debounce_task: asyncio.Task | None = None

        self._last_commit_hash: str | None = None
        self._debounce_task: asyncio.Task | None = None
        
        # Use Sovereign Ignore Service
        from side.services.ignore import SovereignIgnore
        from side.storage.modules.transient import OperationalStore
        from side.storage.modules.base import ContextEngine
        self._ignore_service = SovereignIgnore(self.project_path)
        self.operational = OperationalStore(ContextEngine())
        
        # Temporal Synapse State
        self._last_commit_time = datetime.now(timezone.utc)
        self._revert_count = 0
        self._total_commits_hour = 0
        self._last_commit_msg = ""
        self._git_velocity = 1.0 # 0.0 - 1.0


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
                # 1. Physical Presence Scan (Distributed Context)
                current_scan = self._get_scan_snapshot()
                
                # 2. Check for git commits
                current_commit = self._get_current_commit()
                if current_commit and current_commit != self._last_commit_hash:
                    now = datetime.now(timezone.utc)
                    delta = (now - self._last_commit_time).total_seconds()
                    
                    commit_msg = self._get_commit_message(current_commit)
                    is_revert = any(x in commit_msg.lower() for x in ["revert", "undo", "fixup", "rollback"])
                    
                    if is_revert:
                        self._revert_count += 1
                        logger.warning(f"⚠️ [REVERT DETECTED]: {commit_msg[:50]}...")
                    
                    self._total_commits_hour += 1
                    
                    logger.info(f"New commit detected: {current_commit[:8]} (Delta: {delta}s)")
                    
                    # Calculate Git Velocity (V_git)
                    # V_git = 1.0 - (reverts / total_commits)
                    # High velocity/low reverts = healthy flow. 
                    self._git_velocity = max(0.0, 1.0 - (self._revert_count / max(1, self._total_commits_hour)))
                    
                    self.operational.set_setting("temporal_synapse_velocity", str(round(self._git_velocity, 3)))
                    self.operational.set_setting("git_revert_count", str(self._revert_count))
                    
                    self._last_commit_hash = current_commit
                    self._last_commit_time = now
                    # We reset every hour or after 10 commits to keep the metric fresh
                    if delta > 3600 or self._total_commits_hour > 10:
                        self._revert_count = 0
                        self._total_commits_hour = 0
                    
                    # Trigger full rescan on commit
                    await self._trigger_change(set([self.project_path]))

                # 3. Detect Ghost Intent (Pattern Rejection)
                if rejection_signals := await self._detect_ghost_intent(last_scan, current_scan):
                    for signal in rejection_signals:
                        logger.info(f"👻 [GHOST INTENT]: Pattern rejection detected in {signal['path']}")
                        
                        reason = f"Ghost Deletion: {signal['entropy']} bytes removed."
                        if signal.get("diff"):
                            # Filter out small diffs to avoid noise
                            if len(signal['diff']) > 50:
                                reason = f"{reason}\nDeleted Logic Snippet:\n{signal['diff'][:1000]}"

                        if self.buffer:
                            await self.buffer.ingest("rejection", {
                                "id": f"ghost_{asyncio.get_event_loop().time()}",
                                "file_path": str(signal['path']),
                                "reason": reason
                            })
                        else:
                            from side.storage.modules.strategic import StrategicStore
                            from side.storage.modules.base import ContextEngine
                            strat_store = StrategicStore(ContextEngine())
                            strat_store.save_rejection(
                                rejection_id=f"ghost_{asyncio.get_event_loop().time()}",
                                file_path=str(signal['path']),
                                reason=reason
                            )

                # 4. Detect Physical Changes
                changed = set()
                for path, (mtime, size) in current_scan.items():
                    if path not in last_scan:
                        # New file
                        changed.add(path)
                    elif last_scan[path] != (mtime, size):
                        # Modified file
                        changed.add(path)

                # 5. Detect Deletions
                for path in last_scan:
                    if path not in current_scan:
                        changed.add(path)

                if changed:
                    logger.debug(f"Detected {len(changed)} changed files")
                    self._changed_files.update(changed)
                    await self._schedule_debounce()

                last_scan = current_scan

                # Wait before next scan (Throttled for Performance)
                await asyncio.sleep(5.0)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in watch loop: {e}", exc_info=True)
                await asyncio.sleep(5.0)

    def _get_scan_snapshot(self) -> dict:
        """Takes a snapshot of the current file system state."""
        current_scan = {}
        for file_path in self._walk_files():
            try:
                stat = file_path.stat()
                current_scan[file_path] = (stat.st_mtime, stat.st_size)
            except (OSError, PermissionError):
                continue
        return current_scan

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

    def _get_commit_message(self, commit_hash: str) -> str:
        """Get commit message for hash."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%s", commit_hash],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return ""

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

    async def _detect_ghost_intent(self, old_scan: dict, new_scan: dict) -> list[dict]:
        """
        [HYPER-PERCEPTION]: Detects significant code deletions (Ghost Signals).
        Returns a list of high-entropy deletion events.
        """
        signals = []
        for path, (old_mtime, old_size) in old_scan.items():
            if path in new_scan:
                new_mtime, new_size = new_scan[path]
                if new_size < old_size - 100: # Significant deletion (>100 bytes)
                    # Extract diff for deeper context
                    diff = self._get_git_diff_deletions(path)
                    signals.append({
                        "path": path,
                        "entropy": old_size - new_size,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "diff": diff
                    })
        return signals

    def _get_git_diff_deletions(self, file_path: Path) -> str:
        """Extract deleted lines from git diff."""
        try:
            # We want only deleted lines (starting with -) excluding the --- line
            result = subprocess.run(
                ["git", "diff", "-U0", "HEAD", "--", str(file_path)],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                # filter lines starting with - (but not --- or @)
                deletions = [
                    line[1:] for line in result.stdout.splitlines() 
                    if line.startswith("-") and not line.startswith("---")
                ]
                return "\n".join(deletions)
        except:
            pass
        return ""
