import asyncio
import sys
import traceback
from abc import ABCMeta, abstractmethod
from enum import Enum

from flagship import param_types_validator, log, LogLevel
from flagship.cache_manager import VisitorCacheImplementation
from flagship.constants import TAG_UPDATE_CONTEXT, TAG_VISITOR, DEBUG_CONTEXT, TAG_FETCH_FLAGS, DEBUG_FETCH_FLAGS, \
    ERROR_METHOD_DEACTIVATED, ERROR_METHOD_DEACTIVATED_PANIC, TAG_TRACKING, ERROR_METHOD_DEACTIVATED_NO_CONSENT, \
    ERROR_METHOD_DEACTIVATED_NOT_READY, TAG_AUTHENTICATE, TAG_UNAUTHENTICATE, ERROR_TRACKING_HIT_SUBCLASS, \
    TAG_CACHE_MANAGER
from flagship.errors import VisitorCacheTimeoutException
from flagship.flag import Flag
from flagship.hits import Hit, _Consent, _Activate
from flagship.utils import log_exception


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

    @abstractmethod
    def cache_visitor(self):
        pass

    @abstractmethod
    def lookup_visitor(self):
        pass

    @abstractmethod
    def flush_visitor(self):
        pass

    @abstractmethod
    def flush_hits(self):
        pass


class DefaultStrategy(IVisitorStrategy):

    def __init__(self, strategy=VisitorStrategies.DEFAULT_STRATEGY, visitor=None):
        super(DefaultStrategy, self).__init__(strategy, visitor)
        cache_manager = self.visitor._configuration_manager.cache_manager
        self.visitor_cache_interface = cache_manager \
            if cache_manager is not None and isinstance(cache_manager, VisitorCacheImplementation) \
            else None
        self.timeout = cache_manager.timeout if cache_manager is not None else 0.1

    def update_context(self, context):
        if isinstance(context, tuple) and len(context) == 2:
            self.visitor._update_context(context[0], context[1])
        elif isinstance(context, dict):
            for k, v in context.items():
                self.visitor._update_context(k, v)
        # log(TAG_UPDATE_CONTEXT, LogLevel.DEBUG, "[" + TAG_VISITOR.format(self.visitor.visitor_id) + "] " +
        #     DEBUG_CONTEXT.format(self.visitor.__str__()))

    def fetch_flags(self):
        decision_manager = self.visitor._configuration_manager.decision_manager
        if decision_manager is not None:
            result, modifications = decision_manager.get_campaigns_modifications(self.visitor)
            from flagship import Status
            from flagship import Flagship
            if result is True and Flagship.status() is not Status.PANIC:
                self.visitor._modifications.clear()
                self.visitor._modifications.update(modifications)
                for k, v in modifications.items():
                    self.visitor.assignations[v.variation_group_id] = v.variation_id
                log(TAG_FETCH_FLAGS, LogLevel.DEBUG, "[" + TAG_VISITOR.format(self.visitor.visitor_id) + "] " +
                    DEBUG_FETCH_FLAGS.format(self.visitor.__str__()))
                self.visitor.cache_visitor()

    def get_flag(self, key, default):
        return Flag(self.visitor, key, default)

    # @param_types_validator(True, Hit)
    def send_hit(self, hit):
        if issubclass(type(hit), Hit):
            if not isinstance(hit, _Activate):
                hit._with_visitor_ids(self.visitor.visitor_id, self.visitor.anonymous_id)
            tracking_manager = self.visitor._configuration_manager.tracking_manager
            tracking_manager.add_hit(hit)
        else:
            log(TAG_TRACKING, LogLevel.ERROR, ERROR_TRACKING_HIT_SUBCLASS)

    def set_consent(self, consent):
        self.visitor.has_consented = consent
        self.send_hit(_Consent(consent))

    def authenticate(self, visitor_id):
        self.visitor._configuration_manager.decision_manager.authenticate(self.visitor, visitor_id)

    def unauthenticate(self):
        self.visitor._configuration_manager.decision_manager.unauthenticate(self.visitor)

    def cache_visitor(self):
        try:
            if self.visitor_cache_interface is not None:
                from flagship.cache_helper import visitor_to_cache_json
                asyncio.run(self.visitor_cache_interface.cache_visitor(self.visitor.visitor_id, visitor_to_cache_json(self.visitor)))
        except Exception as e:
            if sys.version_info[0] < 3.8:
                if isinstance(e, asyncio.TimeoutError):
                    log(TAG_CACHE_MANAGER, LogLevel.ERROR,
                        str(VisitorCacheTimeoutException("cache_visitor()", self.visitor.visitor_id)))
                else:
                    log(TAG_CACHE_MANAGER, LogLevel.ERROR, str(e))
            else:
                if isinstance(e, asyncio.exceptions.TimeoutError):
                    log(TAG_CACHE_MANAGER, LogLevel.ERROR,
                        str(VisitorCacheTimeoutException("cache_visitor()", self.visitor.visitor_id)))
                else:
                    log(TAG_CACHE_MANAGER, LogLevel.ERROR, str(e))

    def lookup_visitor(self):
        try:
            if self.visitor_cache_interface is not None:
                from flagship.cache_helper import load_visitor_from_json
                visitor_data = asyncio.run(
                    asyncio.wait_for(self.visitor_cache_interface.lookup_visitor(self.visitor.visitor_id),
                                     timeout=self.timeout))
                # self.visitor_cache_interface.lookup_visitor(self.visitor.visitor_id))
                if visitor_data:
                    load_visitor_from_json(self.visitor, visitor_data)
        except Exception as e:
            if sys.version_info[0] < 3.8:
                if isinstance(e, asyncio.TimeoutError):
                    log(TAG_CACHE_MANAGER, LogLevel.ERROR,
                        str(VisitorCacheTimeoutException("lookup_visitor()", self.visitor.visitor_id)))
                else:
                    log(TAG_CACHE_MANAGER, LogLevel.ERROR, str(e))
            else:
                if isinstance(e, asyncio.exceptions.TimeoutError):
                    log(TAG_CACHE_MANAGER, LogLevel.ERROR,
                        str(VisitorCacheTimeoutException("lookup_visitor()", self.visitor.visitor_id)))
                else:
                    log(TAG_CACHE_MANAGER, LogLevel.ERROR, str(e))

    def flush_visitor(self):
        try:
            if self.visitor_cache_interface is not None:
                asyncio.run(self.visitor_cache_interface.flush_visitor(self.visitor.visitor_id))
        except Exception as e:
            if sys.version_info[0] < 3.8:
                if isinstance(e, asyncio.TimeoutError):
                    log(TAG_CACHE_MANAGER, LogLevel.ERROR,
                        str(VisitorCacheTimeoutException("flush_visitor()", self.visitor.visitor_id)))
                else:
                    log(TAG_CACHE_MANAGER, LogLevel.ERROR, str(e))
            else:
                if isinstance(e, asyncio.exceptions.TimeoutError):
                    log(TAG_CACHE_MANAGER, LogLevel.ERROR,
                        str(VisitorCacheTimeoutException("flush_visitor()", self.visitor.visitor_id)))
                else:
                    log(TAG_CACHE_MANAGER, LogLevel.ERROR, str(e))

    def flush_hits(self):
        try:
            tracking_manager = self.visitor._configuration_manager.tracking_manager
            tracking_manager.delete_hits_by_visitor_id(self.visitor.visitor_id, False)
        except Exception as e:
            log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())


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
        self.visitor.has_consented = consent

    def authenticate(self, visitor_id):
        log(TAG_AUTHENTICATE, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("authenticate()", ERROR_METHOD_DEACTIVATED_PANIC))

    def unauthenticate(self):
        log(TAG_UNAUTHENTICATE, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("unauthenticate()", ERROR_METHOD_DEACTIVATED_PANIC))

    def cache_visitor(self):
        pass  # do nothing

    def lookup_visitor(self):
        pass  # do nothing

    def flush_visitor(self):
        pass  # do nothing

    def flush_hits(self):
        pass  # do nothing


class NoConsentStrategy(DefaultStrategy):

    def __init__(self, strategy=VisitorStrategies.NO_CONSENT_STRATEGY, visitor=None):
        super(NoConsentStrategy, self).__init__(strategy, visitor)

    def send_hit(self, hit):
        if isinstance(hit, _Consent):
            return super(NoConsentStrategy, self).send_hit(hit)
        else:
            log(TAG_TRACKING, LogLevel.ERROR, ERROR_METHOD_DEACTIVATED.format("send_hit()", (
                    ERROR_METHOD_DEACTIVATED_NO_CONSENT + "\n {}").format(self.visitor.visitor_id, str(hit))))

    def cache_visitor(self):
        pass  # do nothing

    def lookup_visitor(self):
        pass  # do nothing


class NotReadyStrategy(DefaultStrategy):

    def __init__(self, strategy=VisitorStrategies.NOT_READY_STRATEGY, visitor=None):
        super(NotReadyStrategy, self).__init__(strategy, visitor)

    def get_flag(self, key, default):
        log(TAG_TRACKING, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("get_flag()", ERROR_METHOD_DEACTIVATED_NOT_READY
                                            .format(self.visitor.visitor_id)))
        return super(NotReadyStrategy, self).get_flag(key, default)

    def send_hit(self, hit):
        log(TAG_TRACKING, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("send_hit()", ERROR_METHOD_DEACTIVATED_NOT_READY
                                            .format(self.visitor.visitor_id)))

    def     update_context(self, context):
        log(TAG_TRACKING, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("update_context()", ERROR_METHOD_DEACTIVATED_NOT_READY
                                            .format(self.visitor.visitor_id)))

    def fetch_flags(self):
        log(TAG_TRACKING, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("fetch_flags()", ERROR_METHOD_DEACTIVATED_NOT_READY
                                            .format(self.visitor.visitor_id)))

    def set_consent(self, consent):
        log(TAG_TRACKING, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("set_consent()", ERROR_METHOD_DEACTIVATED_NOT_READY
                                            .format(self.visitor.visitor_id)))

    def authenticate(self, visitor_id):
        log(TAG_TRACKING, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("authenticate()", ERROR_METHOD_DEACTIVATED_NOT_READY
                                            .format(self.visitor.visitor_id)))

    def unauthenticate(self):
        log(TAG_TRACKING, LogLevel.ERROR,
            ERROR_METHOD_DEACTIVATED.format("unauthenticate()", ERROR_METHOD_DEACTIVATED_NOT_READY
                                            .format(self.visitor.visitor_id)))

    def cache_visitor(self):
        pass  # do nothing

    def flush_visitor(self):
        pass  # do nothing

    def flush_hits(self):
        pass  # do nothing
