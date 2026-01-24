import pytest
import asyncio
from pathlib import Path
from side.forensic_audit.core import ProbeContext, AuditStatus, Severity
from side.forensic_audit.probes.performance import PerformanceProbe
from side.forensic_audit.probes.security import SecurityProbe

@pytest.fixture
def probe_context(tmp_path):
    """Fixture to create a mock probe context."""
    return ProbeContext(
        project_root=str(tmp_path),
        files=[],
        strategic_context={},
        intelligence_store=None,
        llm_client=None
    )

@pytest.mark.asyncio
async def test_performance_n_plus_one_false_positives(tmp_path, probe_context):
    """
    TRAINING: Ensure dictionary .get() isn't flagged as N+1.
    This test prevents regressions of the 'trending.py' false positive.
    """
    probe = PerformanceProbe()
    
    # Create a safe file with dictionary gets
    safe_file = tmp_path / "safe.py"
    safe_file.write_text('''
for item in items:
    val = item.get('key')
    name = user_dict.get('name', 'Anonymous')
''')
    
    probe_context.files = [str(safe_file)]
    results = await probe.run(probe_context)
    
    n1_check = next(r for r in results if r.check_id == "PERF-001")
    assert n1_check.status == AuditStatus.PASS, f"Expected PASS for dict gets, got FAIL: {n1_check.evidence}"

@pytest.mark.asyncio
async def test_performance_n_plus_one_real_issues(tmp_path, probe_context):
    """
    TRAINING: Ensure real N+1 patterns are still caught.
    """
    probe = PerformanceProbe()
    
    # Create a risky file with actual DB-like patterns
    risky_file = tmp_path / "risky.py"
    risky_file.write_text('''
for user_id in user_ids:
    user = db.users.get(user_id)
''')
    
    probe_context.files = [str(risky_file)]
    results = await probe.run(probe_context)
    
    n1_check = next(r for r in results if r.check_id == "PERF-001")
    assert n1_check.status == AuditStatus.FAIL, "Expected FAIL for db.users.get inside loop"

@pytest.mark.asyncio
async def test_security_secrets_detection(tmp_path, probe_context):
    """
    TRAINING: Ensure security probe catches hardcoded secrets using standard patterns.
    """
    probe = SecurityProbe()
    
    # Create a file with a secret that matches current patterns (e.g. api_key)
    secret_file = tmp_path / "secrets.py"
    secret_file.write_text('ADMIN_API_KEY = "ak_test_primary_key_for_backend_2026"')
    
    probe_context.files = [str(secret_file)]
    probe_context.project_root = str(tmp_path) # Important for ignore logic
    results = await probe.run(probe_context)
    
    secret_check = next((r for r in results if r.check_id == "SEC-001"), None)
    assert secret_check.status == AuditStatus.FAIL, "Expected FAIL for hardcoded API Key"

@pytest.mark.asyncio
async def test_security_github_token_detection(tmp_path, probe_context):
    """
    TRAINING: Ensure GitHub tokens are detected.
    """
    probe = SecurityProbe()
    token_file = tmp_path / "deploy.sh"
    token_file.write_text('TOKEN=ghp_ABC123def456GHI789jkl012MNO345PQR678')
    
    probe_context.files = [str(token_file)]
    probe_context.project_root = str(tmp_path)
    results = await probe.run(probe_context)
    
    secret_check = next((r for r in results if r.check_id == "SEC-001"), None)
    assert secret_check.status == AuditStatus.FAIL, "Expected FAIL for GitHub token"
