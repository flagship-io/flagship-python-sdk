import asyncio

import requests
import threading

from flagship.model.campaign import Campaign


class APIClient:
    # __end_point = 'https://decision.flagship.io/v2/'
    __end_point = 'https://decision-api.flagship.io/v1/'
    __campaigns = '/campaigns/?exposeAllKeys=true'

    def __init__(self, env_id):
        self._env_id = env_id
        self._url = 'https://api.flagship.io'

    @property
    def fs_url(self):
        return f'{self._url}/{self._env_id}'

    def __send_campaign_request(self, visitor_id, context):
        body = {
            "visitorId": visitor_id,
            "context": context
        }
        url = self.__end_point + '' + self._env_id + '' + self.__campaigns
        print(url)#todo log url
        r = requests.post(url, json=body)
        return r


    def synchronize_modifications(self, visitor_id, context):
        response = self.__send_campaign_request(visitor_id, context)
        campaigns = Campaign.parse_campaigns(response.json())
        print(*campaigns, sep='\n')
