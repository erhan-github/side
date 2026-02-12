"""
Event Ledger Service.

Correlates log-level resolution events with recent code modifications.
"""

import asyncio
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

from side.storage.modules.audit import AuditService
from side.storage.modules.transient import TransientCache

logger = logging.getLogger(__name__)

class EventLedgerService:
    """
    Monitors logs/activity to close the loop between problem and solution.
    """

    def __init__(self, ledger: AuditService, cache: SessionCache, buffer=None):
        self.audits = audit
        self.operational = operational
        self.buffer = buffer
        self._running = False
        self._task: asyncio.Task | None = None
        self.roi_callback = None
        
        # Patterns (Proactive Discovery)
        self.error_patterns = [
            r"Error", r"Exception", r"failed", r"Traceback", r"panic", r"CRITICAL"
        ]
        
        # Causal State
        self.last_failure: Dict[str, Any] | None = None
        self.potential_fix: Dict[str, Any] | None = None
        self._tail_process: asyncio.subprocess.Process | None = None
        self._last_log_file: Path | None = None

    async def start(self) -> None:
        """Start the event ledger."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self.watch_logs())
        logger.info("📡 [EVENT_LEDGER]: Causal Awareness Active.")

    async def stop(self) -> None:
        """Stop the event ledger."""
        self._running = False
        if self._task:
            self._task.cancel()
        logger.info("📡 [EVENT_LEDGER]: Causal Awareness Halted.")
    
    async def watch_logs(self, log_path: str | Path = "debug/side.log") -> None:
        """
        Real-time log tailing for causal correlation.
        Tails a log file and links saves to error drops.
        """
        self._last_log_file = Path(log_path).resolve()
        if not self._last_log_file.exists():
            self._last_log_file.parent.mkdir(parents=True, exist_ok=True)
            self._last_log_file.touch()

        logger.info(f"📡 [EVENT_CORRELATION]: Tailing logs at {self._last_log_file}")
        
        try:
            self._tail_process = await asyncio.create_subprocess_exec(
                "tail", "-F", str(self._last_log_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            while self._running:
                line = await self._tail_process.stdout.readline()
                if not line:
                    break
                
                content = line.decode().strip()
                await self._process_log_line(content)
                
        except asyncio.CancelledError:
            if self._tail_process:
                self._tail_process.terminate()
        except Exception as e:
            logger.error(f"Tailer Error: {e}")
            await asyncio.sleep(5)
            if self._running:
                asyncio.create_task(self.watch_logs(log_path))

    async def _process_log_line(self, line: str):
        """Processes a single log line for failure or success signatures."""
        # 1. Detect Failure
        if any(re.search(pat, line) for pat in self.error_patterns):
            self.last_failure = {
                "message": line,
                "ts": datetime.now(timezone.utc),
                "type": "log_error"
            }
            self.potential_fix = None
            return

        # 2. Detect Implicit Success (Machine Equilibrium)
        if "Started" in line or "Ready" in line:
            if self.potential_fix:
                await self._verify_resolution("Machine Equilibrium (Process Ready)")

    async def notify_process_exit(self, exit_code: int, signal: int | None = None):
        """Called when a monitored process exits."""
        if exit_code != 0:
            self.last_failure = {
                "message": f"Process exited with code {exit_code}",
                "ts": datetime.now(timezone.utc),
                "type": "machine_crash"
            }
            logger.warning(f"🚨 [MACHINE]: Detected crash (Code: {exit_code})")
        
    async def notify_save(self, file_path: Path):
        """Called by FileWatcher when a file is saved."""
        if not self.last_failure:
            return

        logger.info(f"🔨 [MACHINE]: Analyzing potential fix in {file_path.name}")
        self.potential_fix = {
            "file": file_path,
            "ts": datetime.now(timezone.utc),
            "failure": self.last_failure
        }
        
        # Start a verification window
        asyncio.create_task(self._verification_window())

    async def _verification_window(self):
        """Wait to see if errors re-occur after a fix."""
        await asyncio.sleep(5) # 5 second stabilization window
        if self.potential_fix:
            await self._verify_resolution("No Re-occurrence")

    async def _verify_resolution(self, method: str):
        """Confirms and records a causal link."""
        fix = self.potential_fix
        if not fix: return
        
        problem = fix["failure"]["message"]
        resolution = f"Stabilized via {fix['file'].name} ({method})"
        
        self.record_correlation(problem, resolution, str(fix["file"]))
        
        # Reset State
        self.last_failure = None
        self.potential_fix = None
        
        # Notify ROI Simulator
        if self.roi_callback:
            asyncio.create_task(self.roi_callback(problem, resolution))

    def record_correlation(self, problem: str, resolution: str, file_path: str):
        """
        Manually record a link between a problem and its resolution.
        To be called by the CLI or background watcher.
        """
        now = datetime.now(timezone.utc).isoformat()
        
        if self.buffer:
            asyncio.create_task(self.buffer.ingest("activity", {
                "project_id": "SYSTEM",
                "tool": "event_ledger",
                "action": "event_correlation",
                "payload": {
                    "problem": problem,
                    "resolution": resolution,
                    "file": file_path,
                    "timestamp": now,
                    "algorithm": "Correlation v1.0"
                }
            }))
        else:
            # Save to Audit Store as a 'Verified Pattern'
            self.audits.log_activity(
                project_id="SYSTEM",
                tool="EVENT_LEDGER",
                action="event_correlation",
                payload={
                    "problem": problem,
                    "resolution": resolution,
                    "file": file_path,
                    "timestamp": now,
                    "algorithm": "Correlation v1.0"
                }
            )
        logger.info(f"✨ [EVENT_CORRELATION]: Linked resolution in {file_path} to problem: {problem}")
