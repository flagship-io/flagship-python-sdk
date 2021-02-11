import json
import logging
from datetime import datetime

from flagship.config import Config
from flagship.decorators import exception_handler, types_validator
from flagship.helpers.api import ApiManager
from flagship.helpers.bucketing import BucketingManager
from flagship.helpers.hits import Hit
from flagship.helpers.preset_context import PresetContext
from flagship.model.campaign import Campaign
from flagship.model.modification import Modification


class FlagshipVisitor:

    def __init__(self, bucketing_manager, config, visitor_id, context):
        # type: (BucketingManager, Config, str, dict) -> None
        self._bucketing_manager = bucketing_manager
        self._config = config
        self._api_manager = ApiManager(config)
        self._env_id = config.env_id
        self._api_key = config.api_key
        self._visitor_id = visitor_id
        self._context = dict()
        self.update_context(context)
        self._last_call = datetime.now()
        self.campaigns = list()
        self._modifications = dict()

    def _is_panic_mode(self):
        if self._api_manager is not None and self._api_manager.panic_mode is True:
            return True
        elif self._bucketing_manager is not None and self._bucketing_manager.panic_mode is True:
            return True
        else:
            return False

    @exception_handler()
    @types_validator(True, Hit)
    def send_hit(self, hit):
        # type: (Hit) -> tuple
        """
        Send a Hit to our server for reporting.

        :param hit:
        :return: Tuple(Boolean if it has succeeded, log)
        """
        if self._is_panic_mode() is False:
            if issubclass(type(hit), Hit) is False:
                log = "[send_hit] : {} not a Hit subclass.".format(str(hit))
                self._config.event_handler.on_log(logging.ERROR, log)
                return False, log
            elif hit._is_valid()[0] is False:
                log = "[send_hit] : {} Hit is not valid : {}".format(str(hit), hit._is_valid()[1])
                self._config.event_handler.on_log(logging.ERROR, log)
                return False, log
            else:
                return self._api_manager.send_hit_request(self._visitor_id, hit)

        else:
            log = "[send_hit] '{}' not possible to send while panic mode is enabled.".format(str(hit))
            self._config.event_handler.on_log(logging.ERROR, log)
            return False, log

    @exception_handler()
    @types_validator(True)
    def synchronize_modifications(self):
        """
        When the SDK is set with DECISION_API mode :
        This function will call the decision api and update all the campaigns modifications from the server according to the user context.
        If the SDK is set with BUCKETING mode :
        This function will re-apply targeting and update all the campaigns modifications from the server according to the user context.

        :return: Tuple(Boolean if it has succeeded, log)
        """

        if self._config.mode is Config.Mode.API:
            self.campaigns = self._api_manager.synchronize_modifications(self._visitor_id, self._context)
        else:
            if self._is_panic_mode() is False:
                self._modifications.clear()
                bucketing_data = self._bucketing_manager.get_bucketing_data()
                if bucketing_data is not None and 'content' in bucketing_data:
                    cached_visitor = self._config.visitor_cache_manager._lookup_visitor_data(
                        self._visitor_id) if self._config.visitor_cache_manager is not None else None
                    self.campaigns = Campaign.parse_campaigns(bucketing_data['content'], self._visitor_id,
                                                              cached_visitor)
        if self._is_panic_mode() is False:
            self._api_manager.send_context_request(self._visitor_id, self._context)
            for campaign in self.campaigns:
                self._modifications.update(campaign.get_modifications(self._config.mode is Config.Mode.BUCKETING,
                                                                      self._context))
            self.__log_modifications()
            if self._config.visitor_cache_manager is not None:
                self._config.visitor_cache_manager._save_visitor_data(self._visitor_id, self.get_selected_variations())
            return True, ''
        else:
            log = '[synchronize_modifications] not possible while panic mode is enabled.'
            self._config.event_handler.on_log(logging.ERROR, log)
            return False, log

        #     if self._config.mode is Config.Mode.API:
        #         self.campaigns = self._api_manager.synchronize_modifications(self._visitor_id, self._context)
        #     else:
        #         self._modifications.clear()
        #         bucketing_data = self._bucketing_manager.get_bucketing_data()
        #         if bucketing_data is not None and 'content' in bucketing_data:
        #             self.campaigns = Campaign.parse_campaigns(bucketing_data['content'], self._visitor_id)
        #             self._api_manager.send_context_request(self._visitor_id, self._context)
        #
        #     for campaign in self.campaigns:
        #         self._modifications.update(campaign.get_modifications(self._config.mode is Config.Mode.BUCKETING,
        #                                                               self._context))
        #     self.__log_modifications()
        #     return True, ''

    def __log_modifications(self):
        results = '{'
        for mk, mv in self._modifications.items():
            results += '"{}": {},'.format(mv.key, Modification.value_to_str(mv.value))
        if len(results) > 1:
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
        if self._is_panic_mode() is False:
            if key in self._modifications:
                modification = self._modifications[key]
                return self._api_manager.activate_modification(self._visitor_id, modification.variation_group_id,
                                                               modification.variation_id)
            else:
                log = "[activate_modification] : no modification for the key '{}'.".format(key)
                self._config.event_handler.on_log(logging.ERROR, log)
                return False, log
        else:
            log = "[activate_modification] for key '{}' not possible while panic mode is enabled.".format(key)
            self._config.event_handler.on_log(logging.ERROR, log)
            return False, log

    @exception_handler()
    @types_validator(True, str, [str, bool, int, float, dict, list], bool)
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
        if self._is_panic_mode() is False:
            return self.get_modification_with_results(key, default_value, activate)[0]
        else:
            log = "[get_modification] for key '{}' not possible while panic mode is enabled.".format(key)
            self._config.event_handler.on_log(logging.ERROR, log)
            return default_value

    @exception_handler()
    @types_validator(True, str)
    def get_modification_info(self, key):
        """
       Retrieve a modification campaign information by its key. If the key is not found None is returned.

       :param key: key associated to the modification.
       :return: dict
       """
        if self._is_panic_mode() is False:
            if key in self._modifications:
                return {
                    "campaignId": self._modifications[key].campaign_id,
                    "variationGroupId": self._modifications[key].variation_group_id,
                    "variationId": self._modifications[key].variation_id,
                    "isReference": self._modifications[key].reference
                }
            else:
                self._config.event_handler.on_log(logging.ERROR,
                                                  "[get_modification_info] Key '{}' is not in any campaign."
                                                  .format(key))
                return None
        else:
            log = "[get_modification_info] for key '{}' not possible while panic mode is enabled.".format(key)
            self._config.event_handler.on_log(logging.ERROR, log)
            return None

    @exception_handler()
    @types_validator(True, str, [str, bool, int, float, dict, list], bool)
    def get_modification_with_results(self, key, default_value, activate=False):
        # type: (str, any, bool) -> tuple
        """
        Retrieve a modification value by its key. If the key is not found the default value is returned.

        :param key: key associated to the modification.
        :param default_value: default value returned when the key does not match any modification value.
        :param activate: false by default Set this parameter to true to automatically report on our server that the
        current visitor has seen this modification. If false, call the activate_modification() later.
        :return: tuple (modification value, bool for success, str log, activation results tuple if enabled)
        """
        if self._is_panic_mode() is False:
            if key not in self._modifications:
                log = "[get_modification] : no modification for the key '{}', default value returned.".format(key)
                self._config.event_handler.on_log(logging.ERROR, log)
                return default_value, False, log, None
            elif self._modifications[key].value is None:
                return default_value, True, '', self.activate_modification(key) if activate else None
            else:
                value = self._modifications[key].value
                return value, True, '', self.activate_modification(key) if activate else None
        else:
            log = "[get_modification_with_results] for key '{}' not possible while panic mode is enabled.".format(key)
            self._config.event_handler.on_log(logging.ERROR, log)
            return default_value, False, log, None

    # @exception_handler()
    # @types_validator(True, str)
    # def get_modification_data(self, key):
    #     if key not in self._modifications:
    #         return None
    #     return self._modifications[key]

    def __update_context_value(self, key, value, synchronize=False):
        t = type(value)
        if isinstance(key, PresetContext):
            key = key.value
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

        :param context: Add a tuple (key, value) or a dictionary {key: value}. key must be a str.
        :param synchronize: (optional : false by default) If set to True, it will automatically call
        synchronize_modifications() and then update the modifications from the server for all campaigns
        according to the updated current visitor context. You can also update it manually later with :
        synchronize_modifications()

        :return: tuple of tuple for each context values.
        (key, success, log, result of synchronize if enabled)
        """
        result = tuple()
        if self._is_panic_mode() is False:
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
            return result, self.synchronize_modifications() if synchronize else None
        else:
            log = "[update_context] for key/value '{}' not possible while panic mode is enabled.".format(str(context))
            self._config.event_handler.on_log(logging.ERROR, log)
            return tuple(), None

    def get_selected_variations(self):
        selected_variation_ids = list()
        if self._visitor_id is not None and self.campaigns is not None:
            for k, v in self._modifications.items():
                if v.variation_id not in selected_variation_ids:
                    selected_variation_ids.append(v.variation_id)
                # for variation_group in campaign.variation_groups:
                #     selected_variation_ids.append(variation_group.selected_variation_id)
        return selected_variation_ids
