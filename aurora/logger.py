"""Logging centralizado do Aurora IA.

Mantém logs no diretório configurado e evita handlers duplicados.
"""

import logging
from logging.handlers import RotatingFileHandler

from aurora.config import settings


def _build_logger() -> logging.Logger:
    logger = logging.getLogger("Aurora")
    if logger.handlers:
        return logger

    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    formatter = logging.Formatter(settings.LOG_FORMAT)

    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger


logger = _build_logger()

__all__ = ["logger"]
