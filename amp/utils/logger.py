"""Logging utilities for AMP."""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class AMPFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output."""

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        level = record.levelname
        name = record.name.split('.')[-1]
        message = record.getMessage()

        if self.use_colors and sys.stdout.isatty():
            color = self.COLORS.get(level, '')
            return f"{color}[{timestamp}] {level:8s}{self.RESET} [{name}] {message}"
        else:
            return f"[{timestamp}] {level:8s} [{name}] {message}"


class FileFormatter(logging.Formatter):
    """Formatter for file output."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        return f"[{timestamp}] {record.levelname:8s} [{record.name}] {record.getMessage()}"


_loggers: dict = {}


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name."""
    full_name = f"amp.{name}" if not name.startswith("amp.") else name

    if full_name not in _loggers:
        logger = logging.getLogger(full_name)
        _loggers[full_name] = logger

    return _loggers[full_name]


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    debug: bool = False
) -> None:
    """Set up logging configuration for AMP."""
    log_level = logging.DEBUG if debug else getattr(logging, level.upper(), logging.INFO)

    root_logger = logging.getLogger("amp")
    root_logger.setLevel(log_level)
    root_logger.handlers = []

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(AMPFormatter(use_colors=True))
    root_logger.addHandler(console_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(FileFormatter())
        root_logger.addHandler(file_handler)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("spotipy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)


class LoggerMixin:
    """Mixin class to add logging to any class."""

    @property
    def logger(self) -> logging.Logger:
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
