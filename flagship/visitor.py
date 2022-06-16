import json

from enum import Enum

from flagship import param_types_validator, LogLevel
from flagship.constants import _TAG_VISITOR, _TAG_UPDATE_CONTEXT, _DEBUG_CONTEXT
from flagship.utils import log


class Visitor:
    class Instance(Enum):
        SINGLE_INSTANCE = "SINGLE_INSTANCE",
        NEW_INSTANCE = "NEW_INSTANCE"

    def __init__(self, configuration_manager, visitor_id, **kwargs):
        self.configuration_manager = configuration_manager
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
        print("k: " + str(key) + " / v:" + str(value))

    @param_types_validator(True, [dict, tuple])
    def update_context(self, context):
        if isinstance(context, tuple) and len(context) == 2:
            self.__update_context(context[0], context[1])
        elif isinstance(context, dict):
            for k, v in context.items():
                self.__update_context(k, v)
        log(_TAG_VISITOR.format(self.visitor_id) + _TAG_UPDATE_CONTEXT, LogLevel.DEBUG,
            _DEBUG_CONTEXT.format(self.__str__()))

    def __str__(self):
        visitor_str = "{\n"
        visitor_str += " \"visitor_id\": \"{}\",\n".format(self.visitor_id)
        visitor_str += " \"anonymous_id\": \"{}\",\n".format(self.anonymous_id)
        visitor_str += " \"has_consented\": {},\n".format(self.has_consented)
        visitor_str += " \"is_authenticated\": {},\n".format(self.is_authenticated)
        visitor_str += " \"context\": {}".format(self.context)
        visitor_str += "\n}"
        return visitor_str
