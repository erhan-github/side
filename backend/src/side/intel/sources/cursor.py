"""
Cursor Intent Source.

Ingests intent from Cursor plans.
Parses YAML frontmatter manually to avoid dependencies.
"""

import os
import re
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from side.intel.sources.base import IntentSource

logger = logging.getLogger(__name__)

class CursorSource(IntentSource):
    """
    Reads Cursor plans and extracts 'name' and 'overview' as intent.
    """
    
    def __init__(self, plans_dir: Path | None = None):
        if plans_dir is None:
            self.plans_dir = Path.home() / ".cursor" / "plans"
        else:
            self.plans_dir = plans_dir

    def scan_nodes(self) -> List[Dict[str, Any]]:
        """Scans Cursor plans directory."""
        nodes = []
        if not self.plans_dir.exists():
            return []

        for plan_file in self.plans_dir.glob("*.plan.md"):
            try:
                node_data = self._parse_plan(plan_file)
                if node_data:
                    nodes.append(node_data)
            except Exception as e:
                logger.warning(f"Failed to parse Cursor plan {plan_file.name}: {e}")
                
        return nodes

    def _parse_plan(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parses a single plan file.
        Expects YAML frontmatter:
        ---
        name: ...
        overview: ...
        ---
        """
        content = file_path.read_text(encoding='utf-8')
        
        # 1. Extract Frontmatter
        match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return None
            
        frontmatter = match.group(1)
        
        # 2. Parse basic YAML fields (manual regex for robustness without PyYAML)
        name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
        overview_match = re.search(r"^overview:\s*(.+)$", frontmatter, re.MULTILINE | re.DOTALL)
        
        # Note: Overview might be multi-line in YAML, typically indented. 
        # Our regex simple match might miss complex block scalars.
        # For MVP, we presume simple single line or we clean up.
        
        name = name_match.group(1).strip() if name_match else file_path.stem
        overview = ""
        
        if overview_match:
            # Try to capture until next key or end
            # This is tricky with regex. Let's just grab the whole frontmatter and split by newlines
            # and look for 'overview:'.
             lines = frontmatter.split('\n')
             capture = False
             overview_lines = []
             for line in lines:
                 if line.strip().startswith('overview:'):
                     capture = True
                     val = line.split(':', 1)[1].strip()
                     if val: overview_lines.append(val)
                     continue
                 if capture:
                     # Check if next line is a new key (starts with word:)
                     if re.match(r"^\w+:", line):
                         break
                     overview_lines.append(line.strip())
             overview = " ".join(overview_lines).strip()

        if not overview:
            overview = name # Fallback

        # 3. Birth Time
        stat = file_path.stat()
        birth_time = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        
        # 4. ID (Use filename stem, stripping .plan if present)
        node_id = file_path.stem.replace(".plan", "")

        return {
            "node_id": node_id,
            "raw_intent": f"{name}: {overview}",
            "started_at": birth_time,
            "source": "CURSOR",
            "metadata": {
                "file_path": str(file_path)
            }
        }
