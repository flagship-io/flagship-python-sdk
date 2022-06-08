from flagship import *
from flagship.utils import *
from flagship.config import *
from flagship.utils.decorators import param_types_validator

flagship_config = None


@param_types_validator(False, str, str, FlagshipConfig)
def start(env_id, api_key, config):
    global flagship_config
    flagship_config = config
    new_log("custom tag", FlagshipLogManager.LogLevel.INFO, "Start : " + env_id + " " + str(api_key) + " " + str(config))
    # print()


@param_types_validator(False, str, FlagshipLogManager.LogLevel, str)
def new_log(tag, level, message):
    if flagship_config.log_manager is not None:
        flagship_config.log_manager.on_log(tag, level, message)


@param_types_validator(False, Exception, str)
def new_exception(exception, traceback):
    if flagship_config.log_manager is not None:
        flagship_config.log_manager.on_exception(exception, traceback)
