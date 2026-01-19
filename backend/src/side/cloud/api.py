"""
Side Cloud API.

Hosted service for all users. Token-based limits, not feature-based.
Everyone gets the same features. Upgrade is just more tokens.
"""
import os
import logging
from typing import Optional, Any
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Use Supabase-based auth
from side.auth.supabase_auth import validate_api_key, get_api_key_from_header, UserInfo, record_token_usage
from side.cloud.limiter import limiter, TOKEN_COSTS

# Import auth routers (for OAuth flow)
from side.auth.github import router as github_router

# Ensure we have our own LLM key for cloud
os.environ.setdefault("GROQ_API_KEY", os.getenv("SIDE_GROQ_API_KEY", ""))

from side.llm.client import LLMClient
from side.audit.experts.security import SecurityExpert
from side.audit.experts.architect import ChiefArchitect
from side.audit.experts.performance import PerformanceLead
from side.audit.experts.engineer import SeniorEngineer
from side.audit.experts.base import ExpertContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Side API",
    description="Your Strategic Partner. Token-based, full access for everyone.",
    version="1.0.0",
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # HSTS (Strict-Transport-Security)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Prevention of clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Prevention of MIME sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # XSS Protection (legacy browsers)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Content Security Policy (Basic)
    # Note: Swagger UI needs 'unsafe-inline' and 'unsafe-eval' for now
    # In strict production, this should be tighter
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'"
    
    return response

# Include auth routers
app.include_router(github_router)


# ==================
# MODELS
# ==================

class AuditRequest(BaseModel):
    """Request for an expert audit."""
    code: str
    file_path: str = "snippet.py"
    language: str = "python"
    experts: list[str] = ["security"]


class AuditResult(BaseModel):
    """Result from an expert."""
    expert: str
    status: str
    reason: str
    evidence: Optional[str] = None


class AuditResponse(BaseModel):
    """Response from audit endpoint."""
    results: list[AuditResult]
    usage: dict


class UsageResponse(BaseModel):
    """Usage statistics."""
    used: int
    limit: int
    remaining: int


# ==================
# AUTH DEPENDENCY
# ==================

async def get_current_user(authorization: Optional[str] = Header(None)) -> UserInfo:
    """Validate API key and return user info."""
    api_key = get_api_key_from_header(authorization)
    user_info = validate_api_key(api_key)
    
    if not user_info.valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key. Get one at side.ai/dashboard",
        )
    return user_info


# ==================
# ENDPOINTS
# ==================

@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check."""
    llm = LLMClient()
    return {
        "status": "healthy",
        "llm_available": llm.is_available(),
        "llm_provider": llm.provider.value if llm.provider else None,
    }


@app.post("/v1/audit", response_model=AuditResponse)
async def run_audit(
    request: AuditRequest,
    user: UserInfo = Depends(get_current_user),
) -> AuditResponse:
    """
    Run expert audits on a code snippet.
    
    All users get access to all experts. Token limits apply.
    """
    # Check token limit
    allowed, reason = limiter.check_limit(user.user_id, "audit")
    if not allowed:
        raise HTTPException(status_code=429, detail=reason)
    
    # Map expert names to classes
    expert_map = {
        "security": SecurityExpert,
        "architect": ChiefArchitect,
        "performance": PerformanceLead,
        "engineer": SeniorEngineer,
    }
    
    results = []
    
    for expert_name in request.experts:
        if expert_name not in expert_map:
            continue
            
        expert = expert_map[expert_name]()
        
        if not expert.is_available():
            results.append(AuditResult(
                expert=expert_name,
                status="SKIPPED",
                reason="LLM not available",
            ))
            continue
            
        ctx = ExpertContext(
            check_id=f"cloud.{expert_name}",
            file_path=request.file_path,
            content_snippet=request.code[:4000],
            language=request.language,
        )
        
        result = expert.review(ctx)
        
        results.append(AuditResult(
            expert=expert_name,
            status=result.status.name,
            reason=result.notes or "",
            evidence=result.evidence[0].context if result.evidence else None,
        ))
    
    # Record token usage
    limiter.record_usage(user.user_id, "audit")
    
    return AuditResponse(
        results=results,
        usage=limiter.get_usage(user.user_id),
    )


@app.get("/v1/usage", response_model=UsageResponse)
async def get_usage(user: UserInfo = Depends(get_current_user)) -> UsageResponse:
    """Get current token usage."""
    usage = limiter.get_usage(user.user_id)
    return UsageResponse(**usage)


# ==================
# MAIN
# ==================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
