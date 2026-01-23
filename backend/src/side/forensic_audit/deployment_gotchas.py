"""
Deployment Gotcha Detector for Forensic Engine.

Detects subtle framework and platform issues that only surface in production.
"""

import re
from pathlib import Path
from typing import List, Dict, Any

class DeploymentGotchaDetector:
    """Detects known deployment traps."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)

    def scan(self) -> List[Dict[str, Any]]:
        """Run all deployment checks."""
        issues = []
        issues.extend(self._check_nextjs_auth_cookies())
        issues.extend(self._check_railway_port())
        return issues

    def _check_nextjs_auth_cookies(self) -> List[Dict[str, Any]]:
        """
        Check: Next.js App Router auth callbacks must manually copy cookies.
        Issue: cookies().set() does not propagate to NextResponse.redirect()
        """
        issues = []
        # Look for auth callback routes
        callback_files = list(self.project_root.rglob("**/api/auth/callback/route.ts"))
        
        for file_path in callback_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                
                has_cookies_set = "cookies().set" in content or "cookieStore.set" in content
                has_redirect = "NextResponse.redirect" in content
                
                # Check if there is logic to copy cookies to the response
                # This is a heuristic: looking for response.cookies.set
                has_cookie_copy = "response.cookies.set" in content
                
                if has_cookies_set and has_redirect and not has_cookie_copy:
                    issues.append({
                        "id": "nextjs-cookie-propagation",
                        "type": "DEPLOYMENT_GOTCHA",
                        "severity": "CRITICAL",
                        "file": str(file_path.relative_to(self.project_root)),
                        "line": 1, # Heuristic
                        "message": "Auth cookies won't persist in redirect (Next.js App Router gotcha).",
                        "action": "Manually copy cookies from store to NextResponse using response.cookies.set().",
                        "reference": "https://sidelith.com/docs/nextjs-cookie-propagation"
                    })
            except Exception:
                pass
                
        return issues

    def _check_railway_port(self) -> List[Dict[str, Any]]:
        """
        Check: Railway requires PORT=8080 environment variable in Dockerfile.
        """
        issues = []
        dockerfiles = list(self.project_root.rglob("Dockerfile"))
        
        for file_path in dockerfiles:
            try:
                content = file_path.read_text(encoding="utf-8")
                
                # Check if it sets PORT to something other than 8080 or uses straight 3000
                if "ENV PORT" in content and "8080" not in content:
                     issues.append({
                        "id": "railway-port-mismatch",
                        "type": "DEPLOYMENT_GOTCHA",
                        "severity": "HIGH",
                        "file": str(file_path.relative_to(self.project_root)),
                        "line": 1,
                        "message": "Railway expects PORT=8080, but Dockerfile uses a different port.",
                        "action": "Update Dockerfile to use ENV PORT=8080 for Railway compatibility.",
                        "reference": "https://docs.railway.app/guides/dockerfiles"
                    })
                elif "EXPOSE 3000" in content and "ENV PORT" not in content:
                     issues.append({
                        "id": "railway-port-default",
                        "type": "DEPLOYMENT_GOTCHA",
                        "severity": "MEDIUM",
                        "file": str(file_path.relative_to(self.project_root)),
                        "line": 1,
                        "message": "Dockerfile exposes 3000 but doesn't set PORT env var.",
                        "action": "Add ENV PORT=8080 and EXPOSE 8080 for reliable Railway deployment.",
                        "reference": "https://docs.railway.app/guides/dockerfiles"
                    })
            except Exception:
                pass
                
        return issues
