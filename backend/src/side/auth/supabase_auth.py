"""
Side Auth - Supabase-based authentication.

Uses Supabase for:
- GitHub OAuth (identity only, no repo access)
- User storage (profiles table)
- API key management
- Token tracking

Local-first principle: We only store identity, never code.
"""
import os
import secrets
from typing import Optional
from dataclasses import dataclass
from supabase import create_client, Client

# Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


def get_supabase_client(service_role: bool = False) -> Optional[Client]:
    """Get Supabase client."""
    if not SUPABASE_URL:
        return None
    key = SUPABASE_SERVICE_KEY if service_role else SUPABASE_ANON_KEY
    if not key:
        return None
    return create_client(SUPABASE_URL, key)


@dataclass
class UserInfo:
    """Authenticated user info."""
    user_id: str
    email: Optional[str]
    api_key: str
    tokens_monthly: int
    tokens_used: int
    valid: bool


def generate_api_key() -> str:
    """Generate a new Side API key."""
    return f"sk_{secrets.token_hex(24)}"


def get_user_by_api_key(api_key: str) -> Optional[UserInfo]:
    """Get user from Supabase by API key."""
    client = get_supabase_client(service_role=True)
    if not client:
        return None
        
    try:
        result = client.table("profiles").select("*").eq("api_key", api_key).single().execute()
        if result.data:
            return UserInfo(
                user_id=result.data["id"],
                email=result.data.get("email"),
                api_key=result.data["api_key"],
                tokens_monthly=result.data.get("tokens_monthly", 10000),
                tokens_used=result.data.get("tokens_used", 0),
                valid=True,
            )
    except Exception:
        pass
    return None


def create_user_profile(user_id: str, email: Optional[str] = None) -> Optional[str]:
    """Create a profile with API key for a new user."""
    client = get_supabase_client(service_role=True)
    if not client:
        return None
        
    api_key = generate_api_key()
    
    try:
        client.table("profiles").insert({
            "id": user_id,
            "email": email,
            "api_key": api_key,
            "tokens_monthly": 10000,  # Free tier
            "tokens_used": 0,
        }).execute()
        return api_key
    except Exception:
        return None


def record_token_usage(user_id: str, tokens: int) -> bool:
    """Record token usage for a user."""
    client = get_supabase_client(service_role=True)
    if not client:
        return False
        
    try:
        # Increment tokens_used
        client.rpc("increment_tokens", {"user_id": user_id, "amount": tokens}).execute()
        return True
    except Exception:
        return False


def get_api_key_from_header(authorization: Optional[str]) -> Optional[str]:
    """Extract API key from Authorization header."""
    if not authorization:
        return None
    if authorization.startswith("Bearer "):
        return authorization[7:]
    return authorization


def validate_api_key(api_key: Optional[str]) -> UserInfo:
    """Validate an API key and return user info."""
    if not api_key:
        return UserInfo(user_id="", email=None, api_key="", tokens_monthly=0, tokens_used=0, valid=False)
        
    user = get_user_by_api_key(api_key)
    if user:
        return user
        
    return UserInfo(user_id="", email=None, api_key="", tokens_monthly=0, tokens_used=0, valid=False)
