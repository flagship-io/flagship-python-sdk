
from flagship.decorators import types_validator, exception_handler
from flagship.errors import FlagshipErrorHandler
from handler import FlagshipEventHandler, _DefaultFlagshipEventHandler


class Config:

    event_handler = None  # type: FlagshipEventHandler

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
        self.errors_handler = None
        self.debug = None

        if 'debug' in kwargs:
            debug = kwargs['debug']
            if isinstance(debug, bool):
                self.debug = debug

        if 'errors_handler' in kwargs:
            errors_handler = kwargs['errors_handler']
            if isinstance(errors_handler, FlagshipErrorHandler):
                self.errors_handler = errors_handler

        if 'event_handler' in kwargs:
            event_handler = kwargs['event_handler']
            if isinstance(event_handler, FlagshipEventHandler):
                self.event_handler = event_handler
        if self.event_handler is None:
            self.event_handler = _DefaultFlagshipEventHandler()

        # self.timeout = 200  # in milliseconds
