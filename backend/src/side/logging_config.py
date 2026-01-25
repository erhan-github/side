"""
Comprehensive logging configuration for sideMCP.

Provides detailed logging to help debug issues and track performance.
Implements 'Deep Logic Audit' protocols for consistency and reliability.
"""

import logging
import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Optional: Sentry and PostHog (Safe Imports)
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

try:
    from posthog import Posthog
    POSTHOG_AVAILABLE = True
except ImportError:
    POSTHOG_AVAILABLE = False


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging with enhanced safety."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "func": record.funcName,
            "message": record.getMessage(),
        }
        
        # safely handle exception info
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add any extra attributes safely
        if hasattr(record, "extra"):
            try:
                # Ensure extra is a dict-like object
                extra_data = record.extra # type: ignore
                if isinstance(extra_data, dict):
                     log_entry.update(extra_data)
            except Exception:
                log_entry["_extra_error"] = "Failed to serialize extra attributes"
            
        return json.dumps(log_entry, default=str) # default=str handles non-serializable objects gracefully


def _initialize_sentry() -> None:
    """Initialize Sentry if available and configured."""
    sentry_dsn = os.getenv("SENTRY_DSN")
    if SENTRY_AVAILABLE and sentry_dsn:
        try:
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[FastApiIntegration()],
                traces_sample_rate=1.0,
                environment=os.getenv("RAILWAY_ENVIRONMENT_NAME", "development")
            )
        except Exception as e:
            # Fallback logger isn't setup yet, so we print to stderr as a last resort
            print(f"Failed to initialize Sentry: {e}", file=sys.stderr)


def _get_log_file_path(log_file: Optional[str] = None) -> Path:
    """Determine and create the log file path."""
    if log_file:
        path = Path(log_file)
    else:
        log_dir = Path.home() / ".side-mcp" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        path = log_dir / "sidelith.log"
    return path


def _silence_noisy_loggers() -> None:
    """Reduce noise from external libraries."""
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("mcp").setLevel(logging.WARNING)


def _configure_handlers(root_logger: logging.Logger, log_file: Path, is_production: bool) -> None:
    """Configure file and console handlers."""
    # Choose Formatter
    if is_production:
        formatter = JSONFormatter(datefmt="%Y-%m-%dT%H:%M:%SZ")
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s",
            datefmt="%H:%M:%S"
        )

    # File Handler
    try:
        file_handler = logging.FileHandler(str(log_file), mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to setup file handler for logging: {e}", file=sys.stderr)

    # Note: We are strictly adding a file handler as per original code. 
    # If a StreamHandler is desired for stdout, it should be added here too.
    # The original code only added a FileHandler to the root logger.


def setup_logging(log_level: str = "INFO", log_file: str | None = None) -> None:
    """
    Setup high-fidelity logging and telemetry for sideMCP.
    Orchestrates the logging setup process.
    """
    # 1. Initialize External Telemetry
    _initialize_sentry()
    if SENTRY_AVAILABLE and os.getenv("SENTRY_DSN"):
         # We log this later after logging is set up, or print if urgent.
         pass

    # 2. Determine Log File
    log_file_path = _get_log_file_path(log_file)

    # 3. Configure Root Logger
    root_logger = logging.getLogger()
    
    # Reset existing handlers to avoid duplication if setup_logging is called twice
    if root_logger.handlers:
        root_logger.handlers.clear()

    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    is_production = os.getenv("RAILWAY_ENVIRONMENT_NAME") is not None
    _configure_handlers(root_logger, log_file_path, is_production)

    # 4. Silence Noise
    _silence_noisy_loggers()

    # 5. Final Confirmation
    root_logger.info(f"Observability Layer Active - Env: {os.getenv('RAILWAY_ENVIRONMENT_NAME', 'local')}")
    if SENTRY_AVAILABLE and os.getenv("SENTRY_DSN"):
        root_logger.info("Sentry initialized")


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance."""
    return logging.getLogger(name)
