import logging
import asyncio
from pathlib import Path
from typing import Dict, Any

from side.qa.generator import TestGenerator
from side.storage.modules.forensic import ForensicStore

logger = logging.getLogger(__name__)

class QAService:
    """
    [KAR-22.2] Generative QA Service.
    Automates the creation of reproduction test cases (Red Tests).
    """

    def __init__(self, project_path: Path, forensic_store: ForensicStore):
        self.project_path = project_path
        self.forensic_store = forensic_store
        self.generator = TestGenerator(project_path)
        self.test_dir = project_path / ".side" / "tests"
        self.test_dir.mkdir(parents=True, exist_ok=True)

    async def pilot_red_test(self, finding_id: int):
        """
        Fetches an audit finding and generates a reproduction test.
        """
        # 1. Fetch the finding
        with self.forensic_store.engine.connection() as conn:
            row = conn.execute("SELECT * FROM audits WHERE id = ?", (finding_id,)).fetchone()
            if not row:
                logger.error(f"❌ [QA]: Finding {finding_id} not found.")
                return
            
            finding = dict(row)
            # Metadata might be needed
            if finding.get("metadata"):
                 import json
                 finding["metadata"] = json.loads(finding["metadata"])

        # 2. Generate the Repro
        logger.info(f"🧬 [QA]: Generating reproduction for finding {finding_id}: {finding['message']}")
        repro_code = await self.generator.generate_repro({
            "check_name": finding["tool"],
            "notes": finding["message"],
            "evidence": [{"file_path": finding["file_path"], "line_number": finding["line_number"]}]
        })

        # 3. Save the test
        test_file = self.test_dir / f"repro_{finding_id}_{finding['tool']}.py"
        test_file.write_text(repro_code)
        
        logger.info(f"✅ [QA]: Red Test created at {test_file}")
        return test_file
