from __future__ import absolute_import

from flagship.config import Config
from flagship.visitor import FlagshipVisitor
from flagship.decorators import exception_handler
from flagship.decorators import types_validator


class Flagship:
    class __Flagship:

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
            self._is_initialized = True
            # self._cache_manager = self._config.get('cache_manager')

        @exception_handler()
        @types_validator(True, str, dict)
        def create_visitor(self, visitor_id, context):  # type: (str, dict) -> FlagshipVisitor(object, str, dict)
            """
            Create or get a visitor instance.

            :param visitor_id: Unique visitor identifier.
            :param context: Visitor context.
            :return: FlagshipVisitor
            """
            return FlagshipVisitor(self._config, visitor_id, context)

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
