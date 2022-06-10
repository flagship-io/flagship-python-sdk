from abc import ABCMeta, abstractmethod

import flagship
from flagship.utils.decorators import param_types_validator
from flagship.main.status import Status


class StatusListener:
    __metaclass__ = ABCMeta

    @param_types_validator(True, Status)
    def status(self, new_status):
        if new_status is not flagship.Flagship.status():
            self.on_status_changed(new_status)

    @abstractmethod
    @param_types_validator(True, Status)
    def on_status_changed(self, new_status):
        pass