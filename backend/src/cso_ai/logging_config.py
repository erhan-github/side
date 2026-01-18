"""
Comprehensive logging configuration for sideMCP.

Provides detailed logging to help debug issues and track performance.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: str | None = None) -> None:
    """
    Setup comprehensive logging for sideMCP.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for logs. If None, uses ~/.side-mcp/logs/side-mcp.log
    """
    # Determine log file path
    if log_file is None:
        log_dir = Path.home() / ".side-mcp" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"side-mcp-{datetime.now().strftime('%Y%m%d')}.log"
    
    # Create formatter with detailed information
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-30s | %(funcName)-20s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # IMPORTANT: MCP servers must ONLY write JSON to stdout
    # Console logging would break the MCP protocol
    # All logs go to file only
    
    # File handler (detailed logs)
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(file_handler)  # Only file handler, no console!
    
    # Configure sideMCP loggers
    cso_logger = logging.getLogger("cso_ai")
    cso_logger.setLevel(logging.DEBUG)
    
    # Reduce noise from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("mcp").setLevel(logging.WARNING)  # Reduce MCP noise
    
    # Log startup (to file only)
    root_logger.info("=" * 80)
    root_logger.info(f"sideMCP logging initialized - Level: {log_level}")
    root_logger.info(f"Log file: {log_file}")
    root_logger.info("=" * 80)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: Module name (usually __name__)
    
    Returns:
        Configured logger
    """
    return logging.getLogger(name)
