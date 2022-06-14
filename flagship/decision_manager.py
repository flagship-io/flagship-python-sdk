from abc import ABCMeta, abstractmethod


class IDecisionManager:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_campaigns_modifications(visitor_delegate_dto):
        pass


class DecisionManager(IDecisionManager):
    __metaclass__ = ABCMeta

    def __init__(self, config, update_status):
        self.update_status = update_status
        self.flagship_config = config
        self.panic = False

        # flagship.Flagship._log("coucou", LogLevel.DEBUG, "=>>>>>>>>")

    def init(self):
        pass

    @abstractmethod
    def stop(self):
        pass
