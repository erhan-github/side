"""
[PHASE 6.2] Multi-Dimensional Metrics Calculator
Calculates Time Spent, Persistence, Commonality, and Difficulty for verified fixes.
"""
import time
import logging
from typing import Dict, Any, List, Optional
from side.intel.types import FixMetrics, Difficulty

logger = logging.getLogger(__name__)

class MetricsCalculator:
    """
    Calculates multi-dimensional metrics for verified fixes.
    These metrics power the Cloud Distillation Protocol.
    """
    
    def __init__(self, cloud_client=None):
        """
        Args:
            cloud_client: Optional client for querying global patterns (commonality).
        """
        self.cloud_client = cloud_client

    def calculate_all(
        self,
        issue_detected_at: float,
        fix_applied_at: float,
        verification_at: float,
        fix_attempts: int,
        cluster_size: int,
        severity: str,
        error_pattern: str = None
    ) -> FixMetrics:
        """
        Calculates all metrics for a verified fix.
        
        Args:
            issue_detected_at: Unix timestamp when issue was first detected.
            fix_applied_at: Unix timestamp when fix was applied.
            verification_at: Unix timestamp when verification passed.
            fix_attempts: Number of fix attempts.
            cluster_size: Number of files in the focus cluster.
            severity: The severity of the issue (CRITICAL, ERROR, etc.)
            error_pattern: Optional error pattern for commonality lookup.
        
        Returns:
            A FixMetrics object with all dimensions calculated.
        """
        time_spent = self.calculate_time_spent(issue_detected_at, verification_at)
        persistence = self.calculate_persistence(issue_detected_at, fix_applied_at)
        commonality = self.calculate_commonality(error_pattern)
        difficulty = self.calculate_difficulty(fix_attempts, cluster_size, severity)
        
        return FixMetrics(
            time_spent_seconds=time_spent,
            fix_attempts=fix_attempts,
            persistence_score=persistence,
            commonality_index=commonality,
            difficulty=difficulty,
            cluster_size=cluster_size
        )

    def calculate_time_spent(self, start: float, end: float) -> float:
        """Time from detection to verification in seconds."""
        return max(0, end - start)

    def calculate_persistence(self, detected_at: float, fixed_at: float) -> float:
        """
        Persistence score: How long the issue persisted before being fixed.
        0.0 = Fixed immediately (<1 min)
        0.5 = Fixed in ~30 minutes
        1.0 = Fixed after 1+ hour
        """
        duration_seconds = fixed_at - detected_at
        duration_minutes = duration_seconds / 60
        
        if duration_minutes < 1:
            return 0.0
        elif duration_minutes < 5:
            return 0.2
        elif duration_minutes < 15:
            return 0.4
        elif duration_minutes < 30:
            return 0.6
        elif duration_minutes < 60:
            return 0.8
        else:
            return 1.0

    def calculate_commonality(self, error_pattern: str = None) -> float:
        """
        Commonality index: How often this pattern occurs globally.
        Queries cloud for similar patterns if available.
        
        Returns 0.0-1.0 where 1.0 means very common.
        """
        if not error_pattern or not self.cloud_client:
            return 0.0  # Unknown commonality without cloud
        
        # Local Heuristic (V1) - Replaces Cloud Query
        # In a distributed system, this would query the central hive.

        common_patterns = [
            "None", "undefined", "null", "NoneType",
            "timeout", "connection", "auth", "permission",
            "import", "module", "not found"
        ]
        
        matches = sum(1 for p in common_patterns if p.lower() in error_pattern.lower())
        return min(1.0, matches * 0.2)

    def calculate_difficulty(
        self,
        fix_attempts: int,
        cluster_size: int,
        severity: str
    ) -> str:
        """
        Difficulty rating based on attempts, cluster size, and severity.
        
        LOW: 1 attempt, small cluster (<3), non-critical
        MEDIUM: 2-3 attempts, or medium cluster (3-7), or ERROR severity
        HIGH: 4+ attempts, or large cluster (8+), or CRITICAL/FATAL
        """
        difficulty_score = 0
        
        # Attempts factor
        if fix_attempts >= 4:
            difficulty_score += 3
        elif fix_attempts >= 2:
            difficulty_score += 1
        
        # Cluster size factor
        if cluster_size >= 8:
            difficulty_score += 3
        elif cluster_size >= 3:
            difficulty_score += 1
        
        # Severity factor
        if severity in ("CRITICAL", "FATAL"):
            difficulty_score += 3
        elif severity == "ERROR":
            difficulty_score += 1
        
        # Map score to difficulty
        if difficulty_score >= 5:
            return Difficulty.HIGH.value
        elif difficulty_score >= 2:
            return Difficulty.MEDIUM.value
        else:
            return Difficulty.LOW.value

if __name__ == "__main__":
    # Quick Test
    calc = MetricsCalculator()
    
    now = time.time()
    metrics = calc.calculate_all(
        issue_detected_at=now - 600,  # 10 minutes ago
        fix_applied_at=now - 60,       # 1 minute ago
        verification_at=now,
        fix_attempts=2,
        cluster_size=5,
        severity="ERROR",
        error_pattern="session.user is None"
    )
    
    print(f"Time Spent: {metrics.time_spent_seconds:.0f}s")
    print(f"Persistence: {metrics.persistence_score}")
    print(f"Commonality: {metrics.commonality_index}")
    print(f"Difficulty: {metrics.difficulty}")
