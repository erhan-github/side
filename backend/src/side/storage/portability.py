import os
import json
import shutil
import logging
import zipfile
import tempfile
from pathlib import Path
from side.utils.crypto import shield

logger = logging.getLogger(__name__)

def export_project(project_path: str | Path):
    """
    Exports the Project Soul (local.db + .side-id) for mobility.
    """
    project_path = Path(project_path).resolve()
    id_file = project_path / ".side-id"
    # Unified ledger path
    db_path = Path.home() / ".side" / "local.db"
    
    if not id_file.exists():
        logger.error("❌ [PORTABILITY]: Project ID not found. Run 'side feed' first.")
        return

    project_id = id_file.read_text().strip()
    export_dir = project_path / ".side" / "export"
    export_dir.mkdir(parents=True, exist_ok=True)
    
    bundle_name = f"sovereign_soul_{project_id[:8]}.shield"
    bundle_path = export_dir / bundle_name

    # 1. Create a temporary zip with the necessary Soul components
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        zip_path = tmp_path / "soul.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Package the identity
            zipf.write(id_file, arcname=".side-id")
            # Package the ledger
            if db_path.exists():
                zipf.write(db_path, arcname="local.db")
            
            # Package a human-readable manifest
            manifest = {
                "project_id": project_id,
                "exported_at": os.popen("date -u").read().strip(),
                "node_version": "1.0.0"
            }
            manifest_path = tmp_path / "manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2))
            zipf.write(manifest_path, arcname="manifest.json")

        # 2. Seal the entire Zip
        shield.seal_file(bundle_path, zip_path.read_bytes())
    
    print(f"✨ [PORTABILITY]: Soul Manifest Sealed at: {bundle_path.relative_to(project_path)}")
    print("👉 This file contains your DB and Project ID. Keep it secret, keep it safe.")

def import_project(bundle_path: str | Path):
    """
    Unseals and restores a Project Soul from a mobility manifest.
    """
    bundle_path = Path(bundle_path).resolve()
    if not bundle_path.exists():
        logger.error(f"❌ [PORTABILITY]: Bundle not found: {bundle_path}")
        return

    print(f"🔓 [SOVEREIGN MOBILITY]: Unsealing Project Soul...")
    
    try:
        # 1. Unseal the binary data
        zip_bytes = shield.unseal_file(bundle_path, binary=True)
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            zip_path = tmp_path / "imported_soul.zip"
            zip_path.write_bytes(zip_bytes)
            
            # 2. Extract and Validate
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(tmp_path)
                
                manifest_path = tmp_path / "manifest.json"
                if not manifest_path.exists():
                    logger.error("❌ [PORTABILITY]: Invalid bundle: manifest.json missing.")
                    return
                
                manifest = json.loads(manifest_path.read_text())
                project_id = manifest.get("project_id")
                
                print(f"📍 [IMPORT]: Restoring Project: {project_id}")
                print(f"🗓️ [IMPORT]: Export Date: {manifest.get('exported_at')}")
                
                # 3. Restore Components
                # Restore .side-id
                target_id_file = Path.cwd() / ".side-id"
                shutil.copy(tmp_path / ".side-id", target_id_file)
                
                # Restore local.db
                target_db_path = Path.home() / ".side" / "local.db"
                target_db_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(tmp_path / "local.db", target_db_path)
                
        print("✨ [PORTABILITY]: Soul Restoration Complete. Run 'side recovery' to rebuild context.")
        
    except Exception as e:
        logger.error(f"❌ [PORTABILITY]: Restoration failed: {e}")
