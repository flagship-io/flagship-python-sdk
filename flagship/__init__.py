# from flagship.utils.decorators import param_types_validator
from __future__ import absolute_import

from flagship.main.config import _FlagshipConfig
from flagship.utils.decorators import param_types_validator
from flagship.utils.log_manager import FlagshipLogManager, LogLevel


# from flagship.config import FlagshipConfig


class Flagship:
    __instance = None

    def __init__(self):
        pass

    @staticmethod
    @param_types_validator(False, str, str, _FlagshipConfig)
    def start(env_id, api_key, config):
        Flagship.__get_instance().start(env_id, api_key, config)

    @staticmethod
    def config():
        return Flagship.__get_instance().config

    @staticmethod
    def __get_instance():
        """
        Get the flagship singleton instance.

        :return: Flagship
        """
        if not Flagship.__instance:
            Flagship.__instance = Flagship.__Flagship()
        return Flagship.__instance

    class __Flagship:

        def __init__(self):
            self.config = None

        @param_types_validator(True, str, str, _FlagshipConfig)
        def start(self, env_id, api_key, flagship_config):
            self.config = flagship_config
            self.config.env_id = env_id
            self.config.api_key = api_key
            self.config.log_manager.on_log("custom tag", LogLevel.INFO,
                        "Start : " + env_id + " " + str(api_key) + " \n\nConfig:" + str(self.config))


# from flagship import param_types_validator, LogLevel, Flagship
#
#
# @staticmethod
# @param_types_validator(False, str, LogLevel, str)
# def __log(tag, level, message):
#     log_manager = Flagship.config().log_manager
#     if log_manager is not None:
#         log_manager.on_log(tag, level, message)



# @param_types_validator(False, str, FlagshipLogManager.LogLevel, str)
# def new_log(tag, level, message):
#     if flagship_config.log_manager is not None:
#         flagship_config.log_manager.on_log(tag, level, message)
#
#
# @param_types_validator(False, Exception, str)
# def new_exception(exception, traceback):
#     if flagship_config.log_manager is not None:
#         flagship_config.log_manager.on_exception(exception, traceback)
