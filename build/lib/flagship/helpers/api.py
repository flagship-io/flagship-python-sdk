from __future__ import absolute_import

import json
import logging
import traceback

import requests

from flagship.errors import FlagshipParsingError
from flagship.model.campaign import Campaign


class APIClient:
    __ariane = 'https://ariane.abtasty.com/'
    __end_point = 'https://decision-api.flagship.io/v1/'
    __end_point_v2 = 'https://decision.flagship.io/v2/'
    __campaigns = '/campaigns/?exposeAllKeys=true'
    __activate = 'activate'

    def __init__(self, config):
        self._config = config
        self._env_id = config.env_id
        self.api_key = config.api_key
        self._url = 'https://api.flagship.io'

    @property
    def fs_url(self):
        return '{}/{}'.format(self._url, self._env_id)

    def get_endpoint(self):
        if not self.api_key or len(self.api_key) == 0:
            return self.__end_point
        else:
            return self.__end_point_v2

    def __send_campaign_request(self, visitor_id, context):
        header = {
            "x-api-key": self.api_key
        }
        body = {
            "visitorId": visitor_id,
            "trigger_hit": False,
            "context": context

        }
        url = self.get_endpoint() + '' + self._env_id + '' + self.__campaigns
        r = requests.post(url, headers=header, json=body)
        self.__log_request(url, r, body)
        return r

    def synchronize_modifications(self, visitor_id, context):
        response = self.__send_campaign_request(visitor_id, context)
        campaigns = list()
        try:
            campaigns = Campaign.parse_campaigns(response.json())
        except (ValueError, Exception):
            self._config.event_handler.on_exception_raised(
                FlagshipParsingError("An error occurred while synchronizing campaigns"), traceback.format_exc())
        return campaigns

    def activate_modification(self, visitor_id, variation_group_id, variation_id):
        header = {
            "x-api-key": self.api_key
        }
        body = {
            "cid": self._env_id,
            "vid": visitor_id,
            "caid": variation_group_id,
            "vaid": variation_id
        }
        url = self.get_endpoint() + self.__activate
        r = requests.post(url, headers=header, json=body)
        return self.__log_request(url, r, body)

    def send_hit_request(self, visitor_id, hit):
        body = {
            "cid": self._env_id,
            "vid": visitor_id
        }
        body.update(hit.get_data())
        url = self.__ariane
        r = requests.post(url, json=body)
        return self.__log_request(url, r, body, True)

    def __log_request(self, url, request, body, is_hit=False):
        log = '[Request][{}] {} - payload: {} - response: {}'.format(
                                              str(request.status_code),
                                              url,
                                              str(json.dumps(body)),
                                              str(request.content) if is_hit is False else ""
                                          )
        self._config.event_handler.on_log(logging.INFO if (request.status_code in range(200, 300)) else logging.ERROR,
                                          log)
        return True if (request.status_code in range(200, 300)) else False, str(request.status_code)

