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
    
    def run(self, context: ProbeContext) -> List[AuditResult]:
        return [
            self._check_dockerfile_security(context),
            self._check_docker_compose(context),
            self._check_secrets_management(context),
            self._check_healthchecks(context),
            self._check_resource_limits(context),
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
