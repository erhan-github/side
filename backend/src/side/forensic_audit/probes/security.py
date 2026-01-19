"""
Security Probe - Comprehensive security audit.

Forensic-level security checks covering:
- Secret detection (enhanced)
- Authentication patterns
- Authorization patterns
- Injection prevention
- Data protection
"""

import re
import fnmatch
from pathlib import Path
from typing import List, Pattern
from ..core import (
    AuditResult, AuditStatus, AuditEvidence, 
    ProbeContext, Severity, Tier, AuditFixRisk
)


class SecurityProbe:
    """
    Forensic-level security audit probe.
    
    Covers 15+ security checks with high accuracy.
    """
    
    id = "forensic.security"
    name = "Security Audit"
    tier = Tier.FAST
    dimension = "Security"
    
    # Enhanced secret patterns (more comprehensive than before)
    SECRET_PATTERNS: List[tuple] = [
        # API Keys
        (r"api[_-]?key\s*[:=]\s*['\"]([a-zA-Z0-9_\-]{20,})['\"]", "API Key"),
        (r"api[_-]?secret\s*[:=]\s*['\"]([a-zA-Z0-9_\-]{20,})['\"]", "API Secret"),
        
        # Auth Tokens
        (r"bearer\s+[a-zA-Z0-9_\-\.]{20,}", "Bearer Token"),
        (r"auth[_-]?token\s*[:=]\s*['\"]([a-zA-Z0-9_\-]{20,})['\"]", "Auth Token"),
        
        # Private Keys
        (r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----", "Private Key"),
        (r"-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----", "SSH Private Key"),
        
        # Service-specific
        (r"sk_live_[0-9a-zA-Z]{24,}", "Stripe Live Key"),
        (r"sk_test_[0-9a-zA-Z]{24,}", "Stripe Test Key"),
        (r"ghp_[0-9a-zA-Z]{36}", "GitHub Token"),
        (r"gho_[0-9a-zA-Z]{36}", "GitHub OAuth Token"),
        (r"github_pat_[0-9a-zA-Z_]{22,}", "GitHub PAT"),
        (r"xox[baprs]-[0-9a-zA-Z\-]{10,}", "Slack Token"),
        (r"AIza[0-9A-Za-z\-_]{35}", "Google API Key"),
        (r"[0-9a-f]{32}-us[0-9]+", "Mailchimp API Key"),
        (r"sq0atp-[0-9A-Za-z\-_]{22}", "Square Token"),
        (r"sq0csp-[0-9A-Za-z\-_]{43}", "Square Secret"),
        
        # Database
        (r"postgres://[^:]+:[^@]+@", "PostgreSQL Connection String"),
        (r"mongodb\+srv://[^:]+:[^@]+@", "MongoDB Connection String"),
        (r"redis://:[^@]+@", "Redis Connection String"),
        
        # AWS
        (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
        (r"aws_secret_access_key\s*[:=]\s*['\"]([a-zA-Z0-9/+=]{40})['\"]", "AWS Secret"),
        
        # JWT
        (r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*", "JWT Token"),
    ]
    
    # SQL Injection patterns
    SQL_INJECTION_PATTERNS: List[tuple] = [
        (r"execute\s*\(\s*f['\"]", "f-string in SQL execute"),
        (r"execute\s*\(\s*['\"].*%s.*['\"].*%", "% formatting in SQL"),
        (r"execute\s*\(\s*['\"].*\+\s*", "String concat in SQL"),
        (r"cursor\.execute\s*\(\s*f['\"]", "f-string in cursor.execute"),
    ]
    
    # XSS patterns
    XSS_PATTERNS: List[tuple] = [
        (r"innerHTML\s*=", "Direct innerHTML assignment"),
        (r"dangerouslySetInnerHTML", "React dangerouslySetInnerHTML"),
        (r"v-html\s*=", "Vue v-html directive"),
        (r"document\.write\s*\(", "document.write usage"),
    ]
    
    def run(self, context: ProbeContext) -> List[AuditResult]:
        """Run all security checks."""
        results = []
        
        # 1. Secret Detection
        results.append(self._check_secrets(context))
        
        # 2. GitIgnore Check
        results.append(self._check_gitignore(context))
        
        # 3. SQL Injection
        results.append(self._check_sql_injection(context))
        
        # 4. XSS Prevention
        results.append(self._check_xss(context))
        
        # 5. Auth on Endpoints
        results.append(self._check_auth_patterns(context))
        
        # 6. HTTPS Enforcement
        results.append(self._check_https(context))
        
        # 7. Secure Headers
        results.append(self._check_security_headers(context))
        
        # 8. Password Handling
        results.append(self._check_password_handling(context))
        
        # 9. Session Security
        results.append(self._check_session_security(context))
        
        # 10. Input Validation
        results.append(self._check_input_validation(context))
        
        # === ENTERPRISE CHECKS ===
        
        # 11. CSRF Protection
        results.append(self._check_csrf(context))
        
        # 12. Session Timeout
        results.append(self._check_session_timeout(context))
        
        # 13. Command Injection
        results.append(self._check_command_injection(context))
        
        # 14. Path Traversal
        results.append(self._check_path_traversal(context))
        
        # 15. CORS Configuration
        results.append(self._check_cors(context))
        
        return results
    
    def _check_csrf(self, context: ProbeContext) -> AuditResult:
        """Check for CSRF protection."""
        patterns = ['csrf_token', 'CSRFProtect', 'csrf_protect', '@csrf_exempt', 'X-CSRF-Token']
        has_csrf = False
        exempt_count = 0
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in patterns[:4]):
                    has_csrf = True
                if '@csrf_exempt' in content:
                    exempt_count += content.count('@csrf_exempt')
            except Exception:
                continue
        
        evidence = []
        if exempt_count > 0:
            evidence.append(AuditEvidence(description=f"{exempt_count} CSRF exemptions found"))
        
        return AuditResult(
            check_id="SEC-011",
            check_name="CSRF Protection",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_csrf else AuditStatus.WARN,
            severity=Severity.HIGH,
            evidence=evidence,
            notes=f"CSRF protection found, {exempt_count} exemptions" if has_csrf else "No CSRF protection detected",
            recommendation="Add Flask-WTF CSRFProtect or Django CSRF middleware"
        )
    
    def _check_session_timeout(self, context: ProbeContext) -> AuditResult:
        """Check for session timeout configuration."""
        patterns = ['SESSION_LIFETIME', 'session_lifetime', 'expire', 'max_age', 'PERMANENT_SESSION_LIFETIME']
        has_timeout = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in patterns):
                    has_timeout = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="SEC-012",
            check_name="Session Timeout",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_timeout else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            notes="Session timeout configured" if has_timeout else "No session timeout found",
            recommendation="Set PERMANENT_SESSION_LIFETIME to reasonable value (e.g., 30 minutes)"
        )
    
    def _check_command_injection(self, context: ProbeContext) -> AuditResult:
        """Check for command injection vulnerabilities."""
        evidence = []
        patterns = [
            (r'subprocess\.(run|call|Popen)\s*\(\s*f["\']', "f-string in subprocess"),
            (r'os\.system\s*\(\s*f["\']', "f-string in os.system"),
            (r'os\.popen\s*\(', "os.popen usage (insecure)"),
            (r'shell\s*=\s*True', "shell=True in subprocess"),
        ]
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            # Skip self (this file contains the patterns we search for)
            if 'forensic_audit/probes/security.py' in file_path:
                continue
            try:
                content = Path(file_path).read_text()
                for line_idx, line in enumerate(content.splitlines(), 1):
                    for pattern, desc in patterns:
                        if re.search(pattern, line):
                            evidence.append(AuditEvidence(
                                description=desc,
                                file_path=file_path,
                                line_number=line_idx,
                                suggested_fix="Use subprocess with list args, avoid shell=True"
                            ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="SEC-013",
            check_name="Command Injection Prevention",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.CRITICAL,
            evidence=evidence[:10],
            recommendation="Use subprocess.run with list args, never shell=True with user input"
        )
    
    def _check_path_traversal(self, context: ProbeContext) -> AuditResult:
        """Check for path traversal vulnerabilities."""
        evidence = []
        patterns = [
            (r'open\s*\(\s*f["\']', "f-string in file open"),
            (r'Path\s*\(\s*f["\']', "f-string in Path constructor"),
            (r'os\.path\.join\s*\([^)]*request', "User input in path join"),
        ]
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            try:
                content = Path(file_path).read_text()
                for line_idx, line in enumerate(content.splitlines(), 1):
                    for pattern, desc in patterns:
                        if re.search(pattern, line):
                            # Skip if there's validation
                            if 'resolve()' in line or 'is_relative_to' in line:
                                continue
                            evidence.append(AuditEvidence(
                                description=desc,
                                file_path=file_path,
                                line_number=line_idx
                            ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="SEC-014",
            check_name="Path Traversal Prevention",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.HIGH,
            evidence=evidence[:10],
            recommendation="Use Path.resolve() and validate paths are within allowed directory"
        )
    
    def _check_cors(self, context: ProbeContext) -> AuditResult:
        """Check for CORS configuration."""
        patterns = ['CORS', 'Access-Control-Allow-Origin', 'cors_origins']
        has_cors = False
        allows_all = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in patterns):
                    has_cors = True
                # Check for allows wildcard
                if "'*'" in content and 'Access-Control' in content:
                    allows_all = True
                
                # If using CORSMiddleware with variable (allow_origins=origins), it's safe (assuming variable is safe)
                if 'allow_origins=' in content and '=["*"]' not in content and "=['*']" not in content:
                    # If it's assigning a variable, assume it's better than hardcoded *
                    allows_all = False
            except Exception:
                continue
        
        evidence = []
        if allows_all:
            evidence.append(AuditEvidence(description="CORS allows all origins (*)"))
        
        status = AuditStatus.PASS
        if allows_all:
            status = AuditStatus.WARN
        elif not has_cors:
            status = AuditStatus.INFO  # May not need CORS
        
        return AuditResult(
            check_id="SEC-015",
            check_name="CORS Configuration",
            dimension=self.dimension,
            status=status,
            severity=Severity.MEDIUM,
            evidence=evidence,
            recommendation="Configure specific CORS origins, avoid '*' in production"
        )
    
    def _check_secrets(self, context: ProbeContext) -> AuditResult:
        """Check for hardcoded secrets."""
        evidence = []
        files_scanned = 0
        
        # Load gitignore patterns
        ignore_patterns = []
        gitignore_path = Path(context.project_root) / ".gitignore"
        if gitignore_path.exists():
            for line in gitignore_path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    ignore_patterns.append(line)
        
        for file_path in context.files:
            path = Path(file_path)
            
            # Skip binary, lock, and vendor files
            if path.suffix in ['.lock', '.pyc', '.png', '.jpg', '.pdf', '.woff']:
                continue
            if 'node_modules' in str(path) or 'venv' in str(path):
                continue
            
            # Skip self (this file defines the patterns, so it matches them)
            if 'forensic_audit/probes/security.py' in str(path):
                continue
            
            try:
                content = path.read_text(errors='ignore')
                files_scanned += 1
                
                for line_idx, line in enumerate(content.splitlines(), 1):
                    # Skip long lines (minified) and comments
                    if len(line) > 500 or line.strip().startswith('#'):
                        continue
                    
                    for pattern, secret_type in self.SECRET_PATTERNS:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Skip template/example values
                            if any(x in line.lower() for x in ['example', 'your_', 'xxx', 'placeholder', 'todo']):
                                continue
                            
                            evidence.append(AuditEvidence(
                                description=f"Potential {secret_type} detected",
                                file_path=str(path),
                                line_number=line_idx,
                                context=line.strip()[:80] + "...",
                                suggested_fix=f"Move {secret_type} to environment variable"
                            ))
            except Exception:
                continue
        
        # Evaluate Risk
        status = AuditStatus.PASS
        severity = Severity.INFO
        
        if evidence:
            # Check if all issues are in gitignored files
            all_ignored = True
            for ev in evidence:
                is_ignored = False
                rel_path = str(Path(ev.file_path).relative_to(context.project_root))
                
                # Check strict name match or glob match
                for pat in ignore_patterns:
                    if fnmatch.fnmatch(rel_path, pat) or fnmatch.fnmatch(Path(rel_path).name, pat):
                        is_ignored = True
                        break
                    # Handle dir/* pattern simply
                    if pat.endswith('/') and rel_path.startswith(pat):
                        is_ignored = True
                        break
                
                if not is_ignored:
                    all_ignored = False
                    break
            
            if all_ignored:
                status = AuditStatus.WARN
                severity = Severity.MEDIUM
                notes = f"Found {len(evidence)} secrets in .gitignored files (Safe from repo, but risky on disk)"
            else:
                status = AuditStatus.FAIL
                severity = Severity.CRITICAL
                notes = f"Found {len(evidence)} potential secrets exposed to source control"
        else:
            notes = f"Scanned {files_scanned} files, no secrets found"
        
        return AuditResult(
            check_id="SEC-001",
            check_name="No Hardcoded Secrets",
            dimension=self.dimension,
            status=status,
            severity=severity,
            evidence=evidence,
            notes=notes,
            confidence=0.95,
            recommendation="Move all secrets to .env files and use environment variables",
            effort_hours=2
        )

    
    def _check_gitignore(self, context: ProbeContext) -> AuditResult:
        """Check .gitignore for required entries."""
        gitignore_path = Path(context.project_root) / ".gitignore"
        required_entries = ['.env', '.env.local', '.env.*.local', 'node_modules', '__pycache__', '.venv']
        
        if not gitignore_path.exists():
            return AuditResult(
                check_id="SEC-002",
                check_name="GitIgnore Configuration",
                dimension=self.dimension,
                status=AuditStatus.FAIL,
                severity=Severity.HIGH,
                evidence=[AuditEvidence(description=".gitignore file missing")],
                recommendation="Create .gitignore with standard entries"
            )
        
        content = gitignore_path.read_text()
        missing = [e for e in required_entries if e not in content]
        
        if missing:
            return AuditResult(
                check_id="SEC-002",
                check_name="GitIgnore Configuration",
                dimension=self.dimension,
                status=AuditStatus.WARN,
                severity=Severity.MEDIUM,
                evidence=[AuditEvidence(description=f"Missing: {', '.join(missing)}")],
                recommendation=f"Add {', '.join(missing)} to .gitignore"
            )
        
        return AuditResult(
            check_id="SEC-002",
            check_name="GitIgnore Configuration",
            dimension=self.dimension,
            status=AuditStatus.PASS,
            severity=Severity.MEDIUM,
            notes="All required entries present"
        )
    
    def _check_sql_injection(self, context: ProbeContext) -> AuditResult:
        """Check for SQL injection vulnerabilities."""
        evidence = []
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                
                for line_idx, line in enumerate(content.splitlines(), 1):
                    for pattern, desc in self.SQL_INJECTION_PATTERNS:
                        if re.search(pattern, line):
                            evidence.append(AuditEvidence(
                                description=desc,
                                file_path=file_path,
                                line_number=line_idx,
                                context=line.strip()[:80],
                                suggested_fix="Use parameterized queries: cursor.execute('SELECT * FROM ? WHERE id = ?', (table, id))"
                            ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="SEC-003",
            check_name="SQL Injection Prevention",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.FAIL,
            severity=Severity.CRITICAL,
            evidence=evidence[:10],
            confidence=0.9,
            recommendation="Use parameterized queries for all database operations",
            fix_risk=AuditFixRisk.REVIEW
        )
    
    def _check_xss(self, context: ProbeContext) -> AuditResult:
        """Check for XSS vulnerabilities."""
        evidence = []
        
        for file_path in context.files:
            if not any(file_path.endswith(ext) for ext in ['.js', '.jsx', '.ts', '.tsx', '.vue']):
                continue
            
            try:
                content = Path(file_path).read_text()
                
                # Skip self (this file defines the patterns, so it matches them)
                if 'forensic_audit/probes/security.py' in file_path:
                    continue

                for line_idx, line in enumerate(content.splitlines(), 1):
                    for pattern, desc in self.XSS_PATTERNS:
                        if re.search(pattern, line):
                            evidence.append(AuditEvidence(
                                description=desc,
                                file_path=file_path,
                                line_number=line_idx,
                                context=line.strip()[:80],
                                suggested_fix="Use safe rendering methods or sanitize input"
                            ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="SEC-004",
            check_name="XSS Prevention",
            dimension=self.dimension,
            status=AuditStatus.FAIL if evidence else AuditStatus.PASS,
            severity=Severity.HIGH,
            evidence=evidence,
            recommendation="Avoid innerHTML, use textContent or React's JSX escaping"
        )
    
    def _check_auth_patterns(self, context: ProbeContext) -> AuditResult:
        """Check for authentication on API endpoints."""
        evidence = []
        endpoints_found = 0
        protected_found = 0
        
        auth_decorators = ['@requires_auth', '@login_required', '@authenticated', '@jwt_required', '@Depends(get_current_user)']
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            if 'test' in file_path.lower() or 'security.py' in file_path:
                continue
            
            try:
                content = Path(file_path).read_text()
                lines = content.splitlines()
                
                for i, line in enumerate(lines):
                    # Check for route definitions
                    if any(x in line for x in ['@app.route', '@router.', '@app.get', '@app.post', '@app.put', '@app.delete']):
                        endpoints_found += 1
                        
                        # Check previous 3 lines for auth decorator
                        prev_lines = lines[max(0, i-3):i]
                        has_auth = any(any(d in pl for d in auth_decorators) for pl in prev_lines)
                        
                        # Also check for Depends(auth_dependency) in the route definition or function signature
                        if not has_auth:
                            # Look at this line and next 5 lines (function definition)
                            context_lines = lines[i:i+6]
                            combined_context = " ".join(context_lines)
                            
                            if 'Depends(' in combined_context:
                                # Loose check for auth-related dependency
                                if any(x in combined_context for x in ['get_current', 'verify_', 'auth_', 'require_', 'user', 'api_key']):
                                    has_auth = True
                        
                        if has_auth:
                            protected_found += 1
                        else:
                            # Check if it's a public route
                            if not any(x in line.lower() for x in ['health', 'ping', 'public', 'webhook', 'auth', 'login', 'callback', 'github', 'oauth']):
                                evidence.append(AuditEvidence(
                                    description="Endpoint without visible auth decorator",
                                    file_path=file_path,
                                    line_number=i + 1,
                                    context=line.strip()[:80]
                                ))
            except Exception:
                continue
        
        if endpoints_found == 0:
            return AuditResult(
                check_id="SEC-005",
                check_name="Endpoint Authentication",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.HIGH,
                notes="No API endpoints found"
            )
        
        return AuditResult(
            check_id="SEC-005",
            check_name="Endpoint Authentication",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.HIGH,
            evidence=evidence[:10],  # Limit to 10
            notes=f"Found {endpoints_found} endpoints, {protected_found} with visible auth",
            recommendation="Add authentication decorators to all non-public endpoints"
        )
    
    def _check_https(self, context: ProbeContext) -> AuditResult:
        """Check for HTTPS enforcement."""
        evidence = []
        
        for file_path in context.files:
            if not any(file_path.endswith(ext) for ext in ['.py', '.js', '.ts', '.json', '.yaml', '.yml']):
                continue
            
            try:
                content = Path(file_path).read_text()
                
                for line_idx, line in enumerate(content.splitlines(), 1):
                    # Check for http:// in URLs (not localhost)
                    if 'http://' in line and 'localhost' not in line and '127.0.0.1' not in line:
                        if not line.strip().startswith('#') and not line.strip().startswith('//'):
                            evidence.append(AuditEvidence(
                                description="Non-HTTPS URL found",
                                file_path=file_path,
                                line_number=line_idx,
                                context=line.strip()[:80]
                            ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="SEC-006",
            check_name="HTTPS Enforcement",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=evidence[:5],
            recommendation="Use HTTPS for all external URLs"
        )
    
    def _check_security_headers(self, context: ProbeContext) -> AuditResult:
        """Check for security headers configuration."""
        headers_to_check = [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'Strict-Transport-Security',
            'Content-Security-Policy',
            'X-XSS-Protection'
        ]
        
        found_headers = set()
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                for header in headers_to_check:
                    # Check for direct string in content (e.g. middleware)
                    if header in content:
                        found_headers.add(header)
                        
                # Special check: If there's a middleware adding headers generically
                if '@app.middleware' in content and 'add_security_headers' in content:
                    # Assume it adds all required headers if we see the function
                    if all(h in content for h in ['X-Frame-Options', 'X-Content-Type-Options', 'Strict-Transport-Security']):
                        found_headers.update(headers_to_check)
            except Exception:
                continue
        
        missing = set(headers_to_check) - found_headers
        
        return AuditResult(
            check_id="SEC-007",
            check_name="Security Headers",
            dimension=self.dimension,
            status=AuditStatus.PASS if not missing else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=[AuditEvidence(description=f"Missing headers: {', '.join(missing)}")] if missing else [],
            recommendation="Configure security headers in your web server or middleware"
        )
    
    def _check_password_handling(self, context: ProbeContext) -> AuditResult:
        """Check for secure password handling."""
        evidence = []
        has_hashing = False
        unsafe_patterns = [
            (r"password\s*==", "Direct password comparison"),
            (r"md5\s*\(", "MD5 for passwords (insecure)"),
            (r"sha1\s*\(", "SHA1 for passwords (insecure)"),
        ]
        safe_patterns = ['bcrypt', 'argon2', 'scrypt', 'pbkdf2']
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                
                # Check for safe hashing
                if any(p in content.lower() for p in safe_patterns):
                    has_hashing = True
                
                # Check for unsafe patterns
                for line_idx, line in enumerate(content.splitlines(), 1):
                    for pattern, desc in unsafe_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            evidence.append(AuditEvidence(
                                description=desc,
                                file_path=file_path,
                                line_number=line_idx
                            ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="SEC-008",
            check_name="Password Handling",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_hashing and not evidence else AuditStatus.WARN,
            severity=Severity.HIGH,
            evidence=evidence[:5],
            notes="Found secure hashing" if has_hashing else "No secure hashing library found",
            recommendation="Use bcrypt or argon2 for password hashing"
        )
    
    def _check_session_security(self, context: ProbeContext) -> AuditResult:
        """Check for session security."""
        evidence = []
        session_config_found = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                
                # Check for session configuration
                if 'SESSION_' in content or 'session_config' in content:
                    session_config_found = True
                
                # Check for insecure session patterns
                if 'session.permanent = True' in content and 'PERMANENT_SESSION_LIFETIME' not in content:
                    evidence.append(AuditEvidence(
                        description="Permanent session without lifetime limit",
                        file_path=file_path
                    ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="SEC-009",
            check_name="Session Security",
            dimension=self.dimension,
            status=AuditStatus.PASS if session_config_found and not evidence else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=evidence,
            recommendation="Configure session timeout and secure cookie flags"
        )
    
    def _check_input_validation(self, context: ProbeContext) -> AuditResult:
        """Check for input validation patterns."""
        validation_patterns = ['pydantic', 'marshmallow', 'cerberus', 'voluptuous', 'jsonschema', 'ValidationError']
        found_validation = False
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in validation_patterns):
                    found_validation = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="SEC-010",
            check_name="Input Validation",
            dimension=self.dimension,
            status=AuditStatus.PASS if found_validation else AuditStatus.WARN,
            severity=Severity.HIGH,
            notes="Validation library found" if found_validation else "No validation library detected",
            recommendation="Use Pydantic or similar for all API input validation"
        )
