from __future__ import absolute_import
from __future__ import unicode_literals

import importlib_metadata

from flagship.config import _FlagshipConfig
from flagship.config_manager import ConfigManager
from flagship.constants import TAG_STATUS, INFO_STATUS_CHANGED, TAG_INITIALIZATION, INFO_READY, ERROR_CONFIGURATION, \
    TAG_MAIN, INFO_STOPPED, TAG_TERMINATION
from flagship.decorators import param_types_validator
from flagship.errors import InitializationParamError
from flagship.log_manager import LogLevel
from flagship.status import Status
from flagship.utils import log
from flagship.visitor import Visitor

__name__ = 'flagship'
__version__ = importlib_metadata.distribution(__name__).version


class Flagship:
    __instance = None

    def __init__(self):
        pass

    @staticmethod
    @param_types_validator(False, str, str, [_FlagshipConfig, None])
    def start(env_id, api_key, configuration=None):
        """
        Start the flagship SDK.

        @param env_id: Environment id provided by Flagship.
        @param api_key: Secure api key provided by Flagship.
        @param configuration: Flagship configuration to initialize with. Can be DecisionApi or Bucketing.
        @return:
        """
        Flagship.__get_instance().start(env_id, api_key, configuration)

    @staticmethod
    def config():
        """
        Return the current used flagship configuration.
        @return: _FlagshipConfig
        """
        return Flagship.__get_instance().configuration_manager.flagship_config

    @staticmethod
    def new_visitor(visitor_id, **kwargs):
        """
        Create and return a new Flagship visitor instance.<br><br>

        @param visitor_id: Unique visitor identifier. <br>
        @param kwargs optional parameters: <br><br>

        <b>'instance_type'</b> (Visitor.Instance): Visitor.Instance.NEW_INSTANCE or Visitor.Instance.SINGLE_INSTANCE.
        Default is SINGLE_INSTANCE.<br>
        <b>'authenticated'</b> (bool): Bool that Specifies if the visitor is authenticated (True) or anonymous (False).
        Default value is False. <br>
        <b>'consent'</b> (bool): Bool that Specifies if the visitor has consented for personal data usage. When false some
        features will be deactivated, cache will be deactivated and cleared. True by default. <br>
        <b>'context'</b> (dict): Dict that specifies visitor initial context key / values used for targeting.
        Context keys must be String, and values types must be one of the following : Number, Boolean, String.<br>

        @return: Newly created Visitor instance.
        """
        return Flagship.__get_instance().new_visitor(visitor_id, **kwargs)

    @staticmethod
    def get_visitor():
        """
        This method will return any previous created visitor instance initialized with the SINGLE_INSTANCE.
        @return: Visitor.
        """
        return Flagship.__get_instance().get_visitor()

    @staticmethod
    def status():
        """
        Return the current SDK status.
        @return: Status.
        """
        return Flagship.__get_instance().status

    @staticmethod
    def stop():
        """
        Stop and reset the Flagship instance.
        @return:
        """
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
            self.device_context = {}

        @param_types_validator(True, str, str, [_FlagshipConfig, None])
        def start(self, env_id, api_key, flagship_config):
            # self.update_status(flagship_config, Status.STARTING)
            if not env_id or not api_key:
                raise InitializationParamError()
            self.update_status(flagship_config, Status.STARTING)
            self.configuration_manager.init(env_id, api_key, flagship_config, self.update_status)
            # self.update_status(flagship_config, Status.STARTING)
            if self.configuration_manager.is_set() is False:
                self.update_status(self.configuration_manager.flagship_config, Status.NOT_INITIALIZED)
                self.__log(TAG_INITIALIZATION, LogLevel.ERROR, ERROR_CONFIGURATION)

        def update_status(self, flagship_config, new_status):
            if flagship_config is not None and new_status is not None and new_status != self.status:
                old_status = self.status
                self.status = new_status
                log(TAG_STATUS, LogLevel.DEBUG, INFO_STATUS_CHANGED.format(str(new_status)), flagship_config)
                if new_status is Status.READY:
                    log(TAG_INITIALIZATION, LogLevel.INFO,
                        INFO_READY.format(str(__version__), str(flagship_config)))
                self.configuration_manager.flagship_status_update(new_status, old_status)
                if flagship_config.status_listener is not None:
                    flagship_config.status_listener.on_status_changed(new_status)

        def new_visitor(self, visitor_id, **kwargs):
            new_visitor = Visitor(self.configuration_manager, visitor_id, **kwargs)
            if 'instance_type' in kwargs and kwargs['instance_type'] is Visitor.Instance.SINGLE_INSTANCE:
                self.current_visitor = new_visitor
            return new_visitor

        def get_visitor(self):
            return self.current_visitor

        def stop(self):
            self.current_visitor = None
            self.status = Status.NOT_INITIALIZED
            log(TAG_TERMINATION, LogLevel.INFO, INFO_STOPPED)
            self.configuration_manager.reset()

        def __log(self, tag, level, message):
            try:
                configured_log_manager = self.configuration_manager.flagship_config.log_manager
                if configured_log_manager is not None:
                    configured_log_manager.log(tag, level, message)
            except Exception as e:
                pass
