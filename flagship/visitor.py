import logging
from datetime import datetime

from flagship.config import Config
from flagship.decorators import exception_handler, types_validator
from flagship.helpers.api import APIClient
from flagship.helpers.hits import Hit


class FlagshipVisitor:

    # __config = None  # type: Config

    def __init__(self, config, visitor_id, context):
        # type: (Config, str, dict) -> None
        # FlagshipVisitor.__config = config
        self._config = config
        self._env_id = config.env_id
        self._api_key = config.api_key
        self._visitor_id = visitor_id
        self._context = dict()
        self.update_context(context)
        self._last_call = datetime.now()
        self._api_client = APIClient(config)
        self.campaigns = list()
        self._modifications = dict()

    # def __getattribute__(self, name):
    #     if name != '_last_call':
    #         self._last_call = datetime.now()
    #     return super(self).__getattribute__(name)

    @exception_handler()
    @types_validator(True, Hit)
    def send_hit(self, hit):
        if issubclass(type(hit), Hit):
            self._api_client.send_hit_request(self._visitor_id, hit)
        else:
            self._config.event_handler.on_log(logging.ERROR, "[send_hit] : {} not a Hit subclass.".format(str(hit)))

    @exception_handler()
    @types_validator(True)
    def synchronize_modifications(self):
        self.campaigns = self._api_client.synchronize_modifications(self._visitor_id, self._context)
        for campaign in self.campaigns:
            self._modifications.update(campaign.get_modifications())
        self._config.event_handler.on_log(logging.DEBUG,
                                          "[synchronize_modifications] : Visitor '{} Campaigns = {}"
                                          .format(self._visitor_id, self.__campaigns_to_str()))

    def __campaigns_to_str(self):
        result = '\n     '
        for c in self.campaigns:
            result += (str(c) + '\n     ')
        return result

    @exception_handler()
    @types_validator(True, str)
    def activate_modification(self, key):
        if key in self._modifications:
            modification = self._modifications[key]
            self._api_client.activate_modification(self._visitor_id, modification.variation_group_id,
                                                   modification.variation_id)
        else:
            self._config.event_handler.on_log(logging.ERROR,
                                              "[activate_modification] : no modification for the key '{}'."
                                              .format(key))

    @exception_handler()
    @types_validator(True, str, [str, bool, int, float], bool)
    def get_modification(self, key, default_value, activate=False):
        if key not in self._modifications:
            self._config.event_handler.on_log(logging.ERROR,
                                              "[get_modification] : no modification for the key '{}', default value "
                                              "returned."
                                              .format(key))
            return default_value
        elif self._modifications[key].value is None:
            if activate:
                self.activate_modification(key)
            return default_value
        else:
            if activate:
                self.activate_modification(key)
            return self._modifications[key].value

    @exception_handler()
    @types_validator(True, str)
    def get_modification_data(self, key):
        if key not in self._modifications:
            return None
        return self._modifications[key]

    def __update_context_value(self, key, value, synchronize=False):
        t = type(value)
        if type(key) is not str:
            self._config.event_handler.on_log(logging.ERROR, "[update_context] : key '{}' must be a str.".format(key))
        elif t is not str and t is not int and t is not bool and t is not float:
            self._config.event_handler.on_log(logging.ERROR, "[update_context] : value '{}' must be one of "
                                                             "the following types: str, int, bool, float.".format(key))
        else:
            self._context[key] = value
        if synchronize is True:
            self.synchronize_modifications()

    @exception_handler()
    @types_validator(True, [dict, tuple], bool)
    def update_context(self, context, synchronize=False):
        if isinstance(context, tuple) and len(context) == 2:
            self.__update_context_value(context[0], context[1])
        elif isinstance(context, dict):
            for (k, v) in context.items():
                self.__update_context_value(k, v)
        self._config.event_handler.on_log(logging.DEBUG, "[update_context] : Visitor '{}' Context = {}."
                                          .format(self._visitor_id, self._context))
        if synchronize:
            self.synchronize_modifications()
        # if self._cache:
        #     self._cache.save(self._visitor_id, context)


    def close(self):
        pass
