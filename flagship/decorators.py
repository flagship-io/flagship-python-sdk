import inspect
import traceback

from flagship.errors import TypingError, ParamError
from flagship.handler import FlagshipEventHandler

customer_event_handler = FlagshipEventHandler()  # type: FlagshipEventHandler
# customer_event_handler = None  # type: FlagshipEventHandler

try:
    from inspect import getfullargspec
except Exception:
    from inspect import getargspec
    getfullargspec = getargspec

def exception_handler(**params):
    default = params['default'] if 'default' in params else None

    # errors_handler = params['errors_handler'] if 'errors_handler' in params else None

    def decorator_error(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (TypingError, ParamError) as t:
                if customer_event_handler is not None:
                    tb = traceback.format_exc()
                    customer_event_handler.on_exception_raised(t, tb)
                return func(*args, **kwargs)
            except Exception as e:
                if customer_event_handler is not None:
                    tb = traceback.format_exc()
                    customer_event_handler.on_exception_raised(e, tb)
                if customer_event_handler.catch_all_exceptions is True:
                    return default
                else:
                    raise e

        return wrapper

    return decorator_error


def types_validator(self=False, *types):
    def decorator_typing(func):
        def wrapper(*args, **kwargs):
            for i in range(0 if self is False else 1, len(args)-1):
                j = i if self is False else i - 1
                current_type = types[j]
                raise_error = True
                # Check if list of potential type. ex [int, float, str]
                if isinstance(current_type, list):
                    for t in current_type:
                        if isinstance(args[i], t):
                            raise_error = False
                # Check if dict ex: {t=[str, int], l=10, max=500, min=0}
                elif isinstance(current_type, dict):
                    if 'types' in current_type:
                        dtypes = current_type['types']
                        if isinstance(dtypes, list):
                            for dt in dtypes:
                                if isinstance(args[i], dt):
                                    raise_error = False
                        elif isinstance(args[i], dtypes):
                            raise_error = False
                        if raise_error is True:
                            inspection_args = getfullargspec(func).args
                            method_name = func.__name__ if func.__name__ != '__init__' else args[0].__class__.__name__
                            raise TypingError("Parameter '{}' for '{}' function is not valid. Expecting {} type."
                                            .format(inspection_args[i], method_name, dtypes))
                    if 'max_length' in current_type:
                        max_length = current_type['max_length']
                        if len(str(args[i])) > max_length:
                            inspection_args = getfullargspec(func).args
                            method_name = func.__name__ if func.__name__ != '__init__' else args[0].__class__.__name__
                            raise ParamError("Parameter '{}' for '{}' function is not valid. Expected max value "
                                             "length {}.".format(inspection_args[i], method_name, max_length))
                    if 'max_value' in current_type:
                        max_value = current_type['max_value']
                        param = args[i]
                        if (param is int or float) and (param > max_value):
                            inspection_args = getfullargspec(func).args
                            method_name = func.__name__ if func.__name__ != '__init__' else args[0].__class__.__name__
                            raise ParamError("Parameter '{}' for '{}' function is not valid. Expected max value {}."
                                             .format(inspection_args[i], method_name, max_value))
                    if 'min_value' in current_type:
                        min_value = current_type['min_value']
                        param = args[i]
                        if (param is int or float) and (param < min_value):
                            inspection_args = getfullargspec(func).args
                            method_name = func.__name__ if func.__name__ != '__init__' else args[0].__class__.__name__
                            raise ParamError("Parameter '{}' for '{}' function is not valid. Expected min value {}."
                                             .format(inspection_args[i], method_name, min_value))
                # Check type
                elif isinstance(args[i], current_type):
                    raise_error = False

                if raise_error:
                    inspection_args = getfullargspec(func).args
                    method_name = func.__name__ if func.__name__ != '__init__' else args[0].__class__.__name__
                    e = TypingError("Parameter '{}' for '{}' function is not valid. Expecting {} type."
                                    .format(inspection_args[i], method_name, types[j]))
                    raise e

            return func(*args, **kwargs)

        return wrapper

    return decorator_typing
