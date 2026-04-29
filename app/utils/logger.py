from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

logger = logging.getLogger("pqms")


def setup_logger(output_path: str) -> None:
    if logger.handlers:
        return

    log_dir = Path(output_path)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

    file_handler = RotatingFileHandler(log_file, maxBytes=5_242_880, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
