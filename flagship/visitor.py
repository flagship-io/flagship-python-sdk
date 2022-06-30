

from enum import Enum

from flagship import param_types_validator, LogLevel
from flagship.constants import _TAG_VISITOR, _TAG_UPDATE_CONTEXT, _DEBUG_CONTEXT, _TAG_FETCH_FLAGS, _DEBUG_FETCH_FLAGS
from flagship.flag import Flag
from flagship.utils import log, pretty_dict


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

    def __get_arg(self, kwargs, name, c_type, default, ):
        return kwargs[name] if name in kwargs and isinstance(kwargs[name], c_type) else default

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
        log(_TAG_UPDATE_CONTEXT, LogLevel.DEBUG, "[" + _TAG_VISITOR.format(self.visitor_id) + "] " +
            _DEBUG_CONTEXT.format(self.__str__()))

    def __str__(self):
        return pretty_dict({
            "visitor": {
                "visitor_id": self.visitor_id,
                "anonymous_id": self.anonymous_id,
                "has_consented": self.has_consented,
                "is_authenticated": self.is_authenticated,
                "context": self.context,
                "flags": self.__flags_to_dict()
            }})

    def __flags_to_dict(self):
        flags = dict()
        for k, v in self.modifications.items():
            flags[k] = v.value
        return flags


    def fetch_flags(self):
        decision_manager = self.configuration_manager.decision_manager
        if decision_manager is not None:
            modifications = decision_manager.get_campaigns_modifications(self)
            self.modifications.update(modifications)
            log(_TAG_FETCH_FLAGS, LogLevel.DEBUG, "[" + _TAG_VISITOR.format(self.visitor_id) + "] " +
                _DEBUG_FETCH_FLAGS.format(self.__str__()))


    def get_flag(self, key, default):
        return Flag(self, key, default)


