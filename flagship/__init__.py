from __future__ import absolute_import

from flagship.config import _FlagshipConfig
from flagship.config_manager import ConfigManager
from flagship.constants import TAG_STATUS, INFO_STATUS_CHANGED, TAG_INITIALIZATION, INFO_READY
from flagship.decorators import param_types_validator
from flagship.log_manager import LogLevel
from flagship.status import Status
from flagship.utils import log
from flagship.visitor import Visitor

__name__ = 'flagship'
__version__ = '3.0.0'


class Flagship:
    __instance = None

    def __init__(self):
        pass

    @staticmethod
    @param_types_validator(False, str, str, _FlagshipConfig)
    def start(env_id, api_key, configuration):
        Flagship.__get_instance().start(env_id, api_key, configuration)

    @staticmethod
    def config():
        return Flagship.__get_instance().configuration_manager.flagship_config

    @staticmethod
    def new_visitor(visitor_id, **kwargs):
        return Flagship.__get_instance().new_visitor(visitor_id, **kwargs)

    @staticmethod
    def get_visitor():
        return Flagship.__get_instance().get_visitor()

    @staticmethod
    def status():
        return Flagship.__get_instance().status

    @staticmethod
    def stop():
        return Flagship.__get_instance().stop()

    @staticmethod
    def __get_instance():
        """
        Get the flagship singleton instance.

        :return: Flagship
        """
        if not Flagship.__instance:
            Flagship.__instance = Flagship.__Flagship()
        return Flagship.__instance

    @staticmethod
    def _update_status(new_status):
        Flagship.__get_instance().update_status(new_status)

    class __Flagship:

        def __init__(self):
            self.current_visitor = None
            self.status = Status.NOT_INITIALIZED
            self.configuration_manager = ConfigManager()

        @param_types_validator(True, str, str, _FlagshipConfig)
        def start(self, env_id, api_key, flagship_config):
            self.update_status(Status.STARTING)
            self.configuration_manager.init(env_id, api_key, flagship_config, self.update_status)
            if self.configuration_manager.is_set() is False:
                self.update_status(Status.NOT_INITIALIZED)
                self.__log(TAG_INITIALIZATION, )

        def update_status(self, new_status):
            if new_status is not None and new_status != self.status:
                self.status = new_status
                if self.configuration_manager.flagship_config.status_listener is not None:
                    self.configuration_manager.flagship_config.status_listener.on_status_changed(new_status)
                    log(TAG_STATUS, LogLevel.DEBUG, INFO_STATUS_CHANGED.format(str(new_status)))
                if new_status is Status.READY:
                    log(TAG_INITIALIZATION, LogLevel.INFO,
                        INFO_READY.format(str(__version__), str(self.configuration_manager.flagship_config)))

        def new_visitor(self, visitor_id, **kwargs):
            new_visitor = Visitor(self.configuration_manager, visitor_id, **kwargs)
            if 'instance_type' in kwargs and kwargs['instance_type'] is Visitor.Instance.SINGLE_INSTANCE:
                self.current_visitor = new_visitor
            return new_visitor

        def get_visitor(self):
            return self.current_visitor

        def stop(self):
            self.status = Status.NOT_INITIALIZED
            self.configuration_manager.reset()

        def __log(self, tag, level, message):
            try:
                configured_log_manager = self.configuration_manager.flagship_config.log_manager
                if configured_log_manager is not None:
                    configured_log_manager.log(tag, level, message)
            except Exception as e:
                pass
