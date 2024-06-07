
"""Init log object."""
from logging import getLogger, INFO, FileHandler, Formatter
from datetime import datetime

# Create the logger
logger = getLogger("review_log")
logger.setLevel(INFO)

logger_handler = FileHandler(filename = './Auto-Review-' + datetime.now().strftime("%Y%m%d_%H%M%S") + '.log')

log_formatter = Formatter(fmt='%(levelname)s\t- %(message)s')
logger_handler.setFormatter(log_formatter)

logger.addHandler(logger_handler)
