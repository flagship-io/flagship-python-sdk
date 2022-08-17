from __future__ import absolute_import

import json

from flagship.decision_mode import DecisionMode
from flagship.status import Status
from flagship.status_listener import StatusListener
from flagship.log_manager import FlagshipLogManager, LogLevel, LogManager

__metaclass__ = type


class _FlagshipConfig:
    __env_id = ''
    __api_key = ''

    def __init__(self, mode, **kwargs):
        self.decision_mode = mode if mode is not None else DecisionMode.DECISION_API
        self.env_id = self.__get_arg('env_id', str, self.__env_id, kwargs)
        self.api_key = self.__get_arg('api_key', str, self.__api_key, kwargs)
        self.log_level = self.__get_arg('log_level', LogLevel, LogLevel.ALL, kwargs)
        self.log_manager = self.__get_arg('log_manager', LogManager, FlagshipLogManager(LogLevel.ALL), kwargs)
        self.polling_interval = self.__get_arg('polling_interval', type(1), 60000, kwargs)
        self.timeout = self.__get_arg('timeout', type(1), 2000, kwargs)
        self.status_listener = self.__get_arg('status_listener', StatusListener, None, kwargs)
        # self.cache_manager = self.__get_arg('cache_manager', CacheManager , None, kwargs)
        # self.__update_flagship_status()

    def __get_arg(self, name, c_type, default, kwargs):
        return kwargs[name] if name in kwargs and isinstance(kwargs[name], c_type) else default

    # def __update_flagship_status(self):
    #     if self.status_listener is not None:
    #         self.status_listener.status(Status.READY)

    def is_set(self):
        return self.api_key is not None and self.api_key is not None
        # return self.api_key is not None and self.api_key

    def __str__(self):
        config = {
            'env_id': str(self.env_id),
            'api_key': str(self.api_key),
            'decision_mode': str(self.decision_mode),
            'log_level': str(self.log_level),
            'log_manager': None if self.log_manager is None else str(self.log_manager.__class__.__name__),
            'polling_interval': self.polling_interval,
            'timeout': self.timeout,
            'status_listener': None if self.status_listener is None else str(self.status_listener.__class__.__name__),
            # 'cache_manager': None if self.cache_manager is None else str(self.cache_manager.__class__.__name__)
        }
        return json.dumps(config, indent=4)


class DecisionApi(_FlagshipConfig):
    def __init__(self, **kwargs):
        super(DecisionApi, self).__init__(DecisionMode.DECISION_API, **kwargs)

    def __str__(self):
        config = {
            'env_id': str(self.env_id),
            'api_key': str(self.api_key),
            # 'decision_mode': str(self.decision_mode),
            'log_level': str(self.log_level),
            'log_manager': None if self.log_manager is None else str(self.log_manager.__class__.__name__),
            # 'polling_interval': self.polling_interval,
            'timeout': self.timeout,
            'status_listener': None if self.status_listener is None else str(self.status_listener.__class__.__name__),
            # 'cache_manager': None if self.cache_manager is None else str(self.cache_manager.__class__.__name__)
        }
        return json.dumps(config, indent=4)


class Bucketing(_FlagshipConfig):
    def __init__(self, **kwargs):
        super(Bucketing, self).__init__(DecisionMode.BUCKETING, **kwargs)

    def __str__(self):
        config = {
            'env_id': str(self.env_id),
            'api_key': str(self.api_key),
            # 'decision_mode': str(self.decision_mode),
            'log_level': str(self.log_level),
            'log_manager': None if self.log_manager is None else str(self.log_manager.__class__.__name__),
            'polling_interval': self.polling_interval,
            'timeout': self.timeout,
            'status_listener': None if self.status_listener is None else str(self.status_listener.__class__.__name__),
            # 'cache_manager': None if self.cache_manager is None else str(self.cache_manager.__class__.__name__)
        }
        return json.dumps(config, indent=4)
