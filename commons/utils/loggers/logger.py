import logging
import os

from django.conf import settings


def get_logger(logger_name, log_level=logging.DEBUG):
    '''Method to get logger according to given name and log level.

    Args:
        logger_name: name of the logger.
        log_level: level of the logger.

    Returns:
        python's Logger class instance.

    '''
    # get process id
    pid = os.getpid()

    log_dir_path = os.path.join(settings.BASE_DIR, 'log')
    log_file_path = os.path.join(log_dir_path, logger_name + '.log')

    log_format = (
        "PID: " + str(pid) + "> %(asctime)s - %(name)s - %(levelname)s - "
        "%(message)s"
    )

    # create logger and set log level
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # create log directory if it doesn't exist
    if not os.path.exists(log_dir_path):
        os.makedirs(log_dir_path)

    # Time Rotating File Handler to start new log file every midnight
    timed_rotating_handler = logging.handlers.TimedRotatingFileHandler(
        log_file_path, when='midnight', interval=1
    )

    log_formatter = logging.Formatter(log_format)
    timed_rotating_handler.setFormatter(log_formatter)
    logger.addHandler(timed_rotating_handler)

    return logger
