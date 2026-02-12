"""
JetBrains Bridge.

This module defines the protocol for the Sidelith IntelliJ Plugin.
It acts as the receiver for Context Events (Cursor Movement, File Selection)
from the Java/Kotlin ecosystem.
"""

from typing import Dict, Any, Optional
import time
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class JetBrainsContext:
    project_path: str
    file_path: str
    caret_offset: int
    selection_start: int
    selection_end: int
    content_snippet: str
    plugin_version: str

class JetBrainsBridge:
    """
    Protocol Adapter for IntelliJ/PyCharm.
    Exposes ingest methods for the HTTP API to call.
    """
    
    def __init__(self):
        self.last_context: Optional[JetBrainsContext] = None
        self.connected_since = 0.0

    def handshake(self, version: str) -> Dict[str, Any]:
        """Called when Plugin initializes."""
        self.connected_since = time.time()
        logger.info(f"🔌 [JETBRAINS]: Plugin v{version} Connected.")
        return {
            "status": "CONNECTED",
            "server_version": "3.1.0",
            "capabilities": ["INJECT_CONTEXT", "READ_INTENT", "VERIFY_FIX"]
        }

    def receive_context_update(self, payload: Dict[str, Any]) -> str:
        """
        Ingests a context snapshot from the IDE.
        Corresponds to 'com.sidelith.plugin.ContextListener'.
        """
        try:
            ctx = JetBrainsContext(
                project_path=payload.get("projectPath", ""),
                file_path=payload.get("filePath", ""),
                caret_offset=payload.get("caretOffset", 0),
                selection_start=payload.get("selectionStart", 0),
                selection_end=payload.get("selectionEnd", 0),
                content_snippet=payload.get("contentSnippet", ""),
                plugin_version=payload.get("pluginVersion", "0.0.0")
            )
            
            # Refactor: Use Phoenix Protocol (AuditService)
            # We treat IDE context updates as 'Work Context' signals for Layer 2 RAM.
            # Refactor: Use Phoenix Protocol (AuditService)
            from side.storage.modules.base import ContextEngine
            from side.storage.modules.audit import AuditService
            from pathlib import Path
            
            engine = ContextEngine()
            ledger = AuditService(engine)
            
            # Save as active work context
            ledger.save_work_context(
                project_path=str(Path(ctx.project_path)),
                focus_area=ctx.file_path,
                recent_files=[ctx.file_path],
                recent_commits=[], # IDE doesn't send commits yet
                current_branch="unknown",
                confidence=1.0
            )
            
            self.last_context = ctx
            
            logger.debug(f"🔌 [JETBRAINS]: Context Updated & Synced to Ledger: {ctx.file_path}")
            return "ACK"
        except Exception as e:
            logger.error(f"JetBrains Ingest Error: {e}")
            return "ERR"

    def get_status(self) -> Dict[str, Any]:
        if not self.last_context:
            return {"connected": False}
        return {
            "connected": True,
            "uptime": time.time() - self.connected_since,
            "last_file": self.last_context.file_path,
            "plugin_version": self.last_context.plugin_version
        }

# Singleton Bridge
jetbrains_bridge = JetBrainsBridge()
