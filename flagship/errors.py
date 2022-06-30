class FlagshipException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)


class ParamTypeError(FlagshipException):
    def __init__(self, message):
        super(FlagshipException, self).__init__(message)

class FlagshipParsingError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__('[Parsing Error] ' + message)
