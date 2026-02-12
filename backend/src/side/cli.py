import sys
import os
import argparse
from side.cli_handlers.auth import handle_login, handle_profile, handle_usage
from side.cli_handlers.connect import handle_connect
from side.cli_handlers.audit import handle_audit, handle_health
from side.cli_handlers.intel import handle_index, handle_watch, handle_strategy, handle_maintenance
from side.cli_handlers.wizard import handle_wizard

# Standard libs setup for fast start
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


def main():
    parser = argparse.ArgumentParser(description="Sidelith CLI")
    parser.add_argument("--version", action="version", version="Sidelith v1.0.0-REFRACTED")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Auth
    login_parser = subparsers.add_parser("login", help="Activate your User Profile")
    login_parser.add_argument("--key", help="Activate Pro Tier with an API Key")

    # Profile
    profile_parser = subparsers.add_parser("profile", help="View your Identity & SU Balance")

    # Usage
    usage_parser = subparsers.add_parser("usage", help="View detailed usage & cycle status")

    # Connect
    connect_parser = subparsers.add_parser("connect", help="Generate IDE Configuration")
    connect_parser.add_argument("--cursor", action="store_true", help="Cursor Config")
    connect_parser.add_argument("--vscode", action="store_true", help="VS Code Config")
    connect_parser.add_argument("--claude", action="store_true", help="Claude Desktop Config")
    connect_parser.add_argument("--antigravity", action="store_true", help="Antigravity Config")
    connect_parser.add_argument("--codex", action="store_true", help="OpenAI Codex Config")
    connect_parser.add_argument("--windsurf", action="store_true", help="Windsurf Config")
    connect_parser.add_argument("--tier", default="hobby", choices=["hobby", "pro", "elite"], help="Tier Activation")

    # Diagnostics
    health_parser = subparsers.add_parser("health", help="Trigger a system health audit")
    health_parser.add_argument("path", nargs="?", default=".", help="Project path")

    audit_parser = subparsers.add_parser("audit", help="Run a codebase audit")
    audit_parser.add_argument("category", nargs="?", default="general", choices=["general", "security", "performance", "architecture"], help="Audit category")
    audit_parser.add_argument("--severity", default="critical,high,medium", help="Filter by severity")

    # Intelligence
    index_parser = subparsers.add_parser("index", help="Index the codebase")
    index_parser.add_argument("path", nargs="?", default=".", help="Project path to index")

    watch_parser = subparsers.add_parser("watch", help="Start the Real-time Watcher")
    watch_parser.add_argument("path", nargs="?", default=".", help="Project path to watch")

    strat_parser = subparsers.add_parser("strategy", help="Ask a strategic question")
    strat_parser.add_argument("question", help="The question to ask")
    
    # Maintenance
    maint_parser = subparsers.add_parser("maintenance", help="Run system maintenance (VACUUM/Backup)")
    
    # Signing
    # Wizard
    wizard_parser = subparsers.add_parser("wizard", help="Run the First-Run Experience Setup Wizard")
    
    args = parser.parse_args()

    handlers = {
        "login": handle_login,
        "profile": handle_profile,
        "usage": handle_usage,
        "connect": handle_connect,
        "health": handle_health,
        "audit": handle_audit,
        "index": handle_index,
        "watch": handle_watch,
        "strategy": handle_strategy,
        "maintenance": handle_maintenance,
        "wizard": handle_wizard
    }

    if args.command in handlers:
        handlers[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
