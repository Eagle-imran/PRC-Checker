"""
Structured Logging Module for PRC-Checker.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path


def setup_logger(name: str = "prc_checker", level: int = logging.INFO, log_file: Path | None = None) -> logging.Logger:
    """Configure structured console and file logging."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Optional File Handler
    if log_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(level)
        file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)

    return logger
