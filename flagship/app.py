from flagship import decorators
from flagship.config import Config
from flagship.errors import InitializationError
from flagship.helpers import bucketing
from flagship.helpers.bucketing import Bucketing
from flagship.helpers.preset_context import PresetContext
from flagship.visitor import FlagshipVisitor
from flagship.decorators import exception_handler
from flagship.decorators import types_validator
import logging


class Flagship:
    class __Flagship:

        _config = None  # type: Config

        def __init__(self):
            pass

        @exception_handler()
        @types_validator(True, Config)
        def start(self, config):  # type: (Config) -> None
            """
            Start the flagship sdk or raise a InitializationError if an error occurred.

            :param config: Configuration to initialize.
            """
            self._config = config
            decorators.customer_event_handler = self._config.event_handler

            if self.is_flagship_started() and (config.mode is Config.Mode.API
                                               or (config.mode is Config.Mode.BUCKETING
                                                   and Bucketing.updateBucketingFile(config) is True)):
                self._config.event_handler.on_log(logging.DEBUG, "Started")
            else:
                raise InitializationError("Flagship SDK has not been initialized or started successfully.")

        def is_flagship_started(self):
            if self._config is not None and self._config.api_key is not None and self._config.env_id is not None:
                return True
            else:
                return False

        @exception_handler()
        @types_validator(True, str, dict)
        def create_visitor(self, visitor_id, context={}):  # type: (str, dict) -> FlagshipVisitor(object, str, dict)
            """
            Create a visitor instance. Raise a InitializationError if the SDK has not been successfully initialized.

            :param visitor_id: Unique visitor identifier.
            :param context: Visitor context.
            :return: FlagshipVisitor or None if the
            """
            if self.is_flagship_started() is False:
                raise InitializationError("Flagship SDK has not been initialized or started successfully.")
            else:
                context.update(PresetContext.load())
                visitor = FlagshipVisitor(self._config, visitor_id, context)
                self._config.event_handler.on_log(logging.DEBUG, "Visitor '{}' created. Context : {}".
                                                  format(visitor_id, str(context)))
                return visitor

        def close(self):
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

    # def __new__(cls, *args, **kwargs):
    #     if not Flagship.instance:
    #         Flagship.instance = Flagship.__Flagship(*args, **kwargs)
    #     return Flagship.instance
