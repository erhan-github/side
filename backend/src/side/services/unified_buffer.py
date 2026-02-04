import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class UnifiedBuffer:
    """
    Unified Buffer: High-Frequency Context Sync.
    Aggregates strategic, forensic, and operational signals into a single 
    asynchronous stream to maintain low-latency developer workflow.
    """
    
    def __init__(self, stores: Dict[str, Any], flush_interval: float = 2.0, max_buffer_size: int = 1000):
        self.stores = stores # {'strategic': strat, 'forensic': for, 'operational': op}
        self.flush_interval = flush_interval
        self.max_buffer_size = max_buffer_size
        
        self._buffer = defaultdict(list)
        self._buffer_count = 0 
        self._running = False
        self._flush_task = None
        self._lock = asyncio.Lock()
        
        # Performance Telemetry
        self.signals_ingested = 0
        self.signals_flushed = 0
        self.last_flush_time = 0.0
        self._last_flush_ts = time.time()
        
        # [KAR-6.13] Adaptive Throttle & Feedback
        self._pressure_multiplier = 1.0 # 0.1 (safe) to 1.0 (max)
        self._stream_limit = 50 
        self._feedback_stream = deque(maxlen=self._stream_limit) # Optimized sliding window

    async def start(self):
        """Starts the background flush loop."""
        if self._running:
            return
        self._running = True
        self._flush_task = asyncio.create_task(self._run_flush_loop())
        logger.info(f"⚡ [BUFFER]: Unified Buffer active. (Interval: {self.flush_interval}s)")

    async def stop(self):
        """Final flush and shutdown."""
        self._running = False
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        await self.flush()
        logger.info("⚡ [BUFFER]: Unified Buffer offline.")

    async def ingest(self, category: str, data: Dict[str, Any]):
        """
        Ingests a signal into the buffer. 
        [SEMANTIC GATING] (T-002): Protects high-entropy signals from throttling.
        """
        self.signals_ingested += 1
        importance = self._calculate_importance(category, data)
        
        # Pressure Control: Drop low-importance signals only
        if self._pressure_multiplier < 0.5 and importance < 0.4:
            if self.signals_ingested % 2 == 0:
                return

        async with self._lock:
            self._buffer[category].append(data)
            self._buffer_count += 1
            
            # Update Feedback Stream
            self._feedback_stream.append({
                "category": category,
                "label": data.get("action", data.get("category", "event")),
                "importance": importance,
                "ts": time.time()
            })

            # Immediate flush if buffer exceeds safety limit
            if self._buffer_count >= self.max_buffer_size:
                asyncio.create_task(self.flush())

    def _calculate_importance(self, category: str, data: Dict[str, Any]) -> float:
        """Determines the 'Strategic Entropy' of a signal."""
        # 1. High-Entropy Failures
        if category == "activity":
            action = data.get("action", "")
            if action in ["unhandled_exception", "runtime_warning"]:
                return 1.0
            payload = data.get("payload", {})
            if action == "log_signal" and payload.get("level") == "ERROR":
                return 0.9
        
        # 2. Defensiveness (Rejections & Wisdom)
        if category in ["rejection", "patterns", "insights"]:
            return 0.9
            
        # 3. Structural Updates
        if category == "mesh":
            return 0.5
            
        return 0.1 # Default (Routine I/O)

    def get_stream(self) -> List[Dict[str, Any]]:
        """Returns the ephemeral feedback stream for UI rendering."""
        return list(self._feedback_stream)

    async def _run_flush_loop(self):
        """Continuous background flushing."""
        while self._running:
            await asyncio.sleep(self.flush_interval)
            await self.flush()

    async def flush(self):
        """Commit buffered signals to their respective stores."""
        if self._buffer_count == 0:
            return

        async with self._lock:
            current_buffer = dict(self._buffer)
            self._buffer.clear()
            self._buffer_count = 0

        start_time = time.perf_counter()
        flushed_in_batch = 0

        try:
            # 1. Forensic Activities (Audits, SFI, Shell)
            if activities := current_buffer.get("activity"):
                await asyncio.to_thread(self.stores['forensic'].log_activities_batch, activities)
                flushed_in_batch += len(activities)

            if shell_cmds := current_buffer.get("shell"):
                shell_batch = []
                for cmd in shell_cmds:
                    shell_batch.append({
                        'project_id': 'global',
                        'tool': 'shell',
                        'action': 'command',
                        'payload': cmd['payload']
                    })
                await asyncio.to_thread(self.stores['forensic'].log_activities_batch, shell_batch)
                flushed_in_batch += len(shell_cmds)

            # 2. Strategic Rejections
            if rejections := current_buffer.get("rejection"):
                await asyncio.to_thread(self.stores['strategic'].save_rejections_batch, rejections)
                flushed_in_batch += len(rejections)

            # 3. Operational Mesh Updates
            if mesh_nodes := current_buffer.get("mesh"):
                await asyncio.to_thread(self.stores['operational'].register_mesh_nodes_batch, mesh_nodes)
                flushed_in_batch += len(mesh_nodes)
                
            # 4. Technical Patterns
            if patterns := current_buffer.get("insights") or current_buffer.get("wisdom"):
                await asyncio.to_thread(self.stores['strategic'].save_public_patterns_batch, patterns)
                flushed_in_batch += len(patterns)

            self.signals_flushed += flushed_in_batch
            
            # 5. [HYPER-PERCEPTION]: Calculate Work Velocity (signals/sec)
            now = time.time()
            delta = now - self._last_flush_ts
            if delta > 0:
                velocity = flushed_in_batch / delta
                self.stores['operational'].set_setting("buffer_ingest_velocity", str(round(velocity, 3)))
            self._last_flush_ts = now

            self.last_flush_time = (time.perf_counter() - start_time) * 1000
            
            if flushed_in_batch > 0:
                logger.debug(f"⚡ [BUFFER]: Flushed {flushed_in_batch} signals in {self.last_flush_time:.2f}ms")

        except Exception as e:
            logger.error(f"⚡ [BUFFER]: Flush failure: {e}")
            # Increase pressure on failure
            self._pressure_multiplier = max(0.1, self._pressure_multiplier - 0.2)
            pass
        finally:
            # 5. [ADAPTIVE THROTTLE]: Adjust multiplier based on performance
            # If flush takes > 500ms, decrease multiplier. If < 50ms, increase.
            if self.last_flush_time > 500:
                self._pressure_multiplier = max(0.1, self._pressure_multiplier - 0.1)
            elif self.last_flush_time < 50:
                self._pressure_multiplier = min(1.0, self._pressure_multiplier + 0.05)

# Entry for ServiceManager
async def create_buffer(stores):
    buf = UnifiedBuffer(stores)
    await buf.start()
    return buf
