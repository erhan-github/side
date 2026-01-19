"""
Anonymous Telemetry Service for Side.

Sends non-PII health metrics to Supabase to enable product observability
while maintaining 100% user privacy.
"""

import asyncio
import logging
import os
import platform
import sys
from datetime import datetime, timezone
from typing import Dict, Any

from supabase import create_client, Client

logger = logging.getLogger(__name__)

class TelemetryService:
    """
    Handles anonymous heartbeat and error reporting to Supabase.
    """

    def __init__(self, project_hash: str):
        self.project_hash = project_hash
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        self.client: Client | None = None
        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
            except Exception as e:
                logger.error(f"Telemetry client failed to init: {e}")
        
    async def run_forever(self, interval: int = 3600) -> None:
        """
        Sends an anonymous heartbeat every hour.
        """
        if not self.client:
            logger.debug("Telemetry disabled (no credentials).")
            return

        logger.info("Starting Anonymous Telemetry Heartbeat.")
        
        while True:
            try:
                await self.send_heartbeat()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Telemetry error: {e}")
                await asyncio.sleep(600) # Wait 10 mins on error

    async def send_heartbeat(self) -> None:
        """Send an anonymous pulse to Supabase."""
        payload = {
            "project_hash": self.project_hash,
            "os": platform.system(),
            "os_release": platform.release(),
            "python_version": sys.version.split()[0],
            "app_version": "0.1.0", # Hardcoded for now
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Table 'heartbeats' must exist in Supabase
            self.client.table("heartbeats").insert(payload).execute()
            logger.debug("Telemetry heartbeat sent.")
        except Exception as e:
            logger.error(f"Failed to send heartbeat: {e}")

    async def report_error(self, error_type: str, context: str) -> None:
        """
        Manually report an error type (anonymous).
        """
        if not self.client:
            return

        import re
        # Scrub file paths (e.g. /Users/name/...) to prevent PII leak
        scrubbed_context = re.sub(r'/[Uu]sers/[^/]+/', '/USER/', context)
        # Scrub potential env var leaks
        scrubbed_context = re.sub(r'(?i)(key|token|secret|password)[=" \']+[^\s]+', r'\1=[REDACTED]', scrubbed_context)

        payload = {
            "project_hash": self.project_hash,
            "error_type": error_type,
            "context": scrubbed_context[:1000],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            self.client.table("error_logs").insert(payload).execute()
        except Exception:
            pass # Never crash on telemetry failure
