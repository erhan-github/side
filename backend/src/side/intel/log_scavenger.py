
import os
import time
import logging
import threading
import collections
from pathlib import Path
from typing import List, Dict, Any, Optional
from side.storage.modules.audit import AuditStore
from side.storage.modules.base import ContextEngine
from side.intel.scavengers.mobile import AndroidScavenger
from side.intel.scavengers.docker import DockerScavenger
import asyncio

logger = logging.getLogger(__name__)

class LogScavenger:
    """
    [KAR-8.1] The Log Scavenger.
    Tails external logs (Xcode, Next.js, Python) to capture 'Ground Truth' friction.
    """
    
    def __init__(self, audit: AuditStore, project_path: Path):
        self.audit = audit
        self.project_path = project_path
        self.stop_event = threading.Event()
        self.threads = []
        
        # Paths to scavenge
        self.xcode_root = Path.home() / "Library/Developer/Xcode/DerivedData"
        self.nextjs_root = project_path / "web" / ".next"
        
        # Buffers for "Crime Scene"Context (Last 50 lines)
        self.generic_buffer = collections.deque(maxlen=50)
        
    def start(self):
        """Starts the scavenging threads."""
        logger.info("🚀 [LOG_SCAVENGER]: Starting scavenge cycles...")
        
        # 1. Xcode Tailer
        xcode_thread = threading.Thread(target=self._scavenge_xcode, daemon=True)
        self.threads.append(xcode_thread)
        xcode_thread.start()
        
        # 2. Next.js Monitor
        next_thread = threading.Thread(target=self._scavenge_nextjs, daemon=True)
        self.threads.append(next_thread)
        next_thread.start()

        # 3. Python/Generic Log Monitor (Standard Error Logs)
        python_thread = threading.Thread(target=self._scavenge_generic_logs, daemon=True)
        self.threads.append(python_thread)
        python_thread.start()

        # 4. Android Logcat
        android_thread = threading.Thread(target=self._scavenge_android, daemon=True)
        self.threads.append(android_thread)
        android_thread.start()

        # 5. Docker Logs
        docker_thread = threading.Thread(target=self._scavenge_docker, daemon=True)
        self.threads.append(docker_thread)
        docker_thread.start()
        
    def stop(self):
        self.stop_event.set()
        for t in self.threads:
            t.join(timeout=1)

    def _scavenge_xcode(self):
        """Monitors Xcode Logs for build failures."""
        logger.info("🔭 [LOG_SCAVENGER]: Monitoring Xcode DerivedData...")
        seen_logs = set()
        
        while not self.stop_event.is_set():
            try:
                # Find Logs directories in DerivedData
                # We limit depth to avoid excessive scanning
                log_dirs = list(self.xcode_root.glob("*/Logs/Build"))
                for log_dir in log_dirs:
                    # Look for newest .xcactivitylog files (which are actually gzipped)
                    # For MVP, we just look for filenames that indicate failure
                    # In V2.3, we'll implement deep gzip parsing.
                    latest_logs = sorted(log_dir.glob("*.xcactivitylog"), key=os.path.getmtime, reverse=True)[:5]
                    for log in latest_logs:
                        if log not in seen_logs:
                            # Basic check: Did the last build fail?
                            # Usually success/failure is in the directory structure or internal metadata
                            # Here we simulate detection of a 'BUILD FAILURE' signal
                            seen_logs.add(log)
                            # We check mtime to see if it's recent (last 30s)
                            if time.time() - os.path.getmtime(log) < 30:
                                self._log_friction("XCODE", "BUILD_EVENT", {"file": str(log), "status": "CHECK_REQUIRED"})

            except Exception as e:
                logger.error(f"⚠️ [LOG_SCAVENGER]: Xcode Scavenge Error: {e}")
            
            time.sleep(10) # Throttled scan

    def _scavenge_nextjs(self):
        """Monitors Next.js logs/manifests for runtime errors."""
        logger.info(f"🔭 [LOG_SCAVENGER]: Monitoring Next.js at {self.nextjs_root}...")
        
        while not self.stop_event.is_set():
            try:
                # Next.js often outputs errors to the console/pm2, but we can check 
                # build-time errors in .next/build-manifest.json or similar if they exist
                # or look for trace files.
                trace_files = list(self.nextjs_root.glob("*.trace"))
                for trace in trace_files:
                    if time.time() - os.getmtime(trace) < 15:
                        self._log_friction("NEXTJS", "RUNTIME_TRACE", {"source": str(trace)})
            except Exception as e:
                pass
            
            time.sleep(5)

    def _scavenge_generic_logs(self):
        """
        Monitors standard error logs (*.log, error.out) in project root.
        Targeting Python/Node generic output redirected to files.
        """
        logger.info(f"🔭 [LOG_SCAVENGER]: Monitoring *.log in {self.project_path}...")
        seen_sizes = {}
        
        while not self.stop_event.is_set():
            try:
                # [KAR-8.2] Structural Domain Isolation: Strictly exclude Sidelith internal metadata
                FORBIDDEN_TAGS = ["[LOG_SCAVENGER]", "[SOVEREIGN]", "[GOVERNOR]", "[ENGINE]"]
                
                # 1. Surgical Globbing (Project Root Only)
                log_files = (
                    list(self.project_path.glob("*.log")) + 
                    list(self.project_path.glob("*.err"))
                )
                
                # 2. Strict Structural Filter (Safety by Design)
                # Ensure no internal Sidelith state files are ever observed
                log_files = [
                    f for f in log_files 
                    if ".side" not in f.parts 
                    and "scavenger" not in f.name.lower()
                    and "server" not in f.name.lower()
                ]
                
                for log_file in log_files:
                    try:
                        current_size = log_file.stat().st_size
                        previous_size = seen_sizes.get(log_file, current_size)
                        
                        # If file grew, read the new content
                        if current_size > previous_size:
                            with open(log_file, 'r', errors='ignore') as f:
                                f.seek(previous_size)
                                new_content = f.read()
                                
                                # Split lines for granular analysis
                                lines = new_content.splitlines()
                                for line in lines:
                                    # [CRITICAL] Anti-Recursion: Ignore our own strategic metadata
                                    if any(tag in line for tag in FORBIDDEN_TAGS):
                                        continue
                                        
                                    self.generic_buffer.append(line)
                                    
                                    # [POLYGLOT HEURISTICS]
                                    # Detect generic stack traces across Ruby, PHP, .NET, Java, etc.
                                    is_error = False
                                    error_source = "GENERIC"
                                    
                                    # 1. Ruby / Rails
                                    if ".rb:" in line and "in `" in line:
                                        is_error = True
                                        error_source = "RUBY"
                                    # 2. PHP / Laravel
                                    elif "PHP Fatal error:" in line or "PHP Stack trace:" in line or "thrown in /" in line:
                                        is_error = True
                                        error_source = "PHP"
                                    # 3. .NET / C#
                                    elif "   at " in line and ".cs:line " in line:
                                        is_error = True
                                        error_source = "DOTNET"
                                    # 4. Java / Spring
                                    elif "at " in line and "(" in line and ".java:" in line:
                                        is_error = True
                                        error_source = "JAVA"
                                    # 5. Standard Python/JS
                                    elif "Traceback" in line or "Error:" in line or "Exception" in line:
                                        is_error = True

                                    if is_error:
                                        # Capture the "Crime Scene" (Last 50 lines)
                                        crime_scene = list(self.generic_buffer)
                                        self._log_friction(error_source, "RUNTIME_ERROR", {
                                            "file": log_file.name,
                                            "snippet": line,
                                            "context": crime_scene 
                                        })
                        
                        seen_sizes[log_file] = current_size
                    except Exception:
                        pass
                        
            except Exception as e:
                logger.error(f"Generic Scavenge Error: {e}")
                
            time.sleep(5)

    def _scavenge_android(self):
        """Polls Android Logcat via Scavenger Wrapper."""
        logger.info("📱 [LOG_SCAVENGER]: Starting Android Logcat Monitor...")
        scav = AndroidScavenger()
        
        while not self.stop_event.is_set():
            try:
                # Run async method in sync loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                devices = scav.find_devices()
                if devices:
                    log_data = loop.run_until_complete(scav.tail_logcat())
                    if log_data:
                        self._log_friction("ANDROID", "CRASH", log_data)
                loop.close()
            except Exception as e:
                pass
            time.sleep(10)

    def _scavenge_docker(self):
        """Polls Docker Logs via Scavenger Wrapper."""
        logger.info("🐳 [LOG_SCAVENGER]: Starting Docker Monitor...")
        scav = DockerScavenger()
        
        while not self.stop_event.is_set():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                containers = loop.run_until_complete(scav.get_running_containers())
                for container in containers:
                    log_data = loop.run_until_complete(scav.scan_logs(container["id"]))
                    if log_data:
                         self._log_friction("DOCKER", "CONTAINER_Log", log_data)
                loop.close()
            except Exception as e:
                pass
            time.sleep(10)

    def _log_friction(self, source: str, event_type: str, payload: dict):
        """Persists a friction signal to the Sovereign Ledger. Charges 1 SU."""
        project_id = ContextEngine.get_project_id(self.project_path)
        
        # [ECONOMY]: Charge 1 SU for Signal Capture (Log Event)
        from side.storage.modules.identity import IdentityStore
        identity = IdentityStore(self.audit.engine)
        
        # If charge fails (insufficient SUs), we still log it as FREE (grace period)
        # or we could skip it. For now, we charge.
        identity.charge_action(project_id, "SIGNAL_CAPTURE")
        
        logger.info(f"🚨 [LOG_SCAVENGER]: Captured {source} {event_type} Friction.")
        self.audit.log_activity(
            project_id=project_id,
            tool="LOG_SCAVENGER",
            action=f"capture_{source.lower()}_signal",
            cost_tokens=1, 
            payload={
                "source": source.upper(), # XCODE, ANDROID, DOCKER
                "type": event_type,       # CRASH, ERROR, WARNING
                "raw_data": payload,      # The raw log line/object
                "normalized_error": str(payload.get("error") or payload.get("log") or payload.get("snippet") or "Unknown Error"),
                "timestamp": time.time()
            }
        )

if __name__ == "__main__":
    # Test Standalone
    engine = ContextEngine()
    audit = AuditStore(engine)
    scavenger = LogScavenger(audit, Path.cwd())
    scavenger.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        scavenger.stop()
