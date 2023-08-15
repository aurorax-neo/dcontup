import logging
import os
import sys

LOGGING_LEVEL = logging.INFO
LOGGING_FILE = os.path.join(os.getcwd(), "logging.log")
LOGGING_FMT = '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s'
LOGGING_DATE_FMT = '%Y-%m-%d %H:%M:%S'


def _get_logger(level: int = LOGGING_LEVEL):
    log = logging.getLogger("default_logging")

    for h in log.handlers:
        h.close()
        log.removeHandler(h)
        del h
    log.handlers.clear()
    log.propagate = False

    log.setLevel(level)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter(LOGGING_FMT, datefmt=LOGGING_DATE_FMT))

    fh = logging.FileHandler(LOGGING_FILE, encoding='utf-8')
    fh.setFormatter(logging.Formatter(LOGGING_FMT, datefmt=LOGGING_DATE_FMT))

    log.addHandler(ch)
    log.addHandler(fh)
    return log


def refresh(level: int = LOGGING_LEVEL):
    global logger
    logger = _get_logger(level)


# 日志句柄
logger = _get_logger()
