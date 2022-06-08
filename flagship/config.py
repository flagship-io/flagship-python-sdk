from flagship.utils.log_manager import FlagshipLogManager


class FlagshipConfig:

    log_manager = FlagshipLogManager(FlagshipLogManager.LogLevel.ALL)

    def __init__(self, **kwargs):
        self.log_manager = self.__get_arg('log_manager', FlagshipLogManager(FlagshipLogManager.LogLevel.ALL), kwargs)

    def __get_arg(self, name, default, kwargs):
        return kwargs[name] if name in kwargs and isinstance(kwargs[name], default) else default
