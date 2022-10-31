import traceback
import uuid

from enum import Enum
from flagship import param_types_validator, Status, LogLevel
from flagship.constants import TAG_GET_FLAG, TAG_FLAG_USER_EXPOSITION, TAG_UPDATE_CONTEXT, TAG_VISITOR, \
    ERROR_UPDATE_CONTEXT_TYPE, ERROR_UPDATE_CONTEXT_EMPTY_KEY
from flagship.errors import FlagNotFoundException, FlagExpositionNotFoundException, FlagTypeException
from flagship.hits import _Activate, _Segment
from flagship.http_helper import HttpHelper
from flagship.utils import pretty_dict, log_exception, log
from flagship.visitor_strategies import IVisitorStrategy, PanicStrategy, DefaultStrategy, NoConsentStrategy, \
    NotReadyStrategy


class Visitor(IVisitorStrategy):
    class Instance(Enum):
        """
        This class specifies how Flagship SDK should handle the newly created visitor instance.
        """

        SINGLE_INSTANCE = "SINGLE_INSTANCE",
        """
        The  newly created visitor instance will be returned and saved into the Flagship singleton.
        Call `Flagship.get_visitor()` to retrieve the instance.
        This option should be adopted on applications that handle only one visitor at the same time.
        """

        NEW_INSTANCE = "NEW_INSTANCE"
        """
        The newly created visitor instance wont be saved and will simply be returned. Any previous visitor instance will
        have to be recreated. This option should be adopted on applications that handle multiple visitors at the same 
        time.
        """

    def __init__(self, configuration_manager, visitor_id, **kwargs):
        super(Visitor, self).__init__(self)
        self._configuration_manager = configuration_manager
        self._config = configuration_manager.flagship_config
        self._is_authenticated = self._get_arg(kwargs, 'authenticated', bool, False)
        self._visitor_id = visitor_id
        self._anonymous_id = str(uuid.uuid4()) if self._is_authenticated is True else None
        from flagship.flagship_context import FlagshipContext
        self._context = FlagshipContext.load()
        self._modifications = dict()
        self._has_consented = self._get_arg(kwargs, 'consent', bool, True)
        self.set_consent(self._has_consented)
        self.update_context(self._get_arg(kwargs, 'context', dict, {}))

    # @param_types_validator(True, str, [int, float, str])
    def _update_context(self, key, value):
        from flagship.flagship_context import FlagshipContext
        existing_context = FlagshipContext.exists(key)
        if existing_context:
            if FlagshipContext.is_valid(self, existing_context, value, True):
                self._context[existing_context.value[0]] = value
        else:
            if key is None or len(str(key)) <= 0 or (not isinstance(key, str) and not isinstance(key, FlagshipContext)):
                log(TAG_UPDATE_CONTEXT, LogLevel.ERROR, "[" + TAG_VISITOR.format(self._visitor_id) + "] " +
                    ERROR_UPDATE_CONTEXT_EMPTY_KEY)
            elif not isinstance(value, str) and not isinstance(value, int) and not isinstance(value, float) \
                    and not isinstance(value, bool):
                log(TAG_UPDATE_CONTEXT, LogLevel.ERROR, "[" + TAG_VISITOR.format(self._visitor_id) + "] " +
                    ERROR_UPDATE_CONTEXT_TYPE.format(key, "str, int, float, bool"))
            else:
                self._context[key] = value

    def _expose_flag(self, key):
        try:
            modification = self._get_modification(key)
            if modification is None:
                raise FlagExpositionNotFoundException(self._visitor_id, key)
            HttpHelper.send_activate(self, _Activate(modification.variation_group_id, modification.variation_id))
        except Exception as e:
            log_exception(TAG_FLAG_USER_EXPOSITION, e, traceback.format_exc())

    def _get_modification(self, key):
        if key not in self._modifications:
            return None
        return self._modifications[key]

    def _get_flag_value(self, key, default):
        try:
            modification = self._get_modification(key)
            if modification is None:
                raise FlagNotFoundException(self._visitor_id, key)
            if not isinstance(default, type(modification.value)):
                raise FlagTypeException(self._visitor_id, key)
            value = modification.value if modification is not None else default
            return value
        except Exception as e:
            log_exception(TAG_GET_FLAG, e, traceback.format_exc())
            return default

    def _get_strategy(self):
        import flagship
        if flagship.Flagship.status().value < Status.PANIC.value:
            return NotReadyStrategy(visitor=self)
        elif flagship.Flagship.status() == Status.PANIC:
            return PanicStrategy(visitor=self)
        elif self._has_consented is False:
            return NoConsentStrategy(visitor=self)
        else:
            return DefaultStrategy(visitor=self)

    # def _send_context_request(self):
    #     self._get_strategy().send_hit(_Segment(self._context))

    def __str__(self):
        return pretty_dict({
            "visitor_id": self._visitor_id,
            "anonymous_id": self._anonymous_id,
            "has_consented": self._has_consented,
            "is_authenticated": self._is_authenticated,
            "context": self._context,
            "flags": self._flags_to_dict()
        })

    def _get_arg(self, kwargs, name, c_type, default, ):
        return kwargs[name] if name in kwargs and isinstance(kwargs[name], c_type) else default

    def _flags_to_dict(self):
        flags = dict()
        for k, v in self._modifications.items():
            flags[k] = v.value
        return flags

    def add_new_assignment_to_history(self, variation_group_id, variation_id):
        pass

    #     Methods from Visitor Strategy

    def update_context(self, context):
        return self._get_strategy().update_context(context)

    def fetch_flags(self):
        return self._get_strategy().fetch_flags()

    def get_flag(self, key, default):
        return self._get_strategy().get_flag(key, default)

    def send_hit(self, hit):
        return self._get_strategy().send_hit(hit)

    def set_consent(self, consent):
        self._get_strategy().set_consent(consent)

    def authenticate(self, visitorId):
        self._get_strategy().authenticate(visitorId)

    def unauthenticate(self):
        self._get_strategy().unauthenticate()
