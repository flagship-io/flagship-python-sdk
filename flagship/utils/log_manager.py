import logging
from datetime import datetime
from enum import Enum
from flagship.utils.constants import MAIN_TAG


class FlagshipLogManager:

    class LogLevel(Enum):
        ALL = 100
        CRITICAL = 50
        ERROR = 40
        WARNING = 30
        INFO = 20
        DEBUG = 10
        NONE = 0

    log_level = LogLevel.ALL
    colors = {50: 89, 40: 91, 30: 93, 20: 94, 10: 96}
    start_color = '\033[{}m'
    end_color = '\033[0m'

    def __init__(self, level):
        # type: (LogLevel) -> None
        """
        @rtype: FlagshipLogManager

        """
        if isinstance(level, self.LogLevel) and level.value > 0:
            self.log_level = level
            ch = logging.StreamHandler()
            self.logger = logging.getLogger(MAIN_TAG)
            self.logger.setLevel(logging.NOTSET)
            if len(self.logger.handlers) == 0:
                self.logger.addHandler(ch)

    def on_log(self, tag, level, message):
        if self.logger is not None and 0 < level.value < self.log_level.value:
            now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            color = self.start_color.format(self.colors[level.value])
            template = '{}{} [{}]: {}{}'.format(color, now, MAIN_TAG, message, self.end_color)
            self.logger.log(self.log_level.value, template)

    def on_exception(self, exception, traceback):
        self.on_log(self.LogLevel.CRITICAL, str(exception) + '\n' + traceback)



