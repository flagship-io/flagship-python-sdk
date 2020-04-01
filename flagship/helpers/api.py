import json
import requests

from flagship.model.campaign import Campaign


class APIClient:
    __end_point = 'https://decision.flagship.io/v2/'
    # __end_point = 'https://decision-api.flagship.io/v1/'
    __campaigns = '/campaigns/?exposeAllKeys=true'
    __activate = 'activate'

    def __init__(self, config):
        self._env_id = config.env_id
        self.api_key = config.api_key
        self._url = 'https://api.flagship.io'

    @property
    def fs_url(self):
        return f'{self._url}/{self._env_id}'

    def __send_campaign_request(self, visitor_id, context):
        header = {
            "x-api-key": self.api_key
        }
        body = {
            "visitorId": visitor_id,
            "trigger_hit": False,
            "context": context

        }
        url = self.__end_point + '' + self._env_id + '' + self.__campaigns
        print(url + ' payload : ' + str(json.dumps(body)))  # todo log url
        r = requests.post(url, headers=header, json=body)
        return r

    def synchronize_modifications(self, visitor_id, context):
        response = self.__send_campaign_request(visitor_id, context)
        campaigns = list()
        try:
            campaigns = Campaign.parse_campaigns(response.json())
            print(*campaigns, sep='\n')
        except ValueError:
            print("Parsing campaign error")
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
        url = self.__end_point + self.__activate
        r = requests.post(url, headers=header, json=body)
        print('[' + str(r.status_code) + '] : ' + url + ' payload : ' + json.dumps(body))
