import logging

from .logger import get_logger

error_logger = get_logger(logger_name='error', log_level=logging.ERROR)
