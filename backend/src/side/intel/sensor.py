"""
IDE Sensor.

Detects the active development environment (Cursor, VSCode, Terminal)
to inform context strategy.
"""

import subprocess
import logging
from enum import Enum
from typing import Set

logger = logging.getLogger(__name__)

class IDEnvironment(Enum):
    CURSOR = "CURSOR"
    VSCODE = "VSCODE"
    TERMINAL = "TERMINAL"
    UNKNOWN = "UNKNOWN"

class IDESensor:
    """
    Senses the physical IDE environment via process list.
    """
    
    def detect_environment(self) -> IDEnvironment:
        """Determines which IDE is currently driving the session."""
        running = self._get_running_processes()
        
        if "Cursor" in running or "Cursor Helper" in running:
            return IDEnvironment.CURSOR
        if "Code" in running or "Code Helper" in running or "VSCode" in running:
            return IDEnvironment.VSCODE
        
        # Fallback
        return IDEnvironment.TERMINAL

    def _get_running_processes(self) -> Set[str]:
        """Scans process list for IDE signatures."""
        try:
            # Quick pgrep check for known signatures
            # We check specific app names
            cmd = ["pgrep", "-fl", "Cursor|Code"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return set()
            
            output = result.stdout
            processes = set()
            for line in output.splitlines():
                if "Cursor" in line: processes.add("Cursor")
                if "Code" in line: processes.add("Code")
            
            return processes
        except Exception as e:
            logger.debug(f"Process scan failed: {e}")
            return set()
