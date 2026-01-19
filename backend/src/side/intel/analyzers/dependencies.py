import json
import re
from pathlib import Path
from typing import Any
from .base import BaseAnalyzer, Finding

class DependencyAnalyzer(BaseAnalyzer):
    """Parses dependency files and detects architectural bloat."""
    
    FRAMEWORK_PATTERNS = {
        "FastAPI": ["fastapi"],
        "Django": ["django"],
        "Flask": ["flask"],
        "React": ["react", "react-dom"],
        "Next.js": ["next"],
        "Vue": ["vue"],
        "Tailwind CSS": ["tailwindcss"],
    }

    async def analyze(self, root: Path, files: list[Path]) -> dict[str, Any]:
        results = {}
        all_findings = []
        
        # 1. package.json analysis
        pkg = root / "package.json"
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                deps = list(data.get("dependencies", {}).keys())
                deps.extend(data.get("devDependencies", {}).keys())
                results["npm"] = deps
                
                # Bloat Check: Redux in small projects (Moved from ForensicEngine)
                if any("redux" in d.lower() for d in deps):
                    tsx_count = sum(1 for f in files if f.suffix == '.tsx')
                    if tsx_count > 0 and tsx_count < 20:
                        all_findings.append(Finding(
                            type='ARCH_PURITY', severity='HIGH', file='package.json', line=None,
                            message=f'Redux detected in small project ({tsx_count} components).',
                            action='Consider Zustand or React Context for better velocity.'
                        ))
            except Exception: pass

        # 2. requirements.txt analysis
        req = root / "requirements.txt"
        if req.exists():
            try:
                content = req.read_text(encoding="utf-8")
                results["pip"] = [l.split("==")[0].strip() for l in content.splitlines() if l.strip() and not l.startswith("#")]
            except Exception: pass

        # 3. Framework detection
        all_deps = set()
        for d_list in results.values():
            all_deps.update([d.lower() for d in d_list])
            
        frameworks = []
        for fw, pats in self.FRAMEWORK_PATTERNS.items():
            if any(p.lower() in all_deps for p in pats):
                frameworks.append(fw)
                
        return {
            "dependencies": results,
            "frameworks": frameworks,
            "findings": all_findings
        }
