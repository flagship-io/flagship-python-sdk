from flagship.decision_manager import DecisionManager


class BucketingManager(DecisionManager):

    def __init__(self, config, update_status):
        super(DecisionManager).__init__(config, update_status)

    def stop(self):
        pass

    def get_campaigns_modifications(visitor_delegate_dto):
        pass
