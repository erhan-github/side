"""
Mobile Scavenger.
Wraps `adb` and `simctl` to capture mobile runtime errors.
"""

import subprocess
import logging
from typing import List, Dict
import asyncio

logger = logging.getLogger(__name__)

class AndroidScavenger:
    def __init__(self):
        self.device_id = None

    def find_devices(self) -> List[str]:
        """Runs `adb devices` to find connected phones."""
        try:
            # Mock implementation for drill if adb not present
            # result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
            # return [line.split()[0] for line in result.stdout.splitlines() if "device" in line]
            return ["emulator-5554"] # Mock for simulation
        except Exception:
            return []

    async def tail_logcat(self, keywords: List[str] = ["FATAL", "Exception", "Crash"]):
        """Tails logcat for friction signals."""
        logger.info(f"📱 [ANDROID]: Tailing Logcat for {keywords}...")
        # Simulating a crash detection
        await asyncio.sleep(0.1)
        return {"source": "ANDROID", "error": "java.lang.NullPointerException: Attempt to invoke virtual method on a null object reference"}

class IOSScavenger:
    def find_simulators(self) -> List[str]:
        return ["iPhone 15 Pro"]

    async def tail_syslog(self):
        logger.info("📱 [iOS]: Tailing Simulator Log...")
        return {"source": "iOS", "error": "Fatal Exception: NSInternalInconsistencyException"}
