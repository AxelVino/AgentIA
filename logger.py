import logging
import os
from logging.handlers import RotatingFileHandler

TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")

def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kwargs)

logging.Logger.trace = trace

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    "%H:%M:%S"
)

#terminal
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

#archivo de rotacion
file_handler = RotatingFileHandler(
    "agent.log",
    maxBytes=1_000_000,  # 1 MB
    backupCount=5        # guarda 5 archivos viejos
)

file_handler.setFormatter(formatter)

# Crear el objeto logger que es importado por agent.py
logger = logging.getLogger("AgentLogger")

logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

logger.propagate = False