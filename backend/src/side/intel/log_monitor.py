"""
[INTEL]: Log Monitor - Event-Driven Friction Capture.
Replaces legacy polling with filesystem events (Watchdog) and async streams.
"""

import os
import time
import logging
import threading
import asyncio
from pathlib import Path
from typing import Dict, Any, Deque
from collections import deque

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from side.storage.modules.audit import AuditService
from side.storage.modules.base import ContextEngine
from side.intel.scavengers.mobile import AndroidScavenger
from side.intel.scavengers.docker import DockerScavenger

logger = logging.getLogger(__name__)

class UnifiedLogHandler(FileSystemEventHandler):
    """
    Handles file system events for logs.
    Aggregates triggers to prevent duplicate processing (Debounce).
    """
    def __init__(self, monitor: 'LogMonitor'):
        self.monitor = monitor
        self.last_triggered = 0.0
        self.debounce_interval = 1.0 # Process at most once per second per file

    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Quick filter for relevant files
        filename = str(event.src_path)
        if not (filename.endswith('.log') or filename.endswith('.err') or filename.endswith('.xcactivitylog') or filename.endswith('.trace')):
            return

        # Debounce
        now = time.time()
        if now - self.last_triggered < self.debounce_interval:
            return
        self.last_triggered = now

        # Delegate to monitor for processing
        self.monitor.process_file_change(Path(event.src_path))

class LogMonitor:
    """
    Event-Driven Log Intelligence.
    Monitors friction points using FS Events (High Performance) + Async Streams.
    """
    def __init__(self, audit: AuditService, project_path: Path):
        self.audits = audit
        self.project_path = project_path
        self.stop_event = threading.Event()
        self.threads = []
        
        # Watchdog
        self.observer = Observer()
        self.handler = UnifiedLogHandler(self)
        
        # State
        self.file_cursors: Dict[Path, int] = {}
        self.generic_buffer: Deque[str] = deque(maxlen=50)
        
        # Paths
        self.xcode_root = Path.home() / "Library/Developer/Xcode/DerivedData"
        self.nextjs_root = project_path / "web" / ".next"

    def start(self):
        """Initialize Watchdog Observers and Stream Pollers."""
        logger.info("🔭 [LOG_MONITOR]: Activating Event-Driven Eyes...")
        
        # 1. FS Events (Generic Logs)
        if self.project_path.exists():
            self.observer.schedule(self.handler, str(self.project_path), recursive=False)
            
        # 2. FS Events (Next.js) - Non-recursive to avoid build artifacts noise
        if self.nextjs_root.exists():
            self.observer.schedule(self.handler, str(self.nextjs_root), recursive=False)
            
        # 3. FS Events (Xcode) - Recursive watch on DerivedData can be heavy, be careful
        # Only watch if it exists and we are on Mac
        if self.xcode_root.exists():
            # DerivedData is huge. We might want to poll this specific one or watch specific subdirs?
            # For High-Integrity optimization, watching the WHOLE DerivedData is risky.
            # Let's keep Xcode as a slow poller for now, or watch only specific active builds if known.
            # Decision: Keep Xcode as Poller (Safety), Move Generic + NextJS to Watchdog.
            pass

        self.observer.start()
        
        # 4. Background Stream Pollers (Docker, Android, Xcode)
        # We perform these in a single async loop thread to save resources (vs 3 threads)
        stream_thread = threading.Thread(target=self._run_async_streams, daemon=True)
        self.threads.append(stream_thread)
        stream_thread.start()

    def stop(self):
        self.stop_event.set()
        self.observer.stop()
        self.observer.join()
        for t in self.threads:
            t.join(timeout=2)

    def _run_async_streams(self):
        """
        Runs external stream monitors in a single asyncio loop.
        Efficiently multiplexes Docker, Android, and Xcode polling.
        """
        from side.config import config
        
        # [OPTIMIZATION] Lazy load external scavengers only if enabled
        if not config.enable_advanced_scavengers:
             return

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def _lifecycle():
            # Lazy Import to prevent startup bloat
            try:
                from side.intel.scavengers.mobile import AndroidScavenger
                from side.intel.scavengers.docker import DockerScavenger
                
                android = AndroidScavenger()
                docker = DockerScavenger()
            except ImportError:
                logger.warning("Advanced scavengers not available (missing dependencies).")
                return
            
            while not self.stop_event.is_set():
                # 1. Android
                try:
                    devices = android.find_devices()
                    if devices:
                        log = await android.tail_logcat()
                        if log: self._log_friction("ANDROID", "CRASH", log)
                except Exception as e: 
                    logger.debug(f"Android monitor skipped: {e}")
                
                # 2. Docker
                try:
                    containers = await docker.get_running_containers()
                    for c in containers:
                        log = await docker.scan_logs(c["id"])
                        if log: self._log_friction("DOCKER", "CONTAINER_LOG", log)
                except Exception as e: 
                    logger.debug(f"Docker monitor skipped: {e}")
                
                # 3. Xcode (Legacy Polling for safety)
                try:
                    self._poll_xcode()
                except Exception as e:
                    logger.debug(f"Xcode poller error: {e}")
                
                await asyncio.sleep(5) # Unified 5s heartbeat
                
        loop.run_until_complete(_lifecycle())
        loop.close()

    def _poll_xcode(self):
        """Manual poll for Xcode (safest for huge directories)."""
        try:
            if not self.xcode_root.exists(): return
            
            # Simple check for recent logs
            # Logic similar to original but streamlined
            log_dirs = list(self.xcode_root.glob("*/Logs/Build"))
            for log_dir in log_dirs:
                latest = sorted(log_dir.glob("*.xcactivitylog"), key=os.path.getmtime, reverse=True)[:1]
                if latest and time.time() - os.path.getmtime(latest[0]) < 10:
                     # Simulate event
                     self.process_file_change(latest[0])
        except Exception:
            pass

    def process_file_change(self, file_path: Path):
        """
        Core logic for processing a changed log file.
        Reads only new content (Incremental Analysis).
        """
        try:
            # 1. Filter Self
            if ".side" in file_path.parts or "side.log" in file_path.name:
                return

            current_size = file_path.stat().st_size
            last_pos = self.file_cursors.get(file_path, 0)
            
            if current_size <= last_pos:
                # Rotated or truncated
                last_pos = 0
            
            with open(file_path, 'r', errors='ignore') as f:
                f.seek(last_pos)
                new_content = f.read()
                
                if new_content:
                    self._analyze_chunk(new_content, file_path)
            
            self.file_cursors[file_path] = current_size
            
        except Exception as e:
            logger.warning(f"Failed to process log change {file_path}: {e}")

    def _analyze_chunk(self, content: str, source: Path):
        """Analyzes text chunk for friction signals with High-Fidelity Causal Framing."""
        lines = content.splitlines()
        for i, line in enumerate(lines):
            self.generic_buffer.append(line)
            
            # Heuristics: Detecting deep runtime signatures
            is_error = False
            err_type = "GENERIC"
            
            error_patterns = {
                "PYTHON": ["Traceback", "Exception", "RuntimeError", "NameError", "TypeError"],
                "PHP": ["PHP Fatal", "PHP Parse", "PHP Error"],
                "JS_NODE": ["ReferenceError", "SyntaxError", "FATAL ERROR", "Uncaught Exception"],
                "NATIVE": ["panic:", "segfault", "Segmentation fault"],
                "JAVA": ["java.lang.", "stack trace:"]
            }

            line_lower = line.lower()
            for lang, patterns in error_patterns.items():
                if any(p.lower() in line_lower for p in patterns):
                    is_error = True
                    err_type = lang
                    break
                
            if is_error:
                # [CAUSAL FRAMING]: Extract ±10 lines around the hit
                start_idx = max(0, i - 10)
                end_idx = min(len(lines), i + 10)
                causal_frame = "\n".join(lines[start_idx:end_idx])
                
                self._log_friction(
                    source.name.upper(), 
                    "RUNTIME_ERROR", 
                    {
                        "snippet": line, 
                        "type": err_type, 
                        "file": str(source),
                        "causal_frame": causal_frame # [HIGH-INTEGRITY]
                    }
                )

    def _log_friction(self, source: str, event_type: str, payload: dict):
        """Persists friction to Ledger."""
        # [ECONOMY]: Charge 1 SU? 
        # For now, just log to audit
        project_id = ContextEngine.get_project_id(self.project_path)
        
        logger.info(f"🚨 [MONITOR]: Captured {source} {event_type}")
        self.audits.log_activity(
            project_id=project_id,
            tool="LOG_MONITOR",
            action=f"capture_{source.lower()}",
            payload=payload
        )
