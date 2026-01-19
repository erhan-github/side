"""
Side MCP Server - "Grammarly for Strategy"

Exposes ForensicEngine as MCP tools for IDE integration (Cursor, Windsurf).
This is the bridge between the forensic intelligence and the developer's workflow.
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from side.intel.forensic_engine import ForensicEngine
from side.intel.intelligence_store import IntelligenceStore
from side.storage.simple_db import SimplifiedDatabase


class SideMCPServer:
    """MCP Server for Side forensic intelligence."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.server = Server("side")
        
        # Initialize core components
        self.db = SimplifiedDatabase(str(self.project_root / ".side" / "local.db"))
        self.intel_store = IntelligenceStore(self.db)
        self.forensic_engine = ForensicEngine(str(self.project_root))
        
        # Get or create project ID
        self.project_id = SimplifiedDatabase.get_project_id(self.project_root)
        
        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register all MCP tools."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="get_strategic_alerts",
                    description="Get active strategic alerts (security gaps, architectural bloat, stale docs) for the current project.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "severity": {
                                "type": "string",
                                "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                                "description": "Filter by severity level (optional)"
                            },
                            "rescan": {
                                "type": "boolean",
                                "description": "Force a new scan before returning results",
                                "default": False
                            }
                        }
                    }
                ),
                Tool(
                    name="get_strategic_iq",
                    description="Get the current Strategic IQ score (0-160) based on code health and architectural purity.",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="resolve_finding",
                    description="Mark a strategic finding as resolved after fixing the issue.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "finding_id": {
                                "type": "string",
                                "description": "The ID of the finding to resolve"
                            }
                        },
                        "required": ["finding_id"]
                    }
                ),
                Tool(
                    name="scan_project",
                    description="Run a full forensic scan of the project to detect new issues.",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls."""
            
            if name == "get_strategic_alerts":
                return await self._get_strategic_alerts(arguments)
            elif name == "get_strategic_iq":
                return await self._get_strategic_iq()
            elif name == "resolve_finding":
                return await self._resolve_finding(arguments)
            elif name == "scan_project":
                return await self._scan_project()
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

    async def _get_strategic_alerts(self, args: dict) -> list[TextContent]:
        """Get active strategic alerts."""
        severity = args.get("severity")
        rescan = args.get("rescan", False)
        
        # Optionally rescan
        if rescan:
            findings = await self.forensic_engine.scan()
            self.intel_store.store_findings(self.project_id, findings)
        
        # Get active findings
        findings = self.intel_store.get_active_findings(self.project_id, severity)
        
        if not findings:
            return [TextContent(
                type="text",
                text="✅ No active strategic alerts. Your codebase is clean!"
            )]
        
        # Format findings
        output = f"🔍 **Strategic Alerts** ({len(findings)} active)\n\n"
        
        for finding in findings:
            severity_emoji = {
                'CRITICAL': '🔴',
                'HIGH': '🟠',
                'MEDIUM': '🟡',
                'LOW': '⚪'
            }.get(finding['severity'], '⚪')
            
            output += f"{severity_emoji} **{finding['type']}** ({finding['severity']})\n"
            output += f"   📁 `{finding['file']}`"
            if finding['line']:
                output += f":{finding['line']}"
            output += "\n"
            output += f"   💬 {finding['message']}\n"
            output += f"   💡 {finding['action']}\n"
            output += f"   🆔 `{finding['id']}`\n\n"
        
        return [TextContent(type="text", text=output)]

    async def _get_strategic_iq(self) -> list[TextContent]:
        """Get Strategic IQ score."""
        score = self.intel_store.get_strategic_iq(self.project_id)
        stats = self.intel_store.get_finding_stats(self.project_id)
        
        # Simple grade mapping (0-160 scale -> percentage -> grade)
        percentage = min(100, (score / 160) * 100)
        if percentage >= 90: grade, label = "A", "Production Ready"
        elif percentage >= 80: grade, label = "B", "Needs Polish"
        elif percentage >= 70: grade, label = "C", "MVP Quality"
        elif percentage >= 60: grade, label = "D", "Significant Issues"
        else: grade, label = "F", "Critical Fixes Needed"
        
        output = f"**Strategic IQ: {grade}** ({label})\n\n"
        output += "**Active Findings:**\n"
        output += f"- 🔴 Critical: {stats['critical']}\n"
        output += f"- 🟠 High: {stats['high']}\n"
        output += f"- 🟡 Medium: {stats['medium']}\n"
        output += f"- ⚪ Low: {stats['low']}\n"
        
        return [TextContent(type="text", text=output)]

    async def _resolve_finding(self, args: dict) -> list[TextContent]:
        """Resolve a finding."""
        finding_id = args.get("finding_id")
        
        if not finding_id:
            return [TextContent(type="text", text="❌ Error: finding_id is required")]
        
        success = self.intel_store.resolve_finding(finding_id)
        
        if success:
            return [TextContent(type="text", text=f"✅ Finding `{finding_id}` marked as resolved")]
        else:
            return [TextContent(type="text", text=f"❌ Finding `{finding_id}` not found or already resolved")]

    async def _scan_project(self) -> list[TextContent]:
        """Run a full project scan."""
        findings = await self.forensic_engine.scan()
        new_count = self.intel_store.store_findings(self.project_id, findings)
        
        output = f"✅ Scan complete. Found {len(findings)} total issues ({new_count} new).\n\n"
        output += "Run `get_strategic_alerts` to see details."
        
        return [TextContent(type="text", text=output)]

    async def run(self) -> None:
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main() -> None:
    """Entry point for the MCP server."""
    import sys
    
    # Get project root from args or use current directory
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    
    server = SideMCPServer(project_root)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
