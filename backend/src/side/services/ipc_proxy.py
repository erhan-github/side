import os
import socket
import json
import threading
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class IPCProxy:
    """
    Inter-Process Communication Proxy.
    Connects Sidelith to external simulators/tools via UDS.
    """

    def __init__(self, socket_path: Optional[str] = None):
        import secrets
        from side.env import env
        self.socket_path = socket_path or str(env.get_side_root() / "polyglot.sock")
        self.server_thread = None
        self.running = False
        
        # [MEMORY TUNNEL]: 256-bit Session Security
        self.session_token = secrets.token_hex(32)
        self._authenticated_conns = set()

    def start(self):
        """Starts the UDS proxy server in a background thread."""
        if self.running: return

        # Ensure directory exists
        Path(self.socket_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Cleanup old socket
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

        self.running = True
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        logger.info(f"🔌 [IPC_PROXY]: Listening on {self.socket_path}")

    def stop(self):
        self.running = False
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

    def _run_server(self):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.bind(self.socket_path)
            s.listen()
            s.settimeout(1.0)

            while self.running:
                try:
                    conn, addr = s.accept()
                    with conn:
                        data = conn.recv(4096)
                        if data:
                            self._handle_telemetry(data)
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"UDS Error: {e}")

    def _handle_telemetry(self, raw_data: bytes):
        """Processes incoming signals from unknown bridges."""
        try:
            payload = json.loads(raw_data.decode("utf8"))
            action = payload.get("action", "unknown")
            source = payload.get("source", "external")
            token = payload.get("token", "")

            # [MEMORY TUNNEL]: Enforce Handshake
            if not secrets.compare_digest(token, self.session_token):
                logger.warning(f"🛑 [MEMORY_TUNNEL]: Unauthorized access attempt from {source}")
                return

            if action == "HANDSHAKE":
                logger.info(f"🤝 [MEMORY_TUNNEL]: Handshake accepted from {source}")
                return
            
            print(f"\n📡 [IPC SIGNAL]: Received '{action}' from {source}")
            
            # Integrate with Strategic Mesh
            # In a real app, this would update the Transient Store or trigger a Pulse
            from side.pulse import pulse
            if action == "FLIGHT_CHECK":
                 pulse.check_pulse(payload.get("context", {}))
        
        except Exception as e:
            logger.error(f"Failed to handle telemetry: {e}")

# Singleton instance
ipc_proxy = IPCProxy()
