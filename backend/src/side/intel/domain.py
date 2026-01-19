"""
Side Domain Detector - The "Intelligence Agency" classifier.

This module analyzes a codebase to determine its business domain (EdTech, FinTech, etc.)
so that Side can inject highly specific market intelligence.

Methodology:
1. Scan key files (README, PLAN.md, package.json)
2. Score against domain keyword sets
3. Return primary domain with confidence score
"""

import json
from pathlib import Path
from collections import Counter
import re

class DomainDetector:
    """
    Detects the business domain of a software project.
    """
    
    DOMAINS = {
        "EdTech": [
            "learning", "quiz", "course", "student", "teacher", "curriculum", "lms", 
            "education", "school", "class", "exam", "grade", "skill", "tutor",
            "spaced repetition", "flashcard", "assignment"
        ],
        "FinTech": [
            "money", "payment", "crypto", "wallet", "bank", "finance", "tax", 
            "trading", "stock", "invest", "ledger", "transaction", "currency", 
            "defi", "blockchain", "stripe", "plaid"
        ],
        "Health": [
            "patient", "doctor", "medical", "hipaa", "clinic", "health", "fitness", 
            "drug", "prescription", "therapy", "diagnosis", "diet", "workout", 
            "wearable", "emr", "ehr"
        ],
        "E-commerce": [
            "shop", "cart", "checkout", "product", "sku", "inventory", "order", 
            "store", "merchant", "payment", "shipping", "fulfillment", "marketplace",
            "shopify", "stripe"
        ],
        "SaaS": [
            "subscription", "billing", "saas", "b2b", "enterprise", "dashboard", 
            "analytics", "crm", "tenant", "onboarding", "churn", "mrr", "arr"
        ],
        "DevTool": [
            "cli", "sdk", "api", "developer", "framework", "library", "documentation",
            "compiler", "IDE", "plugin", "extension", "runtime"
        ]
    }

    def detect(self, project_path: Path) -> dict[str, any]:
        """
        Analyze project and return detected domain.
        
        Returns:
            {
                "domain": "EdTech",
                "confidence": 0.85,
                "keywords_found": ["quiz", "student", "course"]
            }
        """
        text_content = self._gather_context(project_path)
        return self._classify_text(text_content)
    
    def _gather_context(self, project_path: Path) -> str:
        """Read key text files to build context buffer."""
        content = []
        
        # Files to check in order of importance
        files = [
            "PLAN.md", ".side/PLAN.md", 
            "README.md", "README.txt",
            "package.json", "requirements.txt", "pyproject.toml",
            "cargo.toml", "go.mod"
        ]
        
        for fname in files:
            fpath = project_path / fname
            if fpath.exists():
                try:
                    # Read first 5KB of each file to capture header/summary
                    text = fpath.read_text(encoding="utf-8", errors="ignore")[:5000]
                    content.append(text)
                except Exception:
                    pass
        
        return "\n".join(content).lower()

    def _classify_text(self, text: str) -> dict[str, any]:
        """Score text against domain keywords."""
        scores = Counter()
        matches = {}
        
        # Tokenize roughly
        words = set(re.findall(r'\w+', text))
        
        for domain, keywords in self.DOMAINS.items():
            domain_matches = []
            for kw in keywords:
                if kw in text:  # Simple substring match for phrases
                    scores[domain] += 1
                    domain_matches.append(kw)
            matches[domain] = domain_matches
            
        if not scores:
            return {"domain": "General Software", "confidence": 0.0, "keywords": []}
            
        best_domain, score = scores.most_common(1)[0]
        
        # Normalize confidence (arbitrary heuristic)
        # 1 match = 0.2, 5 matches = 1.0
        confidence = min(score * 0.2, 1.0)
        
        return {
            "domain": best_domain,
            "confidence": confidence,
            "keywords": matches[best_domain]
        }
