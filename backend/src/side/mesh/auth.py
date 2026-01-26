"""
Authentication for Side.

Simple token-based model. No feature tiers.
"""
import os
import secrets
from typing import Optional
from dataclasses import dataclass


@dataclass
class UserInfo:
    """Info about an authenticated user."""
    user_id: str
    valid: bool
    tokens_remaining: int = 0


# In-memory user store (replace with database in production)
_USERS = {}


def _load_users_from_env():
    """Load users from environment variable."""
    # Format: SIDE_USERS="sk_xxx:user1:10000,sk_yyy:user2:50000"
    # (api_key:user_id:tokens_per_month)
    users_str = os.getenv("SIDE_USERS", "")
    if not users_str:
        return
        
    for entry in users_str.split(","):
        parts = entry.strip().split(":")
        if len(parts) == 3:
            key, user_id, tokens = parts
            _USERS[key] = {"user_id": user_id, "tokens": int(tokens)}


def generate_api_key() -> str:
    """Generate a new API key."""
    return f"sk_{secrets.token_hex(16)}"


def validate_api_key(api_key: Optional[str]) -> UserInfo:
    """Validate an API key and return user info."""
    if not api_key:
        return UserInfo(user_id="", valid=False)
        
    if not _USERS:
        _load_users_from_env()
        
    user_data = _USERS.get(api_key)
    if user_data:
        return UserInfo(
            user_id=user_data["user_id"],
            valid=True,
            tokens_remaining=user_data.get("tokens", 10000),
        )
        
    return UserInfo(user_id="", valid=False)


def get_api_key_from_header(authorization: Optional[str]) -> Optional[str]:
    """Extract API key from Authorization header."""
    if not authorization:
        return None
    if authorization.startswith("Bearer "):
        return authorization[7:]
    return authorization
