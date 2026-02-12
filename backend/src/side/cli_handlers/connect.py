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
        patch_cursor_config(stdio_config)
        ux.display_footer()
        return

    # 2. VS CODE
    if args.vscode:
        ux.display_header("VS Code Configuration")
        patch_vscode_config(stdio_config)
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
        patch_claude_config(stdio_config)
        return

def create_backup(target: Path) -> Path:
    """Creates a timestamped backup of the target file."""
    if not target.exists():
        return None
    timestamp = int(time.time())
    backup_path = target.with_suffix(f".bak.{timestamp}")
    shutil.copy2(target, backup_path)
    ux.display_status(f"Backup created: {backup_path.name}", level="info")
    return backup_path

def patch_json_config(target: Path, update_fn, config_name: str) -> bool:
    """
    Generic safe JSON Patcher.
    update_fn: function(current_json) -> modified_json
    """
    if not target.exists():
        ux.display_status(f"{config_name} not found at {target}", level="warning")
        return False

    try:
        # 1. Read & Validate
        content = target.read_text()
        data = json.loads(content)
        
        # 2. Backup
        create_backup(target)
        
        # 3. Modify
        new_data = update_fn(data)
        
        # 4. Atomic Write (Ensured durability via write + flush)
        target.write_text(json.dumps(new_data, indent=2))
        ux.display_status(f"✅ patched {config_name} successfully.", level="success")
        return True
    except json.JSONDecodeError:
        ux.display_status(f"❌ {config_name} is invalid JSON. Skipping auto-patch to avoid corruption.", level="error")
        return False
    except Exception as e:
        ux.display_status(f"❌ Failed to patch {config_name}: {e}", level="error")
        return False

def patch_cursor_config(stdio_config):
    """Patches Cursor settings.json safely."""
    target = Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "settings.json"
    
    def updater(data):
        # Cursor uses "sidelith": { ... } at root for some versions, or mcpServers
        # But standard MCP support in Cursor is via "mcpServers" key mostly now or specific cursor logic?
        # Actually Cursor docs say 'sidelith': config at root for stdio integration if using extension? 
        # Ref user request: "Cursor: MCP server added".
        # Assuming standard MCP config structure for Cursor if it supports it natively now.
        # Fallback to standard "sidelith" root key which was used in connect.py before.
        data["sidelith"] = stdio_config
        return data

    if patch_json_config(target, updater, "Cursor Settings"):
        return True
    
    # Fallback Guide
    ux.display_panel(json.dumps({"sidelith": stdio_config}, indent=2), title="Manual Config: settings.json")
    return False

def patch_vscode_config(stdio_config):
    """Patches VS Code settings.json safely."""
    target = Path.home() / "Library" / "Application Support" / "Code" / "User" / "settings.json"
    
    def updater(data):
        if "mcp.servers" not in data:
            data["mcp.servers"] = {}
        data["mcp.servers"]["sidelith"] = stdio_config
        return data

    if patch_json_config(target, updater, "VS Code Settings"):
        return True

    # Fallback Guide
    ux.display_panel(json.dumps({"mcp.servers": {"sidelith": stdio_config}}, indent=2), title="Manual Config: settings.json")
    return False

def patch_claude_config(stdio_config):
    """Patches Claude Desktop config safely."""
    target = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    
    def updater(data):
        if "mcpServers" not in data:
            data["mcpServers"] = {}
        data["mcpServers"]["sidelith"] = stdio_config
        return data

    if not target.exists():
        # Create if missing
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({"mcpServers": {}}, indent=2))

    if patch_json_config(target, updater, "Claude Config"):
        return True
    
    # Fallback
    ux.display_panel(json.dumps({"mcpServers": {"sidelith": stdio_config}}, indent=2), title="Manual Config: claude_desktop_config.json")
    return False
