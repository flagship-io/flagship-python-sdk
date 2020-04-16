import logging
from datetime import datetime


class FlagshipEventHandler:

    def __init__(self):
        """
        Implement this class in order to centralize all SDK events.
        """
        pass

    def on_log(self, level, message):
        """
        Called when the sdk emit a log.
        :param level: CRITICAL = 50, ERROR = 40, WARNING = 30, INFO = 20, DEBUG = 10
        :param message: content of the log.
        """
        pass

    def on_exception_raised(self, exception, traceback):
        """
        Called when the SDK has raised an exception.
        :param exception: Exception or Error
        :param traceback: Traceback which raised this error.
        """
        pass


class _DefaultFlagshipEventHandler(FlagshipEventHandler):
    tag = '[Flagship]'
    error_tag = tag + '[ERROR]'
    except_tag = tag + '[EXCEPTION]'
    colors = {50: 89, 40: 91, 30: 93, 20: 94, 10: 96}
    start_color = '\033[{}m'
    end_color = '\033[0m'

    def __init__(self):
        FlagshipEventHandler.__init__(self)
        self.logger = logging.getLogger(self.tag)
        self.logger.setLevel(logging.DEBUG)
        self.ch = logging.StreamHandler()
        self.logger.addHandler(self.ch)

    def on_log(self, level, message):
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        color = self.start_color.format(self.colors[level])
        self.logger.debug('{}{} - {} : {}{}'.format(color, now, self.tag, message, self.end_color))

    def on_exception_raised(self, exception, traceback):
        self.on_log(logging.CRITICAL, str(exception) + '\n' + traceback)