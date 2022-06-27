

from enum import Enum

from flagship import param_types_validator, LogLevel
from flagship.constants import _TAG_VISITOR, _TAG_UPDATE_CONTEXT, _DEBUG_CONTEXT
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
                "context": self.context
            }})

    def fetch_flags(self):
        decision_manager = self.configuration_manager.decision_manager
        if decision_manager is not None:
            is_success, modifications = decision_manager.get_campaigns_modifications(self)
            print(">> is_success: " + str(is_success))
            print(">> modifications: " + str(modifications))
            # if is_success:
            #     self.__update_modifications(modifications)
