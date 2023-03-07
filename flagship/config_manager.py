
from flagship.api_manager import ApiManager
from flagship.bucketing_manager import BucketingManager
from flagship.config import DecisionApi
from flagship.constants import WARNING_DEFAULT_CONFIG, TAG_INITIALIZATION
from flagship.decision_mode import DecisionMode
from flagship.log_manager import LogLevel
from flagship.tracking_manager import TrackingManager
from flagship.status import Status


class ConfigManager:

    def __init__(self):
        # self.flagship_config = DecisionApi()
        self.flagship_config = None
        self.decision_manager = None
        # self.tracking_manager = TrackingManager(self.flagship_config)
        self.tracking_manager = None

    def init(self, env_id, api_key, config=None, update_status=None):
        if config is not None:
            self.flagship_config = config
        else:
            self.flagship_config = DecisionApi(env_id=env_id, api_key=api_key)
            self.flagship_config.log_manager.log(TAG_INITIALIZATION, LogLevel.WARNING, WARNING_DEFAULT_CONFIG)
        self.flagship_config.env_id = env_id
        self.flagship_config.api_key = api_key
        self.init_decision_manager(update_status)
        self.init_cache_manager(env_id)
        self.init_tracking_manager()
        self.decision_manager.start_running()

    def init_decision_manager(self, update_status=None):
        if self.flagship_config.decision_mode is DecisionMode.DECISION_API:
            self.decision_manager = ApiManager(self.flagship_config, update_status)
        else:
            self.decision_manager = BucketingManager(self.flagship_config, update_status)

    def init_cache_manager(self, env_id):
        if self.flagship_config.cache_manager is not None:
            self.flagship_config.cache_manager.init(env_id)

    def init_tracking_manager(self):
        if self.tracking_manager is None:
            self.tracking_manager = TrackingManager(self.flagship_config)
            self.tracking_manager.init(self.flagship_config)
            self.tracking_manager.start_running()

    def is_set(self):
        return self.flagship_config.is_set() and self.decision_manager is not None

    def reset(self):
        if self.decision_manager is not None:
            self.decision_manager.stop_running()
        if self.tracking_manager is not None:
            self.tracking_manager.stop_running()
        self.flagship_config = DecisionApi()
        if self.flagship_config.cache_manager is not None:
            self.flagship_config.cache_manager.close_database()

    def flagship_status_update(self, new_status, old_status):
        if new_status is Status.PANIC and old_status is Status.READY:
            if self.tracking_manager is not None and self.tracking_manager.is_running():
                self.tracking_manager.stop_running(new_status)
                self.tracking_manager = None
        elif new_status is Status.READY and old_status is Status.PANIC:
            self.init_tracking_manager()

