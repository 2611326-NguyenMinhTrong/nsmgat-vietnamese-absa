"""Logger dung chung cho toan bo du an, in ra stdout kem timestamp.

[CD1.4b] Them `them_file_log()`: ngoai stdout, ghi song song ra mot file .log.
Ly do — huan luyen tren CPU mat hang gio, khong the ngoi nhin mai mot cua so
terminal. Co file log thi mo cua so khac chay `scripts/watch_train.py` de theo
doi, va quan trong hon: log con lai SAU KHI cua so terminal da dong. Da mat
mot lan huan luyen vi ly do nay (log chi nam trong bo dem cua terminal).
"""

import logging
import sys
from pathlib import Path

_DINH_DANG = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
_DINH_DANG_GIO = "%Y-%m-%d %H:%M:%S"


def _bo_dinh_dang() -> logging.Formatter:
    return logging.Formatter(fmt=_DINH_DANG, datefmt=_DINH_DANG_GIO)


def get_logger(name: str) -> logging.Logger:
    """Tra ve logger in ra stdout, dinh dang '<thoi_gian> | <name> | <level> | <msg>'."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_bo_dinh_dang())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def them_file_log(logger: logging.Logger, path: str | Path) -> Path:
    """Ghi THEM log ra file (van giu nguyen phan in ra stdout).

    Mo che do "a" (noi tiep) chu khong phai "w": lan chay truoc khong bi xoa.
    Doi lai, mot file co the chua nhieu lan chay — nen `train.py` ghi mot dong
    moc "=== BAT DAU ... ===" moi lan bat dau, va `watch_train.py` lay tu moc
    CUOI CUNG tro di lam lan chay hien tai.

    Goi lai voi cung mot duong dan se KHONG them handler trung (neu khong,
    moi dong log se bi ghi hai lan).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tuyet_doi = str(path.resolve())
    for h in logger.handlers:
        if isinstance(h, logging.FileHandler) and h.baseFilename == tuyet_doi:
            return path

    handler = logging.FileHandler(path, mode="a", encoding="utf-8")
    handler.setFormatter(_bo_dinh_dang())
    logger.addHandler(handler)
    return path
