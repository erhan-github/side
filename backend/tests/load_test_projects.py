"""
Load Test: 1000+ Concurrent Projects

Stress tests Sidelith with high project concurrency.
Validates scalability claims for enterprise deployments.
"""
import asyncio
import time
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class LoadTestResult:
    """Results from load test execution."""
    total_projects: int
    successful_inits: int
    failed_inits: int
    avg_init_time_ms: float
    max_init_time_ms: float
    total_duration_s: float
    projects_per_second: float
    errors: List[str]
    
    @property
    def success_rate(self) -> float:
        return self.successful_inits / self.total_projects if self.total_projects > 0 else 0


class ProjectLoadTester:
    """
    Load tester for concurrent project initialization.
    
    Simulates enterprise scenario with 1000+ projects
    to validate Sidelith's horizontal scalability.
    """
    
    def __init__(self, base_dir: Path, num_projects: int = 1000):
        self.base_dir = base_dir
        self.num_projects = num_projects
        self.project_dirs: List[Path] = []
        self._metrics = {
            "init_times_ms": [],
            "errors": []
        }
    
    def setup(self):
        """Create project directories for testing."""
        logger.info(f"📁 [LOAD TEST]: Creating {self.num_projects} project directories...")
        
        for i in range(self.num_projects):
            proj_dir = self.base_dir / f"project_{i:04d}"
            proj_dir.mkdir(parents=True, exist_ok=True)
            
            # Create minimal Python file
            (proj_dir / "main.py").write_text(f"# Project {i}\nprint('Hello')\n")
            
            self.project_dirs.append(proj_dir)
        
        logger.info(f"📁 [LOAD TEST]: Created {len(self.project_dirs)} directories")
    
    def cleanup(self):
        """Remove test project directories."""
        for proj_dir in self.project_dirs:
            try:
                shutil.rmtree(proj_dir)
            except Exception:
                pass
    
    def run_sequential(self) -> LoadTestResult:
        """Run load test sequentially (baseline)."""
        from side.storage.modules.base import SovereignEngine
        
        logger.info(f"🚀 [LOAD TEST]: Running sequential test on {self.num_projects} projects...")
        
        start_time = time.time()
        successful = 0
        failed = 0
        init_times = []
        errors = []
        
        for proj_dir in self.project_dirs:
            try:
                t0 = time.time()
                db_path = proj_dir / ".side" / "local.db"
                engine = SovereignEngine(db_path)
                init_time = (time.time() - t0) * 1000
                
                init_times.append(init_time)
                successful += 1
                
            except Exception as e:
                failed += 1
                errors.append(str(e))
        
        total_duration = time.time() - start_time
        
        return LoadTestResult(
            total_projects=self.num_projects,
            successful_inits=successful,
            failed_inits=failed,
            avg_init_time_ms=sum(init_times) / len(init_times) if init_times else 0,
            max_init_time_ms=max(init_times) if init_times else 0,
            total_duration_s=total_duration,
            projects_per_second=successful / total_duration if total_duration > 0 else 0,
            errors=errors[:10]  # First 10 errors
        )
    
    async def run_concurrent(self, max_concurrent: int = 100) -> LoadTestResult:
        """Run load test with concurrent initialization."""
        from side.storage.modules.base import SovereignEngine
        
        logger.info(f"🚀 [LOAD TEST]: Running concurrent test ({max_concurrent} workers)...")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        start_time = time.time()
        init_times = []
        errors = []
        successful = 0
        failed = 0
        
        async def init_project(proj_dir: Path):
            nonlocal successful, failed
            async with semaphore:
                try:
                    t0 = time.time()
                    db_path = proj_dir / ".side" / "local.db"
                    
                    # Run sync code in executor
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, SovereignEngine, db_path)
                    
                    init_time = (time.time() - t0) * 1000
                    init_times.append(init_time)
                    successful += 1
                    
                except Exception as e:
                    failed += 1
                    errors.append(str(e))
        
        await asyncio.gather(*[init_project(p) for p in self.project_dirs])
        
        total_duration = time.time() - start_time
        
        return LoadTestResult(
            total_projects=self.num_projects,
            successful_inits=successful,
            failed_inits=failed,
            avg_init_time_ms=sum(init_times) / len(init_times) if init_times else 0,
            max_init_time_ms=max(init_times) if init_times else 0,
            total_duration_s=total_duration,
            projects_per_second=successful / total_duration if total_duration > 0 else 0,
            errors=errors[:10]
        )


def run_load_test(num_projects: int = 1000, concurrent: int = 100) -> LoadTestResult:
    """
    Run a complete load test.
    
    Args:
        num_projects: Number of projects to simulate
        concurrent: Max concurrent initializations
        
    Returns:
        LoadTestResult with metrics
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        tester = ProjectLoadTester(base_dir, num_projects)
        
        try:
            tester.setup()
            result = asyncio.run(tester.run_concurrent(concurrent))
            return result
        finally:
            tester.cleanup()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("SIDELITH LOAD TEST: 1000+ Concurrent Projects")
    print("=" * 60)
    
    result = run_load_test(num_projects=1000, concurrent=100)
    
    print(f"\nResults:")
    print(f"  Total Projects:     {result.total_projects}")
    print(f"  Successful:         {result.successful_inits}")
    print(f"  Failed:             {result.failed_inits}")
    print(f"  Success Rate:       {result.success_rate * 100:.1f}%")
    print(f"  Avg Init Time:      {result.avg_init_time_ms:.2f}ms")
    print(f"  Max Init Time:      {result.max_init_time_ms:.2f}ms")
    print(f"  Total Duration:     {result.total_duration_s:.2f}s")
    print(f"  Projects/Second:    {result.projects_per_second:.1f}")
    
    if result.success_rate >= 0.99:
        print("\n✅ PASS: 99%+ success rate achieved")
    else:
        print(f"\n❌ FAIL: Success rate {result.success_rate * 100:.1f}% below 99%")
