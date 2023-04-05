from flagship.constants import ERROR_INITIALIZATION_PARAM, ERROR_CACHE_HIT_TIMEOUT, ERROR_CACHE_HIT_LOOKUP_FORMAT


class FlagshipException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)


class InitializationParamError(FlagshipException):
    def __init__(self):
        super(FlagshipException, self).__init__('[Initialization Param Error] ' + ERROR_INITIALIZATION_PARAM)


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

class FlagTypeException(Exception):
    def __init__(self, visitor_id, flag_key):
        from flagship.constants import ERROR_FLAG_TYPE_DIFFERENT
        super(Exception, self).__init__('[FlagTypeError] ' + ERROR_FLAG_TYPE_DIFFERENT.format(flag_key, visitor_id))

class FlagExpositionNotFoundException(Exception):
    def __init__(self, visitor_id, flag_key):
        from flagship.constants import ERROR_FLAG_EXPOSITION_FLAG_NOT_FOUND
        super(Exception, self).__init__(
            '[FlagNotFoundError] ' + ERROR_FLAG_EXPOSITION_FLAG_NOT_FOUND.format(flag_key, visitor_id))


class VisitorCacheFormatException(Exception):
    def __init__(self, visitor_id):
        from flagship.constants import ERROR_CACHE_VISITOR_LOOKUP_FORMAT
        super(VisitorCacheFormatException, self).__init__('[VisitorCacheFormatError] ' +
                                                          ERROR_CACHE_VISITOR_LOOKUP_FORMAT.format(visitor_id))


class HitCacheFormatException(Exception):
    def __init__(self, hit_id):
        from flagship.constants import ERROR_CACHE_VISITOR_LOOKUP_FORMAT
        super().__init__('[HitCacheFormatError] ' + ERROR_CACHE_HIT_LOOKUP_FORMAT.format(hit_id))


class VisitorCacheTimeoutException(Exception):
    def __init__(self, method_name, visitor_id):
        from flagship.constants import ERROR_CACHE_VISITOR_LOOKUP_TIMEOUT
        super(VisitorCacheTimeoutException, self).__init__(
            '[VisitorCacheTimeoutError] ' + ERROR_CACHE_VISITOR_LOOKUP_TIMEOUT.format(method_name, visitor_id))

class HitCacheTimeoutException(Exception):
    def __init__(self, method_name):
        from flagship.constants import ERROR_CACHE_VISITOR_LOOKUP_TIMEOUT
        super().__init__('[HitCacheTimeoutError] ' + ERROR_CACHE_HIT_TIMEOUT.format(method_name))
