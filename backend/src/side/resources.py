"""
Resource management for Side MCP.
"""

from pathlib import Path
from mcp.types import (
    Resource,
    TextContent,
)

class ResourceManager:
    def __init__(self):
        pass # No DB connection needed for Sidelith Prime

    def list_resources(self) -> list[Resource]:
        return [
            Resource(
                uri="side://tips",
                name="Daily Intel",
                description="Strategic tips and system hacks.",
                mimeType="text/plain"
            )
        ]

    def read_resource(self, uri: str) -> str:
        if uri == "side://tips":
            import random
            tips = [
                "💡 Tip: Sidelith Prime is 100% local and fast (<2ms).",
                "💡 Tip: Use 'side fix' to capture your decision intent.",
                "💡 Tip: 'side sync' downloads the latest Global Precedents.",
            ]
            return random.choice(tips)

        raise ValueError(f"Unknown resource: {uri}")

def register_resource_handlers(server, resource_manager: ResourceManager):
    @server.list_resources()
    async def list_resources() -> list[Resource]:
        return resource_manager.list_resources()

    @server.read_resource()
    async def read_resource(uri: str) -> list[TextContent]:
        content = resource_manager.read_resource(uri)
        return [TextContent(type="text", text=content)]
