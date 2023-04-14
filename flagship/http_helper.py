from __future__ import absolute_import

import json
import traceback
from enum import Enum

import requests

from flagship.constants import TAG_HTTP_REQUEST, DEBUG_REQUEST, URL_TRACKING, URL_BUCKETING, TAG_BUCKETING, \
    URL_ACTIVATE, URL_DECISION_API, URL_CAMPAIGNS
from flagship.decorators import param_types_validator
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
        url = URL_DECISION_API + config.env_id + URL_CAMPAIGNS
        import flagship
        headers = {
            "x-api-key": config.api_key,
            "x-sdk-client": "python",
            "x-sdk-version": flagship.__version__
        }
        content = {
            "visitorId": visitor.visitor_id,
            "anonymousId": visitor.anonymous_id,
            "visitor_consent": visitor.has_consented,
            "trigger_hit": False,
            "context": visitor.context

        }
        success, response = HttpHelper.send_http_request(HttpHelper.RequestType.POST, url, headers, content,
                                                         config.timeout)
        if success and len(response.content) > 0:
            # return True, json.loads(response.content.decode("utf-8"))
            return True, response.content
        else:
            return False, dict()

    @staticmethod
    def send_hit(config, hit):
        try:
            import flagship
            headers = {
                "x-sdk-client": "python",
                "x-sdk-version": flagship.__version__
            }
            body = {
                "cid": config.env_id
            }
            body.update(hit.data())
            timeout = config.tracking_manager_config.timeout / 1000.0
            response = requests.post(url=URL_TRACKING, headers=headers, json=body, timeout=timeout)
            HttpHelper.log_request(HttpHelper.RequestType.POST, URL_TRACKING, headers, body, response)
            return response
        except Exception as e:
            HttpHelper.log_request(HttpHelper.RequestType.POST, URL_TRACKING, headers, body, None)
            return None

    # @staticmethod
    # def send_activate(visitor, hit):
    #     config = visitor._config
    #     import flagship
    #     headers = {
    #         "x-api-key": config.api_key,
    #         "x-sdk-client": "python",
    #         "x-sdk-version": flagship.__version__
    #     }
    #     body = {
    #         "cid": config.env_id,
    #     }
    #     if visitor.anonymous_id is not None:
    #         body['aid'] = visitor.anonymous_id
    #         body['vid'] = visitor.visitor_id
    #     else:
    #         body['vid'] = visitor.visitor_id
    #         body['aid'] = None
    #     body.update(hit.data())
    #     response = requests.post(url=URL_ACTIVATE, headers=headers, json=body, timeout=config.timeout)
    #     HttpHelper.log_request(HttpHelper.RequestType.POST, URL_ACTIVATE, headers, body, response)
    #     return response

    @staticmethod
    def send_activates(config, hits):

        import flagship
        headers = {
            # 'x-api-key': config.api_key,
            'x-sdk-client': 'python',
            'x-sdk-version': flagship.__version__
        }
        batch = list()
        if isinstance(hits, list):
            for h in hits:
                batch.append(h.data())
        else:
            batch.append(hits.data())
        if len(batch) > 0:
            body = {
                "cid": config.env_id,
                "batch": batch
            }
            try:
                timeout = config.tracking_manager_config.timeout
                response = requests.post(url=URL_ACTIVATE, headers=headers, json=body, timeout=timeout)
                HttpHelper.log_request(HttpHelper.RequestType.POST, URL_ACTIVATE, headers, body, response)
                return response
            except Exception as e:
                HttpHelper.log_request(HttpHelper.RequestType.POST, URL_TRACKING, headers, body, None)
        return None

    # @staticmethod
    # def send_context(visitor, hit):
    #     env_id = visitor._config.env_id
    #     endpoint = URL_CONTEXT.format(env_id)
    #     import flagship
    #     headers = {
    #         'x-sdk-client': 'android',
    #         'x-sdk-version': flagship.__version__
    #     }
    #     body = hit.data()
    #     response = requests.post(url=endpoint, headers=headers, json=body, timeout=visitor._config.timeout)
    #     HttpHelper.log_request(HttpHelper.RequestType.POST, endpoint, headers, body, response)

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
        body_str = "Request body =>\n" \
                 "{}\n" \
                 "Response body =>\n" \
                 "{}\n"
        if response is None:
            message = DEBUG_REQUEST.format(method.name, url, 'FAIL', int(0))
            pretty_request = pretty_dict(content, 2)
            pretty_response = ''
        else:
            message = DEBUG_REQUEST.format(method.name, url, response.status_code,
                                           int(response.elapsed.total_seconds() * 1000))
            try:
                response_dict = json.loads(response.content.decode("utf-8"))
            except Exception as e:
                response_dict = {}
            pretty_request = pretty_dict(content, 2)
            pretty_response = pretty_dict(response_dict, 2)
        message += body_str.format(pretty_request, pretty_response)
        log(TAG_HTTP_REQUEST,
            LogLevel.DEBUG if response is not None and response.status_code in range(200, 305) else LogLevel.ERROR,
            message)
