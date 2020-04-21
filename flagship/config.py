
from flagship.decorators import types_validator, exception_handler
from flagship.handler import FlagshipEventHandler


class Config:

    @exception_handler(log=True)
    @types_validator(True, str, str)
    def __init__(self, env_id, api_key, **kwargs):
        # type: (str, str, object) -> None
        """

        Configuration class to provide for starting the SDK.

        :param env_id: environment ID provided by Flagship
        :param api_key: api key provided by Flagship.
        :param kwargs: <br>
        'errors_handler': custom FlagshipErrorHandler to provide for error handling.

        """
        self.env_id = env_id
        self.api_key = api_key
        self.debug = None
        self.event_handler = None

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

        # self.timeout = 200  # in milliseconds
