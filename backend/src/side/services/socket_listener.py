import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

class SocketListenerService:
    """
    [KAR-6.16] Universal Polyglot Log Ingestor.
    Listens on a Unix Domain Socket for high-frequency signals from any language.
    """
    def __init__(self, buffer, socket_path: str = "/tmp/side.sock"):
        self.buffer = buffer
        self.socket_path = Path(socket_path)
        self._server = None
        self._running = False
        self._task = None

    async def start(self):
        """Starts the Unix Domain Socket server."""
        if self._running:
            return
        
        # Cleanup old socket if it exists
        if self.socket_path.exists():
            try:
                os.remove(self.socket_path)
            except Exception:
                pass

        try:
            self._running = True
            self._server = await asyncio.start_unix_server(
                self._handle_client, 
                path=str(self.socket_path)
            )
            
            # Set permissions so any local process can write
            os.chmod(self.socket_path, 0o666)
            
            # Use a background task to keep the server running if needed, 
            # though start_unix_server handles the loop.
            # We just need to keep a reference.
            self._task = asyncio.create_task(self._server.serve_forever())
            
            logger.info(f"📡 [SOCKET]: Polyglot Listener active on {self.socket_path}")
        except Exception as e:
            self._running = False
            logger.error(f"📡 [SOCKET]: Failed to start listener: {e}")

    async def stop(self):
        """Stops the server and cleans up the socket file."""
        self._running = False
        if self._task:
            self._task.cancel()
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        
        if self.socket_path.exists():
            try:
                os.remove(self.socket_path)
            except Exception:
                pass
        
        logger.info("📡 [SOCKET]: Polyglot Listener offline.")

    async def _handle_client(self, reader, writer):
        """Processes incoming data from a client connection."""
        try:
            while self._running:
                data = await reader.readline()
                if not data:
                    break
                
                line = data.decode().strip()
                if not line:
                    continue

                try:
                    payload = json.loads(line)
                    category = payload.get("category", "activity")
                    
                    # Offload to Unified Buffer for asynchronous batching
                    # Note: We don't await ingest here to keep the socket reading lightning fast
                    # UnifiedBuffer.ingest is already async and uses a lock, but we can fire-and-forget
                    # or await it since it's just a buffer append.
                    asyncio.create_task(self.buffer.ingest(category, payload))
                except json.JSONDecodeError:
                    logger.warning(f"📡 [SOCKET]: Received malformed JSON signal: {line[:50]}...")
                except Exception as e:
                    logger.error(f"📡 [SOCKET]: Error processing signal: {e}")
        except asyncio.CancelledError:
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
