import logging
import argparse
from pathlib import Path
from side.tools.core import get_engine, get_audit_log as get_ledger
from side.intel.session_manager import SessionManager
from side.intel.history_player import HistoryPlayer

logger = logging.getLogger(__name__)

def handle_session(args: argparse.Namespace):
    """
    Handles 'side session' commands: start, stop, list, rewind.
    """
    project_path = Path(".").resolve()
    
    # Initialize Services
    # Initialize Services
    from side.tools.core import get_audit_log, get_engine
    audit = get_audit_log()
    engine = get_engine()
    
    manager = SessionManager(project_path, audit)
    
    command = args.subcommand
    
    if command == "start":
        name = args.name or "Session"
        sid = manager.start_session(name=name)
        print(f"🔴 Sidelith Session Started: {name}")
        print(f"   ID: {sid}")
        print("   Recording active. All context changes are tracked.")
        
    elif command == "stop":
        sid = manager.end_session()
        if sid:
            print(f"⏹️ Session Stopped: {sid}")
            print("   Checkpoint saved.")
        else:
            print("⚠️ No active session found.")
            
    elif command == "status":
        sid = manager.get_active_session_id()
        if sid:
            print(f"✅ Active Session: {sid}")
        else:
            print("⚪ No active session.")
            
    elif command == "rewind":
        if not args.target_session:
            print("❌ Error: --target-session ID is required for rewind.")
            return
            
        sid = args.target_session
        print(f"⚠️ WARNING: You are about to REWIND to session {sid}.")
        print("   This will perform a HARD GIT RESET and rollback intelligence.")
        print("   Any uncommitted changes will be LOST.")
        confirm = input("   Are you sure? (type 'rewind' to confirm): ")
        
        if confirm == "rewind":
            player = HistoryPlayer(project_path, audit)
            
            # Retrieve session details (commit) via Audit Service
            activities = audit.get_causal_timeline(sid)
            start_commit = None
            
            for act in activities:
                # get_causal_timeline already decrypts 'payload' and wraps in a dict
                data = act.get('data', {})
                if data.get('action') == 'session_start':
                    start_commit = data.get('payload', {}).get('start_commit')
                    break
                
            if start_commit:
                result = player.rollback_to_session(sid, start_commit)
                if result["success"]:
                    print(f"✅ Rewind Successful. You are now back at {start_commit[:8]}.")
                else:
                    print(f"❌ Rewind Failed: {result.get('error')}")
            else:
                print(f"❌ Could not find start_commit for session {sid} in local logs.")
        else:
            print("cancelled.")
        else:
            print("cancelled.")
