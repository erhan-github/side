"""
Sidelith Cloud API.

Capacity-based limits, not feature-based.
Everyone gets the same features. Upgrade is just more capacity (CP).
"""
import os
import logging
from typing import Optional, Any, List
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Use Supabase-based auth
from side.auth.supabase_auth import validate_api_key, get_api_key_from_header, UserInfo, record_token_usage
from side.mesh.limiter import limiter, CAPACITY_COSTS

# Import auth routers (for OAuth flow)
from side.auth.github import router as github_router

# Ensure we have our own LLM key for cloud
os.environ.setdefault("GROQ_API_KEY", os.getenv("SIDE_GROQ_API_KEY", ""))

from side.llm.client import LLMClient
# from side.audit.experts.security import SecurityExpert
# from side.audit.experts.architect import ChiefArchitect
# from side.audit.experts.performance import PerformanceLead
# from side.audit.experts.engineer import SeniorEngineer
# from side.audit.experts.base import ExpertContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Side API",
    description="Your Strategic Partner. Capacity-based, full access for everyone.",
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
    monthly_allowance_used: int
    monthly_allowance_limit: int
    monthly_allowance_remaining: int
    addon_balance: int
    total_remaining: int
    month: str

class LedgerItem(BaseModel):
    """Audit ledger item."""
    timestamp: float
    operation: str
    cost: int
    model: str


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
            detail="Invalid API key. Get one at sidelith.com/dashboard",
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
    
    All users get access to all experts. Capacity limits apply.
    """
    return AuditResponse(
        results=[],
        usage=limiter.get_usage(user.user_id),
    )


@app.get("/v1/billing/ledger", response_model=List[LedgerItem])
async def get_billing_ledger(
    user: UserInfo = Depends(get_current_user),
    limit: int = 50
):
    """
    Get audit transaction ledger (**Billing Ledger**).
    ENTERPRISE-GRADE TRANSPARENCY:
    Every capacity deduction is logged and auditable.
    """
    return limiter.get_billing_ledger(user.user_id, limit)

@app.get("/v1/usage", response_model=UsageResponse)
async def get_usage(user: UserInfo = Depends(get_current_user)) -> UsageResponse:
    """Get current capacity usage."""
    usage = limiter.get_usage(user.user_id)
    return UsageResponse(**usage)


# ==================
# MAIN
# ==================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
