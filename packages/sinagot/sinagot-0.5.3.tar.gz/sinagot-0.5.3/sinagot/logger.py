import logging

from sinagot.config import get_settings


def get_logger() -> logging.Logger:
    settings = get_settings()
    logger = logging.getLogger("sinagot")

    logger.setLevel(settings.LOGGING_LEVEL)
    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())
    return logger
