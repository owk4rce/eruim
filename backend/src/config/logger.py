import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

from backend.src.utils.constants import LOGS_FOLDER


def setup_logger(app=None, is_initial=False):
    """Configure application logger with file and console handlers"""

    # Set log level
    if is_initial:
        log_level = logging.DEBUG
    else:
        if not app:
            raise ValueError("Flask app instance is required for non-initial setup.")
        log_level = logging.DEBUG if app.config['DEBUG'] else logging.INFO

    # Create logs directory if it doesn't exist
    if not os.path.exists(LOGS_FOLDER):
        os.makedirs(LOGS_FOLDER)

    # Create formatter
    formatter = logging.Formatter(
        '%(levelname)s - [%(asctime)s UTC] - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Setup file handler
    file_handler = RotatingFileHandler(
        os.path.join(LOGS_FOLDER, f'app_{datetime.utcnow().strftime("%Y-%m-%d")}.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Get the logger
    logger = logging.getLogger('backend')
    logger.setLevel(log_level)
    logger.handlers = []  # because of multiple setups (new setup shouldn't multiply handlers)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    if is_initial:
        logger.info("Initial logger setup completed.")
    else:
        mode = 'DEBUG' if app.config['DEBUG'] else 'PRODUCTION'
        logger.info(f"Logger configured for {mode} mode.")

    return logger
