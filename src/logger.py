# src/logger.py

from loguru import logger
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger.add(
    f"{LOG_DIR}/scraper.log",
    rotation="10 MB",
    level="INFO",
    format="{time} | {level} | {message}",
)

__all__ = ["logger"]
