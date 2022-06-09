from __future__ import absolute_import

from datetime import datetime
from enum import Enum
import logging
from flagship.utils.decorators import param_types_validator


class LogLevel(Enum):
    ALL = 100
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NONE = 0


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
        if isinstance(level, LogLevel) and level.value > 0:
            self.log_level = level
            ch = logging.StreamHandler()
            self.logger = logging.getLogger(self.MAIN_TAG)
            self.logger.setLevel(logging.NOTSET)
            if len(self.logger.handlers) == 0:
                self.logger.addHandler(ch)

    @param_types_validator(True, str, LogLevel, str)
    def on_log(self, tag, level, message):
        if self.logger is not None and 0 < level.value < self.log_level.value:
            now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            color = self.start_color.format(self.colors[level.value])
            template = '{}[{}][{}][{}]: {}{}'.format(color, now, self.MAIN_TAG, tag, message, self.end_color)
            self.logger.log(self.log_level.value, template)

    def on_exception(self, exception, traceback):
        self.on_log(LogLevel.CRITICAL, str(exception) + '\n' + traceback)
