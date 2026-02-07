import sys
import os
import json
import logging
import asyncio
import warnings
from typing import Any, Dict, Optional
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

class SystemMonitorService:
    """
    System Monitor & Event Logger.
    Hooks into the CPython runtime to capture low-level system events.
    """

    def __init__(self, buffer, project_path: Path):
        self.buffer = buffer
        self.project_path = project_path
        self.project_id = str(project_path.name) # Simple ID for now
        self._running = False
        self._queue = asyncio.Queue()

    async def start(self):
        """Register the audit hook and start the ingestion loop."""
        if self._running:
            return
        
        self._running = True
        sys.addaudithook(self._audit_hook)
        
        # Failure Ingestion
        self._setup_failure_hooks()
        
        logger.info("🕰️ [SYSTEM_MONITOR]: Audit & Failure Hooks Registered.")
        
        # Start the persistence loop
        asyncio.create_task(self._persistence_loop())

    def _audit_hook(self, event: str, args: tuple):
        """
        CPython Audit Hook (PEP 578).
        Captures low-level events and adds them to the causal queue.
        """
        try:
            # Selective Filtering (Event Filtering: Ignore noise)
            relevant_events = {
                "os.system", "subprocess.Popen", "open", "socket.connect", "import"
            }
            
            if event not in relevant_events:
                return

            # Check locality (only care about events near our project)
            if event == "open":
                path = str(args[0])
                if not path.startswith(str(self.project_path)) and ".side" not in path:
                    return

            # Construct the Signal (T-001)
            signal = {
                "event": event,
                "args": self._parse_audit_args(event, args),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "causal_score": self._calculate_momentum(event)
            }
            
            # Put in queue
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.call_soon_threadsafe(self._queue.put_nowait, signal)

        except Exception:
            pass

    def _parse_audit_args(self, event: str, args: tuple) -> Any:
        # ... (rest of method unchanged)
        """Transmutes raw hook arguments into structured, machine-readable formats."""
        try:
            if event == "socket.connect" and len(args) >= 2:
                target = args[1]
                if isinstance(target, (list, tuple)) and len(target) >= 2:
                    return {"host": str(target[0]), "port": int(target[1])}
            
            if event == "open" and len(args) >= 1:
                return {"path": str(args[0]), "mode": str(args[1]) if len(args) > 1 else "r"}
            
            if event in ["subprocess.Popen", "os.system"] and len(args) >= 1:
                return {"command": str(args[0])}
                
        except Exception:
            pass
        return [str(a) for a in args] # Fallback

    def _setup_failure_hooks(self):
        """Registers hooks for warnings, exceptions, and root logging."""
        
        # 1. Runtime Warnings
        self._old_showwarning = warnings.showwarning
        warnings.showwarning = self._warning_hook
        
        # 2. Unhandled Exceptions (Crashes)
        self._old_excepthook = sys.excepthook
        sys.excepthook = self._exception_hook
        
        # 3. Root Logging (Dependency Errors)
        root_logger = logging.getLogger()
        self.log_handler = SystemLogHandler(self)
        root_logger.addHandler(self.log_handler)

    def _warning_hook(self, message, category, filename, lineno, file=None, line=None):
        """Captures Python warnings as strategic signals."""
        signal = {
            "event": "runtime_warning",
            "category": str(category.__name__),
            "message": str(message),
            "source": f"{filename}:{lineno}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "causal_score": 0.5
        }
        self._enqueue_signal(signal)
        if self._old_showwarning:
            self._old_showwarning(message, category, filename, lineno, file, line)

    def _exception_hook(self, exc_type, exc_value, exc_traceback):
        """Captures unhandled exceptions as high-momentum signals."""
        signal = {
            "event": "unhandled_exception",
            "type": str(exc_type.__name__),
            "message": str(exc_value),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "causal_score": 1.0 # Maximum strategic weight
        }
        self._enqueue_signal(signal)
        if self._old_excepthook:
            self._old_excepthook(exc_type, exc_value, exc_traceback)

    def _enqueue_signal(self, signal: Dict[str, Any]):
        """Helper to safely enqueue signals to the persistence loop."""
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.call_soon_threadsafe(self._queue.put_nowait, signal)

    def _calculate_momentum(self, event: str) -> float:
        """Assigns 'Strategic Weight' to events."""
        weights = {
            "subprocess.Popen": 0.8,
            "os.system": 0.9,
            "socket.connect": 0.6,
            "open": 0.2,
            "import": 0.4
        }
        return weights.get(event, 0.1)

    async def _persistence_loop(self):
        """Pass signals to the SignalBuffer."""
        while self._running:
            try:
                signal = await self._queue.get()
                
                # Route to Signal Buffer
                payload = {
                    "momentum": signal.get("causal_score", 0.5),
                    "v_temporal": 0.85
                }
                
                for k, v in signal.items():
                    if k not in ["event", "causal_score"]:
                        payload[k] = v

                await self.buffer.ingest("activity", {
                    "project_id": self.project_id,
                    "tool": "system_monitor",
                    "action": signal["event"],
                    "payload": payload
                })
                
                self._queue.task_done()
            except Exception as e:
                logger.error(f"System Monitor persistent failure: {e}")
                await asyncio.sleep(1)

    async def stop(self):
        self._running = False
        # Cleanup hooks
        warnings.showwarning = self._old_showwarning
        sys.excepthook = self._old_excepthook
        logging.getLogger().removeHandler(self.log_handler)
        logger.info("🕰️ [SYSTEM_MONITOR]: Monitor Offline.")

class SystemLogHandler(logging.Handler):
    """Bridge for ingesting logging.ERROR/WARNING into the Central Store."""
    def __init__(self, auditor: SystemMonitorService):
        super().__init__(level=logging.WARNING)
        self.auditor = auditor

    def emit(self, record):
        if record.levelno >= logging.WARNING:
            signal = {
                "event": "log_signal",
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "causal_score": 0.7 if record.levelno >= logging.ERROR else 0.4
            }
            self.auditor._enqueue_signal(signal)
