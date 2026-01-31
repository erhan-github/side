"""
TaskDecomposer - Parallel Work Distribution.

Implements the parallel worker pattern referenced in DREAM_JOURNEY_SCENARIO.md.
Splits large analysis tasks into parallel chunks for efficient processing.
"""
import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

logger = logging.getLogger(__name__)


@dataclass
class TaskChunk:
    """A single unit of work for parallel processing."""
    id: int
    payload: Any
    priority: int = 0
    result: Any = None
    error: Optional[str] = None
    duration_ms: float = 0


@dataclass
class DecompositionResult:
    """Aggregated results from parallel task execution."""
    total_chunks: int
    completed_chunks: int
    failed_chunks: int
    total_duration_ms: float
    results: List[Any] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class TaskDecomposer:
    """
    Splits large tasks into parallel chunks for efficient processing.
    
    Used in Alice's Day scenario for Deep Audit parallel execution:
    - Splits codebase audit into file batches
    - Executes 4 parallel workers
    - Aggregates results for unified report
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._metrics = {
            "total_decompositions": 0,
            "total_chunks_processed": 0,
            "total_failures": 0,
            "avg_chunk_duration_ms": 0
        }
    
    def decompose_by_files(self, files: List[Path], chunk_size: int = 10) -> List[TaskChunk]:
        """
        Decompose a list of files into balanced chunks.
        
        Args:
            files: List of file paths to process
            chunk_size: Number of files per chunk
        
        Returns:
            List of TaskChunk objects ready for parallel execution
        """
        chunks = []
        for i in range(0, len(files), chunk_size):
            batch = files[i:i + chunk_size]
            chunks.append(TaskChunk(
                id=i // chunk_size,
                payload=batch,
                priority=0
            ))
        
        logger.info(f"📦 [DECOMPOSER]: Split {len(files)} files into {len(chunks)} chunks")
        return chunks
    
    def decompose_by_count(self, items: List[Any], num_chunks: int = 4) -> List[TaskChunk]:
        """
        Decompose items into a fixed number of balanced chunks.
        
        Args:
            items: List of items to process
            num_chunks: Target number of chunks (default: 4 workers)
        
        Returns:
            List of TaskChunk objects
        """
        if not items:
            return []
        
        chunk_size = max(1, len(items) // num_chunks)
        chunks = []
        
        for i in range(0, len(items), chunk_size):
            chunks.append(TaskChunk(
                id=len(chunks),
                payload=items[i:i + chunk_size],
                priority=0
            ))
        
        logger.info(f"📦 [DECOMPOSER]: Split {len(items)} items into {len(chunks)} balanced chunks")
        return chunks
    
    def execute_parallel(
        self, 
        chunks: List[TaskChunk], 
        worker_fn: Callable[[TaskChunk], Any]
    ) -> DecompositionResult:
        """
        Execute chunks in parallel using thread pool.
        
        Args:
            chunks: List of TaskChunk objects
            worker_fn: Function to execute on each chunk
        
        Returns:
            DecompositionResult with aggregated outcomes
        """
        if not chunks:
            return DecompositionResult(0, 0, 0, 0)
        
        start_time = time.time()
        self._metrics["total_decompositions"] += 1
        
        completed = 0
        failed = 0
        results = []
        errors = []
        
        futures = {
            self.executor.submit(self._execute_chunk, chunk, worker_fn): chunk
            for chunk in chunks
        }
        
        for future in as_completed(futures):
            chunk = futures[future]
            try:
                result = future.result()
                chunk.result = result
                results.append(result)
                completed += 1
            except Exception as e:
                chunk.error = str(e)
                errors.append(f"Chunk {chunk.id}: {e}")
                failed += 1
                logger.error(f"❌ [DECOMPOSER]: Chunk {chunk.id} failed: {e}")
        
        total_duration = (time.time() - start_time) * 1000
        self._metrics["total_chunks_processed"] += completed
        self._metrics["total_failures"] += failed
        
        # Update average duration
        if completed > 0:
            avg_chunk = sum(c.duration_ms for c in chunks if c.result) / completed
            self._metrics["avg_chunk_duration_ms"] = (
                self._metrics["avg_chunk_duration_ms"] * 0.9 + avg_chunk * 0.1
            )
        
        logger.info(f"✅ [DECOMPOSER]: Completed {completed}/{len(chunks)} chunks in {total_duration:.1f}ms")
        
        return DecompositionResult(
            total_chunks=len(chunks),
            completed_chunks=completed,
            failed_chunks=failed,
            total_duration_ms=total_duration,
            results=results,
            errors=errors
        )
    
    def _execute_chunk(self, chunk: TaskChunk, worker_fn: Callable) -> Any:
        """Execute a single chunk and track timing."""
        start = time.time()
        result = worker_fn(chunk)
        chunk.duration_ms = (time.time() - start) * 1000
        return result
    
    async def execute_parallel_async(
        self,
        chunks: List[TaskChunk],
        worker_fn: Callable[[TaskChunk], Any]
    ) -> DecompositionResult:
        """
        Async version of parallel execution for IO-bound tasks.
        """
        if not chunks:
            return DecompositionResult(0, 0, 0, 0)
        
        start_time = time.time()
        
        async def process_chunk(chunk: TaskChunk) -> TaskChunk:
            try:
                start = time.time()
                if asyncio.iscoroutinefunction(worker_fn):
                    chunk.result = await worker_fn(chunk)
                else:
                    loop = asyncio.get_event_loop()
                    chunk.result = await loop.run_in_executor(None, worker_fn, chunk)
                chunk.duration_ms = (time.time() - start) * 1000
            except Exception as e:
                chunk.error = str(e)
            return chunk
        
        processed_chunks = await asyncio.gather(
            *[process_chunk(c) for c in chunks]
        )
        
        completed = sum(1 for c in processed_chunks if c.result is not None)
        failed = sum(1 for c in processed_chunks if c.error is not None)
        
        return DecompositionResult(
            total_chunks=len(chunks),
            completed_chunks=completed,
            failed_chunks=failed,
            total_duration_ms=(time.time() - start_time) * 1000,
            results=[c.result for c in processed_chunks if c.result is not None],
            errors=[c.error for c in processed_chunks if c.error is not None]
        )
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get decomposer performance metrics."""
        return dict(self._metrics)
    
    def shutdown(self):
        """Gracefully shutdown the thread pool."""
        self.executor.shutdown(wait=True)


# Global singleton for easy access
_decomposer: Optional[TaskDecomposer] = None


def get_decomposer(max_workers: int = 4) -> TaskDecomposer:
    """Get or create the global TaskDecomposer instance."""
    global _decomposer
    if _decomposer is None:
        _decomposer = TaskDecomposer(max_workers=max_workers)
    return _decomposer
