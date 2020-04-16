import inspect
import traceback

from flagship.errors import TypingError, FlagshipErrorHandler
from handler import FlagshipEventHandler

errors_handler = None  # type: FlagshipErrorHandler
customer_event_handler = None  # type: FlagshipEventHandler


def exception_handler(**params):
    default = params['default'] if 'default' in params else None
    log = params['log'] if 'log' in params else False
    exception = params['exception'] if 'exception' in params else None

    # errors_handler = params['errors_handler'] if 'errors_handler' in params else None

    def decorator_error(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TypingError as t:
                if errors_handler is not None:
                    tb = traceback.format_exc()
                    errors_handler.new_error_raised(t, tb)
                    customer_event_handler.on_exception_raised(t, tb)
                return func(*args, **kwargs)
            except Exception as e:
                if errors_handler is not None:
                    tb = traceback.format_exc()
                    errors_handler.new_error_raised(e, tb)
                    customer_event_handler.on_exception_raised(e, tb)
                    if log is True:
                        print('\033[91m' + 'Error {} : '.format(e) + tb + '\033[0m')
                return default

        return wrapper

    return decorator_error


def types_validator(self=False, *types):
    def decorator_typing(func):
        def wrapper(*args, **kwargs):
            for i in range(0 if self is False else 1, len(args)):
                j = i if self is False else i - 1
                current_type = types[j]
                raise_error = True
                if isinstance(current_type, list):
                    for t in current_type:
                        if isinstance(args[i], t):
                            raise_error = False
                elif isinstance(args[i], current_type):
                    raise_error = False
                if raise_error:
                    inspection_args = inspect.getargspec(func).args
                    method_name = func.__name__ if func.__name__ != '__init__' else args[0].__class__.__name__
                    e = TypingError("Arguments '{}' for '{}' function is not valid. Expecting {} type."
                                    .format(inspection_args[i], method_name, types[j]))
                    raise e
            return func(*args, **kwargs)
            # raise TypingError("Arguments supplied for types_validator() are not valid.")

        return wrapper

    return decorator_typing
