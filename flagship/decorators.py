import inspect
import traceback

from flagship.errors import TypingError


def exception_handler(default=None):
    def decorator_error(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TypingError:
                return func(*args, **kwargs)
            except Exception as e:
                tb = traceback.format_exc()
                print('\033[91m' + 'Error ' + tb + '\033[0m')
                return default

        return wrapper

    return decorator_error


def types_validator(self=False, *types):
    def decorator_typing(func):
        @exception_handler()
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
                    method_name = func.__name__ if func.__name__ is not '__init__' else \
                        args[0].__class__.__name__
                    raise TypingError("Arguments '{}' for '{}' function is not valid. Expecting {} type."
                                      .format(inspection_args[i], method_name, types[j]))
                # if not isinstance(args[i], type):
                #
                #     inspection_args = inspect.getargspec(func).args
                #     method_name = func.__name__ if func.__name__ is not '__init__' else \
                #         args[0].__class__.__name__
                #     raise TypingError("Arguments '{}' for '{}' function is not valid. Expecting {} type."
                #                       .format(inspection_args[i], method_name, types[j]))
            return func(*args, **kwargs)
            # raise TypingError("Arguments supplied for types_validator() are not valid.")

        return wrapper


    return decorator_typing
