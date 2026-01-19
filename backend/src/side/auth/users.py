"""
User management for Side.

Stores users and generates API keys.
"""
import logging
import secrets
from datetime import datetime
from typing import Optional, Any
from dataclasses import dataclass, field
from fastapi import APIRouter, HTTPException, Header, Depends

router = APIRouter(prefix="/users", tags=["users"])


@dataclass
class User:
    """Side user."""
    id: str
    github_id: int
    username: str
    email: Optional[str]
    avatar_url: Optional[str]
    api_key: str
    tokens_monthly: int = 10_000  # Free tier default
    tokens_used: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# In-memory user storage (use database in production)
_users: dict[str, User] = {}          # api_key -> User
_github_ids: dict[int, str] = {}      # github_id -> api_key


def generate_api_key() -> str:
    """Generate a new Side API key."""
    return f"sk_{secrets.token_hex(24)}"


def create_user(
    github_id: int,
    username: str,
    email: Optional[str] = None,
    avatar_url: Optional[str] = None,
) -> User:
    """Create a new user with auto-generated API key."""
    api_key = generate_api_key()
    user_id = secrets.token_hex(8)
    
    user = User(
        id=user_id,
        github_id=github_id,
        username=username,
        email=email,
        avatar_url=avatar_url,
        api_key=api_key,
    )
    
    _users[api_key] = user
    _github_ids[github_id] = api_key
    
    return user


def get_user_by_api_key(api_key: str) -> Optional[User]:
    """Get user by API key."""
    return _users.get(api_key)


def get_user_by_github_id(github_id: int) -> Optional[User]:
    """Get user by GitHub ID."""
    api_key = _github_ids.get(github_id)
    if api_key:
        return _users.get(api_key)
    return None


def get_api_key_from_header(authorization: Optional[str]) -> Optional[str]:
    """Extract API key from Authorization header."""
    if not authorization:
        return None
    if authorization.startswith("Bearer "):
        return authorization[7:]
    return authorization



def get_current_user_dep(authorization: Optional[str] = Header(None)) -> User:
    """FastAPI dependency to get current user."""
    api_key = get_api_key_from_header(authorization)
    if not api_key:
        raise HTTPException(401, "Missing API key")
        
    user = get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(401, "Invalid API key")
    return user


# ==================
# API ENDPOINTS
# ==================

@router.get("/me")
async def get_current_user(user: User = Depends(get_current_user_dep)) -> dict[str, Any]:
    """Get the current authenticated user."""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar_url": user.avatar_url,
        "tokens_monthly": user.tokens_monthly,
        "tokens_used": user.tokens_used,
        "tokens_remaining": user.tokens_monthly - user.tokens_used,
        "api_key": user.api_key,  # Show their key
    }


@router.post("/regenerate-key")
async def regenerate_api_key(user: User = Depends(get_current_user_dep)) -> dict[str, str]:
    """Regenerate the user's API key."""
    old_key = user.api_key
    
    # Generate new key
    new_key = generate_api_key()
    
    # Update storage
    del _users[old_key]
    user.api_key = new_key
    _users[new_key] = user
    _github_ids[user.github_id] = new_key
    
    return {"api_key": new_key}
