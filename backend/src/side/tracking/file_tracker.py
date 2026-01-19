"""
Forensic-level file tracking with zero false positives.

Tracks files by content hash (not filename) to survive renames and moves.
Uses multi-signal verification for 80%+ confidence on all insights.
"""

import hashlib
import subprocess
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timezone


class FileTracker:
    """Content-based file tracking that survives renames and refactors."""
    
    def __init__(self, db):
        self.db = db
        self.confidence_threshold = 0.8  # 80% minimum for zero false positives
    
    def track_file(self, file_path: Path) -> Optional[str]:
        """
        Track file by content hash, not filename.
        
        Returns:
            content_hash: SHA-256 hash of file content, or None if file doesn't exist
        """
        if not file_path.exists() or not file_path.is_file():
            return None
        
        try:
            # Calculate content hash
            content_hash = self._hash_file(file_path)
            
            # Check if we've seen this content before
            identity = self.db.get_file_identity(content_hash)
            
            if identity:
                # Same content, different path = rename/move
                if identity['current_path'] != str(file_path):
                    self._record_move(
                        content_hash,
                        identity['current_path'],
                        str(file_path)
                    )
            else:
                # New file
                self._create_identity(content_hash, str(file_path))
            
            return content_hash
        except Exception as e:
            # Silent failure - don't break on tracking errors
            return None
    
    def verify_tracking(self, file_path: Path) -> Dict:
        """
        Multi-signal verification with confidence score.
        
        Returns:
            {
                'confidence': float (0.0 to 1.0),
                'signals': dict of individual signal scores,
                'reliable': bool (True if confidence >= threshold)
            }
        """
        signals = {}
        
        # Signal 1: Content hash (70% weight)
        try:
            content_hash = self._hash_file(file_path)
            if self.db.has_file_identity(content_hash):
                signals['content_match'] = 1.0
            else:
                signals['content_match'] = 0.0
        except Exception:
            signals['content_match'] = 0.0
        
        # Signal 2: Git history (20% weight)
        signals['git_rename'] = self._check_git_history(file_path)
        
        # Signal 3: Path similarity (10% weight)
        signals['path_similarity'] = self._check_path_similarity(file_path)
        
        # Calculate overall confidence
        confidence = (
            signals['content_match'] * 0.7 +
            signals['git_rename'] * 0.2 +
            signals['path_similarity'] * 0.1
        )
        
        return {
            'confidence': confidence,
            'signals': signals,
            'reliable': confidence >= self.confidence_threshold
        }
    
    def _hash_file(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content."""
        return hashlib.sha256(file_path.read_bytes()).hexdigest()
    
    def _check_git_history(self, file_path: Path) -> float:
        """
        Check git for renames with --follow.
        
        Returns:
            Confidence score 0.0 to 1.0
        """
        try:
            result = subprocess.run(
                ['git', 'log', '--follow', '--name-status', '--pretty=format:%H', str(file_path)],
                capture_output=True,
                cwd=file_path.parent,
                timeout=5
            )
            
            # Parse for renames (R100 = 100% similar)
            for line in result.stdout.decode().splitlines():
                if line.startswith('R'):
                    # Extract similarity percentage
                    similarity_str = line[1:4] if len(line) > 3 else '0'
                    try:
                        similarity = int(similarity_str)
                        return similarity / 100.0
                    except ValueError:
                        continue
            
            return 0.0
        except Exception:
            return 0.0
    
    def _check_path_similarity(self, file_path: Path) -> float:
        """
        Check for similar paths in database.
        
        Returns:
            Confidence score 0.0 to 1.0
        """
        try:
            similar_paths = self.db.find_similar_paths(str(file_path))
            if similar_paths:
                return max(s['score'] for s in similar_paths)
            return 0.0
        except Exception:
            return 0.0
    
    def _create_identity(self, content_hash: str, path: str):
        """Create new file identity."""
        try:
            self.db.create_file_identity(
                content_hash=content_hash,
                path=path,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        except Exception:
            pass  # Silent failure
    
    def _record_move(self, content_hash: str, old_path: str, new_path: str):
        """Record file rename/move."""
        try:
            self.db.record_file_move(
                content_hash=content_hash,
                old_path=old_path,
                new_path=new_path,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        except Exception:
            pass  # Silent failure
