from enum import Enum

from flagship.decorators import types_validator, exception_handler
from flagship.handler import FlagshipEventHandler


class Config:
    class Mode(Enum):
        API = 'API'
        BUCKETING = 'BUCKETING'

    @exception_handler(log=True)
    def __init__(self, **kwargs):
        # type: (object) -> None
        """

        Configuration class to provide for starting the SDK.

        :param kwargs: <br>
        'event_handler': custom FlagshipEventHandler to provide for log and error handling.
        "polling_interval': Bucketing polling interval in seconds. Default is 60 seconds. Min is 1 second. If <= 0 is
        given, polling will be disabled. In api mode, panic status will be updated at each call of
        synchronize_modifications. In Bucketing mode, panic status will be updated at each polling interval, or at start
         time if polling is disabled.
        'debug':  True/False
        'mode': Api/Bucketing
        'timeout': set a custom timeout in seconds for campaign request. Default is 2 seconds.
        """
        self.env_id = None
        self.api_key = None
        self.debug = None
        self.event_handler = None
        self.mode = Config.Mode.API
        self.bucketing_refresh_interval = 60
        self.timeout = float(2.0)

        if 'debug' in kwargs:
            debug = kwargs['debug']
            if isinstance(debug, bool):
                self.debug = debug

        if 'event_handler' in kwargs:
            event_handler = kwargs['event_handler']
            if isinstance(event_handler, FlagshipEventHandler):
                self.event_handler = event_handler
            else:
                self.event_handler = FlagshipEventHandler()
        else:
            self.event_handler = FlagshipEventHandler()

        if 'polling_interval' in kwargs:
            bucketing_refresh_interval = kwargs['polling_interval']
            if isinstance(bucketing_refresh_interval, int) or isinstance(bucketing_refresh_interval, float) \
                    or isinstance(bucketing_refresh_interval, long):
                self.bucketing_refresh_interval = bucketing_refresh_interval

        if 'mode' in kwargs:
            mode = kwargs['mode']
            if isinstance(mode, Config.Mode):
                self.mode = mode

        if 'timeout' in kwargs:
            timeout = kwargs['timeout']
            if (isinstance(timeout, int) or isinstance(timeout, float)) and timeout > 0:
                self.timeout = float(timeout)
