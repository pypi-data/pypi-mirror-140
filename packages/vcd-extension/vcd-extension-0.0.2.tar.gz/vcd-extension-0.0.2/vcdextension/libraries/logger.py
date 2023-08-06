"""
Logger

:date: Mar 7, 2021
:author: Aldo Diaz, Marcelo Sureda

Logger is the component responsible for capturing events that occurs during
framework's execution. Provides consistency to event handling inside the
whole framework.
"""

import logging
from os import mkdir, \
    path
from datetime import datetime
from vcdextension.libraries import constants


class Logger:
    """
    Logger Class
    Class responsible for capturing events during framework's execution.
    Is a Pythonic implementation of the Singleton pattern.
    """
    _log = None

    def __new__(cls):
        if cls._log is None:
            cls._log = super(Logger, cls).__new__(cls)

            # Initialize logger
            cls._log = logging.getLogger(constants.FRAMEWORK_NAME)
            cls._log.setLevel(logging.getLevelName(constants.DEFAULT_LOG_LEVEL))

            formatter = logging.Formatter('{asctime} | {levelname:<8} | '
                                          '{filename}[{funcName}]: {message}',
                                          style='{')

            if not path.isdir(constants.LOG_DIR):
                mkdir(constants.LOG_DIR)
            now = datetime.now()
            file_handler = logging.FileHandler(constants.LOG_DIR + "/" +
                                               constants.FRAMEWORK_NAME + "_" +
                                               now.strftime("%Y-%m-%d") + ".log")
            file_handler.setFormatter(formatter)

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)

            cls._log.addHandler(file_handler)
            cls._log.addHandler(stream_handler)

        return cls._log
