import logging
from datetime import datetime

from flagship.config import Config
from flagship.decorators import exception_handler, types_validator
from flagship.helpers.api import APIClient
from flagship.helpers.hits import Hit
from flagship.model.modification import Modification


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
        # type: (Hit) -> tuple
        """
        Send a Hit to our server for reporting.

        :param hit:
        :return: Tuple(Boolean if it has succeeded, log)
        """
        if issubclass(type(hit), Hit):
            return self._api_client.send_hit_request(self._visitor_id, hit)
        else:
            log = "[send_hit] : {} not a Hit subclass.".format(str(hit))
            self._config.event_handler.on_log(logging.ERROR, log)
            return False, log

    @exception_handler()
    @types_validator(True)
    def synchronize_modifications(self):
        # type: () -> tuple
        """
        Synchronize and fetch campaign modifications
        :return: Tuple(Boolean if it has succeeded, log)

        """
        self.campaigns = self._api_client.synchronize_modifications(self._visitor_id, self._context)
        for campaign in self.campaigns:
            self._modifications.update(campaign.get_modifications())
        self._config.event_handler.on_log(logging.DEBUG,
                                          "[synchronize_modifications] : Visitor '{} Campaigns = {}"
                                          .format(self._visitor_id, self.__campaigns_to_str()))
        self.__log_modifications()
        return True, ''

    def __log_modifications(self):
        results = '{'
        for mk, mv in self._modifications.items():
            results += '"{}": {},'.format(mv.key, Modification.value_to_str(mv.value))
        results = results[:-1]
        results += '}'
        self._config.event_handler.on_log(logging.DEBUG, "[synchronize_modifications] : Visitor '{} "
                                                         "Modifications = {}".format(self._visitor_id, results))

    def __campaigns_to_str(self):
        result = '\n     '
        for c in self.campaigns:
            result += (str(c) + '\n     ')
        return result

    @exception_handler()
    @types_validator(True, str)
    def activate_modification(self, key):
        # type: (str) -> tuple
        """
        Report this user has seen this modification.

        :param key: modification key
        :return: tuple (bool for success, log : str)
        """
        if key in self._modifications:
            modification = self._modifications[key]
            return self._api_client.activate_modification(self._visitor_id, modification.variation_group_id,
                                                          modification.variation_id)
        else:
            log = "[activate_modification] : no modification for the key '{}'.".format(key)
            self._config.event_handler.on_log(logging.ERROR, log)
            return False, log


    @exception_handler()
    @types_validator(True, str, [str, bool, int, float], bool)
    def get_modification(self, key, default_value, activate=False):
        # type: (str, any, bool) -> tuple
        """
        Retrieve a modification value by its key. If the key is not found the default value is returned.

        :param key: key associated to the modification.
        :param default_value: default value returned when the key does not match any modification value.
        :param activate: false by default Set this parameter to true to automatically report on our server that the
        current visitor has seen this modification. If false, call the activate_modification() later.
        :return: value
        """
        return self.get_modification_with_info(key, default_value, activate)[0]

    @exception_handler()
    @types_validator(True, str, [str, bool, int, float], bool)
    def get_modification_with_info(self, key, default_value, activate=False):
        # type: (str, any, bool) -> tuple
        """
        Retrieve a modification value by its key. If the key is not found the default value is returned.

        :param key: key associated to the modification.
        :param default_value: default value returned when the key does not match any modification value.
        :param activate: false by default Set this parameter to true to automatically report on our server that the
        current visitor has seen this modification. If false, call the activate_modification() later.
        :return: tuple (modification value, bool for success, str log, activation results tuple if enabled)
        """
        if key not in self._modifications:
            log = "[get_modification] : no modification for the key '{}', default value returned.".format(key)
            self._config.event_handler.on_log(logging.ERROR, log)
            return default_value, False, log, None
        elif self._modifications[key].value is None:
            return default_value, True, '', self.activate_modification(key) if activate else None
        else:
            value = self._modifications[key].value
            return value, True, '', self.activate_modification(key) if activate else None

    @exception_handler()
    @types_validator(True, str)
    def get_modification_data(self, key):
        if key not in self._modifications:
            return None
        return self._modifications[key]

    def __update_context_value(self, key, value, synchronize=False):
        t = type(value)
        if type(key) is not str:
            log = "[update_context] : key '{}' must be a str.".format(key)
            self._config.event_handler.on_log(logging.ERROR, log)
            return key, False, log, None
        elif t is not str and t is not int and t is not bool and t is not float:
            log = "[update_context] : value '{}' must be one of the following types: str, int, bool, float.".format(key)
            self._config.event_handler.on_log(logging.ERROR, log)
            return key, False, log, None
        else:
            self._context[key] = value
        return key, True, '', self.synchronize_modifications() if synchronize is True else None

    @exception_handler()
    @types_validator(True, [dict, tuple], bool)
    def update_context(self, context, synchronize=False):
        # type: (object, bool) -> tuple
        """
        Update the visitor context value matching the given key used for targeting.

        A new context value associated with this key will be created if there is no previous matching value.
        Context Key must be an str, and value types must on of the following : int, float, str, bool.

        :param context: Add a tuple (key, value) or a dictionary {key: value}
        :param synchronize: (optional : false by default) If set to True, it will automatically call
        synchronize_modifications() and then update the modifications from the server for all campaigns
        according to the updated current visitor context. You can also update it manually later with :
        synchronize_modifications()

        :return: tuple of tuple for each context values.
        (key, success, log, result of synchronize if enabled)
        """
        result = tuple()
        if isinstance(context, tuple) and len(context) == 2:
            result = () + (self.__update_context_value(context[0], context[1]))
        elif isinstance(context, dict):
            for (k, v) in context.items():
                result_update = (self.__update_context_value(k, v))
                if len(result) == 0:
                    result = (result_update,)
                else:
                    result += (result_update,)

        self._config.event_handler.on_log(logging.DEBUG, "[update_context] : Visitor '{}' Context = {}."
                                          .format(self._visitor_id, self._context))
        # if self._cache:
        #     self._cache.save(self._visitor_id, context)

        return result, self.synchronize_modifications() if synchronize else None

    def close(self):
        pass
