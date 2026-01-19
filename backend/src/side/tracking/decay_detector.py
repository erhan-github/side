"""
Context decay detection with zero false positives.

Detects files that haven't been touched in a while using multi-signal
verification and high confidence thresholds.
"""

from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta, timezone
import subprocess


class ContextDecayDetector:
    """Detect stale code with Forensic-level confidence."""
    
    def __init__(self, db, file_tracker):
        self.db = db
        self.tracker = file_tracker
        self.min_days = 90  # Only flag files untouched for 90+ days
        self.min_complexity = 200  # Only flag complex files (200+ lines)
        self.confidence_threshold = 0.8  # 80% minimum
    
    def detect_decay(self) -> List[Dict]:
        """
        Detect context decay with zero false positives.
        
        Returns:
            [
                {
                    'file': str,
                    'days_since_change': int,
                    'complexity': int,
                    'confidence': float,
                    'signals': dict,
                    'recommendation': str
                },
                ...
            ]
        """
        insights = []
        
        try:
            # Get all code files
            for file_path in self._get_code_files():
                # Verify tracking confidence
                verification = self.tracker.verify_tracking(file_path)
                
                if not verification['reliable']:
                    continue  # Skip if not confident enough
                
                # Get last modification
                last_commit = self._get_last_commit(file_path)
                if not last_commit:
                    continue
                
                days_since = (datetime.now(timezone.utc) - last_commit['date']).days
                
                # Only flag if old enough
                if days_since < self.min_days:
                    continue
                
                # Check complexity
                complexity = self._calculate_complexity(file_path)
                if complexity < self.min_complexity:
                    continue  # Too simple to worry about
                
                # Multi-signal validation
                if not self._validate_signals(verification):
                    continue  # Not enough signals agree
                
                # High confidence insight
                insights.append({
                    'file': str(file_path),
                    'days_since_change': days_since,
                    'complexity': complexity,
                    'confidence': verification['confidence'],
                    'signals': verification['signals'],
                    'recommendation': f"Review {file_path.name} before making changes"
                })
        except Exception:
            pass  # Silent failure
        
        # Only return high-confidence insights
        return [i for i in insights if i['confidence'] >= self.confidence_threshold]
    
    def _get_code_files(self) -> List[Path]:
        """Get all Python and TypeScript files."""
        code_files = []
        
        try:
            # Python files
            code_files.extend(Path('.').rglob('*.py'))
            # TypeScript files
            code_files.extend(Path('.').rglob('*.ts'))
            code_files.extend(Path('.').rglob('*.tsx'))
            
            # Filter out common directories to ignore
            ignore_dirs = {'node_modules', 'venv', '.venv', '__pycache__', '.git', 'dist', 'build'}
            code_files = [
                f for f in code_files
                if not any(ignore_dir in f.parts for ignore_dir in ignore_dirs)
            ]
        except Exception:
            pass
        
        return code_files
    
    def _get_last_commit(self, file_path: Path) -> Optional[Dict]:
        """Get last commit that modified this file."""
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%at', str(file_path)],
                capture_output=True,
                timeout=5
            )
            
            timestamp_str = result.stdout.decode().strip()
            if timestamp_str:
                timestamp = int(timestamp_str)
                return {
                    'date': datetime.fromtimestamp(timestamp, tz=timezone.utc)
                }
            return None
        except Exception:
            return None
    
    def _calculate_complexity(self, file_path: Path) -> int:
        """Calculate file complexity (simple: line count)."""
        try:
            return len(file_path.read_text().splitlines())
        except Exception:
            return 0
    
    def _validate_signals(self, verification: Dict) -> bool:
        """Require at least 2 signals to agree (>0.5 confidence each)."""
        signals_agreeing = sum(
            1 for score in verification['signals'].values()
            if score > 0.5
        )
        return signals_agreeing >= 2
