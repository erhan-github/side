import logging
import argparse
from pathlib import Path
from side.tools.core import get_engine, get_ledger
from side.intel.session_manager import SessionManager
from side.intel.history_player import HistoryPlayer

logger = logging.getLogger(__name__)

def handle_session(args: argparse.Namespace):
    """
    Handles 'side session' commands: start, stop, list, rewind.
    """
    project_path = Path(".").resolve()
    
    # Initialize Services
    audit = get_audit_log()
    # Alternatively, instantiate directly if get_audit_service relies on context we don't have
    # For now, let's assume we can instantiate AuditService via a helper or directly
    
    # Using direct instantiationpattern from other handlers if needed, but let's try the core helper
    # If get_audit_service is bound to a specific request context, we might need a CLI-specific way.
    # Let's assume standard initialization for CLI.
    from side.storage.modules.base import ContextEngine
    from side.storage.modules.audit import AuditService
    
    # Quick Bootstrap
    db = get_engine()
    # We need the lower level engine for AuditService
    # This is a bit hacky, normally we'd have a full container. 
    # Let's instantiate Engine manually for CLI operation.
    engine = ContextEngine(db)
    audit = AuditService(engine)
    
    manager = SessionManager(project_path, audit)
    # Rewind Engine only needed for rewind command
    
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
            # We need the start_commit for this session. 
            # In a real impl, we'd query the DB/Session Ledger to find the start_commit for this SID.
            # For this MVP, we might need to load it from disk or assume the user provides the commit?
            # Better: SessionManager should allow querying session details.
            
            # TODO: Add `get_session_details(sid)` to manager or just query DB.
            # Hack for MVP: We assume the session file has it if it's the current one, 
            # or we query the audit log for 'session_start' event.
            
            # Query Audit for target commit
            with engine.connection() as conn:
                row = conn.execute(
                    "SELECT payload FROM activities WHERE session_id = ? AND action = 'session_start'", 
                    (sid,)
                ).fetchone()
                
            if row:
                import json
                payload = json.loads(row['payload'])
                # The payload in activities is 'sealed' by default in log_activity? 
                # Wait, log_activity calls shield.seal(payload).
                # We need to unseal it.
                from side.utils.crypto import shield
                try:
                    # audit.py stores 'payload' column which is JSON of sealed strings or?
                    # audit.py: payload = shield.seal(act.model_dump_json(include={'payload'}))
                    # So we need to decrypt.
                    raw_payload = shield.unseal(row['payload'])
                    data = json.loads(raw_payload)
                    start_commit = data.get('payload', {}).get('start_commit')
                except:
                    print("❌ Failed to retrieve session commit. Crypto error.")
                    return
                
                if start_commit:
                    result = player.rollback_to_session(sid, start_commit)
                    if result["success"]:
                        print(f"✅ Rewind Successful. You are now back at {start_commit[:8]}.")
                    else:
                        print(f"❌ Rewind Failed: {result.get('error')}")
                else:
                    print("❌ Could not find start_commit for this session.")
            else:
                print(f"❌ Session {sid} not found in local logs.")
        else:
            print("cancelled.")
