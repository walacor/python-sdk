import logging
import os

from logging.handlers import TimedRotatingFileHandler

LOG_LEVEL = os.getenv("WALACOR_SDK_LOG_LEVEL", "INFO").upper()
LOG_LEVEL_NUM = getattr(logging, LOG_LEVEL, logging.INFO)

LOG_DIR = os.getenv(
    "WALACOR_SDK_LOG_DIR", os.path.join(os.path.expanduser("~"), ".walacor_sdk", "logs")
)
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "sdk.log")

formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")

file_handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=7
)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)


def get_logger(name: str = "walacor_sdk") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL_NUM)
    logger.propagate = False

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
