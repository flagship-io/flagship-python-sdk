import logging

from flagship import decorators
from flagship.config import Config
from flagship.decorators import exception_handler
from flagship.decorators import types_validator
from flagship.errors import InitializationError
from flagship.helpers.bucketing import BucketingManager
from flagship.helpers.preset_context import PresetContext
from flagship.visitor import FlagshipVisitor


class Flagship:
    class __Flagship:

        def __init__(self):
            self._config = None  # type : Config
            self._bucketing_manager = None

        @exception_handler()
        @types_validator(True, str, str, Config)
        def start(self, env_id, api_key, config):  # type: (Config) -> None
            """
            Start the flagship sdk or raise a InitializationError if an error occurred.

            :param env_id: Environment id provided by Flagship.
            :param api_key: Flagship secure api key.
            :param config: Configuration to initialize.
            """
            self._bucketing_manager = None
            self._config = config
            if self._config.env_id != env_id:
                self._config.env_id = env_id
            if self._config.api_key != api_key:
                self._config.api_key = api_key
            decorators.customer_event_handler = self._config.event_handler

            if self.is_flagship_started() and (
                    config.mode is Config.Mode.API or (config.mode is Config.Mode.BUCKETING)):
                if config.mode is Config.Mode.BUCKETING:
                    if self._bucketing_manager is not None:
                        self._bucketing_manager.close()
                    self._bucketing_manager = BucketingManager(self._config)
                    self._bucketing_manager.init_bucketing()
                self._config.event_handler.on_log(logging.DEBUG, "Started")
            else:
                raise InitializationError("Flagship SDK has not been initialized or started successfully.")

        def is_flagship_started(self):
            if self._config is not None and self._config.api_key is not None and self._config.env_id is not None:
                return True
            else:
                return False

        @exception_handler()
        @types_validator(True, str, bool, dict)
        def create_visitor(self, visitor_id=None, authenticated=False, context={}):
            # type: (str, bool, dict) -> FlagshipVisitor(BucketingManager, Config, str, bool, dict)
            """
            Create a visitor instance. Raise a InitializationError if the SDK has not been successfully initialized.

            :param visitor_id: Unique visitor identifier.
            :param authenticated: Specify if the current visitor is authenticated or anonymous
            :param context: Visitor context.
            :return: FlagshipVisitor or None if the
            """
            if self.is_flagship_started() is False:
                raise InitializationError("Flagship SDK has not been initialized or started successfully.")
            else:
                visitor_context = {}
                visitor_context.update(PresetContext.load())
                visitor_context.update(context)
                visitor = FlagshipVisitor(self._bucketing_manager, self._config, visitor_id, authenticated, visitor_context)
                self._config.event_handler.on_log(logging.DEBUG, "Visitor '{}' created. Context : {}".
                                                  format(visitor_id, str(visitor_context)))
                return visitor

        def close(self):
            if self._bucketing_manager is not None:
                self._bucketing_manager.close()
            __instance = None

    __instance = None

    @staticmethod
    def instance():
        """
        Get the flagship singleton instance.

        :return: Flagship
        """
        if not Flagship.__instance:
            Flagship.__instance = Flagship.__Flagship()
        return Flagship.__instance
