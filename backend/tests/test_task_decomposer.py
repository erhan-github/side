"""
Test: TaskDecomposer Parallel Workers

Verifies TaskDecomposer parallel execution functionality.
"""
import pytest
import time
from pathlib import Path
from side.parallel.task_decomposer import TaskDecomposer, TaskChunk, get_decomposer


class TestTaskDecomposer:
    """Tests for TaskDecomposer functionality."""
    
    def test_decompose_by_files_creates_chunks(self):
        """decompose_by_files should split files into chunks."""
        decomposer = TaskDecomposer(max_workers=4)
        
        files = [Path(f"file_{i}.py") for i in range(25)]
        chunks = decomposer.decompose_by_files(files, chunk_size=10)
        
        assert len(chunks) == 3  # 25 files / 10 = 3 chunks
        assert len(chunks[0].payload) == 10
        assert len(chunks[1].payload) == 10
        assert len(chunks[2].payload) == 5
        
        decomposer.shutdown()
    
    def test_decompose_by_count_balances_chunks(self):
        """decompose_by_count should create balanced chunks."""
        decomposer = TaskDecomposer(max_workers=4)
        
        items = list(range(100))
        chunks = decomposer.decompose_by_count(items, num_chunks=4)
        
        assert len(chunks) == 4
        # Each chunk should have ~25 items
        for chunk in chunks:
            assert len(chunk.payload) in [25, 0]  # Edge case handling
        
        decomposer.shutdown()
    
    def test_execute_parallel_runs_all_chunks(self):
        """execute_parallel should process all chunks."""
        decomposer = TaskDecomposer(max_workers=4)
        
        items = list(range(20))
        chunks = decomposer.decompose_by_count(items, num_chunks=4)
        
        def worker(chunk: TaskChunk):
            return sum(chunk.payload)
        
        result = decomposer.execute_parallel(chunks, worker)
        
        assert result.completed_chunks == 4
        assert result.failed_chunks == 0
        assert sum(result.results) == sum(range(20))
        
        decomposer.shutdown()
    
    def test_parallel_is_faster_than_serial(self):
        """Parallel execution should be faster than serial for slow tasks."""
        decomposer = TaskDecomposer(max_workers=4)
        
        def slow_worker(chunk: TaskChunk):
            time.sleep(0.1)  # Simulate slow work
            return len(chunk.payload)
        
        items = list(range(8))
        chunks = decomposer.decompose_by_count(items, num_chunks=4)
        
        start = time.time()
        result = decomposer.execute_parallel(chunks, slow_worker)
        parallel_time = time.time() - start
        
        # Serial would take 4 * 0.1 = 0.4s
        # Parallel should take ~0.1s (plus overhead)
        assert parallel_time < 0.3, f"Parallel took {parallel_time:.2f}s, expected <0.3s"
        assert result.completed_chunks == 4
        
        decomposer.shutdown()
    
    def test_metrics_are_tracked(self):
        """Decomposer should track execution metrics."""
        decomposer = TaskDecomposer(max_workers=2)
        
        chunks = [TaskChunk(id=i, payload=i) for i in range(4)]
        decomposer.execute_parallel(chunks, lambda c: c.payload * 2)
        
        metrics = decomposer.metrics
        
        assert metrics["total_decompositions"] >= 1
        assert metrics["total_chunks_processed"] >= 4
        
        decomposer.shutdown()
    
    def test_handles_worker_errors_gracefully(self):
        """Decomposer should handle worker errors without crashing."""
        decomposer = TaskDecomposer(max_workers=2)
        
        def failing_worker(chunk: TaskChunk):
            if chunk.id == 1:
                raise ValueError("Intentional error")
            return chunk.payload
        
        chunks = [TaskChunk(id=i, payload=i) for i in range(4)]
        result = decomposer.execute_parallel(chunks, failing_worker)
        
        assert result.failed_chunks == 1
        assert result.completed_chunks == 3
        assert len(result.errors) == 1
        
        decomposer.shutdown()
    
    def test_global_singleton_works(self):
        """get_decomposer() should return singleton."""
        d1 = get_decomposer()
        d2 = get_decomposer()
        
        assert d1 is d2
