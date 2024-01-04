from __future__ import absolute_import

from abc import ABCMeta, abstractmethod
from datetime import datetime
from enum import Enum
import logging
from flagship.decorators import param_types_validator


class LogLevel(Enum):
    """
    This enum class defines Flagship log levels that can be used to control SDK outputs.
    """

    ALL = 100
    """
    All logs will be logged.
    """
    CRITICAL = 50
    """
    Critical errors and below will be logged.
    """

    ERROR = 40
    """
    Errors, caught exception events and below will be logged.
    """

    WARNING = 30
    """
    Only Warnings events and below will be logged.
    """

    INFO = 20
    """
    Only info logs and below will be logged.
    """

    DEBUG = 10
    """
    Only debug logs and below will be logged.
    """

    NONE = 0
    """
    NONE = 0: Logging will be disabled.
    """


class LogManager:
    """
    Class to extend in order to provide a custom Log manager.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    @param_types_validator(True, str, LogLevel, str)
    def log(self, tag, level, message):
        """
        Called when the SDK produce a log.
        @param tag: location of the SDK where the log come from.
        @param level: Severity of the log emitted.
        @param message: log message.
        @return:
        """
        pass

    @abstractmethod
    @param_types_validator(True, Exception, str)
    def exception(self, tag, exception, traceback):
        """
        Called when the SDK has caught an Exception.
        @param tag: origin of the exception
        @param exception: exception that caused the exception.
        @param traceback: exception traceback.
        @return:
        """
        pass


class FlagshipLogManager:
    MAIN_TAG = "Flagship"

    log_level = LogLevel.ALL
    colors = {50: 89, 40: 91, 30: 93, 20: 94, 10: 96}
    start_color = '\033[{}m'
    end_color = '\033[0m'

    def __init__(self, level):
        # type: (LogLevel) -> None
        """
        @rtype: FlagshipLogManager

        """
        if isinstance(level, LogLevel):
            self.log_level = level
            ch = logging.StreamHandler()
            self.logger = logging.getLogger(self.MAIN_TAG)
            self.logger.setLevel(logging.NOTSET)
            if len(self.logger.handlers) == 0:
                self.logger.addHandler(ch)

    @param_types_validator(True, str, LogLevel, str)
    def log(self, tag, level, message):
        if self.logger is not None and 0 < level.value <= self.log_level.value:
            now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            color = self.start_color.format(self.colors[level.value])
            template = '{}[{}][{}][{}]: {}{}'.format(color, now, self.MAIN_TAG, tag, message, self.end_color)
            self.logger.log(self.log_level.value, template)

    @param_types_validator(True, str, Exception, str)
    def exception(self, tag, exception, traceback, print_traceback=False):

        self.log(tag, LogLevel.CRITICAL, str(exception) + ('\n' + traceback if print_traceback else ''))
        # self.log(tag, LogLevel.CRITICAL, str(exception))
