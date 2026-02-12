import asyncio
import logging
from datetime import datetime, time, timedelta, timezone

logger = logging.getLogger(__name__)

class StateSnapshotService:
    """
    State Snapshot Service.
    Compresses high-frequency events into hourly state summaries.
    """
    
    def __init__(self, engine, strategic, audit, operational):
        self.engine = engine
        self.plans = strategic
        self.audit = audit
        self.operational = operational
        self._task = None
        self._last_distillation = datetime.now()

    async def start(self):
        """Starts the active synthesis loop."""
        self._task = asyncio.create_task(self._run_loop())
        logger.info("🚀 [STATE_SNAPSHOT]: Active Synthesis Online.")

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run_loop(self):
        while True:
            try:
                # [STRATEGIC PIVOT]: Check if user is active and it's been > 30 mins
                now = datetime.now()
                last_activity_str = self.operational.get_setting("last_user_activity")
                
                if last_activity_str:
                    last_act = float(last_activity_str)
                    # Use float comparison for current time vs last activity
                    import time
                    if (time.time() - last_act) < 300: # Active in last 5 mins
                        if (now - self._last_distillation).total_seconds() > 1800: # 30 min window
                            await self.perform_distillation()
                            self._last_distillation = now
                
                await asyncio.sleep(60) # Heartbeat check
            except Exception as e:
                logger.error(f"🚀 [ROLLING_CHRONICLE]: Synthesis failed: {e}")
                await asyncio.sleep(300)

    async def perform_distillation(self):
        """Orchestrate the continuous synthesis process."""
        logger.info("⚡ [ROLLING_CHRONICLE]: Initiating Continuous Distillation...")
        
        # 1. Decay Strategic History
        strat_counts = self.plans.decay_strategic_history(days=30)
        
        # 2. Distill Audit Log Memory
        for_counts = self.audit.distill_audit_memory(days=14)
        
        # Before pruning raw activities, we distill them into high-entropy lessons.
        activity_summaries = await self.audit.summarize_activity_bursts(days=30)
        for summary in activity_summaries:
            self.plans.save_learning(
                learning_id=f"distill_{summary['tool']}_{int(datetime.now().timestamp())}",
                impact="medium",
                insight=f"Distilled Learning from {summary['intensity']} activities in {summary['tool']}.",
                source=f"distillation:{summary['tool']}"
            )
            
        # 4. Prune raw activities
        act_count = self.audit.prune_activities(days=30)
        
        total_forgotten = sum(strat_counts.values()) + sum(for_counts.values()) + act_count
        
        project_id = self.engine.get_project_id()
        self.audit.log_activity(
            project_id=project_id,
            tool="ROLLING_CHRONICLE",
            action="cache_decay",
            payload={
                "forgotten": total_forgotten,
                "strat": strat_counts,
                "audit": for_counts,
                "activities_pruned": act_count,
                "window": "ROLLING_ACTIVE_WINDOW"
            }
        )
        
        logger.info(f"✨ [RollingChronicle]: Successfully distilled {total_forgotten} fragments.")
        logger.info(f"   > Learnings Pruned: {strat_counts.get('learnings', 0)}")
        logger.info(f"   > Audits Distilled: {for_counts.get('audits_pruned', 0)}")
