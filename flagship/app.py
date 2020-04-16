from __future__ import absolute_import

import logging

from flagship import decorators
from flagship.config import Config
from flagship.visitor import FlagshipVisitor
from flagship.decorators import exception_handler
from flagship.decorators import types_validator
from handler import _DefaultFlagshipEventHandler, FlagshipEventHandler

class Flagship:

    class __Flagship:

        _config = None  # type: Config

        def __init__(self):
            self._is_initialized = False

        @exception_handler()
        @types_validator(True, Config)
        def start(self, config):    # type: (Config) -> None
            """
            Start the flagship sdk.
            :param config: Configuration to initialize.
            """
            self._config = config
            decorators.customer_event_handler = self._config.event_handler
            decorators.errors_handler = self._config.errors_handler
            self._is_initialized = True
            self._config.event_handler.on_log(logging.DEBUG, "Started")

        @exception_handler()
        @types_validator(True, str, dict)
        def create_visitor(self, visitor_id, context={}):  # type: (str, dict) -> FlagshipVisitor(object, str, dict)
            """
            Create or get a visitor instance.

            :param visitor_id: Unique visitor identifier.
            :param context: Visitor context.
            :return: FlagshipVisitor
            """
            visitor = FlagshipVisitor(self._config, visitor_id, context)
            self._config.event_handler.on_log(logging.DEBUG, "Visitor '{}' created. Context : {}".format(visitor_id, str(context)))
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
