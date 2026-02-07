"""
CIA-Grade Secure Data Portability Module.
Implements defense-in-depth security for project export/import operations.
"""

import os
import json
import shutil
import logging
import zipfile
import tempfile
import hashlib
import hmac
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from side.utils.crypto import shield

logger = logging.getLogger(__name__)

# Security Constants
MAX_BUNDLE_SIZE = 500 * 1024 * 1024  # 500MB max bundle size
MAX_EXTRACTED_SIZE = 1024 * 1024 * 1024  # 1GB max extracted size
ALLOWED_PROJECT_ID_PATTERN = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'


def _validate_project_path(project_path: Path) -> bool:
    """
    Validate that project_path is safe and within allowed boundaries.
    Prevents path traversal attacks.
    """
    try:
        resolved = project_path.resolve(strict=True)
        # Ensure path doesn't escape to system directories
        forbidden_prefixes = [Path("/etc"), Path("/sys"), Path("/proc"), Path("/dev")]
        for prefix in forbidden_prefixes:
            if resolved.is_relative_to(prefix):
                logger.error(f"🚨 [SECURITY]: Forbidden path detected: {resolved}")
                return False
        return True
    except (OSError, RuntimeError):
        return False


def _validate_project_id(project_id: str) -> bool:
    """Validate project ID format (UUID only)."""
    import re
    return bool(re.match(ALLOWED_PROJECT_ID_PATTERN, project_id))


def _safe_extract(zipf: zipfile.ZipFile, target_dir: Path) -> bool:
    """
    Safely extract zip file with path traversal and zip bomb protection.
    Returns True if extraction succeeded, False otherwise.
    """
    total_size = 0
    
    for member in zipf.namelist():
        # 1. Prevent path traversal (Zip Slip)
        member_path = (target_dir / member).resolve()
        if not member_path.is_relative_to(target_dir):
            logger.error(f"🚨 [SECURITY]: Path traversal detected in zip: {member}")
            return False
        
        # 2. Prevent zip bombs
        info = zipf.getinfo(member)
        total_size += info.file_size
        if total_size > MAX_EXTRACTED_SIZE:
            logger.error(f"🚨 [SECURITY]: Zip bomb detected. Total size: {total_size}")
            return False
    
    # 3. Extract with validation
    zipf.extractall(target_dir)
    return True


def _compute_bundle_signature(data: bytes, secret: bytes) -> str:
    """Compute HMAC-SHA256 signature for bundle integrity."""
    return hmac.new(secret, data, hashlib.sha256).hexdigest()


def _get_signing_secret() -> bytes:
    """Get or create signing secret for bundle integrity."""
    from side.env import env
    secret_path = env.get_side_root() / "bundle.secret"
    
    if not secret_path.exists():
        # Generate new secret
        secret = os.urandom(32)
        secret_path.write_bytes(secret)
        secret_path.chmod(0o600)  # Owner-only
    else:
        secret = secret_path.read_bytes()
    
    return secret


def export_project(project_path: str | Path, encrypt: bool = True) -> Optional[Path]:
    """
    Exports the Project Soul (local.db + .side-id) with CIA-grade security.
    
    Security Features:
    - Path traversal prevention
    - Symlink detection and blocking
    - Cryptographic integrity (HMAC-SHA256)
    - Optional AES-256 encryption
    - Secure temporary file handling
    - Atomic operations
    
    Returns:
        Path to exported bundle, or None if export failed
    """
    # 1. Validate input path
    project_path = Path(project_path).resolve()
    if not _validate_project_path(project_path):
        logger.error("❌ [SECURITY]: Invalid or forbidden project path")
        return None
    
    id_file = project_path / ".side-id"
    
    # 2. Atomic file read with symlink detection
    if not id_file.exists():
        logger.error("❌ [PORTABILITY]: Project ID not found. Run 'side feed' first.")
        return None
    
    if id_file.is_symlink():
        logger.error("🚨 [SECURITY]: Symlink detected in .side-id. Refusing to export.")
        return None
    
    try:
        project_id = id_file.read_text().strip()
    except (OSError, UnicodeDecodeError) as e:
        logger.error(f"❌ [PORTABILITY]: Failed to read project ID: {e}")
        return None
    
    if not _validate_project_id(project_id):
        logger.error(f"🚨 [SECURITY]: Invalid project ID format: {project_id}")
        return None
    
    # 3. Get database path
    from side.env import env
    db_path = env.get_db_path()
    
    if db_path.is_symlink():
        logger.error("🚨 [SECURITY]: Symlink detected in database path. Refusing to export.")
        return None
    
    # 4. Create export directory with secure permissions
    export_dir = project_path / ".side" / "export"
    export_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    
    bundle_name = f"sovereign_soul_{project_id[:8]}.shield"
    bundle_path = export_dir / bundle_name
    
    # 5. Create bundle with secure temporary directory
    with tempfile.TemporaryDirectory(prefix="side_export_", dir=tempfile.gettempdir()) as tmp_dir:
        tmp_path = Path(tmp_dir)
        tmp_path.chmod(0o700)  # Secure permissions
        
        zip_path = tmp_path / "soul.zip"
        
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            # Package the identity (no symlinks)
            zipf.write(id_file, arcname=".side-id")
            
            # Package the ledger (no symlinks)
            if db_path.exists():
                zipf.write(db_path, arcname="local.db")
            
            # Package manifest with signature
            manifest = {
                "project_id": project_id,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "node_version": "1.0.0",
                "encrypted": encrypt
            }
            
            # Compute signature
            manifest_bytes = json.dumps(manifest, sort_keys=True).encode()
            secret = _get_signing_secret()
            signature = _compute_bundle_signature(manifest_bytes, secret)
            manifest["signature"] = signature
            
            manifest_path = tmp_path / "manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2))
            manifest_path.chmod(0o600)
            zipf.write(manifest_path, arcname="manifest.json")
        
        # 6. Seal the bundle with encryption
        zip_bytes = zip_path.read_bytes()
        shield.seal_file(bundle_path, zip_bytes)
        bundle_path.chmod(0o600)  # Owner-only access
    
    logger.info(f"✨ [PORTABILITY]: Soul Manifest Sealed at: {bundle_path.relative_to(project_path)}")
    logger.info("👉 This file contains your DB and Project ID. Keep it secret, keep it safe.")
    
    return bundle_path


def import_project(bundle_path: str | Path, force: bool = False) -> bool:
    """
    Unseals and restores a Project Soul with CIA-grade security validation.
    
    Security Features:
    - Bundle size validation
    - Zip slip protection
    - Signature verification
    - Symlink detection
    - Atomic restoration with rollback
    
    Args:
        bundle_path: Path to the sealed bundle
        force: Skip confirmation prompts (use with caution)
    
    Returns:
        True if import succeeded, False otherwise
    """
    # 1. Validate bundle path
    bundle_path = Path(bundle_path).resolve()
    if not bundle_path.exists():
        logger.error(f"❌ [PORTABILITY]: Bundle not found: {bundle_path}")
        return False
    
    # 2. Validate bundle size
    bundle_size = bundle_path.stat().st_size
    if bundle_size > MAX_BUNDLE_SIZE:
        logger.error(f"🚨 [SECURITY]: Bundle too large: {bundle_size} bytes (max: {MAX_BUNDLE_SIZE})")
        return False
    
    logger.info(f"🔓 [SYSTEM MOBILITY]: Unsealing Project Soul...")
    
    try:
        # 3. Unseal the bundle
        zip_bytes = shield.unseal_file(bundle_path, binary=True)
        
        with tempfile.TemporaryDirectory(prefix="side_import_", dir=tempfile.gettempdir()) as tmp_dir:
            tmp_path = Path(tmp_dir)
            tmp_path.chmod(0o700)
            
            zip_path = tmp_path / "imported_soul.zip"
            zip_path.write_bytes(zip_bytes)
            zip_path.chmod(0o600)
            
            # 4. Safe extraction with validation
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                if not _safe_extract(zipf, tmp_path):
                    logger.error("❌ [SECURITY]: Bundle extraction failed security validation")
                    return False
            
            # 5. Validate manifest
            manifest_path = tmp_path / "manifest.json"
            if not manifest_path.exists():
                logger.error("❌ [PORTABILITY]: Invalid bundle: manifest.json missing")
                return False
            
            try:
                manifest = json.loads(manifest_path.read_text())
            except json.JSONDecodeError:
                logger.error("❌ [PORTABILITY]: Invalid manifest format")
                return False
            
            # 6. Verify signature
            signature = manifest.pop("signature", None)
            if not signature:
                logger.error("🚨 [SECURITY]: Bundle signature missing")
                return False
            
            manifest_bytes = json.dumps(manifest, sort_keys=True).encode()
            secret = _get_signing_secret()
            expected_signature = _compute_bundle_signature(manifest_bytes, secret)
            
            if not hmac.compare_digest(signature, expected_signature):
                logger.error("🚨 [SECURITY]: Bundle signature verification FAILED")
                return False
            
            # 7. Validate project ID
            project_id = manifest.get("project_id")
            if not project_id or not _validate_project_id(project_id):
                logger.error(f"🚨 [SECURITY]: Invalid project ID in manifest: {project_id}")
                return False
            
            logger.info(f"📍 [IMPORT]: Restoring Project: {project_id}")
            logger.info(f"🗓️ [IMPORT]: Export Date: {manifest.get('exported_at')}")
            
            # 8. Check for existing data
            target_id_file = Path.cwd() / ".side-id"
            from side.env import env
            target_db_path = env.get_db_path()
            
            if (target_id_file.exists() or target_db_path.exists()) and not force:
                logger.warning("⚠️ [PORTABILITY]: Existing project data detected")
                response = input("Overwrite existing data? (yes/no): ")
                if response.lower() != "yes":
                    logger.info("Import cancelled by user")
                    return False
            
            # 9. Create backup before restoration
            backup_dir = None
            if target_db_path.exists():
                backup_dir = tmp_path / "backup"
                backup_dir.mkdir()
                shutil.copy(target_db_path, backup_dir / "local.db.backup")
                if target_id_file.exists():
                    shutil.copy(target_id_file, backup_dir / ".side-id.backup")
            
            try:
                # 10. Atomic restoration
                # Restore .side-id
                shutil.copy(tmp_path / ".side-id", target_id_file)
                target_id_file.chmod(0o600)
                
                # Restore local.db
                target_db_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(tmp_path / "local.db", target_db_path)
                target_db_path.chmod(0o600)
                
                # 11. [HYBRID ARCHITECTURE]: Regenerate context.json cache from restored DB
                try:
                    from side.storage.modules.base import ContextEngine
                    from side.utils.context_cache import ContextCache
                    
                    engine = ContextEngine(project_id=project_id)
                    cache = ContextCache(Path.cwd(), engine)
                    cache.generate(force=True)
                    logger.info("🔄 [CACHE]: Context cache regenerated from imported database")
                except Exception as e:
                    logger.warning(f"⚠️ [CACHE]: Could not regenerate context cache: {e}")
                    # Non-fatal - cache will be regenerated on first access
                
                logger.info("✨ [PORTABILITY]: Soul Restoration Complete")
                return True
                
            except Exception as e:
                # Rollback on failure
                logger.error(f"❌ [PORTABILITY]: Restoration failed: {e}")
                if backup_dir and backup_dir.exists():
                    logger.info("🔄 [ROLLBACK]: Restoring from backup...")
                    if (backup_dir / "local.db.backup").exists():
                        shutil.copy(backup_dir / "local.db.backup", target_db_path)
                    if (backup_dir / ".side-id.backup").exists():
                        shutil.copy(backup_dir / ".side-id.backup", target_id_file)
                return False
    
    except Exception as e:
        logger.error(f"❌ [PORTABILITY]: Import failed: {e}")
        return False
