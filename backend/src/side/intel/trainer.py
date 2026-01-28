
import json
import logging
from pathlib import Path
from side.utils.crypto import shield

logger = logging.getLogger(__name__)

def generate_training_data(project_path: Path, output_file: str = "strategic_training.jsonl"):
    """
    Converts Sovereign Memory into a fine-tuning dataset.
    """
    sovereign_file = project_path / ".side" / "sovereign.json"
    if not sovereign_file.exists():
        logger.error("❌ [TRAINER]: Sovereign Memory not found. Run 'side feed --historic' first.")
        return

    print("🧠 [TRAINER]: Synthesizing Strategic Training Pairs...")
    
    try:
        raw = shield.unseal_file(sovereign_file)
        data = json.loads(raw)
        fragments = data.get("history_fragments", [])
        
        pairs = []
        for frag in fragments:
            pair = {
                "instruction": f"Explain the strategic architectural decision behind commit {frag['hash']}.",
                "input": frag.get("summary", ""),
                "output": frag.get("wisdom", "")
            }
            pairs.append(pair)
            
        # Export to JSONL
        output_path = project_path / ".side" / output_file
        with open(output_path, "w") as f:
            for p in pairs:
                f.write(json.dumps(p) + "\n")
                
        print(f"✅ [SUCCESS]: Generated {len(pairs)} training pairs at {output_path.relative_to(project_path)}")
        print("👉 Use this dataset with 'unsloth' or 'ollama create' for local fine-tuning.")
        
    except Exception as e:
        logger.error(f"❌ [TRAINER]: Data generation failed: {e}")

if __name__ == "__main__":
    import sys
    generate_training_data(Path.cwd())
