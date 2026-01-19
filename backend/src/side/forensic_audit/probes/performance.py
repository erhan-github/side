"""
Performance Probe - Comprehensive performance audit.

Forensic-level performance checks covering:
- N+1 query detection
- Async usage patterns
- Memory leak patterns
- Database efficiency
- Frontend performance
"""

import re
from pathlib import Path
from typing import List
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier


class PerformanceProbe:
    """Forensic-level performance audit probe."""
    
    id = "forensic.performance"
    name = "Performance Audit"
    tier = Tier.FAST
    dimension = "Performance"
    
    def run(self, context: ProbeContext) -> List[AuditResult]:
        """Run all performance checks."""
        return [
            self._check_n_plus_one(context),
            self._check_async_patterns(context),
            self._check_blocking_calls(context),
            self._check_unbounded_loops(context),
            self._check_large_file_reads(context),
            self._check_db_connection_pooling(context),
            self._check_caching_patterns(context),
            self._check_batch_operations(context),
        ]
    
    def _check_n_plus_one(self, context: ProbeContext) -> AuditResult:
        """Detect N+1 query patterns."""
        evidence = []
        patterns = [
            (r"for\s+\w+\s+in\s+.*:\s*\n\s*.*\.query\(", "Query inside loop"),
            (r"for\s+\w+\s+in\s+.*:\s*\n\s*.*\.execute\(", "Execute inside loop"),
            (r"for\s+\w+\s+in\s+.*:\s*\n\s*.*\.find\(", "Find inside loop"),
            (r"for\s+\w+\s+in\s+.*:\s*\n\s*.*\.get\(", "Get inside loop (potential N+1)"),
        ]
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                for pattern, desc in patterns:
                    matches = list(re.finditer(pattern, content, re.MULTILINE))
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        evidence.append(AuditEvidence(
                            description=desc,
                            file_path=file_path,
                            line_number=line_num,
                            suggested_fix="Use batch queries or prefetch related data"
                        ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="PERF-001",
            check_name="N+1 Query Detection",
            dimension=self.dimension,
            status=AuditStatus.FAIL if evidence else AuditStatus.PASS,
            severity=Severity.HIGH,
            evidence=evidence[:10],
            recommendation="Use JOINs, prefetch_related, or batch queries"
        )
    
    def _check_async_patterns(self, context: ProbeContext) -> AuditResult:
        """Check for proper async/await usage."""
        evidence = []
        async_funcs = 0
        sync_in_async = []
        
        blocking_calls = ['time.sleep', 'requests.', 'open(', 'subprocess.run']
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                lines = content.splitlines()
                in_async = False
                
                for i, line in enumerate(lines):
                    if 'async def' in line:
                        in_async = True
                        async_funcs += 1
                    elif line.strip().startswith('def ') and not line.strip().startswith('def __'):
                        in_async = False
                    
                    if in_async:
                        for bc in blocking_calls:
                            if bc in line and 'asyncio' not in line:
                                evidence.append(AuditEvidence(
                                    description=f"Blocking call in async function: {bc}",
                                    file_path=file_path,
                                    line_number=i + 1,
                                    suggested_fix="Use async alternatives (asyncio.sleep, httpx, aiofiles)"
                                ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="PERF-002",
            check_name="Async Usage Patterns",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=evidence[:10],
            notes=f"Found {async_funcs} async functions",
            recommendation="Use async variants for I/O operations in async functions"
        )
    
    def _check_blocking_calls(self, context: ProbeContext) -> AuditResult:
        """Check for blocking calls on hot paths."""
        evidence = []
        
        hot_paths = ['api', 'route', 'handler', 'view', 'endpoint']
        blocking_patterns = [
            (r'time\.sleep\s*\(', 'time.sleep() blocks event loop'),
            (r'requests\.(get|post|put|delete)\s*\(', 'requests library is blocking'),
        ]
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            if not any(hp in file_path.lower() for hp in hot_paths):
                continue
            
            try:
                content = Path(file_path).read_text()
                for line_idx, line in enumerate(content.splitlines(), 1):
                    for pattern, desc in blocking_patterns:
                        if re.search(pattern, line):
                            evidence.append(AuditEvidence(
                                description=desc,
                                file_path=file_path,
                                line_number=line_idx
                            ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="PERF-003",
            check_name="No Blocking Calls on Hot Paths",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=evidence[:5],
            recommendation="Use httpx for async HTTP, asyncio.sleep for delays"
        )
    
    def _check_unbounded_loops(self, context: ProbeContext) -> AuditResult:
        """Detect potentially unbounded loops."""
        evidence = []
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                lines = content.splitlines()
                
                for i, line in enumerate(lines):
                    if 'while True' in line or 'while 1:' in line:
                        # Check next 10 lines for break
                        next_lines = lines[i:i+10]
                        if not any('break' in nl for nl in next_lines):
                            evidence.append(AuditEvidence(
                                description="while True without visible break",
                                file_path=file_path,
                                line_number=i + 1
                            ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="PERF-004",
            check_name="No Unbounded Loops",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=evidence[:5],
            recommendation="Add break conditions or timeouts to infinite loops"
        )
    
    def _check_large_file_reads(self, context: ProbeContext) -> AuditResult:
        """Detect large file reads without streaming."""
        evidence = []
        
        patterns = [
            (r'\.read\(\)\s*$', 'read() without size limit'),
            (r'\.read_text\(\)', 'read_text() loads entire file'),
            (r'json\.load\s*\(\s*open', 'json.load without streaming'),
        ]
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                for line_idx, line in enumerate(content.splitlines(), 1):
                    for pattern, desc in patterns:
                        if re.search(pattern, line):
                            # Skip if it's clearly a small file
                            if 'config' in line.lower() or '.json' in line.lower():
                                continue
                            evidence.append(AuditEvidence(
                                description=desc,
                                file_path=file_path,
                                line_number=line_idx,
                                suggested_fix="Use streaming or chunked reads for large files"
                            ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="PERF-005",
            check_name="Streaming for Large Files",
            dimension=self.dimension,
            status=AuditStatus.PASS if len(evidence) < 5 else AuditStatus.WARN,
            severity=Severity.LOW,
            evidence=evidence[:5],
            recommendation="Use chunked reads or streaming for large files"
        )
    
    def _check_db_connection_pooling(self, context: ProbeContext) -> AuditResult:
        """Check for database connection pooling."""
        has_pooling = False
        pooling_indicators = ['pool_size', 'create_engine', 'pool_recycle', 'connection_pool', 'QueuePool']
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                if any(pi in content for pi in pooling_indicators):
                    has_pooling = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="PERF-006",
            check_name="Database Connection Pooling",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_pooling else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            notes="Connection pooling detected" if has_pooling else "No connection pooling found",
            recommendation="Use SQLAlchemy with pool_size or similar for production"
        )
    
    def _check_caching_patterns(self, context: ProbeContext) -> AuditResult:
        """Check for caching patterns."""
        caching_indicators = ['@cache', '@lru_cache', 'redis', 'memcached', 'cache_key', 'get_or_set']
        has_caching = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(ci in content for ci in caching_indicators):
                    has_caching = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="PERF-007",
            check_name="Caching Strategy",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_caching else AuditStatus.INFO,
            severity=Severity.LOW,
            notes="Caching patterns found" if has_caching else "Consider adding caching for expensive operations",
            recommendation="Use @lru_cache for pure functions, Redis for distributed"
        )
    
    def _check_batch_operations(self, context: ProbeContext) -> AuditResult:
        """Check for batch operations patterns."""
        evidence = []
        
        single_op_patterns = [
            (r'for\s+\w+\s+in\s+.*:\s*\n\s*.*\.insert\(', "Single insert in loop"),
            (r'for\s+\w+\s+in\s+.*:\s*\n\s*.*\.save\(', "Single save in loop"),
            (r'for\s+\w+\s+in\s+.*:\s*\n\s*.*\.create\(', "Single create in loop"),
        ]
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                for pattern, desc in single_op_patterns:
                    if re.search(pattern, content, re.MULTILINE):
                        evidence.append(AuditEvidence(
                            description=desc,
                            file_path=file_path,
                            suggested_fix="Use bulk_create, insert_many, or batch operations"
                        ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="PERF-008",
            check_name="Batch Operations",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=evidence[:5],
            recommendation="Use batch/bulk operations for multiple inserts/updates"
        )
