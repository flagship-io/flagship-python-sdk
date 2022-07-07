from abc import ABCMeta, abstractmethod

from flagship import log, LogLevel
from flagship.constants import TAG_FLAG, ERROR_METHOD_DEACTIVATED_PANIC, \
    ERROR_FLAG_METHOD_DEACTIVATED, ERROR_METHOD_DEACTIVATED_NO_CONSENT, ERROR_METHOD_DEACTIVATED_NOT_READY
from flagship.flag_metadata import FlagMetadata


class IFlagStrategy:
    __metaclass__ = ABCMeta

    @abstractmethod
    def value(self, user_exposed=True):
        pass

    @abstractmethod
    def user_exposed(self):
        pass

    @abstractmethod
    def exists(self):
        pass

    @abstractmethod
    def metadata(self):
        pass


class Flag(IFlagStrategy):

    def __init__(self, visitor, key, default_value):
        self._visitor = visitor
        self.key = key
        self.default_value = default_value

    def value(self, user_exposed=True):
        self._get_flag_strategy().value()

    def user_exposed(self):
        self._get_flag_strategy().user_exposed()

    def exists(self):
        return self._get_flag_strategy().metadata().exists()

    def metadata(self):
        return self._get_flag_strategy().metadata()

    def _get_flag_strategy(self):
        from flagship.visitor_strategies import VisitorStrategies
        visitor_strategy = self._visitor._get_strategy()
        if visitor_strategy.strategy is VisitorStrategies.NOT_READY_STRATEGY:
            return _NotReadyStrategy(self)
        elif visitor_strategy.strategy is VisitorStrategies.PANIC_STRATEGY:
            return _PanicFlagStrategy(self)
        elif visitor_strategy.strategy is VisitorStrategies.NO_CONSENT_STRATEGY:
            return _NoConsentStrategy(self)
        else:
            return _DefaultFlagStrategy(self)


class _DefaultFlagStrategy(IFlagStrategy):

    def __init__(self, flag):
        self.flag = flag

    def value(self, user_exposed=True):
        value = self.flag._visitor._get_flag_value(self.flag.key, self.flag.default_value)
        if user_exposed:
            self.user_exposed()
        return value

    def user_exposed(self):
        self.flag._visitor._expose_flag(self.flag.key)

    def exists(self):
        return self.metadata().exists()

    def metadata(self):
        return FlagMetadata(self.flag._visitor._get_modification(self.flag.key))


class _PanicFlagStrategy(_DefaultFlagStrategy):

    def __init__(self, flag):
        super(_PanicFlagStrategy, self).__init__(flag)

    def value(self, user_exposed=True):
        log(TAG_FLAG, LogLevel.ERROR,
            ERROR_FLAG_METHOD_DEACTIVATED.format(self.flag.key, "value()", ERROR_METHOD_DEACTIVATED_PANIC))
        return self.flag.default_value

    def user_exposed(self):
        log(TAG_FLAG, LogLevel.ERROR,
            ERROR_FLAG_METHOD_DEACTIVATED.format(self.flag.key, "user_exposed()", ERROR_METHOD_DEACTIVATED_PANIC))

    def exists(self):
        log(TAG_FLAG, LogLevel.ERROR,
            ERROR_FLAG_METHOD_DEACTIVATED.format(self.flag.key, "exists()", ERROR_METHOD_DEACTIVATED_PANIC))
        return False

    def metadata(self):
        log(TAG_FLAG, LogLevel.ERROR,
            ERROR_FLAG_METHOD_DEACTIVATED.format(self.flag.key, "metadata()", ERROR_METHOD_DEACTIVATED_PANIC))
        return FlagMetadata(None)


class _NoConsentStrategy(_DefaultFlagStrategy):

    def __init__(self, flag):
        super(_NoConsentStrategy, self).__init__(flag)
        self.flag = flag

    def value(self, user_exposed=True):
        value = self.flag._visitor._get_flag_value(self.flag.key, self.flag.default_value)
        if user_exposed:
            self.user_exposed()
        return value

    def user_exposed(self):
        log(TAG_FLAG, LogLevel.ERROR,
            ERROR_FLAG_METHOD_DEACTIVATED.format(self.flag.key, "user_exposed()", ERROR_METHOD_DEACTIVATED_NO_CONSENT
                                                 .format(self.flag._visitor._visitor_id)))


class _NotReadyStrategy(_DefaultFlagStrategy):

    def __init__(self, flag):
        super(_NotReadyStrategy, self).__init__(flag)
        self.flag = flag

    def value(self, user_exposed=True):
        log(TAG_FLAG, LogLevel.ERROR,
            ERROR_FLAG_METHOD_DEACTIVATED.format(self.flag.key, "value()", ERROR_METHOD_DEACTIVATED_NOT_READY))
        return self.flag.default_value

    def user_exposed(self):
        log(TAG_FLAG, LogLevel.ERROR,
            ERROR_FLAG_METHOD_DEACTIVATED.format(self.flag.key, "user_exposed()", ERROR_METHOD_DEACTIVATED_NOT_READY))

    def exists(self):
        log(TAG_FLAG, LogLevel.ERROR,
            ERROR_FLAG_METHOD_DEACTIVATED.format(self.flag.key, "exists()", ERROR_METHOD_DEACTIVATED_NOT_READY))
        return False

    def metadata(self):
        log(TAG_FLAG, LogLevel.ERROR,
            ERROR_FLAG_METHOD_DEACTIVATED.format(self.flag.key, "metadata()", ERROR_METHOD_DEACTIVATED_NOT_READY))
        return FlagMetadata(None)


