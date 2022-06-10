from flagship.main.api_manager import ApiManager
from flagship.main.bucketing_manager import BucketingManager
from flagship.main.config import DecisionApi
from flagship.main.decision_mode import DecisionMode


class ConfigManager:
    def __init__(self):
        self.flagship_config = DecisionApi()
        self.decision_manager = None

    def init(self, env_id, api_key, config):
        self.flagship_config = config
        self.flagship_config.env_id = env_id
        self.flagship_config.api_key = api_key
        self.decision_manager = ApiManager(
            self.flagship_config) if config.mode is DecisionMode.DECISION_API else BucketingManager(
            self.flagship_config)
        self.decision_manager.init()

    def is_set(self):
        return self.flagship_config.is_set() and self.decision_manager is not None

    def reset(self):
        if self.decision_manager is not None:
            self.decision_manager.stop()
        self.flagship_config = DecisionApi()

