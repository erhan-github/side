#!/usr/bin/env python3
"""
Real-time log viewer for CSO.ai MCP server.

Usage:
    python view_logs.py [--follow] [--level DEBUG|INFO|WARNING|ERROR]
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime


def get_latest_log_file() -> Path:
    """Get the most recent log file."""
    log_dir = Path.home() / ".cso-ai" / "logs"
    if not log_dir.exists():
        print(f"❌ Log directory not found: {log_dir}")
        print("The MCP server hasn't been started yet or logging is not configured.")
        sys.exit(1)
    
    log_files = list(log_dir.glob("cso-ai-*.log"))
    if not log_files:
        print(f"❌ No log files found in: {log_dir}")
        sys.exit(1)
    
    # Get most recent log file
    latest = max(log_files, key=lambda p: p.stat().st_mtime)
    return latest


def tail_file(file_path: Path, follow: bool = False, level_filter: str | None = None):
    """
    Tail a log file, optionally following it.
    
    Args:
        file_path: Path to log file
        follow: If True, keep reading new lines (like tail -f)
        level_filter: Optional log level to filter (DEBUG, INFO, WARNING, ERROR)
    """
    import time
    
    print(f"📋 Reading log file: {file_path}")
    print(f"📅 Last modified: {datetime.fromtimestamp(file_path.stat().st_mtime)}")
    if level_filter:
        print(f"🔍 Filtering for level: {level_filter}")
    print("=" * 80)
    print()
    
    with open(file_path, 'r') as f:
        # Read existing content
        if follow:
            # Seek to end for follow mode
            f.seek(0, 2)
        else:
            # Read all existing content
            for line in f:
                if should_show_line(line, level_filter):
                    print(line, end='')
        
        # Follow mode
        if follow:
            print("\n👀 Watching for new log entries... (Ctrl+C to stop)\n")
            try:
                while True:
                    line = f.readline()
                    if line:
                        if should_show_line(line, level_filter):
                            print(line, end='')
                    else:
                        time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n\n✋ Stopped watching logs.")


def should_show_line(line: str, level_filter: str | None) -> bool:
    """Check if line should be shown based on level filter."""
    if not level_filter:
        return True
    return f"| {level_filter} " in line


def main():
    parser = argparse.ArgumentParser(
        description="View CSO.ai MCP server logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # View latest logs
  python view_logs.py
  
  # Follow logs in real-time
  python view_logs.py --follow
  
  # Filter by log level
  python view_logs.py --follow --level ERROR
  
  # View specific log file
  python view_logs.py --file ~/.cso-ai/logs/cso-ai-20260116.log
        """
    )
    
    parser.add_argument(
        '--follow', '-f',
        action='store_true',
        help='Follow log file (like tail -f)'
    )
    
    parser.add_argument(
        '--level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Filter by log level'
    )
    
    parser.add_argument(
        '--file',
        type=Path,
        help='Specific log file to view (default: latest)'
    )
    
    args = parser.parse_args()
    
    # Get log file
    if args.file:
        log_file = args.file
        if not log_file.exists():
            print(f"❌ Log file not found: {log_file}")
            sys.exit(1)
    else:
        log_file = get_latest_log_file()
    
    # Tail the file
    tail_file(log_file, follow=args.follow, level_filter=args.level)


if __name__ == "__main__":
    main()
