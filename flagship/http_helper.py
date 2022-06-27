from __future__ import absolute_import

import json

import requests
from enum import Enum

from flagship.decorators import param_types_validator
from flagship.log_manager import LogLevel
from flagship.constants import _TAG_HTTP_REQUEST, _DEBUG_REQUEST
from flagship.utils import pretty_dict, log


class HttpHelper:
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
    def __log_request(method, url, headers, content, response):
        message = _DEBUG_REQUEST.format(method.name, url, response.status_code,
                                        int(response.elapsed.total_seconds() * 1000))
        message += pretty_dict({
            # "request_headers": headers,
            "request_body": content,
            "response_body": json.loads(response.content.decode("utf-8"))
        })
        log(_TAG_HTTP_REQUEST, LogLevel.DEBUG if response.status_code in range(200, 305) else LogLevel.ERROR, message)
