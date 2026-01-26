"""
Sovereign Protocol Verification.
Tests the 'Shadow Anchor' compliance and Precedent Loading.
"""
import sys
import unittest
import json
from pathlib import Path
from dataclasses import dataclass

# Add backend python path
project_root = Path(__file__).parent.parent.parent.parent.parent
backend_path = project_root / "backend" / "src"
sys.path.append(str(backend_path))

from side.strategic_engine import StrategicDecisionEngine, StrategicContext, DecisionType, ConfidenceLevel

class TestSovereignProtocol(unittest.TestCase):
    
    def setUp(self):
        self.engine = StrategicDecisionEngine()
        self.context = StrategicContext(project_path=str(project_root), stage="test")
        
    def test_anchor_not_found_default(self):
        """Test that missing anchor triggers Audit Mode."""
        # Temporarily rename .side/sovereign.json if it exists (mocking)
        # For unit test simplicity, we assume engine handles non-existence gracefully
        # or we mock the _load_sovereign_anchor method
        
        # Inject empty anchor
        self.engine.anchor = {}
        
        rec = self.engine.analyze_strategic_intent("Should I use MongoDB?", self.context, force_reload=False)
        
        self.assertEqual(rec.decision_type, DecisionType.SOVEREIGN_AUDIT)
        self.assertEqual(rec.recommendation, "Define Sovereign Invariant")
        print(f"\n✅ Audit Mode Verified: {rec.recommendation}")

    def test_anchor_enforcement(self):
        """Test that Identity Invariant (Port) is enforced."""
        # Inject Mock Anchor
        self.engine.anchor = {
            "identity": {
                "primary_port": 9999,
                "mission": "Test Sovereign"
            }
        }
        
        rec = self.engine.analyze_strategic_intent("I want to change the port.", self.context, force_reload=False)
        
        self.assertEqual(rec.decision_type, DecisionType.TECH_STACK)
        self.assertIn("Enforce Port 9999", rec.recommendation)
        self.assertEqual(rec.confidence, ConfidenceLevel.VERY_HIGH)
        print(f"\n✅ Anchor Enforcement Verified: {rec.recommendation}")

if __name__ == "__main__":
    unittest.main()
