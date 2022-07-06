from __future__ import absolute_import

import json
import requests
from enum import Enum
from flagship.constants import TAG_HTTP_REQUEST, DEBUG_REQUEST, URL_ARIANE
from flagship.decorators import param_types_validator
from flagship.log_manager import LogLevel
from flagship.utils import pretty_dict, log


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
            HttpHelper.__log_request(method, url, headers, content, response)
            return True, response
        except Exception as e:
            print(e)
            return False, None

    @staticmethod
    def send_hit(visitor, hit):
        config = visitor._config
        import flagship
        headers = {
            "x-api-key": config.api_key,
            "x-sdk-client": "python",
            "x-sdk-version": flagship.__version__
        }
        body = {
            "eid": config.env_id,
        }
        if visitor._anonymous_id is not None:
            body['cuid'] = visitor._visitor_id
            body['vid'] = visitor._anonymous_id
        else:
            body['vid'] = visitor._visitor_id
            body['cuid'] = None
        body.update(hit.get_data())
        response = requests.post(url=URL_ARIANE, headers=headers, data=body, timeout=config.timeout)
        HttpHelper.__log_request(HttpHelper.RequestType.POST, URL_ARIANE, headers, body, response)


    @staticmethod
    def __log_request(method, url, headers, content, response):
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
                 "{}\n"\
            .format(pretty_request, pretty_response)
        message += string
        log(TAG_HTTP_REQUEST, LogLevel.DEBUG if response.status_code in range(200, 305) else LogLevel.ERROR, message)


