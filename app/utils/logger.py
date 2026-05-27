"""
logger.py — Konfigurasi logging terpusat.
"""

import logging
import sys


def setup_logger(name: str = "wasteai", level: int = logging.INFO) -> logging.Logger:
    """
    Buat dan konfigurasi logger.

    Args:
        name: Nama logger.
        level: Level logging (default INFO).

    Returns:
        Logger yang sudah dikonfigurasi.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # sudah diinisialisasi

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


# Logger global
log = setup_logger()
