import inspect
import traceback

from flagship import flagship
from flagship.utils.constants import PARAM_TYPE_ERROR
from flagship.utils.errors import ParamTypeError


def exception_handler(**params):
    default = params['default'] if 'default' in params else None

    def decorator_error(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                tb = traceback.format_exc()
                flagship.new_exception(e, tb)
        return wrapper

    return decorator_error


def param_types_validator(self=False, *types):
    """

    @return: object
    @param self: Does the decorated method use self param.
    @param types: Decorated method param types list.
    """
    def decorator_typing(func):
        def wrapper(*args, **kwargs):
            p = 0 if self is False else 1
            for i in range(p, len(args)):
                raise_error = True
                ctype = types[i]
                if isinstance(ctype, list):
                    for t in ctype:
                        if isinstance(args[i], t):
                            raise_error = False
                elif isinstance(args[i], ctype):
                    raise_error = False
                if raise_error:
                    inspection_args = inspect.getfullargspec(func).args
                    method_name = func.__name__ if func.__name__ != '__init__' else args[0].__class__.__name__
                    e = ParamTypeError(PARAM_TYPE_ERROR.format(inspection_args[i], method_name, types[i]))
                    raise e
            return func(*args, **kwargs)

        return wrapper

    return decorator_typing
