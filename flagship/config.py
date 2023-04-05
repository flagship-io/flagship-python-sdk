from __future__ import absolute_import

import json

from flagship.cache_manager import CacheManager, SqliteCacheManager
from flagship.decision_mode import DecisionMode
from flagship.status import Status
from flagship.status_listener import StatusListener
from flagship.log_manager import FlagshipLogManager, LogLevel, LogManager

__metaclass__ = type

from flagship.tracking_manager import TrackingManagerConfig


class _FlagshipConfig(object):
    """
     FlagshipConfig configuration.
    """

    __env_id = ''
    __api_key = ''

    def __init__(self, mode, **kwargs):
        self.decision_mode = mode if mode is not None else DecisionMode.DECISION_API
        self.env_id = self.get_arg(kwargs, 'env_id', str) or self.__env_id
        self.api_key = self.get_arg(kwargs, 'api_key', str) or self.__api_key
        self.log_level = self.get_arg(kwargs, 'log_level', LogLevel) or LogLevel.ALL
        self.log_manager = self.get_arg(kwargs, 'log_manager', LogManager) or FlagshipLogManager(LogLevel.ALL)
        self.polling_interval = self.get_arg(kwargs, 'polling_interval', type(1)) or 60000
        self.timeout = self.get_arg(kwargs, 'timeout', type(1)) or 2000
        self.status_listener = self.get_arg(kwargs, 'status_listener', StatusListener) or None
        self.tracking_manager_config = self.get_arg(kwargs, 'tracking_manager_config',
                                                    TrackingManagerConfig) or TrackingManagerConfig()
        self.cache_manager = self.get_arg(kwargs, 'cache_manager', CacheManager) or None
        # self.__update_flagship_status()

    def get_arg(self, kwargs, name, c_type):
        return kwargs[name] if name in kwargs and isinstance(kwargs[name], c_type) else None

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
            'tracking_manager_config': str(self.tracking_manager_config.__class__.__name__),
            'cache_manager': None if self.cache_manager is None else str(self.cache_manager.__class__.__name__)
        }
        return json.dumps(config, indent=4)


class DecisionApi(_FlagshipConfig):
    def __init__(self, **kwargs):
        """
        Run the SDK in DecisionApi mode. The campaign assignments and targeting validation take place server-side.
        In this mode, each call to the fetchFlags method to refresh the flags will create an HTTP request.
        @param kwargs: optional parameters, see below.

        @keyword log_level: Specifies a log level to filter logs emitted by the SDK. Requires LogLevel type.
        @keyword log_manager: Specifies a custom implementation of LogManager in order to receive logs from the SDK.
        Requires a LogManager class implementation.
        @keyword timeout: Specifies timeout for decision api requests in milliseconds. Default is 2000ms.
        @keyword status_listener: Specifies a callback to be notified when the SDK status has changed.
        Requires a StatusListener class implementation.
        @keyword tracking_manager_config: Define a custom tracking manager configuration.
       """
        super(DecisionApi, self).__init__(DecisionMode.DECISION_API, **kwargs)
        # super(_FlagshipConfig, self).__init__(DecisionMode.DECISION_API, **kwargs)
        # _FlagshipConfig.__init__(self, DecisionMode.DECISION_API, **kwargs)

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
            'tracking_manager_config': str(self.tracking_manager_config.__class__.__name__),
            'cache_manager': None if self.cache_manager is None else str(self.cache_manager.__class__.__name__)
        }
        return json.dumps(config, indent=4)





class Bucketing(_FlagshipConfig):
    def __init__(self, **kwargs):
        """
        When the SDK is running in Bucketing mode, the SDK downloads all the campaigns configurations at once in a
        single bucketing file so that variation assignment can be computed client-side by the SDK. This bucketing file
        is stored in cache and will only be downloaded again when campaign configurations are modified in the Flagship
        interface.
        @param kwargs: optional parameters, see below.

        @keyword log_level: Specifies a log level to filter logs emitted by the SDK. Requires LogLevel type.
        @keyword log_manager: Specifies a custom implementation of LogManager in order to receive logs from the SDK.
        Requires a LogManager class implementation.
        @keyword timeout: Specifies timeout for bucketing requests in milliseconds. Default is 2000ms.
        @keyword status_listener: Specifies a callback to be notified when the SDK status has changed.
        Requires a StatusListener class implementation.
        @keyword polling_interval: Define the time interval between two bucketing updates in milliseconds.
        @keyword tracking_manager_config: Define a custom tracking manager configuration.
        Default is 60 seconds.
        """
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
            'tracking_manager_config': str(self.tracking_manager_config.__class__.__name__),
            'cache_manager': None if self.cache_manager is None else str(self.cache_manager.__class__.__name__)
        }
        return json.dumps(config, indent=4)
