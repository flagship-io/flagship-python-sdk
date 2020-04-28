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


class ParamError(ValueError):
    def __init__(self, message):
        super(ValueError, self).__init__(message)


class InitializationError(Exception):
    def __init__(self, message):
        # type: (str) -> None
        """
        Raised then the SDK has not been started successfully.
        :param message:
        """
        super(Exception, self).__init__(message)

# class DecisionAPIError(Exception):
#     def __init__(self, message, errors):
#
#         # Call the base class constructor with the parameters it needs
#         super().__init__(message)
#
#         # Now for your custom code...
#         self.errors = errors
