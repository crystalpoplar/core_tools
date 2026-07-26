"""Logger utility module."""

import logging
import os

import concurrent_log_handler

from . import value_setter


def create_logger(
    name: str,
    log_file: str,
    level: int = logging.INFO,
    log_versions: int = 5,
    max_size: int = 50000,
    output_dir: str = value_setter.logging_dir,
) -> logging.Logger:
    """Create a rotating file logger."""
    os.makedirs(output_dir, exist_ok=True)

    configured_logger = logging.getLogger(name)
    configured_logger.setLevel(level)
    configured_logger.propagate = False

    log_path = os.path.abspath(os.path.join(output_dir, log_file))
    for existing_handler in configured_logger.handlers:
        if getattr(existing_handler, "baseFilename", None) == log_path:
            existing_handler.setLevel(level)
            return configured_logger

    handler = concurrent_log_handler.ConcurrentRotatingFileHandler(
        log_path,
        "a",
        maxBytes=max_size,
        backupCount=log_versions,
    )
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    configured_logger.addHandler(handler)
    return configured_logger
