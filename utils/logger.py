# utils/logger.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from utils.helpers import BASE_PATH

LOG_FILE = Path(BASE_PATH) / "youtube_pwned.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def _configure_root_logger():
    root = logging.getLogger()
    if root.handlers:
        return  # ya configurado

    root.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    root.addHandler(ch)

    fh = RotatingFileHandler(str(LOG_FILE), maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    root.addHandler(fh)

_configure_root_logger()

def get_logger(name: str):
    return logging.getLogger(name)
