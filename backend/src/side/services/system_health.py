"""
System Health Service.

Monitors CPU temperature and power usage to detect high load.
"""

import asyncio
import logging
import subprocess
import sys
import json
import psutil
from pathlib import Path
from typing import Any, Dict

from side.storage.modules.transient import OperationalStore
from side.models.core import HardwareStats

logger = logging.getLogger(__name__)

class SystemHealthService:
    """
    Monitors hardware-level signals to provide System Load metrics.
    """

    def __init__(self, operational: OperationalStore, interval: float = 10.0):
        self.operational = operational
        self.interval = interval
        self._running = False
        self._task: asyncio.Task | None = None
        
        # Load Thresholds
        self.TEMP_THRESHOLD = 85.0  # Celsius
        self.CPU_THRESHOLD = 80.0   # Percent

    async def start(self) -> None:
        """Start the system health monitor."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self.run_forever())
        logger.info("📡 [SYSTEM_HEALTH]: Hardware Monitor Active.")

    async def stop(self) -> None:
        """Stop the system health monitor."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("📡 [SYSTEM_HEALTH]: Hardware Monitor Halted.")

    async def run_forever(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                # 1. Sample Hardware
                stats = await self._sample_hardware()
                
                # 2. Analyze Load
                load_score = self._calculate_load(stats.model_dump())
                
                # 3. Store in Operational Ledger
                self.operational.set_setting("system_health_score", str(round(load_score, 3)))
                self.operational.set_setting("system_health_stats", stats.model_dump_json())
                
                if load_score > 0.8:
                    logger.warning(f"🔥 [HIGH LOAD ALERT]: Abnormal System Load detected (Score: {load_score}).")
                
                await asyncio.sleep(self.interval)
            except Exception as e:
                logger.error(f"System Health Error: {e}")
                await asyncio.sleep(self.interval * 2)

    async def _sample_hardware(self) -> HardwareStats:
        """Samples platform-specific hardware signals."""
        cpu_total = psutil.cpu_percent(interval=None)
        load_avg = psutil.getloadavg()[0] # 1 min average
        
        temp = 0.0
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if entries:
                            temp = max(temp, entries[0].current)
        except Exception:
            pass
            
        return HardwareStats(
            temp=temp,
            cpu_total=cpu_total,
            load_avg=load_avg,
            timestamp=asyncio.get_event_loop().time()
        )

    def _calculate_load(self, stats: Dict[str, Any]) -> float:
        """
        Calculates normalized load score (0.0 - 1.0).
        
        Load is determined by the highest load signal.
        """
        cpu_load = stats.get("cpu_total", 0.0) / 100.0
        
        # Load average / Number of cores is a good indicator of 'Strain'
        try:
            cpu_count = psutil.cpu_count() or 1
            load_norm = stats.get("load_avg", 0.0) / cpu_count
        except:
            load_norm = 0.0

        temp = stats.get("temp", 0.0)
        temp_norm = 0.0
        if temp > 0:
            temp_norm = max(0.0, min(1.0, (temp - 40.0) / 50.0))
        
        # We blend strictly: If ANY of these are high, the user feels it.
        load = max(cpu_load, load_norm, temp_norm)
        
        return load
