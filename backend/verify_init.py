import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

try:
    print("Checking Root Package...")
    import side
    print(f"  VERSION: {side.VERSION}")
    
    print("\nChecking Models Package...")
    from side.models import ProjectStats, ProjectNode, ContextSnapshot, DevelopmentVelocity
    print(f"  ProjectStats: {ProjectStats}")
    
    print("\nChecking Storage Modules...")
    from side.storage.modules import ContextEngine, StrategicStore, SchemaStore
    print(f"  ContextEngine: {ContextEngine}")
    
    print("\nChecking Services Package...")
    from side.services import BackgroundService, DataBuffer, FileWatcher
    print(f"  BackgroundService: {BackgroundService}")
    
    print("\nChecking Utils Package...")
    from side.utils import shield, get_ignore_store, event_bus
    print(f"  shield: {shield}")
    
    print("\n✅ Verification SUCCESS: All package exports are confidently correct.")
except Exception as e:
    print(f"\n❌ Verification FAILED: {e}")
    sys.exit(1)
