"""
Signal Auditor Service for Sidelith Hyper-Perception.

Audits machine-level signals (logs, history, clipboard) to verify 
reachability and harvest high-fidelity intent signals.
"""

import asyncio
import logging
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

from side.storage.modules.transient import OperationalStore
from side.models.core import SignalReport

logger = logging.getLogger(__name__)

class SignalAuditorService:
    """
    Analyzes 'Dark Signals' from the OS to feed the Intelligence Substrate.
    """

    def __init__(self, operational: OperationalStore):
        self.operational = operational
        self._running = False
        self._task: asyncio.Task | None = None
        from ..env import env
        self.report_path = env.get_side_root() / "signal_reachability.json"

    async def start(self) -> None:
        """Start the signal auditor."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self.run_forever())
        logger.info("🔍 [SIGNAL AUDITOR]: Deep Discovery Active.")

    async def stop(self) -> None:
        """Stop the signal auditor."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("🔍 [SIGNAL AUDITOR]: Deep Discovery Halted.")

    async def run_forever(self, interval: float = 60.0) -> None:
        """Periodic audit loop."""
        while self._running:
            try:
                report = await self.audit_all_signals()
                self._save_report(report)
                
                # Update Operational Ledger with Reachability Index
                report_dict = report.model_dump()
                reachability = sum(1 for s in report_dict.values() if isinstance(s, dict) and s.get("reachable")) / (len(report_dict) - 1) # Subtract created_at
                self.operational.set_setting("signal_reachability_index", str(round(reachability, 3)))
                
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Signal Auditor Error: {e}")
                await asyncio.sleep(interval * 2)

    async def audit_all_signals(self) -> SignalReport:
        """Audits all targeted machine signals."""
        return SignalReport(
            zsh_history=await self._check_zsh_history(),
            os_log=await self._check_os_log(),
            clipboard=await self._check_clipboard(),
            lsof_side=await self._check_lsof(),
            disk_io=await self._check_disk_io(),
        )

    async def _check_zsh_history(self) -> Dict[str, Any]:
        history_path = Path.home() / ".zsh_history"
        reachable = history_path.exists() and os.access(history_path, os.R_OK)
        return {
            "reachable": reachable,
            "path": str(history_path),
            "size": history_path.stat().st_size if reachable else 0,
            "importance": "8/10",
            "intent": "Shell Command Intent (Trial & Error Tracking)"
        }

    async def _check_os_log(self) -> Dict[str, Any]:
        """Checks if we can tail system logs."""
        try:
            # Quick check for log command existence and permissions
            process = await asyncio.create_subprocess_exec(
                "log", "show", "--last", "1s",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            reachable = process.returncode == 0
        except:
            reachable = False
            
        return {
            "reachable": reachable,
            "importance": "10/10",
            "intent": "System-level Error Pulse (Causal Linkage)"
        }

    async def _check_clipboard(self) -> Dict[str, Any]:
        """Checks if we can monitor the system clipboard (Pulse)."""
        try:
            # We use pbpaste on Mac for a quick check
            process = await asyncio.create_subprocess_exec(
                "pbpaste",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            reachable = process.returncode == 0
            # [MYSTERY SIGNAL]: Clipboard Entropy
            content = stdout.decode().strip()
            entropy = len(set(content)) / len(content) if content else 0
        except:
            reachable = False
            entropy = 0
            
        return {
            "reachable": reachable,
            "importance": "9/10",
            "intent": "Context Outsourcing (Copy-Paste from AI)",
            "current_entropy": round(entropy, 3)
        }

    async def _check_lsof(self) -> Dict[str, Any]:
        """Check open files for Sidelith itself (Health)."""
        try:
            process = await asyncio.create_subprocess_exec(
                "lsof", "-p", str(os.getpid()),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            reachable = process.returncode == 0
        except:
            reachable = False
            
        return {
            "reachable": reachable,
            "importance": "5/10",
            "intent": "Internal Health & FD Leaks"
        }

    async def _check_disk_io(self) -> Dict[str, Any]:
        """Audit disk IO visibility."""
        import psutil
        try:
            counters = psutil.disk_io_counters()
            reachable = counters is not None
        except:
            reachable = False
            
        return {
            "reachable": reachable,
            "importance": "6/10",
            "intent": "Physical Burn Rate"
        }

    def _save_report(self, report: SignalReport) -> None:
        """Saves report to disk and operational store."""
        try:
            self.report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.report_path, "w") as f:
                f.write(report.model_dump_json(indent=2))
            self.operational.set_setting("signal_reachability_report", report.model_dump_json())
        except Exception as e:
            logger.error(f"Failed to save signal report: {e}")
