
import sys
from pathlib import Path
# Add backend/src to path
sys.path.append(str(Path('/Users/erhanerdogan/Desktop/side/backend/src')))

from side.storage.simple_db import SimplifiedDatabase
from side.intel.intelligence_store import IntelligenceStore
from side.services.monolith import DIMENSION_WEIGHTS, SEVERITY_MULTIPLIERS

db = SimplifiedDatabase()
repo_root = Path('/Users/erhanerdogan/Desktop/side')
project_id = db.get_project_id(repo_root)
store = IntelligenceStore(db)

findings = store.get_active_findings(project_id)
print(f"Total active findings in DB: {len(findings)}")

def strategic_sort_key(f):
    dim = f.get('metadata', {}).get('dimension', 'system').lower()
    sev = f.get('severity', 'LOW').upper()
    weight = DIMENSION_WEIGHTS.get(dim, 10)
    multiplier = SEVERITY_MULTIPLIERS.get(sev, 1)
    return -(weight * multiplier)

findings.sort(key=strategic_sort_key)

print("\n--- Sorted Findings (Top 15) ---")
for i, f in enumerate(findings[:15]):
    print(f"{i+1}. [{f['severity']}] {f['type']} ({f.get('metadata', {}).get('dimension', 'N/A')}) - ID: {f['id']}")

seen_ids = set()
count = 0
for f in findings:
    if count >= 10: break
    if f['id'] in seen_ids: continue
    seen_ids.add(f['id'])
    count += 1
    
print(f"\nRendered count in Forensic loop: {count}")
print(f"Seen IDs count: {len(seen_ids)}")
