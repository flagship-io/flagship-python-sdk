from abc import ABCMeta, abstractmethod
from enum import Enum
from flagship import param_types_validator, log, LogLevel
from flagship.constants import TAG_UPDATE_CONTEXT, TAG_VISITOR, DEBUG_CONTEXT, TAG_FETCH_FLAGS, DEBUG_FETCH_FLAGS, \
    ERROR_METHOD_DEACTIVATED, ERROR_METHOD_DEACTIVATED_PANIC, TAG_TRACKING, ERROR_METHOD_DEACTIVATED_NO_CONSENT, \
    ERROR_METHOD_DEACTIVATED_NOT_READY, TAG_AUTHENTICATE, TAG_UNAUTHENTICATE, ERROR_TRACKING_HIT_SUBCLASS
from flagship.flag import Flag
from flagship.hits import Hit, _Consent, _Activate
from flagship.http_helper import HttpHelper


class VisitorStrategies(Enum):
    DEFAULT_STRATEGY = 'DEFAULT_STRATEGY'
    PANIC_STRATEGY = 'PANIC_STRATEGY'
    NO_CONSENT_STRATEGY = 'NO_CONSENT_STRATEGY'
    NOT_READY_STRATEGY = "NOT_READY_STRATEGY"


class IVisitorStrategy:
    __metaclass__ = ABCMeta

    def __init__(self, strategy=VisitorStrategies.DEFAULT_STRATEGY, visitor=None):
        self.strategy = strategy
        self.visitor = visitor

    @abstractmethod
    @param_types_validator(True, [dict, tuple])
    def update_context(self, context):
        pass

    @abstractmethod
    def fetch_flags(self):
        pass

    @abstractmethod
    @param_types_validator(True, [str, str])
    def get_flag(self, key, default):
        pass

    @abstractmethod
    @param_types_validator(True, Hit)
    def send_hit(self, hit):
        pass

    @abstractmethod
    @param_types_validator(True, bool)
    def set_consent(self, consent):
        pass

    @abstractmethod
    @param_types_validator(True, str)
    def authenticate(self, visitorId):
        pass

    @abstractmethod
    @param_types_validator(True)
    def unauthenticate(self):
        pass

class DefaultStrategy(IVisitorStrategy):

    def __init__(self, strategy=VisitorStrategies.DEFAULT_STRATEGY, visitor=None):
        super(DefaultStrategy, self).__init__(strategy, visitor)

    def update_context(self, context):
        if isinstance(context, tuple) and len(context) == 2:
            self.visitor._update_context(context[0], context[1])
        elif isinstance(context, dict):
            for k, v in context.items():
                self.visitor._update_context(k, v)
        log(TAG_UPDATE_CONTEXT, LogLevel.DEBUG, "[" + TAG_VISITOR.format(self.visitor._visitor_id) + "] " +
            DEBUG_CONTEXT.format(self.visitor.__str__()))

    def fetch_flags(self):
        decision_manager = self.visitor._configuration_manager.decision_manager
        if decision_manager is not None:
            result, modifications = decision_manager.get_campaigns_modifications(self.visitor)
            from flagship import Status
            from flagship import Flagship
            if result is True and Flagship.status() is not Status.PANIC:
                self.visitor._modifications.update(modifications)
                log(TAG_FETCH_FLAGS, LogLevel.DEBUG, "[" + TAG_VISITOR.format(self.visitor._visitor_id) + "] " +
                    DEBUG_FETCH_FLAGS.format(self.visitor.__str__()))

    def get_flag(self, key, default):
        return Flag(self.visitor, key, default)

    # @param_types_validator(True, Hit)
    def send_hit(self, hit):
        if issubclass(type(hit), Hit):
            hit._with_visitor_ids(self.visitor._visitor_id, self.visitor._anonymous_id)
            tracking_manager = self.visitor._configuration_manager.tracking_manager
            tracking_manager.add_hit(hit)
            #HttpHelper.send_hit(self.visitor, hit)
        else:
            log(TAG_TRACKING, LogLevel.ERROR, ERROR_TRACKING_HIT_SUBCLASS)


    def set_consent(self, consent):
        self.visitor._has_consented = consent
        # HttpHelper.send_hit(self.visitor, _Consent(consent))
        self.send_hit(_Consent(consent))

    def authenticate(self, visitor_id):
        self.visitor._configuration_manager.decision_manager.authenticate(self.visitor, visitor_id)

    def unauthenticate(self):
        self.visitor._configuration_manager.decision_manager.unauthenticate(self.visitor)


class PanicStrategy(DefaultStrategy):

    def __init__(self, strategy=VisitorStrategies.PANIC_STRATEGY, visitor=None):
        super(DefaultStrategy, self).__init__(strategy, visitor)

    def update_context(self, context):
        log(TAG_UPDATE_CONTEXT, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("update_context()", ERROR_METHOD_DEACTIVATED_PANIC))
        return False, dict()

    def fetch_flags(self):
        super(PanicStrategy, self).fetch_flags()

    def get_flag(self, key, default):
        return super(PanicStrategy, self).get_flag(key, default)

    def send_hit(self, hit):
        log(TAG_TRACKING, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("send_hit()", ERROR_METHOD_DEACTIVATED_PANIC))

    def set_consent(self, consent):
        self.visitor._has_consented = consent

    def authenticate(self, visitor_id):
        log(TAG_AUTHENTICATE, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("authenticate()", ERROR_METHOD_DEACTIVATED_PANIC))

    def unauthenticate(self):
        log(TAG_UNAUTHENTICATE, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("unauthenticate()", ERROR_METHOD_DEACTIVATED_PANIC))


class NoConsentStrategy(DefaultStrategy):

    def __init__(self, strategy=VisitorStrategies.NO_CONSENT_STRATEGY, visitor=None):
        super(NoConsentStrategy, self).__init__(strategy, visitor)

    def send_hit(self, hit):
        log(TAG_TRACKING, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("send_hit()", ERROR_METHOD_DEACTIVATED_NO_CONSENT
                                            .format(self.visitor._visitor_id)))


class NotReadyStrategy(DefaultStrategy):

    def __init__(self, strategy=VisitorStrategies.NOT_READY_STRATEGY, visitor=None):
        super(NotReadyStrategy, self).__init__(strategy, visitor)

    def get_flag(self, key, default):
        log(TAG_TRACKING, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("get_flag()", ERROR_METHOD_DEACTIVATED_NOT_READY
                                            .format(self.visitor._visitor_id)))
        return super(NotReadyStrategy, self).get_flag(key, default)

    def send_hit(self, hit):
        log(TAG_TRACKING, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("send_hit()", ERROR_METHOD_DEACTIVATED_NOT_READY
                                            .format(self.visitor._visitor_id)))

    def update_context(self, context):
        log(TAG_TRACKING, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("update_context()", ERROR_METHOD_DEACTIVATED_NOT_READY
                                            .format(self.visitor._visitor_id)))

    def fetch_flags(self):
        log(TAG_TRACKING, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("fetch_flags()", ERROR_METHOD_DEACTIVATED_NOT_READY
                                            .format(self.visitor._visitor_id)))

    def set_consent(self, consent):
        log(TAG_TRACKING, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("set_consent()", ERROR_METHOD_DEACTIVATED_NOT_READY
                                            .format(self.visitor._visitor_id)))

    def authenticate(self, visitor_id):
        log(TAG_TRACKING, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("authenticate()", ERROR_METHOD_DEACTIVATED_NOT_READY
                                            .format(self.visitor._visitor_id)))

    def unauthenticate(self):
        log(TAG_TRACKING, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("unauthenticate()", ERROR_METHOD_DEACTIVATED_NOT_READY
                                            .format(self.visitor._visitor_id)))

