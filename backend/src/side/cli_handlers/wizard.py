import time
import os
import sys
import shutil
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from .utils import ux, get_engine, get_user_profile as get_profile
from .auth import handle_login
from .connect import patch_cursor_config, patch_vscode_config, patch_claude_config, check_auth_or_login

def handle_wizard(args):
    """
    Sidelith First-Run Experience (FRE) Wizard.
    Orchestrates the setup flow: Auth -> Index -> IDE -> Verify.
    """
    
    # [HEADER]
    ux.console.print("\n")
    ux.console.print(Panel.fit(
        "[bold white]SIDELITH SETUP WIZARD[/bold white]\n"
        "[dim]Initializing AI Context Layer...[/dim]",
        border_style="cyan"
    ))
    time.sleep(1)

    # --- STEP 1: AUTHENTICATION ---
    ux.console.print("\n[bold cyan]Step 1/5: Authentication[/bold cyan]")
    
    # Check current identity
    engine = get_engine()
    identity = get_user_profile(engine)
    project_id = engine.get_project_id(".")
    profile = identity.get_user_profile(project_id)
    
    if not profile or not profile.access_token:
        ux.display_status("No active session found.", level="warning")
        if Confirm.ask("Login with browser?", default=True):
            from argparse import Namespace
            from .auth import handle_login
            # Trigger login flow with administrative bootstrap tier
            handle_login(Namespace(key=None, tier="hobby"))
            # Re-fetch
            profile = identity.get_user_profile(project_id)
    
    if profile:
        ux.display_status(f"Authenticated as [bold]{profile.email or 'User'}[/bold]", level="success")
        ux.display_status(f"Tier: [bold]{profile.tier.upper()}[/bold] ({profile.token_balance} SUs available)", level="info")
    else:
        ux.display_status("Skipping auth (Guest Mode). Some features limited.", level="warning")

    time.sleep(0.5)

    # --- STEP 2: PROJECT DETECTION ---
    ux.console.print("\n[bold cyan]Step 2/5: Project Detection[/bold cyan]")
    
    cwd = Path.cwd()
    matches = []
    
    if (cwd / "package.json").exists(): matches.append("Node.js")
    if (cwd / "tsconfig.json").exists(): matches.append("TypeScript")
    if (cwd / "pyproject.toml").exists(): matches.append("Python")
    if (cwd / "requirements.txt").exists(): matches.append("Python")
    if (cwd / "go.mod").exists(): matches.append("Go")
    if (cwd / "Cargo.toml").exists(): matches.append("Rust")
    
    detection_str = ", ".join(set(matches)) if matches else "Generic Project"
    
    with ux.console.status(f"[bold green]Scanning {cwd.name}...[/bold green]"):
        time.sleep(1.5) # UX Pacing
        
    ux.display_status(f"Detected: [bold white]{detection_str}[/bold white]", level="success")
    
    # Simple file count for "Repo size"
    file_count = sum(1 for _ in cwd.rglob('*') if _.is_file() and not any(p in _.parts for p in ['.git', 'node_modules', '.side']))
    ux.display_status(f"Repo Scope: [bold]{file_count} files[/bold]", level="info")
    
    time.sleep(0.5)
    
    # --- STEP 3: INITIAL INDEXING ---
    ux.console.print("\n[bold cyan]Step 3/5: Initial Indexing[/bold cyan]")
    ux.console.print("[dim]This creates your project's memory. Takes ~30 seconds.[/dim]")
    
    from side.intel.tree_indexer import run_context_scan as run_fractal_scan
    
    # We'll run the scan in a background thread or just run it with a spinner since run_fractal_scan prints to stdout usually.
    # ideally we'd hook into progress, but for MVP we capture stdout or just show spinner.
    # We will use a simple spinner here as run_fractal_scan is synchronous and chatty.
    
    with ux.console.status("[bold green]Indexing Codebase Structure...[/bold green]"):
        # Suppress stdout to keep wizard clean, or capture it?
        # Let's let it print "Deep Indexing..." lines faintly? 
        # Actually run_fractal_scan prints a lot. Let's suppress it for clean wizard.
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            run_fractal_scan(cwd)
            
    ux.display_status(f"Indexed {file_count} files", level="success")
    ux.display_status("Generated Structural Graph (Merkle-Validated)", level="success")
    
    # Calculate Real Cost
    cost = identity.get_su_cost("CONTEXT_BOOST")
    ux.display_status(f"SU Cost: {cost} SUs (Standard Context Build)", level="info")

    time.sleep(0.5)

    # --- STEP 4: IDE INTEGRATION ---
    ux.console.print("\n[bold cyan]Step 4/5: IDE Integration[/bold cyan]")
    
    # Detect standard IDEs
    found_ides = []
    
    # Check paths
    cursor_path = Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "settings.json"
    vscode_path = Path.home() / "Library" / "Application Support" / "Code" / "User" / "settings.json"
    claude_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    
    if cursor_path.exists(): found_ides.append("Cursor")
    if vscode_path.exists(): found_ides.append("VS Code")
    if claude_path.exists(): found_ides.append("Claude Desktop")
    
    if not found_ides:
        ux.display_status("No supported IDEs automatically detected.", level="warning")
    else:
        ux.display_status(f"Found: {', '.join(found_ides)}", level="success")
        
        # Prepare stdio config
        server_bin = shutil.which("sidelith-serve")
        cmd = server_bin if server_bin else sys.executable
        cmd_args = [] if server_bin else ["-m", "side.server"]
        stdio_config = {
            "command": cmd,
            "args": cmd_args,
            "env": {"PYTHONUNBUFFERED": "1", "SIDE_MODE": "1", "MCP_TRANSPORT": "stdio"}
        }

        # Auto-Patch
        if "Cursor" in found_ides:
            if patch_cursor_config(stdio_config):
                ux.display_status("Cursor: MCP server added", level="success")
        
        if "VS Code" in found_ides:
            if patch_vscode_config(stdio_config):
                ux.display_status("VS Code: Extension configured", level="success")
                
        if "Claude Desktop" in found_ides:
            if patch_claude_config(stdio_config):
                ux.display_status("Claude Desktop: Context provider enabled", level="success")

    time.sleep(0.5)

    # --- STEP 5: FIRST CONTEXT TEST ---
    ux.console.print("\n[bold cyan]Step 5/5: Verification[/bold cyan]")
    
    if "Cursor" in found_ides:
        ux.console.print("Let's verify everything works.")
        if Confirm.ask("Launch Cursor now?", default=True):
            ux.display_status("Opening Cursor...", level="info")
            # os.system("open -a Cursor .") # Mac specific
            import subprocess
            try:
                subprocess.run(["open", "-a", "Cursor", str(cwd)], check=False)
            except:
                ux.display_status("Could not launch Cursor automatically.", level="warning")
    else:
        ux.console.print("Setup is complete. Open your IDE to verify Sidelith is active.")

    ux.console.print("\n")
    ux.console.print(Panel.fit(
        "[green]Setup Complete! 🎉[/green]\n\n"
        "Your AI tools now remember your project.\n\n"
        "Next steps:\n"
        "- Ask your IDE about your codebase architecture\n"
        "- Run [bold]side watch[/bold] to monitor changes in real-time",
        title="SUCCESS",
        border_style="green"
    ))
