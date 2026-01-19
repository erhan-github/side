"""
Auto-detect project context from files and git.

Detects tech stack, code patterns, work patterns, and focus areas
with zero manual input required.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timezone
from collections import Counter


class ContextDetector:
    """Auto-detect project context with privacy-first approach."""
    
    def __init__(self, db, file_tracker):
        self.db = db
        self.tracker = file_tracker
    
    def detect_tech_stack(self) -> Dict:
        """
        Parse package.json, requirements.txt for tech stack.
        
        Returns:
            {'frontend': [...], 'backend': [...], 'tools': [...]}
        """
        stack = {'frontend': [], 'backend': [], 'tools': []}
        
        try:
            # Frontend (package.json)
            pkg_path = Path('package.json')
            if pkg_path.exists():
                pkg = json.loads(pkg_path.read_text())
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                stack['frontend'] = list(deps.keys())
        except Exception:
            pass  # Silent failure
        
        try:
            # Backend (requirements.txt)
            req_path = Path('requirements.txt')
            if req_path.exists():
                deps = req_path.read_text().splitlines()
                stack['backend'] = [
                    d.split('==')[0].split('>=')[0].split('~=')[0].strip()
                    for d in deps
                    if d.strip() and not d.startswith('#')
                ]
        except Exception:
            pass  # Silent failure
        
        return stack
    
    def analyze_code_patterns(self, days: int = 7) -> Dict:
        """
        Analyze git commits for code patterns.
        
        Returns:
            {
                'async_usage': int,
                'error_handling': int,
                'type_hints': int,
                'tests_added': int
            }
        """
        patterns = {
            'async_usage': 0,
            'error_handling': 0,
            'type_hints': 0,
            'tests_added': 0
        }
        
        try:
            commits = self._get_recent_commits(days)
            
            for commit in commits:
                diff = self._get_commit_diff(commit)
                
                # Count patterns in added lines only
                added_lines = [line for line in diff.splitlines() if line.startswith('+')]
                diff_text = '\n'.join(added_lines)
                
                if 'async def' in diff_text or 'await ' in diff_text:
                    patterns['async_usage'] += 1
                if 'try:' in diff_text or 'except' in diff_text:
                    patterns['error_handling'] += 1
                if ': str' in diff_text or '-> ' in diff_text:
                    patterns['type_hints'] += 1
                if 'test_' in diff_text or 'def test' in diff_text:
                    patterns['tests_added'] += 1
        except Exception:
            pass  # Silent failure
        
        return patterns
    
    def detect_work_patterns(self, days: int = 30) -> Dict:
        """
        Analyze commit frequency and timing.
        
        Returns:
            {
                'commits_per_day': float,
                'peak_hour': int,
                'active_days_per_week': int,
                'total_commits': int
            }
        """
        try:
            commits = self._get_recent_commits(days)
            
            if not commits:
                return {}
            
            timestamps = [c['timestamp'] for c in commits]
            hours = [datetime.fromtimestamp(t).hour for t in timestamps]
            days_of_week = [datetime.fromtimestamp(t).weekday() for t in timestamps]
            
            return {
                'commits_per_day': round(len(commits) / days, 1),
                'peak_hour': Counter(hours).most_common(1)[0][0] if hours else None,
                'active_days_per_week': len(set(days_of_week)),
                'total_commits': len(commits)
            }
        except Exception:
            return {}
    
    def detect_focus_areas(self, days: int = 7) -> List[Dict]:
        """
        Find most changed files with content-based tracking.
        
        Returns:
            [
                {
                    'file': str,
                    'changes': int,
                    'confidence': float
                },
                ...
            ]
        """
        try:
            commits = self._get_recent_commits(days)
            file_changes = {}
            
            for commit in commits:
                files = self._get_changed_files(commit)
                for file in files:
                    file_path = Path(file)
                    if not file_path.exists():
                        continue
                    
                    # Track by content hash (survives renames)
                    content_hash = self.tracker.track_file(file_path)
                    if content_hash:
                        file_changes[content_hash] = file_changes.get(content_hash, 0) + 1
            
            # Sort by frequency
            sorted_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)
            
            # Return top 10 with confidence
            focus = []
            for content_hash, count in sorted_files[:10]:
                identity = self.db.get_file_identity(content_hash)
                if identity:
                    focus.append({
                        'file': identity['current_path'],
                        'changes': count,
                        'confidence': 1.0  # High confidence (git-based)
                    })
            
            return focus
        except Exception:
            return []
    
    def _get_recent_commits(self, days: int) -> List[Dict]:
        """Get recent git commits."""
        try:
            result = subprocess.run(
                ['git', 'log', f'--since={days}.days.ago', '--format=%H %at'],
                capture_output=True,
                timeout=10
            )
            
            commits = []
            for line in result.stdout.decode().splitlines():
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    commits.append({
                        'hash': parts[0],
                        'timestamp': int(parts[1])
                    })
            
            return commits
        except Exception:
            return []
    
    def _get_commit_diff(self, commit: Dict) -> str:
        """Get diff for a commit."""
        try:
            result = subprocess.run(
                ['git', 'show', commit['hash']],
                capture_output=True,
                timeout=5
            )
            return result.stdout.decode()
        except Exception:
            return ""
    
    def _get_changed_files(self, commit: Dict) -> List[str]:
        """Get list of changed files in a commit."""
        try:
            result = subprocess.run(
                ['git', 'show', '--name-only', '--format=', commit['hash']],
                capture_output=True,
                timeout=5
            )
            return [f.strip() for f in result.stdout.decode().splitlines() if f.strip()]
        except Exception:
            return []
