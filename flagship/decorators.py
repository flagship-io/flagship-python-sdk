import inspect

from flagship.constants import ERROR_PARAM_TYPE
from flagship.errors import ParamTypeError


# def exception_handler(**params):
#     default = params['default'] if 'default' in params else None
#
#     def decorator_error(func):
#         def wrapper(*args, **kwargs):
#             try:
#                 return func(*args, **kwargs)
#             except Exception as e:
#                 tb = traceback.format_exc()
#                 flagship.new_exception(e, tb)
#         return wrapper
#
#     return decorator_error


def param_types_validator(self=False, *types):
    """

    @return: object
    @param self: Does the decorated method use self param.
    @param types: Decorated method param types list.
    """
    def decorator_typing(func):
        def wrapper(*args, **kwargs):
            for i in range(0 if self is False else 1, len(args)):
            # for i in range(0 if self is False else 1, len(args) - 1):
                j = i if self is False else i - 1
                raise_error = True
                ctype = types[j]
                if isinstance(ctype, list):
                    for t in ctype:
                        if isinstance(args[i], t):
                            raise_error = False
                elif isinstance(args[i], ctype):
                    raise_error = False
                if raise_error:
                    inspection_args = inspect.getargspec(func).args
                    method_name = func.__name__ if func.__name__ != '__init__' else args[0].__class__.__name__
                    e = ParamTypeError(ERROR_PARAM_TYPE.format(inspection_args[i], method_name, types[j]))
                    raise e
            return func(*args, **kwargs)

        return wrapper

    return decorator_typing
