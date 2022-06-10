from abc import ABCMeta, abstractmethod

import flagship
from flagship.utils.log_manager import LogLevel


class DecisionManager:
    __metaclass__ = ABCMeta

    def __init__(self, config):
        self.flagship_config = config
        flagship.Flagship._log("coucou", LogLevel.DEBUG, "=>>>>>>>>")

    def init(self):
        pass

    @abstractmethod
    def stop(self):
        pass
