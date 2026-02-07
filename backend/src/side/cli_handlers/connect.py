from pathlib import Path
import json
import time
import shutil
import sys
from argparse import Namespace
from .utils import ux
from .auth import check_auth_or_login

def handle_connect(args):
    ux.display_status("Generating Integration Configuration...", level="info")
    
    # Check auth status
    profile = check_auth_or_login(tier=getattr(args, "tier", "hobby"))
    
    # Find the absolute path to the Server.
    server_bin = shutil.which("sidelith-serve")
    cmd = server_bin if server_bin else sys.executable
    cmd_args = [] if server_bin else ["-m", "side.server"]

    # Common standard config
    stdio_config = {
        "command": cmd,
        "args": cmd_args,
        "env": {
            "PYTHONUNBUFFERED": "1",
            "SIDE_MODE": "1",
            "MCP_TRANSPORT": "stdio"
        }
    }

    # Auto-detection
    if not any([args.cursor, args.vscode, args.claude, args.antigravity, args.codex, args.windsurf]):
        ux.display_status("Scanning for compatible IDEs...", level="info")
        
        # 1. Claude Check
        claude_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        if claude_path.exists():
            ux.display_status("Claude Desktop detected.", level="success")
            args.claude = True
        
        # 2. Cursor Check
        cursor_path = Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "settings.json"
        if cursor_path.exists():
            ux.display_status("Cursor detected.", level="success")
            args.cursor = True
            
        # 3. VS Code Check
        vscode_path = Path.home() / "Library" / "Application Support" / "Code" / "User" / "settings.json"
        if vscode_path.exists():
            ux.display_status("VS Code detected.", level="success")
            args.vscode = True

    # 1. CURSOR
    if args.cursor:
        ux.display_header("Cursor Configuration")
        ux.display_status("Ideally use HTTP SSE, but stdio provided for stability:", level="info")
        ux.display_panel(json.dumps({"sidelith": stdio_config}, indent=2), title="settings.json (mcpServers)")
        ux.display_footer()
        return

    # 2. VS CODE
    if args.vscode:
        ux.display_header("VS Code Configuration")
        ux.display_status("Add this to your MCP Extension settings:", level="info")
        ux.display_panel(json.dumps({"mcp.servers": {"sidelith": stdio_config}}, indent=2), title="settings.json")
        ux.display_footer()
        return

    # 3. OPENAI CODEX
    if args.codex:
        ux.display_header("OpenAI Codex Configuration")
        ux.display_status("Add this to your config.toml:", level="info")
        ux.display_panel(json.dumps({"mcpServers": {"sidelith": stdio_config}}, indent=2), title="config.toml")
        ux.display_footer()
        return

    # 4. WINDSURF
    if args.windsurf:
        ux.display_header("Windsurf Configuration")
        ux.display_panel(json.dumps({"mcpServers": {"sidelith": stdio_config}}, indent=2), title="Configuration")
        ux.display_footer()
        return

    # Intelligence Operations
    if args.antigravity:
        ux.display_header("System Configuration")
        ux.display_panel(json.dumps(stdio_config, indent=2), title="config.json")
        ux.display_footer()
        return

    # 5. CLAUDE (Auto-Patch + Default Fallback)
    if args.claude or (not args.cursor and not args.vscode and not args.antigravity):
        claude_config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        
        if claude_config_path.exists():
            print(f"   Found Claude Config: {claude_config_path}")
            try:
                # Backup
                backup_path = claude_config_path.with_suffix(f".bak.{int(time.time())}")
                shutil.copy(claude_config_path, backup_path)
                
                content = json.loads(claude_config_path.read_text())
                if "mcpServers" not in content:
                    content["mcpServers"] = {}
                
                content["mcpServers"]["sidelith"] = stdio_config
                claude_config_path.write_text(json.dumps(content, indent=2))
                print("\n✅ [SUCCESS]: Sidelith connected to Claude Desktop.")
                return 
            except Exception as e:
                print(f"   ⚠️ Auto-Patch Failed: {e}")
        
        # Fallback
        config = {
            "mcpServers": {
                "sidelith": stdio_config
            }
        }
        print("\n📋 COPY THIS TO YOUR 'claude_desktop_config.json':")
        print("---------------------------------------------------------------")
        print(json.dumps(config, indent=2))
        print("---------------------------------------------------------------")
