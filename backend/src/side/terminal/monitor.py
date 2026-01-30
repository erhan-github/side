import socket
import json
import logging
import asyncio
from pathlib import Path
from typing import Optional
from side.storage.simple_db import SimplifiedDatabase

logger = logging.getLogger(__name__)

class TerminalMonitor:
    """
    Sidelith Terminal Monitor: Listens for shell execution events via UDP.
    Feeds the Local Context Graph with real-time runtime data.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 3998):
        self.host = host
        self.port = port
        self.db = SimplifiedDatabase()
        self.project_id = self.db.get_project_id(str(Path.cwd()))
        self.is_running = False

    async def start(self):
        """Starts the UDP server to listen for shell hooks."""
        self.is_running = True
        
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        sock.setblocking(False)
        
        logger.info(f"🔭 Terminal Monitor active on {self.host}:{self.port}")
        print(f"🔭 Sidelith Terminal Monitor active on {self.host}:{self.port}")

        loop = asyncio.get_running_loop()
        
        while self.is_running:
            try:
                data = await loop.sock_recv(sock, 1024)
                message = data.decode().strip()
                await self._process_message(message)
            except Exception as e:
                if self.is_running:
                    logger.error(f"Monitor error: {e}")
                await asyncio.sleep(0.1)

    async def _process_message(self, message: str):
        """
        Parses the shell hook message.
        Expected format: "CMD|EXIT_CODE|CWD"
        """
        try:
            parts = message.split("|")
            if len(parts) < 3:
                return

            command = parts[0]
            exit_code = parts[1]
            cwd = parts[2]

            # Log to Activity Ledger
            self.db.forensic.log_activity(
                project_id=self.project_id,
                tool="terminal",
                action="TERMINAL_EXEC",
                cost_tokens=0,
                payload={
                    "command": command,
                    "exit_code": exit_code,
                    "cwd": cwd,
                    "status": "FAIL" if exit_code != "0" else "SUCCESS"
                }
            )
            
            if exit_code != "0":
                print(f"🚨 [RUNTIME ERROR]: Command '{command}' failed with code {exit_code}")
                # Future: Trigger auto-diagnostic or 'ask side'
            
        except Exception as e:
            logger.error(f"Failed to process terminal message: {e}")

    def stop(self):
        self.is_running = False

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    monitor = TerminalMonitor()
    try:
        asyncio.run(monitor.start())
    except KeyboardInterrupt:
        monitor.stop()
