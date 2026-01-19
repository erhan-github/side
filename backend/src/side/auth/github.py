"""
GitHub OAuth flow for Side.

Premium onboarding: One click to authenticate.
"""
import os
import secrets
import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from .users import create_user, get_user_by_github_id

router = APIRouter(prefix="/auth", tags=["auth"])

# GitHub OAuth config
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:3000/auth/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


class OAuthState(BaseModel):
    """Temporary OAuth state storage."""
    state: str
    redirect_to: str = "/dashboard"


# In-memory state storage (use Redis in production)
_oauth_states: dict[str, OAuthState] = {}


@router.get("/github")
async def github_login(redirect_to: str = "/dashboard") -> RedirectResponse:
    """
    Start GitHub OAuth flow.
    
    Redirects user to GitHub for authorization.
    """
    if not GITHUB_CLIENT_ID:
        raise HTTPException(500, "GitHub OAuth not configured")
        
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    _oauth_states[state] = OAuthState(state=state, redirect_to=redirect_to)
    
    # Redirect to GitHub
    github_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={GITHUB_REDIRECT_URI}"
        f"&scope=read:user,user:email"
        f"&state={state}"
    )
    
    return RedirectResponse(github_url)


@router.get("/github/callback")
async def github_callback(code: str = Query(...), state: str = Query(...)) -> RedirectResponse:
    """
    Handle GitHub OAuth callback.
    
    Creates user account and generates API key.
    """
    # Verify state
    oauth_state = _oauth_states.pop(state, None)
    if not oauth_state:
        raise HTTPException(400, "Invalid state parameter")
        
    if not GITHUB_CLIENT_SECRET:
        raise HTTPException(500, "GitHub OAuth not configured")
        
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_REDIRECT_URI,
            },
            headers={"Accept": "application/json"},
        )
        
        if token_response.status_code != 200:
            raise HTTPException(400, "Failed to exchange code for token")
            
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(400, f"No access token: {token_data}")
            
        # Get user info from GitHub
        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )
        
        if user_response.status_code != 200:
            raise HTTPException(400, "Failed to get user info")
            
        github_user = user_response.json()
        
    # Create or get user
    user = get_user_by_github_id(github_user["id"])
    if not user:
        user = create_user(
            github_id=github_user["id"],
            username=github_user["login"],
            email=github_user.get("email"),
            avatar_url=github_user.get("avatar_url"),
        )
        
    # Redirect to frontend with API key
    redirect_url = f"{FRONTEND_URL}{oauth_state.redirect_to}?api_key={user.api_key}&new={1 if not user else 0}"
    return RedirectResponse(redirect_url)
