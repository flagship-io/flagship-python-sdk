from flagship.status import Status
from flagship.decision_manager import DecisionManager


class ApiManager(DecisionManager):

    def __init__(self, config, update_status):
        super(ApiManager, self).__init__(config, update_status)
        update_status(Status.READY)

    def get_campaigns_modifications(visitor_delegate_dto):
        pass

    def stop(self):
        pass


