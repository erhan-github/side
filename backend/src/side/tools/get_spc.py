import sys
import json
from pathlib import Path

# Add backend/src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from side.storage.modules.base import ContextEngine
from side.storage.modules.transient import OperationalStore

def get_spc():
    try:
        engine = ContextEngine()
        ops = OperationalStore(engine)
        
        spc = ops.get_setting("system_perception_coefficient") or "0.8"
        vs = ops.get_setting("silicon_velocity_derived") or "0.8"
        vg = ops.get_setting("temporal_synapse_velocity") or "0.8"
        vc = ops.get_setting("cognitive_flow_score") or "0.8"
        
        f_source = ops.get_setting("friction_source") or "OPTIMAL"
        g_friction = ops.get_setting("global_friction_level") or "0.0"
        l_friction = ops.get_setting("local_friction_contribution") or "0.0"
        
        # [PERCEPTION]: Fetch Strategic Alerts
        from side.storage.modules.strategy import StrategyStore
        strat = StrategyStore(engine)
        rejections = strat.list_rejections(limit=3)
        alerts = [{"id": r["id"], "reason": r["rejection_reason"], "file": r["file_path"]} for r in rejections]

        # Also get status
        status = "HEALTHY"
        if float(spc) < 0.4:
            status = "FRICTION_SPIKE"
        elif float(spc) < 0.6:
            status = "WARNING"
            
        return {
            "spc_score": float(spc),
            "vectors": {
                "silicon_velocity": float(vs),
                "temporal_synapse": float(vg),
                "cognitive_flow": float(vc)
            },
            "telemetry": {
                "source": f_source,
                "global_heat": float(g_friction),
                "local_heat": float(l_friction),
                "alerts": alerts
            },
            "status": status,
            "timestamp": ops.get_setting("last_user_activity") or ""
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(json.dumps(get_spc()))
