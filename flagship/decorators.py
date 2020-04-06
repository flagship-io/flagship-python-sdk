import traceback

def exception_handler(default):
    def decorator_error(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                tb = traceback.format_exc()
                print('Error ' + tb)
                return default
        return wrapper
    return decorator_error
