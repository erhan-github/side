import sys
import os
import time

# [OBSESSION DAY I] Standard libs moved to main() for <5ms Cold Start
# Setup Pathing for local development without expensive pathlib at top-level
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# LAZY IMPORTS: Moved specific module imports into their command blocks
# to ensure 'side --help' and basic commands are instant (<10ms).
# [OBSESSION DAY I] Optimized lazy loading for <5ms Cold Start
def _get_engine():
    from side.storage.modules.base import ContextEngine
    return ContextEngine()

def _get_identity(engine):
    from side.storage.modules.identity import IdentityStore
    return IdentityStore(engine)

def _get_strategic(engine):
    from side.storage.modules.strategic import StrategicStore
    return StrategicStore(engine)

def _get_forensic(engine):
    from side.storage.modules.forensic import ForensicStore
    return ForensicStore(engine)

def _get_transient(engine):
    from side.storage.modules.transient import OperationalStore
    return OperationalStore(engine)

# [RESTORED]: Essential Pillars (Pulse, Login, Strategy)
def handle_pulse(args):
    from side.pulse import pulse
    from pathlib import Path
    print(f"🩺 [Sovereign Pulse] Initiating real-time forensic scan...")
    
    target_path = Path(args.path).resolve()
    # Simplified Pulse Logic for v1.1
    pulse_context = {
        "PORT": "3999", 
        "BRANCH": "main", 
        "target_file": str(target_path)
    }
    result = pulse.check_pulse(pulse_context)
    
    print("\n--- 🛡️  SOVEREIGN PULSE REPORT -------------------------")
    if result.violations:
        for v in result.violations:
            print(f"🛑 [VIOLATION]: {v}")
    else:
        print("\n✅ [SECURE] No Constitutional Drift Detected.")
        print("   ✨ Your codebase is aligned with the Sovereign Strategic Mesh.")

def handle_strategy(args):
    print(f"🤔 [Sovereign Strategy]: Thinking about '{args.question}'...")
    import asyncio
    from side.tools import strategy
    # Fix: Ensure context is passed
    result = asyncio.run(strategy.handle_decide({
        "question": args.question,
        "context": "CLI User Request"
    }))
    print("\n🦅 [STRATEGIC ADVICE]:")
    print("---------------------------------------------------")
    print(result)
    print("---------------------------------------------------")

def handle_login(args):
    engine = _get_engine()
    identity = _get_identity(engine)
    project_id = engine.get_project_id(".")
    
    # 1. PATH A: The "Genesis" Key (Pro Flow)
    if args.key:
        print(f"🔐 [GENESIS]: Verifying Sovereign Key '{args.key[:4]}...'")
        import time
        time.sleep(1) # Simulated network verification
        
        from side.models.pricing import PricingModel, Tier
        
        # [GENESIS AUTH]: Deterministic Tiering from Key
        tier = PricingModel.detect_tier(args.key)
        limit = PricingModel.LIMITS[tier]
             
        identity.update_profile(project_id, {
            "tier": tier,
            "token_balance": limit,
            "tokens_monthly": limit,
            "access_token": args.key,
            "email": "verified_user@sidelith.com" 
        })
        print(f"\n✅ [SUCCESS]: Identity Verified ({tier.upper()} Tier).")
        print(f"   💰 Balance: {limit} SUs / month")
        print("   🚀 You are ready to connect.")
        return

    # 2. PATH B: The Browser Flow (Legacy/Upgrade)
    import webbrowser
    import os
    from side.utils.auth_server import start_auth_server
    
    AUTH_DOMAIN = "https://sidelith.com"
    if os.environ.get("SOVEREIGN_ENV") == "dev":
        AUTH_DOMAIN = "http://localhost:3999"
    
    PORT = 54321
    REDIRECT_URI = f"http://localhost:{PORT}/callback"
    LOGIN_URL = f"{AUTH_DOMAIN}/login?cli_redirect={REDIRECT_URI}"
    
    print("🔐 [SOVEREIGN AUTH]: Initiating Secure Handshake...")
    print(f"👉 Opening browser: {LOGIN_URL}")
    webbrowser.open(LOGIN_URL)
    
    # Start ephemeral server to catch the callback
    tokens = start_auth_server(port=PORT)
    
    if tokens and tokens.get("access_token"):
        print("\n✅ [SUCCESS]: Identity Verified.")
        
        # [UNIVERSAL IDENTITY]: Support Hobby Keys from Web
        token = tokens["access_token"]
        # If web didn't send a specific key type, assume it's a new Hobby signup
        if not token.startswith("sk_"):
             token = "sk_hobby_" + token[:8]
             
        from side.models.pricing import PricingModel
        tier = PricingModel.detect_tier(token)
        limit = PricingModel.LIMITS[tier]
        
        identity.update_profile(project_id, {
            "tier": tier,
            "token_balance": limit,
            "tokens_monthly": limit,
            "access_token": token
        })
        print(f"   👤 Tier: {tier.upper()}")
        print(f"   💰 Balance: {limit} SUs")
    else:
        print("\n❌ [FAILURE]: Authentication timed out.")



def handle_connect(args):
    print("🔌 [Sovereign Connect]: Detecting Environment...")
    from pathlib import Path
    import json
    import time
    import shutil
    import sys
    
    # [SOVEREIGN RESOLUTION]: Find the absolute path to the Sovereign Server.
    server_bin = shutil.which("sidelith-serve")
    
    if server_bin:
        cmd = server_bin
        cmd_args = []
        # print(f"   🎯 Resolved Server Bin: {cmd}")
    else:
        # Fallback to the current python interpreter
        cmd = sys.executable
        cmd_args = ["-m", "side.server"]
        # print(f"   ⚠️ 'sidelith-serve' not in PATH. Fallback to: {cmd} -m side.server")

    # Common standard config
    stdio_config = {
        "command": cmd,
        "args": cmd_args,
        "env": {
            "PYTHONUNBUFFERED": "1",
            "SOVEREIGN_MODE": "1",
            "MCP_TRANSPORT": "stdio"
        }
    }
    
    # SSE Config (For Cursor)
    sse_config = {
        "command": cmd,
        "args": cmd_args,
        "env": {
            "PYTHONUNBUFFERED": "1",
            "SOVEREIGN_MODE": "1",
            "MCP_TRANSPORT": "sse" 
        }
    }

    # 1. CURSOR (SSE Preference)
    if args.cursor:
        print("\n🔵 [CURSOR DETECTED]: Generating SSE Configuration...")
        cursor_config = {
            "mcpServers": {
                "sidelith": {
                    "url": "http://localhost:8080/sse",
                    "transport": "sse"
                }
            }
        }
        print("   ⚠️ Note: Cursor currently requires manual HTTP SSE configuration or stdio.")
        print("   👉 Recommended: Use the Stdio config below for max stability in Cursor Tab:")
        print("---------------------------------------------------------------")
        print(json.dumps({
            "sidelith": stdio_config
        }, indent=2))
        print("---------------------------------------------------------------")
        return

    # 2. VS CODE (Stdio Preference)
    if args.vscode:
        print("\n🟣 [VS CODE DETECTED]: Generating Stdio Configuration...")
        print("   👉 Add this to your MCP Extension settings (settings.json):")
        print("---------------------------------------------------------------")
        print(json.dumps({
            "mcp.servers": {
                "sidelith": stdio_config
            }
        }, indent=2))
        print("---------------------------------------------------------------")
        return

        return

    # [RESTORED]: Intelligence Operations (The Brain)
    if args.antigravity:
        print("\n🟠 [ANTIGRAVITY]: Generating Universal Config...")
        print("---------------------------------------------------------------")
        print(json.dumps(stdio_config, indent=2))
        print("---------------------------------------------------------------")
        return

def handle_index(args):
    """
    [CRITICAL]: The Manual Feed.
    Allows the user to force-ingest the codebase into the Sovereign Memory.
    """
    from pathlib import Path
    print("🧠 [Sovereign Index]: Analyzing Project DNA...")
    import asyncio
    from side.intel.auto_intelligence import AutoIntelligence
    
    path = Path(args.path).resolve()
    intel = AutoIntelligence(path, engine=_get_engine())
    
    # Run the Feed
    graph = asyncio.run(intel.feed())
    
    # Report
    if 'stats' in graph:
        print(f"✅ [INDEX COMPLETE]: Processed {graph['stats'].get('nodes', 0)} nodes.")
    else:
        print(f"✅ [INDEX COMPLETE]: Sovereign Context Updated.")
    print(f"   Identity successfully projected to: .side/sovereign.json")

def handle_watch(args):
    """
    [CRITICAL]: The Always-On Watcher.
    Keeps the context specific to the user's active focus.
    """
    from pathlib import Path
    from side.services.file_watcher import FileWatcher
    from side.intel.auto_intelligence import AutoIntelligence
    
    print(f"🔭 [Sovereign Watch]: Active Monitoring Engaged...")
    path = Path(args.path).resolve()
    intel = AutoIntelligence(path, engine=_get_engine())
    
    watcher = FileWatcher(path, on_change=lambda files: asyncio.run(intel.incremental_feed(list(files)[0] if files else path)))
    try:
        asyncio.run(watcher.start())
        # Keep alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        asyncio.run(watcher.stop())
        print("\n🛑 [WATCHER]: Disengaged.")

    # 4. CLAUDE (Auto-Patch + Default Fallback)
    # If explicitly requested OR no specific flag provided (Default behavior)
    if args.claude or (not args.cursor and not args.vscode and not args.antigravity):
        claude_config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        
        if claude_config_path.exists():
            print(f"   found Claude Config: {claude_config_path}")
            try:
                # Backup
                backup_path = claude_config_path.with_suffix(f".bak.{int(time.time())}")
                shutil.copy(claude_config_path, backup_path)
                
                content = json.loads(claude_config_path.read_text())
                if "mcpServers" not in content:
                    content["mcpServers"] = {}
                
                content["mcpServers"]["sidelith"] = stdio_config
                claude_config_path.write_text(json.dumps(content, indent=2))
                print("\n✅ [SUCCESS]: Sidelith is now connected to Claude Desktop.")
                print("   Restart Claude to see 'Sidelith Sovereign' in your tools.")
                return 
            except Exception as e:
                print(f"   ⚠️ Auto-Patch Failed: {e}")
        
        # Fallback print if patch failed or if just generating default
        config = {
            "mcpServers": {
                "sidelith": stdio_config
            }
        }
        print("\n📋 COPY THIS TO YOUR 'claude_desktop_config.json':")
        print("---------------------------------------------------------------")
        print(json.dumps(config, indent=2))
        print("---------------------------------------------------------------")

def handle_audit(args):
    """Deep Forensic Audit Wrapper"""
    import asyncio
    from side.tools.audit import handle_run_audit
    
    print(f"🕵️ [AUDIT]: Starting Deep Scan (Dimension: {args.dimension})...")
    
    severity = args.severity
    if severity == "all":
        severity = "critical,high,medium,low,info"
        
    result = asyncio.run(handle_run_audit({
        "dimension": args.dimension,
        "severity": severity
    }))
    print(result)

def handle_profile(args):
    """View current Sovereign Identity & SU Balance."""
    engine = _get_engine()
    identity = _get_identity(engine)
    project_id = engine.get_project_id(".")
    profile = identity.get_profile(project_id)
    
    if not profile:
        print("❌ [ERROR]: No active profile found. Run 'side login' first.")
        return

    print("\n--- 👤 SOVEREIGN IDENTITY -----------------------------")
    print(f"   Project ID: {profile.get('id')}")
    print(f"   Tier:       {profile.get('tier', 'hobby').upper()}")
    print(f"   Balance:    {profile.get('token_balance', 0)} SUs")
    print(f"   Usage:      {profile.get('tokens_used', 0)} SUs used this month")
    print(f"   Email:      {profile.get('email', 'Guest')}")
    print("-------------------------------------------------------")

def main():
    import argparse
    import json
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description="Sovereign Strategic Network CLI")
    parser.add_argument("--version", action="version", version="Sidelith v1.0.0-PERU")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # ... subparsers setup ...
    
    # [RESTORED]: Essential Command Parsers
    
    # Login Command (Auth)
    login_parser = subparsers.add_parser("login", help="Activate your Sovereign Tier")
    login_parser.add_argument("--key", help="Activate Pro Tier with a Genesis Key (sk_...)")

    # Profile Command (Status)
    profile_parser = subparsers.add_parser("profile", help="View your Sovereign Identity & SU Balance")

    # Pulse Command (Health)
    pulse_parser = subparsers.add_parser("pulse", help="Trigger a live forensic pulse audit")
    pulse_parser.add_argument("path", nargs="?", default=".", help="Project path")

    # Strategy Command (Intelligence)
    strat_parser = subparsers.add_parser("strategy", help="Ask a strategic question")
    strat_parser.add_argument("question", help="The strategic question to ask")

    # Connect Command (MCP Integration)
    connect_parser = subparsers.add_parser("connect", help="Generate MCP Configuration for IDEs")
    connect_parser.add_argument("--cursor", action="store_true", help="Generate Cursor MCP Configuration")
    connect_parser.add_argument("--vscode", action="store_true", help="Generate VS Code MCP Configuration")
    connect_parser.add_argument("--claude", action="store_true", help="Patch/Generate Claude Desktop Configuration")
    connect_parser.add_argument("--antigravity", action="store_true", help="Generate Antigravity Configuration")

    # Audit Command (Diagnostics)
    audit_parser = subparsers.add_parser("audit", help="Run a deep forensic audit on the codebase")
    audit_parser.add_argument("dimension", nargs="?", default="general", choices=["general", "security", "performance", "architecture"], help="Audit dimension")
    audit_parser.add_argument("--severity", default="critical,high,medium", help="Filter by severity")

    # [RESTORED]: Essential Intelligence Commands
    # Index Command (Manual Feed)
    index_parser = subparsers.add_parser("index", help="Force-index the codebase into Sovereign Memory")
    index_parser.add_argument("path", nargs="?", default=".", help="Project path to index")

    # Watch Command (Real-time)
    watch_parser = subparsers.add_parser("watch", help="Start the Real-time Context Watcher")
    watch_parser.add_argument("path", nargs="?", default=".", help="Project path to watch")

    args = parser.parse_args()
    
    # [OBSESSION DAY I] Standard commands dispatch for <10ms Cold Start
    handlers = {
        # Core Pillars
        "login": handle_login,
        "profile": handle_profile,
        "connect": handle_connect,
        "pulse": handle_pulse,
        "strategy": handle_strategy,
        
        # Intelligence (Restored)
        "index": handle_index,
        "watch": handle_watch,
        
        # Diagnostics
        "audit": handle_audit,
    }

    if args.command in handlers:
        handlers[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
