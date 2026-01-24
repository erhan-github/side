"""
Resource management for Side MCP.
"""

from pathlib import Path
from mcp.types import (
    Resource,
    TextContent,
)

from side.storage.simple_db import SimplifiedDatabase

class ResourceManager:
    def __init__(self):
        try:
            db_path = Path.home() / ".side" / "local.db"
            self.db = SimplifiedDatabase(db_path)
        except Exception:
            self.db = None

    def list_resources(self) -> list[Resource]:
        return [
            Resource(
                uri="side://monolith",
                name="Strategic Monolith",
                description="The live dashboard of project status, tasks, and credits.",
                mimeType="text/markdown"
            ),
            Resource(
                uri="side://activity",
                name="Activity Log (Live)",
                description="Recent system actions, costs, and traces.",
                mimeType="application/json"
            ),
            Resource(
                uri="side://profile",
                name="Pilot Profile",
                description="User stats, level, tech stack, and tier.",
                mimeType="application/json"
            ),
            Resource(
                uri="side://tips",
                name="Daily Intel",
                description="Strategic tips and system hacks.",
                mimeType="text/plain"
            )
        ]

    def read_resource(self, uri: str) -> str:
        project_id = self.db.get_project_id(Path.cwd())
        
        if uri == "side://tips":
            import random
            tips = [
                "💡 Tip: Use 'side://monolith' to track your budget in real-time.",
                "💡 Tip: Badges like 'The Janitor' grant instant SU bounties.",
                "💡 Tip: If you run out of credits, the Manus Drip refills you tomorrow.",
                "💡 Tip: Keep .env files out of git to avoid Security findings.",
                "💡 Hack: Use 'strategy' tool with specific context for better ROI.",
            ]
            return random.choice(tips)

        if uri == "side://monolith":
            # Read from disk for speed/consistency
            monolith_path = Path.cwd() / ".side" / "MONOLITH.md"
            if monolith_path.exists():
                return monolith_path.read_text()
            return "# Monolith Not Found\nRun `side.welcome` to initialize."
            
        if uri == "side://activity":
            # Query DB
            with self.db._connection() as conn:
                rows = conn.execute(
                    """
                    SELECT tool, action, cost_tokens, created_at 
                    FROM activities 
                    WHERE project_id = ? 
                    ORDER BY created_at DESC LIMIT 20
                    """,
                    (project_id,)
                ).fetchall()
                data = [dict(row) for row in rows]
                return str(data) # JSON string

        if uri == "side://profile":
            # Query DB
            prof = self.db.get_profile(project_id)
            # Add Gamification stats
            with self.db._connection() as conn:
                stats = conn.execute("SELECT * FROM user_stats WHERE project_id = ?", (project_id,)).fetchone()
                if stats:
                    prof["gamification"] = dict(stats)
            return str(prof)

        raise ValueError(f"Unknown resource: {uri}")

def register_resource_handlers(server, resource_manager: ResourceManager):
    @server.list_resources()
    async def list_resources() -> list[Resource]:
        return resource_manager.list_resources()

    @server.read_resource()
    async def read_resource(uri: str) -> list[TextContent]:
        content = resource_manager.read_resource(uri)
        return [TextContent(type="text", text=content)]
