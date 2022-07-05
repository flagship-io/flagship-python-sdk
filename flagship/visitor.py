import traceback

from enum import Enum

from flagship import param_types_validator, LogLevel
from flagship.constants import TAG_VISITOR, TAG_UPDATE_CONTEXT, DEBUG_CONTEXT, TAG_FETCH_FLAGS, DEBUG_FETCH_FLAGS, \
    TAG_GET_FLAG, TAG_FLAG_USER_EXPOSITION
from flagship.errors import FlagNotFoundException, FlagExpositionNotFoundException
from flagship.flag import Flag
from flagship.hits import Hit, _Activate
from flagship.http_helper import HttpHelper
from flagship.utils import log, pretty_dict, log_exception


class Visitor:
    class Instance(Enum):
        SINGLE_INSTANCE = "SINGLE_INSTANCE",
        NEW_INSTANCE = "NEW_INSTANCE"

    def __init__(self, configuration_manager, visitor_id, **kwargs):
        self.configuration_manager = configuration_manager
        self.config = configuration_manager.flagship_config
        self.visitor_id = visitor_id
        self.anonymous_id = None
        self.is_authenticated = self.__get_arg(kwargs, 'authenticated', bool, False)
        self.has_consented = self.__get_arg(kwargs, 'consent', bool, True)
        self.context = self.__get_arg(kwargs, 'context', dict, {})
        self.modifications = dict()


    @param_types_validator(True, str, [int, float, str])
    def __update_context(self, key, value):
        self.context[key] = value

    @param_types_validator(True, [dict, tuple])
    def update_context(self, context):
        if isinstance(context, tuple) and len(context) == 2:
            self.__update_context(context[0], context[1])
        elif isinstance(context, dict):
            for k, v in context.items():
                self.__update_context(k, v)
        log(TAG_UPDATE_CONTEXT, LogLevel.DEBUG, "[" + TAG_VISITOR.format(self.visitor_id) + "] " +
            DEBUG_CONTEXT.format(self.__str__()))

    def fetch_flags(self):
        decision_manager = self.configuration_manager.decision_manager
        if decision_manager is not None:
            modifications = decision_manager.get_campaigns_modifications(self)
            self.modifications.update(modifications)
            log(TAG_FETCH_FLAGS, LogLevel.DEBUG, "[" + TAG_VISITOR.format(self.visitor_id) + "] " +
                DEBUG_FETCH_FLAGS.format(self.__str__()))

    def get_flag(self, key, default):
        return Flag(self, key, default)

    def expose_flag(self, key):
        try:
            modification = self._get_modification(key)
            if modification is None:
                raise FlagExpositionNotFoundException(self.visitor_id, key)
            HttpHelper.send_hit(self, _Activate(modification.variation_group_id, modification.variation_id))
        except Exception as e:
            log_exception(TAG_FLAG_USER_EXPOSITION, e, traceback.format_exc())

    @param_types_validator(True, Hit)
    def send_hit(self, hit):
        if issubclass(hit, Hit):
            HttpHelper.send_hit(self, hit)

    def _get_modification(self, key):
        if key not in self.modifications:
            return None
        return self.modifications[key]

    def _get_flag_value(self, key, default):
        try:
            modification = self._get_modification(key)
            if modification is None:
                raise FlagNotFoundException(self.visitor_id, key)
            value = modification.value if modification is not None else default
            return value
        except Exception as e:
            log_exception(TAG_GET_FLAG, e, traceback.format_exc())
            return default

    def __str__(self):
        return pretty_dict({
            "visitor_id": self.visitor_id,
            "anonymous_id": self.anonymous_id,
            "has_consented": self.has_consented,
            "is_authenticated": self.is_authenticated,
            "context": self.context,
            "flags": self.__flags_to_dict()
        })

    def __get_arg(self, kwargs, name, c_type, default, ):
        return kwargs[name] if name in kwargs and isinstance(kwargs[name], c_type) else default

    def __flags_to_dict(self):
        flags = dict()
        for k, v in self.modifications.items():
            flags[k] = v.value
        return flags


