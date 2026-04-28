from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.utils.config import settings

LOG_DIR = Path(settings.output_path)
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

_file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5_242_880, backupCount=3, encoding="utf-8")
_file_handler.setFormatter(formatter)

_console_handler = logging.StreamHandler()
_console_handler.setFormatter(formatter)

logger = logging.getLogger("pqms")
logger.setLevel(logging.INFO)
logger.addHandler(_file_handler)
logger.addHandler(_console_handler)
