"""Logger dung chung cho toan bo du an, in ra stdout kem timestamp."""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Tra ve logger in ra stdout, dinh dang '<thoi_gian> | <name> | <level> | <msg>'."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
