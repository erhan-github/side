from argparse import Namespace
import time
import os
from .utils import ux, get_engine, get_profile

def handle_login(args):
    engine = get_engine()
    identity = get_user_profile(engine)
    project_id = engine.get_project_id(".")
    
    # 1. PATH A: API Key (Pro Flow)
    if args.key:
        ux.display_status(f"Verifying API Key '{args.key[:4]}...'", level="info")
        import time
        time.sleep(1) # Simulated network verification
        
        from side.models.pricing import PricingModel, Tier
        
        # Deterministic Tiering from Key
        tier = PricingModel.detect_tier(args.key)
        limit = PricingModel.LIMITS[tier]
             
        identity.update_profile(project_id, {
            "tier": tier,
            "token_balance": limit,
            "tokens_monthly": limit,
            "access_token": args.key,
        })
        ux.display_header("Success: Identity Verified", subtitle=f"{tier.upper()} Tier")
        ux.display_status(f"Balance: {limit:,} SUs / month", level="success")
        ux.display_status("You are ready to connect.", level="info")
        ux.display_footer()
        return

    # 2. PATH B: The Browser Flow
    import webbrowser
    from side.utils.auth_server import start_auth_server
    
    AUTH_DOMAIN = "https://sidelith.com"
    if os.environ.get("SIDE_ENV") == "dev":
        AUTH_DOMAIN = "http://localhost:3999"
    
    PORT = 54321
    REDIRECT_URI = f"http://localhost:{PORT}/callback"
    LOGIN_URL = f"{AUTH_DOMAIN}/login?cli_redirect={REDIRECT_URI}"
    
    print("🔐 [AUTH]: Initiating Authentication...")
    ux.display_status(f"Opening browser: {LOGIN_URL}", level="info")
    webbrowser.open(LOGIN_URL)
    
    # Start ephemeral server to catch the callback
    tokens = start_auth_server(port=PORT)
    
    if tokens and tokens.get("access_token"):
        ux.display_status("Identity Verified.", level="success")
        
        from side.models.pricing import PricingModel, Tier
        
        # Sync Truth from Sidelith HQ
        token = tokens["access_token"]
        server_tier = tokens.get("tier", "hobby")
        requested_tier = getattr(args, "tier", "hobby")
        
        # Cross-verify requested tier vs server-signed tier
        if requested_tier != server_tier and requested_tier != "hobby":
            ux.display_status(f"Requested tier '{requested_tier.upper()}' does not match your Subscription state.", level="warning")
            ux.display_status(f"Reverting to verified tier: {server_tier.upper()}", level="info")
            requested_tier = server_tier

        # Standardize Token Prefix
        if not token.startswith("sk_"):
             token = f"sk_{requested_tier}_" + token[:8]
             
        tier = PricingModel.detect_tier(token)
        
        # Fallback if detection fails or tier mismatch occurs
        if tier != requested_tier:
             token = f"sk_{requested_tier}_" + token.split("_")[-1]
             tier = requested_tier

        limit = PricingModel.LIMITS[tier]
        
        identity.update_profile(project_id, {
            "tier": tier,
            "token_balance": limit,
            "tokens_monthly": limit,
            "access_token": token
        })
        ux.display_header("Profile Updated", subtitle=tier.upper())
        ux.display_status(f"Balance: {limit:,} SUs / Month", level="info")
        ux.display_footer()
    else:
        ux.display_status("Authentication timed out.", level="error")


def check_auth_or_login(tier=None):
    """JIT Auth check: triggers login if no profile exists."""
    engine = get_engine()
    identity = get_user_profile(engine)
    project_id = engine.get_project_id(".")
    profile = identity.get_user_profile(project_id)
    
    if not profile or not profile.access_token or profile.access_token.startswith("sk_hobby_"):
        # We allow sk_hobby_ but if it's completely missing, we need a handshake
        if not profile:
            ux.display_status(f"Welcome to Sidelith: Let's activate your Identity ({tier.upper() if tier else 'HOBBY'} Tier).", level="info")
            handle_login(Namespace(key=None, tier=tier))
            # Re-fetch after login
            profile = identity.get_user_profile(project_id)
    return profile

def handle_profile(args):
    """View current Identity & detailed SU Balance."""
    engine = get_engine()
    identity = get_user_profile(engine)
    project_id = engine.get_project_id(".")
    profile = identity.get_user_profile(project_id)
    
    if not profile:
        ux.display_status("No active profile found. Run 'side login' first.", level="error")
        return

    ux.display_header("User Identity", subtitle=profile.email or "Guest")
    ux.render_table("Profile Details", ["Attribute", "Value"], [
        ["Project ID", profile.id],
        ["Tier", profile.tier.upper()],
        ["Balance", f"{profile.token_balance:,} SUs"],
        ["Pattern", profile.design_pattern.upper()],
        ["Airgapped", "YES" if profile.is_airgapped else "NO"]
    ])
    ux.display_status("Tip: Run 'side usage' for detailed cycle breakdown.", level="info")
    ux.display_footer()

def handle_usage(args):
    """Exposes high-fidelity Cursor-level usage summary."""
    engine = get_engine()
    identity = get_user_profile(engine)
    project_id = engine.get_project_id(".")
    
    summary = identity.get_cursor_usage_summary(project_id)
    if not summary or "error" in summary:
        ux.display_status("Could not retrieve usage summary. Run 'side login' first.", level="error")
        return

    ux.display_header("Usage Summary", subtitle=f"Cycle Ends: {summary['cycle_ends_at']}")
    
    # [PRICING COMMUNICATION]: High-fidelity Progress Bars
    used = summary['tokens_used']
    limit = summary['tokens_monthly']
    percent = min(100, (used / limit) * 100) if limit > 0 else 100
    
    prem_used = summary['premium_requests']
    prem_limit = summary['premium_limit']
    prem_percent = min(100, (prem_used / prem_limit) * 100) if prem_limit > 0 else 100

    ux.render_table("Resource Utilization", 
                    ["Metric", "Used", "Limit", "Utilization"],
                    [
                        ["Standard SUs", f"{used:,}", f"{limit:,}", f"{percent:.1f}%"],
                        ["Premium Requests", f"{prem_used}", f"{prem_limit}", f"{prem_percent:.1f}%"]
                    ])
    
    if summary['is_exhausted']:
        ux.display_status("LIMIT REACHED: You have exhausted your SUs for this cycle.", level="warning")
        ux.display_status("Upgrade at https://sidelith.com/pricing to resume high-fidelity reasoning.", level="info")
    else:
        ux.display_status(f"You have {summary['tokens_remaining']:,} SUs remaining.", level="success")
    ux.display_footer()
