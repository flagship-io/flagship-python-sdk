from datetime import datetime

from flagship.decorators import exception_handler
from flagship.helpers.api import APIClient
from flagship.helpers.hits import Hit


class FlagshipVisitor:

    def __init__(self, config, visitor_id, context: dict):
        self._env_id = config.env_id
        self._api_key = config.api_key
        self._visitor_id = visitor_id
        self._context = dict()
        self.update_context(context)
        self._last_call = datetime.now()
        self._api_client = APIClient(config)
        self.campaigns = list()
        self._modifications = dict()

    def __getattribute__(self, name):
        if name != '_last_call':
            self._last_call = datetime.now()
        return super().__getattribute__(name)

    def send_hit(self, hit: Hit):
        if issubclass(type(hit), Hit):
            self._api_client.send_hit_request(self._visitor_id, hit)

    def synchronize_modifications(self):
        self.campaigns = self._api_client.synchronize_modifications(self._visitor_id, self._context)
        for campaign in self.campaigns:
            self._modifications.update(campaign.get_modifications())

    def activate_modification(self, key: str):
        if key in self._modifications:
            modification = self._modifications[key]
            self._api_client.activate_modification(self._visitor_id, modification.variation_group_id,
                                                   modification.variation_id)

    def get_modification(self, key: str, default_value, activate=False):
        if key not in self._modifications:
            return default_value
        elif self._modifications[key].value is None:
            if activate:
                self.activate_modification(key)
            return default_value
        else:
            if activate:
                self.activate_modification(key)
            return self._modifications[key].value

    def get_modification_data(self, key: str):
        if key not in self._modifications:
            return None
        return self._modifications[key]

    def __update_context_value(self, key, value, synchronize=False):
        t = type(value)
        if type(key) is not str:
            print("Update context : key {} must be a str.".format(key))
        elif t is not str and t is not int and t is not bool and t is not float:
            print("Update context : value {} must be a str, int, bool, float.".format(value))
        else:
            self._context[key] = value
        if synchronize is True:
            self.synchronize_modifications()

    @exception_handler(43)
    def update_context(self, context, synchronize=False):
        v = 1/0
        if isinstance(context, tuple) and len(context) == 2:
            self.__update_context_value(context[0], context[1])
        elif isinstance(context, dict):
            for (k, v) in context.items():
                self.__update_context_value(k, v)
        if synchronize:
            self.synchronize_modifications()

        # if self._cache:
        #     self._cache.save(self._visitor_id, context)

    def close(self):
        pass
