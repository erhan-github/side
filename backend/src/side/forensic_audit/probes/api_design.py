"""
API Design Probe - Comprehensive API audit.

Forensic-level API checks covering:
- REST standards
- Error responses
- Input validation
- Rate limiting
- Versioning
"""

import re
from pathlib import Path
from typing import List
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier


class APIDesignProbe:
    """Forensic-level API design audit probe."""
    
    id = "forensic.api_design"
    name = "API Design Audit"
    tier = Tier.FAST
    dimension = "API Design"
    
    def run(self, context: ProbeContext) -> List[AuditResult]:
        return [
            self._check_consistent_responses(context),
            self._check_error_handling(context),
            self._check_pagination(context),
            self._check_rate_limiting(context),
            self._check_versioning(context),
            self._check_input_validation(context),
        ]
    
    def _check_consistent_responses(self, context: ProbeContext) -> AuditResult:
        """Check for consistent API response format."""
        response_patterns = ['jsonify', 'BaseResponse', 'Response(', 'JSONResponse']
        has_consistent = False
        
        for file_path in context.files:
            if not any(x in file_path.lower() for x in ['api', 'route', 'view', 'endpoint']):
                continue
            try:
                content = Path(file_path).read_text()
                if any(rp in content for rp in response_patterns):
                    has_consistent = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="API-001",
            check_name="Consistent Response Format",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_consistent else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Use a BaseResponse class for all API responses"
        )
    
    def _check_error_handling(self, context: ProbeContext) -> AuditResult:
        """Check for API error handling."""
        patterns = ['HTTPException', 'ErrorResponse', 'abort(', 'raise_for_status']
        has_error_handling = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in patterns):
                    has_error_handling = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="API-002",
            check_name="API Error Handling",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_error_handling else AuditStatus.WARN,
            severity=Severity.HIGH,
            recommendation="Use HTTPException or custom error handlers"
        )
    
    def _check_pagination(self, context: ProbeContext) -> AuditResult:
        """Check for pagination support."""
        patterns = ['offset', 'limit', 'page', 'per_page', 'cursor', 'next_page']
        has_pagination = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content.lower() for p in patterns):
                    has_pagination = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="API-003",
            check_name="Pagination Support",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_pagination else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Add limit/offset or cursor-based pagination"
        )
    
    def _check_rate_limiting(self, context: ProbeContext) -> AuditResult:
        """Check for rate limiting."""
        patterns = ['rate_limit', 'RateLimiter', 'throttle', 'slowapi', 'ratelimit']
        has_rate_limiting = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content.lower() for p in patterns):
                    has_rate_limiting = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="API-004",
            check_name="Rate Limiting",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_rate_limiting else AuditStatus.WARN,
            severity=Severity.HIGH,
            recommendation="Add rate limiting with slowapi or similar"
        )
    
    def _check_versioning(self, context: ProbeContext) -> AuditResult:
        """Check for API versioning."""
        patterns = ['/v1/', '/v2/', '/api/v', 'api_version', 'X-API-Version']
        has_versioning = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in patterns):
                    has_versioning = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="API-005",
            check_name="API Versioning",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_versioning else AuditStatus.INFO,
            severity=Severity.LOW,
            recommendation="Use URL versioning (/v1/) for public APIs"
        )
    
    def _check_input_validation(self, context: ProbeContext) -> AuditResult:
        """Check for API input validation."""
        patterns = ['pydantic', 'BaseModel', '@validator', 'Field(', 'ValidationError']
        has_validation = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in patterns):
                    has_validation = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="API-006",
            check_name="Input Validation",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_validation else AuditStatus.WARN,
            severity=Severity.HIGH,
            recommendation="Use Pydantic models for all API inputs"
        )
