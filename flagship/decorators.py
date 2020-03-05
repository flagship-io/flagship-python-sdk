

def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # replace print with proper logger
            print("error : ", e)
            return None
    return wrapper
