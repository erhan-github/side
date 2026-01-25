"""
Side Task Decomposer - The Strategy Engine.

Splits high-level intents into atomic, parallelizable jobs.
"Divide and Conquer".
"""

from typing import List, Dict
from .queue import JobQueue

class TaskDecomposer:
    """
    Analyzes user intent and spawns micro-tasks.
    """
    
    def __init__(self, queue: JobQueue, project_id: str):
        self.queue = queue
        self.project_id = project_id
        
    def decompose_request(self, intent: str, context: Dict) -> str:
        """
        Take a user request and fill the queue.
        Returns the batch_id (parent task ID).
        """
        # 1. Deterministic Heuristics (Tier 1)
        # Fast, rule-based splitting.
        
        # Example: "Refactor <file>"
        if "refactor" in intent.lower() and "file" in context:
            return self._plan_refactor(context['file'])
            
        # Example: "Audit"
        if "audit" in intent.lower():
            return self._plan_full_audit()
            
        # Fallback: General Research (Tier 2 - LLM would go here)
        return self._plan_research(intent)

    def _plan_refactor(self, filename: str) -> str:
        """Strategy for refactoring a file."""
        print(f"⚡ Decomposing Refactor for {filename}")
        
        # 1. Map Dependencies (Who calls me?)
        self.queue.enqueue(self.project_id, "dependency_map", {"target": filename}, priority=10)
        
        # 2. Safety Check (Tests)
        self.queue.enqueue(self.project_id, "discover_tests", {"target": filename}, priority=10)
        
        # 3. Security Scan (Don't break secrets)
        self.queue.enqueue(self.project_id, "security_scan", {"target": filename}, priority=9)
        
        # 4. Complexity Analysis (Baseline)
        self.queue.enqueue(self.project_id, "complexity_gauge", {"target": filename}, priority=8)
        
        return "refactor_batch_1"

    def _plan_full_audit(self) -> str:
        """Strategy for full project audit."""
        # Split by dimension for parallelism
        dims = ["security", "performance", "code_quality", "architecture"]
        for d in dims:
            self.queue.enqueue(self.project_id, "audit_dimension", {"dimension": d}, priority=5)
        return "audit_batch_1"

    def _plan_research(self, query: str) -> str:
        """Strategy for general questions."""
        # 1. Search Monolith
        self.queue.enqueue(self.project_id, "context_search", {"query": query}, priority=10)
        return "research_batch_1"
