class FlagshipException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)


class ParamTypeError(FlagshipException):
    def __init__(self, message):
        super(FlagshipException, self).__init__(message)


class FlagshipParsingError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__('[ParsingError] ' + message)


class FlagNotFoundException(Exception):
    def __init__(self, visitor_id, flag_key):
        from flagship.constants import ERROR_FLAG_NOT_FOUND
        super(Exception, self).__init__('[FlagNotFoundError] ' + ERROR_FLAG_NOT_FOUND.format(flag_key, visitor_id))


class FlagExpositionNotFoundException(Exception):
    def __init__(self, visitor_id, flag_key):
        from flagship.constants import ERROR_FLAG_EXPOSITION_FLAG_NOT_FOUND
        super(Exception, self).__init__(
            '[FlagNotFoundError] ' + ERROR_FLAG_EXPOSITION_FLAG_NOT_FOUND.format(flag_key, visitor_id))
