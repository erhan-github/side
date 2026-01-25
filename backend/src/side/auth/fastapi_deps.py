from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from side.auth.supabase_auth import validate_api_key, UserInfo

# Define schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
security = HTTPBearer(auto_error=False)

async def get_current_user(
    api_key: Optional[str] = Security(api_key_header),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> UserInfo:
    """
    Authenticate user via X-API-Key header or Bearer token.
    Returns UserInfo if valid, raises 403 if invalid.
    """
    token = None
    
    # 1. Check Header
    if api_key:
        token = api_key
    # 2. Check Bearer
    elif bearer:
        token = bearer.credentials
        
    if not token:
        raise HTTPException(
            status_code=403, 
            detail="Could not validate credentials. Please provide 'X-API-Key' header or 'Authorization: Bearer <key>'"
        )
        
    user = validate_api_key(token)
    
    if not user.valid:
        raise HTTPException(
            status_code=403,
            detail="Invalid authentication credentials"
        )
        
    return user
