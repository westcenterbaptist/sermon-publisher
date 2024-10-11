import logging
import sys
from colorlog import ColoredFormatter

def setup_logging(log_level: str = 'INFO') -> None:
    """
    Configures the logging settings for the application with colored output.

    :param log_level: Logging level as a string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    # Define log colors for different levels
    LOG_COLORS = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }

    # Create a ColoredFormatter
    formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors=LOG_COLORS,
        reset=True,
        style='%'
    )

    # Create a StreamHandler with the ColoredFormatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Get the root logger and set its level and handler
    logger = logging.getLogger()
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    logger.setLevel(numeric_level)
    logger.handlers = []  # Clear existing handlers
    logger.addHandler(handler)
