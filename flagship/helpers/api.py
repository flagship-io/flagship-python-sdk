from __future__ import absolute_import

import json
import logging
import traceback
import requests
from flagship.errors import FlagshipParsingError
from flagship.model.campaign import Campaign
from flagship import __version__


class ApiManager:
    __ariane = 'https://ariane.abtasty.com/'
    __end_point_v2 = 'https://decision.flagship.io/v2/'
    __end_point_bucketing = 'https://cdn.flagship.io/{id}/bucketing.json'
    __campaigns = '/campaigns/?exposeAllKeys=true&sendContextEvent=false'
    __activate = 'activate'
    __events = '/events'

    def __init__(self, config):
        self._config = config
        self._env_id = config.env_id
        self.api_key = config.api_key
        self._url = 'https://api.flagship.io'
        self.panic_mode = False

    @property
    def fs_url(self):
        return '{}/{}'.format(self._url, self._env_id)

    def get_endpoint(self):
        return self.__end_point_v2

    def __send_campaign_request(self, visitor_id, anoymousId, context):
        context_to_send = self.__clean_context(context)
        header = {
            "x-api-key": self.api_key,
            "x-sdk-client": "python",
            "x-sdk-version": __version__
        }
        body = {
            "visitorId": visitor_id,
            "trigger_hit": False,
            "context": context_to_send

        }
        if anoymousId is not None:
            body["anonymousId"] = anoymousId
        try:
            url = self.get_endpoint() + '' + self._env_id + '' + self.__campaigns
            print(str(self._config.timeout))
            r = requests.post(url, headers=header, json=body, timeout=self._config.timeout)
            self.__log_request(url, r, body)
            return r
        except AssertionError:
            raise
        except Exception as e:
            self._config.event_handler.on_log(logging.ERROR, str(e))
            return None

    def synchronize_modifications(self, visitor_id, anonymousId, context):
        response = self.__send_campaign_request(visitor_id, anonymousId, context)
        campaigns = list()
        if response is not None:
            json_response = response.json()
            panic_mode = self.check_for_panic(json_response)
            if panic_mode != self.panic_mode:
                self.panic_mode = panic_mode
                self._config.event_handler.on_log(logging.INFO, "[synchronize_modifications] Panic mode is " +
                                                  ("disabled." if self.panic_mode is False else "enabled."))
            if self.panic_mode is False:
                try:
                    campaigns = Campaign.parse_campaigns(json_response)
                except (ValueError, Exception):
                    self._config.event_handler.on_exception_raised(
                        FlagshipParsingError("An error occurred while synchronizing campaigns"), traceback.format_exc())
        return campaigns

    def check_for_panic(self, json_response):
        if json_response is not None and 'panic' in json_response:
            return json_response.get("panic", False)
        return False

    def activate_modification(self, visitor_id, anonymous_id, variation_group_id, variation_id):
        header = {
            # "x-api-key": self.api_key
            "x-sdk-client": "python",
            "x-sdk-version": __version__
        }
        body = {
            "cid": self._env_id,
            "caid": variation_group_id,
            "vaid": variation_id
        }
        if visitor_id is not None and len(visitor_id) > 0 and anonymous_id is not None:
            body["aid"] = anonymous_id
            body["vid"] = visitor_id
        elif visitor_id is not None and len(visitor_id) > 0 and anonymous_id is None:
            body["vid"] = visitor_id
        else:
            body["vid"] = anonymous_id

        url = self.get_endpoint() + self.__activate
        r = requests.post(url, headers=header, json=body)
        return self.__log_request(url, r, body)

    def send_context_request(self, visitor_id, context):
        context_to_send = self.__clean_context(context)
        header = {
            # "x-api-key": self.api_key
            "x-sdk-client": "python",
            "x-sdk-version": __version__
        }
        body = {
            "type": 'CONTEXT',
            "data": context_to_send,
            "visitorId": visitor_id
        }
        url = self.get_endpoint() + '' + self._env_id + '' + self.__events
        r = requests.post(url, headers=header, json=body)
        return self.__log_request(url, r, body)

    def __clean_context(self, context):
        context_to_send = dict(context)
        for n in list(context_to_send.keys()):
            if n.startswith("fs_"):
                context_to_send.pop(n)
        return context_to_send

    def send_hit_request(self, visitor_id, anonymous_id, hit):
        body = {
            "cid": self._env_id,
        }
        if visitor_id is not None and len(visitor_id) > 0 and anonymous_id is not None:
            body["cuid"] = visitor_id
            body["vid"] = anonymous_id
        elif visitor_id is not None and len(visitor_id) > 0 and anonymous_id is None:
            body["vid"] = visitor_id
        else:
            body["vid"] = anonymous_id
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

    @staticmethod
    def send_bucketing_request(config, last_modified):
        url = ApiManager.__end_point_bucketing.replace('{id}', config.env_id)
        headers = {}
        if last_modified is not None:
            headers['If-Modified-Since'] = last_modified
        request = requests.get(url, headers=headers)
        log = '[Request][{}] {} - response: {}'.format(
            str(request.status_code),
            url,
            str(request.content.decode('utf-8'))
        )
        config.event_handler.on_log(logging.INFO if (request.status_code in range(200, 300)) else logging.ERROR, log)
        code = request.status_code
        if code == 200 and 'Last-Modified' in request.headers:
            return code, request.headers['Last-Modified'], request.json()
        else:
            return code, None, None
