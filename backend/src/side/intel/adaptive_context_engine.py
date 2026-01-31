
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Set
from side.intel.relevance_engine import Signal, RelevanceEngine
from side.intel.context_allocator import ContextAllocator, ContextPacket
from side.intel.verification_director import VerificationDirector
from side.storage.modules.base import SovereignEngine
from side.storage.modules.forensic import ForensicStore
from side.intel.intent_context_injector import IntentContextInjector
from side.utils.crypto import shield

logger = logging.getLogger(__name__)

class AdaptiveContextEngine:
    """
    [ACE] The Adaptive Context Engine.
    Unifies all intelligence components to deliver optimal, relevant context in <50ms.
    
    Flow:
    1. Focus Event -> Build Dependency Cluster
    2. Query All Signal Sources (Filtered by Cluster)
    3. Score by Relevance, Allocate by Token Budget
    4. Track Active Issues for Verification Loop
    """
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.engine = SovereignEngine()
        self.forensic = ForensicStore(self.engine)
        
        # Load pre-computed dependency graph from Fractal Index
        self.dependency_graph = self._load_dependency_graph()
        
        # Initialize sub-components
        self.relevance = RelevanceEngine(self.dependency_graph)
        self.allocator = ContextAllocator(self.relevance, budget=8000)
        self.injector = IntentContextInjector(self.engine)
        self.verification = VerificationDirector(self.forensic)

    def _load_dependency_graph(self) -> Dict[str, Set[str]]:
        """Loads the dependency graph from the Fractal Index."""
        import json
        graph = {}
        index_path = self.project_path / ".side" / "local.json"
        
        if index_path.exists():
            try:
                raw = shield.unseal_file(index_path)
                data = json.loads(raw)
                # Extract imports from DNA signals (simplified)
                for file_info in data.get("context", {}).get("files", []):
                    path = file_info.get("path", "")
                    imports = set(file_info.get("imports", []))
                    graph[path] = imports
            except Exception as e:
                logger.warning(f"Failed to load dependency graph: {e}")
        
        return graph

    def get_focus_cluster(self, focus_file: str, depth: int = 2) -> List[str]:
        """Gets the dependency cluster for a focused file."""
        cluster = {focus_file}
        
        # Direct imports
        direct_deps = self.dependency_graph.get(focus_file, set())
        cluster.update(direct_deps)
        
        # Reverse imports
        for file, deps in self.dependency_graph.items():
            if focus_file in deps:
                cluster.add(file)
        
        # 2nd-degree imports if depth > 1
        if depth > 1:
            for dep in list(direct_deps):
                cluster.update(self.dependency_graph.get(dep, set()))
        
        return list(cluster)

    def gather_signals(self, focus_cluster: List[str]) -> List[Signal]:
        """Gathers signals from all sources, filtered by focus cluster."""
        signals = []
        project_id = self.engine.get_project_id()
        
        # 1. Forensic Audits
        audits = self.forensic.get_recent_audits(project_id, limit=50)
        for audit in audits:
            if audit.get("file_path") in focus_cluster or not audit.get("file_path"):
                signals.append(Signal(
                    source="FORENSIC",
                    file_path=audit.get("file_path", ""),
                    content=audit.get("message", ""),
                    severity=audit.get("severity", "INFO"),
                    timestamp=time.time(),  # Simplified; use run_at in production
                    symbols=[],
                    token_cost=len(audit.get("message", "")) // 4
                ))
        
        # 2. Activities (Log Scavenger, etc.)
        activities = self.forensic.get_recent_activities(project_id, limit=30)
        for act in activities:
            payload = act.get("payload", {})
            if isinstance(payload, dict):
                source_file = payload.get("data", {}).get("file", "")
                if source_file in focus_cluster or act.get("tool") == "LOG_SCAVENGER":
                    signals.append(Signal(
                        source=act.get("tool", "ACTIVITY"),
                        file_path=source_file,
                        content=str(payload),
                        severity="INFO",
                        timestamp=time.time(),
                        symbols=[],
                        token_cost=len(str(payload)) // 4
                    ))
        
        # 3. Strategic Timeline (Tasks/Walkthroughs mentioning cluster)
        # This would query the sovereign.json strategic_timeline
        # Simplified for now: just add a placeholder
        
        return signals

    def process_focus_event(
        self,
        focus_file: str,
        focus_symbols: List[str] = None,
        cursor_line: int = None
    ) -> ContextPacket:
        """
        Main entry point. Processes a focus event and returns optimal context.
        
        Args:
            focus_file: The user's currently active file.
            focus_symbols: Symbols near the cursor.
            cursor_line: The line number of the cursor.
        
        Returns:
            A ContextPacket ready for LLM injection.
        """
        start_time = time.time()
        focus_symbols = focus_symbols or []
        
        # 1. Build Focus Cluster
        cluster = self.get_focus_cluster(focus_file)
        
        # 2. Gather All Signals (Filtered)
        signals = self.gather_signals(cluster)
        
        # 3. Allocate by Relevance
        packet = self.allocator.allocate(signals, focus_file, focus_symbols)
        
        # 3b. Inject Institutional Memory (Intent Fusion)
        if intent_context := self.injector.get_context_snippet(self.engine.get_project_id(), cluster):
             # We inject this as a high-priority "system" signal or prepend to prompt
             # For now, let's assume packet has a 'system_preamble' or we add a signal
             pass 
             # Implementation Detail: ideally ACE packet supports explicit sections.
             # We will add it as a synthesized signal for now.
             from side.intel.relevance_engine import Signal
             packet.signals.insert(0, Signal(
                 source="INSTITUTIONAL_MEMORY",
                 file_path="side://memory",
                 content=intent_context,
                 severity="WARN",
                 timestamp=time.time(),
                 symbols=[],
                 token_cost=len(intent_context)//4
             ))
        
        # 4. Register Issue if Errors Present
        error_signals = [s for s in packet.signals if s.severity in ("ERROR", "CRITICAL", "FATAL")]
        if error_signals:
            self.verification.register_issue(focus_file, cluster, error_signals)
        
        latency_ms = (time.time() - start_time) * 1000
        logger.info(f"⚡ [ACE]: Context delivered in {latency_ms:.1f}ms. Cluster: {len(cluster)} files, Signals: {len(packet.signals)}")
        
        return packet

    def verify_after_fix(self, focus_file: str) -> Dict[str, Any]:
        """Re-gathers signals and verifies if active issues are resolved."""
        cluster = self.get_focus_cluster(focus_file)
        current_signals = self.gather_signals(cluster)
        
        results = []
        for issue in self.verification.get_active_issues():
            if issue.focus_file == focus_file:
                result = self.verification.verify_fix(issue.fingerprint, current_signals)
                results.append(result)
        
        return {"verification_results": results}

if __name__ == "__main__":
    # Quick Test
    logging.basicConfig(level=logging.INFO)
    ace = AdaptiveContextEngine(Path.cwd())
    
    packet = ace.process_focus_event("backend/src/side/server.py", ["mcp", "tool"])
    print(ace.allocator.format_for_llm(packet))
