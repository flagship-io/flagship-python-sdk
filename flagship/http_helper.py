from __future__ import absolute_import

import json
import traceback

import requests
from enum import Enum
from flagship.constants import TAG_HTTP_REQUEST, DEBUG_REQUEST, URL_TRACKING, URL_BUCKETING, TAG_BUCKETING, \
    ERROR_BUCKETING_REQUEST, URL_ACTIVATE, URL_CONTEXT, URL_DECISION_API, URL_CAMPAIGNS, URL_CONTEXT_PARAM
from flagship.decorators import param_types_validator
from flagship.hits import _Activate
from flagship.log_manager import LogLevel
from flagship.utils import pretty_dict, log, log_exception


class HttpHelper:

    def __init__(self):
        pass

    class RequestType(Enum):
        POST = "POST",
        GET = "GET"

    @staticmethod
    @param_types_validator(False, RequestType, str, dict, dict, int)
    def send_http_request(method, url, headers, content, timeout=2000):
        try:
            response = requests.request(method=method.name, url=url, headers=headers, json=content, timeout=timeout)
            HttpHelper.log_request(method, url, headers, content, response)
            return True, response
        except Exception as e:
            print(traceback.format_exc())
            return False, None

    @staticmethod
    def send_campaign_request(visitor):
        config = visitor._configuration_manager.flagship_config
        url = URL_DECISION_API + config.env_id + URL_CAMPAIGNS + \
              (URL_CONTEXT_PARAM if visitor._has_consented is False else "")
        # url = URL_DECISION_API + config.env_id + URL_CAMPAIGNS
        import flagship
        headers = {
            "x-api-key": config.api_key,
            "x-sdk-client": "python",
            "x-sdk-version": flagship.__version__
        }
        content = {
            "visitorId": visitor._visitor_id,
            "anonymousId": visitor._anonymous_id,
            "trigger_hit": False,
            "context": visitor._context

        }
        success, response = HttpHelper.send_http_request(HttpHelper.RequestType.POST, url, headers, content,
                                                         config.timeout)
        if success and len(response.content) > 0:
            # return True, json.loads(response.content.decode("utf-8"))
            return True, response.content
        else:
            return False, dict()

    # @staticmethod
    # def send_hit(visitor, hit):
    #     # if isinstance(hit, _Activate):
    #     #     HttpHelper.send_activate(hit)
    #     # else:
    #         config = visitor._config
    #         import flagship
    #         headers = {
    #             "x-api-key": config.api_key,
    #             "x-sdk-client": "python",
    #             "x-sdk-version": flagship.__version__
    #         }
    #         body = {
    #             "cid": config.env_id
    #         }
    #         if visitor._anonymous_id is not None:
    #             body['cuid'] = visitor._visitor_id
    #             body['vid'] = visitor._anonymous_id
    #         else:
    #             body['vid'] = visitor._visitor_id
    #             body['cuid'] = None
    #         body.update(hit.get_data())
    #         response = requests.post(url=URL_TRACKING, headers=headers, json=body, timeout=config.timeout)
    #         HttpHelper.log_request(HttpHelper.RequestType.POST, URL_TRACKING, headers, body, response)

    @staticmethod
    def send_batch(config, batch):
        import flagship
        headers = {
            "x-sdk-client": "python",
            "x-sdk-version": flagship.__version__
        }
        body = {
            "cid": config.env_id
        }
        body.update(batch.data())
        response = requests.post(url=URL_TRACKING, headers=headers, json=body, timeout=config.timeout)
        HttpHelper.log_request(HttpHelper.RequestType.POST, URL_TRACKING, headers, body, response)

    @staticmethod
    def send_activate(visitor, hit):
        config = visitor._config
        import flagship
        headers = {
            "x-api-key": config.api_key,
            "x-sdk-client": "python",
            "x-sdk-version": flagship.__version__
        }
        body = {
            "cid": config.env_id,
        }
        if visitor._anonymous_id is not None:
            body['aid'] = visitor._anonymous_id
            body['vid'] = visitor._visitor_id
        else:
            body['vid'] = visitor._visitor_id
            body['aid'] = None
        body.update(hit.get_data())
        response = requests.post(url=URL_ACTIVATE, headers=headers, json=body, timeout=config.timeout)
        HttpHelper.log_request(HttpHelper.RequestType.POST, URL_ACTIVATE, headers, body, response)

    @staticmethod
    def send_context(visitor, hit):
        env_id = visitor._config.env_id
        endpoint = URL_CONTEXT.format(env_id)
        import flagship
        headers = {
            'x-sdk-client': 'android',
            'x-sdk-version': flagship.__version__
        }
        body = hit.get_data()
        response = requests.post(url=endpoint, headers=headers, json=body, timeout=visitor._config.timeout)
        HttpHelper.log_request(HttpHelper.RequestType.POST, endpoint, headers, body, response)
    @staticmethod
    def send_bucketing_request(config, last_modified=""):
        try:
            url = URL_BUCKETING.format(config.env_id)
            headers = {
                "Content-Type": "application/json",
                "If-Modified-Since": last_modified
            }
            response = requests.get(url=url, headers=headers, timeout=config.timeout)
            HttpHelper.log_request(HttpHelper.RequestType.GET, url, headers, {}, response)
            code = response.status_code
            if 'Last-Modified' in response.headers:
                last_modified = response.headers['Last-Modified']
            content = response.content.decode("utf-8")
            if code < 300:
                return last_modified, content
        except Exception as e:
            log_exception(TAG_BUCKETING, e, traceback.format_exc())
            # log(TAG_BUCKETING, LogLevel.ERROR, ERROR_BUCKETING_REQUEST)
        return None, None

    @staticmethod
    def log_request(method, url, headers, content, response):
        message = DEBUG_REQUEST.format(method.name, url, response.status_code,
                                       int(response.elapsed.total_seconds() * 1000))
        try:
            response_dict = json.loads(response.content.decode("utf-8"))
        except Exception as e:
            response_dict = {}
        pretty_request = pretty_dict(content, 2)
        pretty_response = pretty_dict(response_dict, 2)
        string = "Request body =>\n" \
                 "{}\n" \
                 "Response body =>\n" \
                 "{}\n" \
            .format(pretty_request, pretty_response)
        message += string
        log(TAG_HTTP_REQUEST, LogLevel.DEBUG if response.status_code in range(200, 305) else LogLevel.ERROR, message)
