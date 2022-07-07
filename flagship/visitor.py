import traceback

from enum import Enum
from flagship import param_types_validator, Status
from flagship.constants import TAG_GET_FLAG, TAG_FLAG_USER_EXPOSITION
from flagship.errors import FlagNotFoundException, FlagExpositionNotFoundException
from flagship.hits import _Activate
from flagship.http_helper import HttpHelper
from flagship.utils import pretty_dict, log_exception
from flagship.visitor_strategies import IVisitorStrategy, PanicStrategy, DefaultStrategy, NoConsentStrategy, \
    NotReadyStrategy


class Visitor(IVisitorStrategy):

    class Instance(Enum):
        SINGLE_INSTANCE = "SINGLE_INSTANCE",
        NEW_INSTANCE = "NEW_INSTANCE"

    def __init__(self, configuration_manager, visitor_id, **kwargs):
        super(Visitor, self).__init__(self)
        self._configuration_manager = configuration_manager
        self._config = configuration_manager.flagship_config
        self._visitor_id = visitor_id
        self._anonymous_id = None
        self._is_authenticated = self.__get_arg(kwargs, 'authenticated', bool, False)
        self._context = self.__get_arg(kwargs, 'context', dict, {})
        self._modifications = dict()
        self._has_consented = self.__get_arg(kwargs, 'consent', bool, True)
        self._get_strategy().set_consent(self._has_consented)

    @param_types_validator(True, str, [int, float, str])
    def _update_context(self, key, value):
        self._context[key] = value

    def _expose_flag(self, key):
        try:
            modification = self._get_modification(key)
            if modification is None:
                raise FlagExpositionNotFoundException(self._visitor_id, key)
            HttpHelper.send_hit(self, _Activate(modification.variation_group_id, modification.variation_id))
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

    def __str__(self):
        return pretty_dict({
            "visitor_id": self._visitor_id,
            "anonymous_id": self._anonymous_id,
            "has_consented": self._has_consented,
            "is_authenticated": self._is_authenticated,
            "context": self._context,
            "flags": self.__flags_to_dict()
        })

    def __get_arg(self, kwargs, name, c_type, default, ):
        return kwargs[name] if name in kwargs and isinstance(kwargs[name], c_type) else default

    def __flags_to_dict(self):
        flags = dict()
        for k, v in self._modifications.items():
            flags[k] = v.value
        return flags

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


