"""
Docker Scavenger.
Wraps `docker logs` to capture container tracebacks.
"""

import subprocess
import logging
import asyncio

logger = logging.getLogger(__name__)

class DockerScavenger:
    async def get_running_containers(self):
        # Mock for simulation
        return [{"id": "a1b2c3d4", "image": "postgres:14", "name": "side-db"}]

    async def scan_logs(self, container_id: str):
        logger.info(f"🐳 [DOCKER]: Scanning logs for {container_id}...")
        # Simulating a DB error
        await asyncio.sleep(0.1)
        if container_id == "a1b2c3d4":
            return {
                "container": container_id,
                "log": "ERROR:  duplicate key value violates unique constraint \"users_pkey\""
            }
        return None
