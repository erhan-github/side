
import os
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class BrainBridge:
    """
    The 'High-Fidelity Bridge'.
    Surgically extracts tasks and walkthroughs from the Antigravity Brain
    and converts them into High-Density Strategic Schemas.
    """
    
    def __init__(self, brain_root: Path):
        self.brain_root = brain_root

    def scan_nodes(self) -> List[Dict[str, Any]]:
        """Scans all nodes for temporal-anchored documents."""
        nodes = []
        if not self.brain_root.exists():
            return []

        for node_dir in self.brain_root.iterdir():
            if node_dir.is_dir():
                node_data = self._process_node(node_dir)
                if node_data:
                    nodes.append(node_data)
        return nodes

    def _process_node(self, node_dir: Path) -> Dict[str, Any] | None:
        """Processes a single project node."""
        tasks = []
        walkthroughs = []
        
        # 1. Harvest Tasks (Surgical scan for task.md)
        for task_file in node_dir.glob("task.md*"):
            if ".metadata" in task_file.name: continue
            
            task_data = self._parse_task(task_file)
            if task_data:
                tasks.append(task_data)

        # 2. Harvest Walkthroughs (Surgical scan for *WALKTHROUGH.md)
        for walk_file in node_dir.glob("*WALKTHROUGH.md*"):
            if ".metadata" in walk_file.name: continue
            
            walk_data = self._parse_walkthrough(walk_file)
            if walk_data:
                walkthroughs.append(walk_data)

        if not tasks and not walkthroughs:
            return None

        return {
            "node_id": node_dir.name,
            "tasks": tasks,
            "walkthroughs": walkthroughs
        }

    def _get_birth_time(self, file_path: Path) -> str:
        """Gets the definitive Birth Time of a document."""
        # 1. Check internal marker (The 'Ground Truth')
        try:
            content = file_path.read_text()
            match = re.search(r"Generated[:\s*]+\*\*?(\d{4}-\d{2}-\d{2})", content)
            if match:
                return f"{match.group(1)}T00:00:00Z"
        except:
            pass
            
        # 2. Fallback to OS Time (Native & Cross-Platform)
        try:
            mtime = file_path.stat().st_mtime
            return datetime.fromtimestamp(mtime).isoformat() + "Z"
        except:
            return datetime.now().isoformat() + "Z"

    def _parse_task(self, file_path: Path) -> Dict[str, Any] | None:
        """Converts task.md into task_ledger_v1 with priority parsing."""
        try:
            content = file_path.read_text()
            birth_time = self._get_birth_time(file_path)
            
            # Priority Extraction
            p0 = len(re.findall(r"## 🔴 P0", content)) > 0
            p1 = len(re.findall(r"## 🟡 P1", content)) > 0
            
            # Aggregate stats
            p0_tasks = re.findall(r"## 🔴 P0.*?##", content, re.DOTALL)
            p0_done = p0_tasks[0].count("[x]") if p0_tasks else 0
            p0_total = p0_done + (p0_tasks[0].count("[ ]") if p0_tasks else 0)

            completedCount = content.count("[x]")
            totalCount = completedCount + content.count("[ ]")
            
            return {
                "id": file_path.name,
                "birth_time": birth_time,
                "summary": {
                    "total": totalCount,
                    "done": completedCount,
                    "production_readiness": re.findall(r"Score[:\s*]+(\d+/100)", content)
                },
                "priorities": {
                    "P0": {"total": p0_total, "done": p0_done}
                }
            }
        except Exception as e:
            return None

    def _parse_walkthrough(self, file_path: Path) -> Dict[str, Any] | None:
        """Converts walkthrough.md into decision_trace_v1 with pivot detection."""
        try:
            content = file_path.read_text()
            birth_time = self._get_birth_time(file_path)
            
            # Extract Pivots/Decisions
            pivots = []
            pivot_matches = re.finditer(r"#### ✅ (.*?)\n.*?Decision[:\s*]+(.*?)\n", content, re.DOTALL)
            for m in pivot_matches:
                pivots.append({
                    "subject": m.group(1).strip(),
                    "decision": m.group(2).strip()
                })

            # Extract Proofs
            proofs = []
            if "Performance Proof" in content:
                metrics = re.finditer(r"Average[:\s*]+([\d\.]+\w+)", content)
                for m in metrics:
                    proofs.append({"metric": "latency", "value": m.group(1)})

            return {
                "trace_id": file_path.name,
                "event_time": birth_time,
                "pivots": pivots,
                "proofs": proofs
            }
        except:
            return None

if __name__ == "__main__":
    # Test Run
    bridge = BrainBridge(Path("/Users/erhanerdogan/.gemini/antigravity/brain"))
    nodes = bridge.scan_nodes()
    print(json.dumps(nodes[:2], indent=2))
