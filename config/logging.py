"""
Beautelligence Video Pipeline - Structured Logging Configuration

Provides consistent logging with structured output for debugging and monitoring.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

import structlog


def setup_logging(log_level: str = "INFO", log_dir: Path | None = None) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Optional directory for log files
    """
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
        stream=sys.stdout,
    )

    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(colors=True),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Set up file logging if directory provided
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"pipeline_{datetime.now().strftime('%Y%m%d')}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

        logging.getLogger().addHandler(file_handler)


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Bound structlog logger
    """
    return structlog.get_logger(name)
