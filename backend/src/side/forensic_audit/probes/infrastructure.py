"""
Infrastructure Probe - Enterprise infrastructure audit.

Forensic-level infrastructure checks covering:
- Docker security
- Kubernetes basics
- Cloud configuration
- Secrets management
"""

from pathlib import Path
from typing import List
import re
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier


class InfrastructureProbe:
    """Forensic-level infrastructure audit probe."""
    
    id = "forensic.infrastructure"
    name = "Infrastructure Audit"
    tier = Tier.FAST
    dimension = "Infrastructure"
    
    async def run(self, context: ProbeContext) -> List[AuditResult]:
        return [
            self._check_dockerfile_security(context),
            self._check_docker_compose(context),
            self._check_secrets_management(context),
            self._check_healthchecks(context),
            self._check_resource_limits(context),
            self._check_k8s_basics(context),
            self._check_terraform_security(context),
            self._check_proxy_constraints(context),
        ]
    
    def _check_dockerfile_security(self, context: ProbeContext) -> AuditResult:
        """Check Dockerfile security best practices."""
        dockerfile_path = Path(context.project_root) / "Dockerfile"
        evidence = []
        
        if not dockerfile_path.exists():
            return AuditResult(
                check_id="INFRA-001",
                check_name="Dockerfile Security",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.MEDIUM,
                notes="No Dockerfile found"
            )
        
        content = dockerfile_path.read_text()
        
        # Check for root user
        if 'USER root' in content or ('USER' not in content and 'FROM' in content):
            evidence.append(AuditEvidence(
                description="Container may run as root",
                file_path=str(dockerfile_path),
                suggested_fix="Add 'USER nonroot' or create a non-root user"
            ))
        
        # Check for latest tag
        if ':latest' in content:
            evidence.append(AuditEvidence(
                description="Using :latest tag (non-deterministic)",
                file_path=str(dockerfile_path),
                suggested_fix="Pin to specific version (e.g., python:3.11-slim)"
            ))
        
        # Check for COPY vs ADD
        if 'ADD ' in content and 'http' not in content:
            evidence.append(AuditEvidence(
                description="Using ADD instead of COPY",
                suggested_fix="Use COPY unless extracting archives"
            ))
        
        return AuditResult(
            check_id="INFRA-001",
            check_name="Dockerfile Security",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=evidence,
            recommendation="Run as non-root, pin versions, use COPY"
        )
    
    def _check_docker_compose(self, context: ProbeContext) -> AuditResult:
        """Check docker-compose security."""
        compose_files = ['docker-compose.yml', 'docker-compose.yaml', 'compose.yml']
        root = Path(context.project_root)
        evidence = []
        
        compose_path = None
        for cf in compose_files:
            if (root / cf).exists():
                compose_path = root / cf
                break
        
        if not compose_path:
            return AuditResult(
                check_id="INFRA-002",
                check_name="Docker Compose Security",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.MEDIUM,
                notes="No docker-compose file found"
            )
        
        content = compose_path.read_text()
        
        # Check for privileged mode
        if 'privileged: true' in content:
            evidence.append(AuditEvidence(
                description="Container runs in privileged mode",
                suggested_fix="Remove 'privileged: true'"
            ))
        
        # Check for hardcoded secrets
        if re.search(r'password:\s*[\'"][^\'"]+[\'"]', content):
            evidence.append(AuditEvidence(
                description="Hardcoded password in compose file",
                suggested_fix="Use environment variables or secrets"
            ))
        
        return AuditResult(
            check_id="INFRA-002",
            check_name="Docker Compose Security",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.HIGH,
            evidence=evidence,
            recommendation="Avoid privileged mode, use secrets"
        )
    
    def _check_secrets_management(self, context: ProbeContext) -> AuditResult:
        """Check for proper secrets management."""
        patterns = ['vault', 'secrets_manager', 'kms', 'sops', 'sealed-secret']
        has_secrets_mgmt = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content.lower() for p in patterns):
                    has_secrets_mgmt = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="INFRA-003",
            check_name="Secrets Management",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_secrets_mgmt else AuditStatus.INFO,
            severity=Severity.LOW,
            notes="Secrets management found" if has_secrets_mgmt else "Consider HashiCorp Vault or AWS Secrets Manager",
            recommendation="Use a secrets manager for production"
        )
    
    def _check_healthchecks(self, context: ProbeContext) -> AuditResult:
        """Check for health check endpoints."""
        patterns = ['/health', '/healthz', '/ready', '/readiness', '/liveness', 'HEALTHCHECK']
        has_healthcheck = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in patterns):
                    has_healthcheck = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="INFRA-004",
            check_name="Health Checks",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_healthcheck else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Add /health endpoint for container orchestration"
        )
    
    def _check_resource_limits(self, context: ProbeContext) -> AuditResult:
        """Check for resource limits in container config."""
        patterns = ['mem_limit', 'cpus:', 'resources:', 'memory:', 'limits:']
        has_limits = False
        
        compose_files = ['docker-compose.yml', 'docker-compose.yaml']
        root = Path(context.project_root)
        
        for cf in compose_files:
            path = root / cf
            if path.exists():
                content = path.read_text()
                if any(p in content for p in patterns):
                    has_limits = True
                    break
        
        return AuditResult(
            check_id="INFRA-005",
            check_name="Resource Limits",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_limits else AuditStatus.INFO,
            severity=Severity.LOW,
            recommendation="Set memory and CPU limits in docker-compose"
        )

    def _check_k8s_basics(self, context: ProbeContext) -> AuditResult:
        """Check for basic Kubernetes security/performance issues."""
        evidence = []
        
        for file_path in context.files:
            if not any(file_path.endswith(ext) for ext in ['.yaml', '.yml']):
                continue
                
            try:
                content = Path(file_path).read_text()
                # Heuristic: Is it a K8s file?
                if 'apiVersion:' not in content or 'kind:' not in content:
                    continue
                    
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    # Check for missing resources
                    # This is hard with regex line-by-line, but we can check if 'resources:' is missing in Deployment/Pod
                    pass
                
                if 'kind: Deployment' in content or 'kind: Pod' in content:
                    if 'resources:' not in content:
                         evidence.append(AuditEvidence(
                            description="Kubernetes manifest missing resource limits",
                            file_path=file_path,
                            suggested_fix="Define resources.requests and resources.limits"
                        ))
                    if 'imagePullPolicy: Always' in content:
                        evidence.append(AuditEvidence(
                            description="imagePullPolicy: Always (performance risk)",
                            file_path=file_path,
                            suggested_fix="Use IfNotPresent or specific tags"
                        ))

            except Exception:
                continue
                
        return AuditResult(
            check_id="INFRA-006",
            check_name="Kubernetes Basics",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=evidence[:5],
            recommendation="Define resource limits and use stable image policies"
        )

    def _check_terraform_security(self, context: ProbeContext) -> AuditResult:
        """Check for basic Terraform security misconfigurations."""
        evidence = []
        
        for file_path in context.files:
            if not file_path.endswith('.tf'):
                continue
                
            try:
                content = Path(file_path).read_text()
                
                # Check for 0.0.0.0/0 in ingress
                if '0.0.0.0/0' in content and 'ingress' in content:
                     evidence.append(AuditEvidence(
                        description="Security Group open to world (0.0.0.0/0)",
                        file_path=file_path,
                        suggested_fix="Restrict CIDR blocks to necessary IPs"
                    ))
                
                # Check for public buckets
                if 'acl' in content and ('"public-read"' in content or "'public-read'" in content):
                    evidence.append(AuditEvidence(
                        description="S3 Bucket has public-read ACL",
                        file_path=file_path,
                        suggested_fix="Use private ACL and CloudFront for public assets"
                    ))
                    
            except Exception:
                continue

        return AuditResult(
            check_id="INFRA-007",
            check_name="Terraform Security",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.HIGH,
            evidence=evidence[:5],
            recommendation="Restrict Security Groups and S3 ACLs"
        )

    def _check_proxy_constraints(self, context: ProbeContext) -> AuditResult:
        """Check for proxy-level constraints (e.g., header size limits)."""
        evidence = []
        
        # Look for railway.toml or docker-compose.yml for proxy config
        for file_path in context.files:
            if not any(file_path.endswith(ext) for ext in ['.toml', '.yml', '.yaml']):
                continue
                
            try:
                content = Path(file_path).read_text()
                
                # Heuristic: Check for large header proxies or lack of config
                # Standard proxies like Nginx/Railway often have 8KB limits.
                if 'proxy' in content.lower() or 'ingress' in content.lower():
                    if 'header_size' not in content.lower() and 'buffer_size' not in content.lower():
                         evidence.append(AuditEvidence(
                            description="Invisible Proxy Constraint: Default header limits (8KB) may apply",
                            file_path=file_path,
                            suggested_fix="Define explicit proxy_buffer_size or optimize auth header size"
                        ))
            except Exception:
                continue
                
        return AuditResult(
            check_id="INFRA-008",
            check_name="Proxy Constraints",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=evidence[:3],
            recommendation="Verify upstream proxy header limits to prevent silent auth failures"
        )
