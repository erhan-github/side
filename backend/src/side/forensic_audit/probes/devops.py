"""
DevOps Probe - Comprehensive DevOps audit.

Forensic-level DevOps checks covering:
- CI/CD configuration
- Docker setup
- Environment management
"""

from pathlib import Path
from typing import List
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier


class DevOpsProbe:
    """Forensic-level DevOps audit probe."""
    
    id = "forensic.devops"
    name = "DevOps Audit"
    tier = Tier.FAST
    dimension = "DevOps"
    
    def run(self, context: ProbeContext) -> List[AuditResult]:
        return [
            self._check_ci_config(context),
            self._check_docker(context),
            self._check_env_example(context),
            self._check_readme(context),
            self._check_makefile(context),
        ]
    
    def _check_ci_config(self, context: ProbeContext) -> AuditResult:
        """Check for CI/CD configuration."""
        ci_paths = [
            '.github/workflows',
            '.gitlab-ci.yml',
            '.circleci',
            'Jenkinsfile',
            '.travis.yml'
        ]
        
        root = Path(context.project_root)
        has_ci = any((root / cp).exists() for cp in ci_paths)
        
        return AuditResult(
            check_id="DEVOPS-001",
            check_name="CI/CD Configuration",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_ci else AuditStatus.FAIL,
            severity=Severity.HIGH,
            recommendation="Add .github/workflows/ci.yml for GitHub Actions"
        )
    
    def _check_docker(self, context: ProbeContext) -> AuditResult:
        """Check for Docker configuration."""
        docker_files = ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml']
        root = Path(context.project_root)
        has_docker = any((root / df).exists() for df in docker_files)
        
        return AuditResult(
            check_id="DEVOPS-002",
            check_name="Docker Configuration",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_docker else AuditStatus.INFO,
            severity=Severity.LOW,
            recommendation="Add Dockerfile for containerized deployment"
        )
    
    def _check_env_example(self, context: ProbeContext) -> AuditResult:
        """Check for .env.example file."""
        root = Path(context.project_root)
        env_examples = ['.env.example', '.env.sample', '.env.template']
        has_example = any((root / ef).exists() for ef in env_examples)
        
        return AuditResult(
            check_id="DEVOPS-003",
            check_name="Environment Template",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_example else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Add .env.example with all required variables"
        )
    
    def _check_readme(self, context: ProbeContext) -> AuditResult:
        """Check for README."""
        root = Path(context.project_root)
        readme_files = ['README.md', 'README.rst', 'README.txt']
        has_readme = any((root / rf).exists() for rf in readme_files)
        
        return AuditResult(
            check_id="DEVOPS-004",
            check_name="README Present",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_readme else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Add README.md with setup instructions"
        )
    
    def _check_makefile(self, context: ProbeContext) -> AuditResult:
        """Check for Makefile or task runner."""
        root = Path(context.project_root)
        task_files = ['Makefile', 'justfile', 'taskfile.yml']
        has_tasks = any((root / tf).exists() for tf in task_files)
        
        return AuditResult(
            check_id="DEVOPS-005",
            check_name="Task Runner",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_tasks else AuditStatus.INFO,
            severity=Severity.LOW,
            recommendation="Add Makefile with common commands"
        )
