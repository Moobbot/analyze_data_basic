"""
Centralized logging configuration for Invoice Data Audit Tool.

Provides a consistent logging interface across all modules with:
- Console and file handlers
- Configurable log levels
- Structured log format
- Log rotation support
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


def get_logger(
    name: str,
    log_level: int = logging.INFO,
    log_file: Optional[Path] = None,
    enable_console: bool = True,
    enable_file: bool = True,
) -> logging.Logger:
    """
    Get or create a logger with specified configuration.

    Args:
        name: Logger name (typically __name__ of the calling module)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, uses default location
        enable_console: Whether to output to console
        enable_file: Whether to output to file

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if logger.handlers:
        return logger

    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File Handler with rotation
    if enable_file:
        if log_file is None:
            # Default log location
            from pathlib import Path

            log_dir = Path(__file__).parent.parent / "output_analyze" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "pipeline.log"

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def set_log_level(logger: logging.Logger, level: int) -> None:
    """
    Set log level for logger and all its handlers.

    Args:
        logger: Logger instance
        level: New log level
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


# Default logger for quick usage
default_logger = get_logger("invoice_audit")
