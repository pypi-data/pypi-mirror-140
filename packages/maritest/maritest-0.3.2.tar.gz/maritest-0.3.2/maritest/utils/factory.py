import logging
from enum import Enum


get_specific_logger = logging.getLogger("Maritest Logger")


class LogEnum(str, Enum):
    """Enum class that represent for Log level"""
    INFO = "INFO"
    DEBUG = "DEBUG"
    WARNING = "WARNING"


class Logger:
    """Private class for logger factory"""
    _logger = None

    @staticmethod
    def __set_logger(log_level: str = LogEnum.INFO):
        """
        Private method to create logger stream handler
        based on log_level argument
        """
        if Logger._logger is None:
            Logger._logger = get_specific_logger
            Logger._logger.propagate = False
            Logger._logger.setLevel(logging.DEBUG)

            logger_output = logging.StreamHandler()
            logger_output.setLevel(logging.DEBUG)

            logger_formatter = logging.Formatter(
                fmt="%(asctime)s | %(filename)s | %(funcName)s | %(message)s",
                datefmt="%d-%m-%Y %I:%M:%S",
            )

            logger_file = logging.FileHandler("maritest.log")
            logger_file.setFormatter(logger_formatter)

            logger_output.setFormatter(logger_formatter)
            Logger._logger.addHandler(logger_output)
            Logger._logger.addHandler(logger_file)
        else:
            Logger._logger = get_specific_logger

        if log_level == LogEnum.INFO:
            Logger._logger.setLevel(logging.INFO)
        elif log_level == LogEnum.DEBUG:
            Logger._logger.setLevel(logging.DEBUG)
        elif log_level == LogEnum.WARNING:
            Logger._logger.setLevel(logging.WARNING)
        return Logger._logger

    @staticmethod
    def get_logger(log_level: str):
        if log_level is not None:
            return Logger.__set_logger(log_level=log_level)
