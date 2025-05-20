import logging
import sys

_LOGGER_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"

_DEFAULT_LEVEL = logging.DEBUG

# Cache for loggers to avoid duplicate handlers
_loggers = {}

def get_logger(name: str = "rcpch-guidelines") -> logging.Logger:
    if name in _loggers:
        return _loggers[name]
    logger = logging.getLogger(name)
    logger.setLevel(_DEFAULT_LEVEL)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(_LOGGER_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.propagate = False
    _loggers[name] = logger
    return logger 