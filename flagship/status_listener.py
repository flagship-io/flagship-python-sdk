from abc import ABCMeta, abstractmethod

import flagship
from flagship.decorators import param_types_validator
from flagship.status import Status


class StatusListener:
    """
    This is the Implementation to call when the SDK status has changed.
    """
    __metaclass__ = ABCMeta

    @param_types_validator(True, Status)
    def status(self, new_status):
        if new_status is not flagship.Flagship.status():
            self.on_status_changed(new_status)

    @abstractmethod
    @param_types_validator(True, Status)
    def on_status_changed(self, new_status):
        """
        Implement this method to be notified each time the SDK status changes.
        @param new_status: New SDK status
        """
        pass
