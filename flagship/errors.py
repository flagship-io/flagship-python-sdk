class FlagshipErrorHandler:
    def __init__(self):
        pass

    def new_error_raised(self, exception, traceback):
        pass


class FlagshipError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)


class FlagshipParsingError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__('[FlagshipParsingError] ' + message)


class ContextError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)


class TypingError(TypeError):
    def __init__(self, message):
        super(TypeError, self).__init__(message)

# class DecisionAPIError(Exception):
#     def __init__(self, message, errors):
#
#         # Call the base class constructor with the parameters it needs
#         super().__init__(message)
#
#         # Now for your custom code...
#         self.errors = errors
