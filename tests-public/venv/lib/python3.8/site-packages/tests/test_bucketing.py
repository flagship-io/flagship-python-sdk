# coding: utf8

import json
import os

import responses

from flagship.app import Flagship
from flagship.config import Config


def test_bucketing_wrong_config():
    class Wrong:
        def __init__(self):
            pass

    try:
        fs = Flagship.instance()
        fs.start(Config("my_env_id", "my_api", mode=Wrong))
        assert False
    except Exception as e:
        assert True

@responses.activate
def test_bucketing_init():

    @responses.activate
    def test_bucketing_304():

        @responses.activate
        def e_test_bucketing_200_again():
            json_response = '{"campaigns":[{"variationGroups":[{"variations":[{"allocation":100,"modifications":{"type":"FLAG","value":{"featureEnabled":true}},"id":"xxxx"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":true,"key":"isVIPUser"}]}]},"id":"yyyy"},{"variations":[{"allocation":100,"modifications":{"type":"FLAG","value":{"featureEnabled":false}},"id":"cccc"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":false,"key":"isVIPUser"}]}]},"id":"vvvv"}],"type":"toggle","id":"aaaa"},{"variationGroups":[{"variations":[{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":null}},"id":"zzzz","reference":true},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":1111}},"id":"eeee"},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":3333}},"id":"rrrr"},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":22.22,"rank":2222}},"id":"tttt"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":"password","key":"access"}]}]},"id":"yyyy"}],"type":"ab","id":"iiii"}]}'
            headers = {
                "Last-Modified": "Fri,  05 Jun 2023 12:20:40 GMT"
            }
            responses.reset()
            responses.add(responses.GET,
                          'https://cdn.flagship.io/my_env_id/bucketing.json',
                          json=json.loads(json_response), status=200, adding_headers=headers)
            fs = Flagship.instance()
            fs.start(Config("my_env_id", "my_api_key", mode=Config.Mode.BUCKETING))
            with open("bucketing.json", 'r') as f:
                content = f.read()
                assert len(content) > 2
                json_object = json.loads(content)
                last_modified = json_object['last_modified']
                assert last_modified is not None
                assert last_modified == "Fri,  05 Jun 2023 12:20:40 GMT"


        json_response = '{}'
        headers = {
            "Last-Modified": "fake"
        }
        responses.reset()
        responses.add(responses.GET,
                      'https://cdn.flagship.io/my_env_id/bucketing.json',
                      json=json.loads(json_response), status=304, adding_headers=headers)
        responses.add(responses.POST,
                      'https://decision.flagship.io/v2/my_env_id/events',
                      json=json.loads('{}'), status=200)
        responses.add(responses.POST,
                      'https://decision.flagship.io/v2/activate',
                      json=json.loads('{}'), status=200)

        fs = Flagship.instance()
        fs.start(Config("my_env_id", "my_api_key", mode=Config.Mode.BUCKETING))
        visitor = Flagship.instance().create_visitor("ä",
                                                     {'isVIPUser': True, 'bin_a': 1,
                                                      'bin_b': 1})  # type: FlagshipVisitor
        visitor.update_context(('access', 'password'), True)
        assert visitor.get_modification('rank', "=null", True) != "=null"
        contains_activate = False
        contains_events = False
        for c in responses.calls:

            if contains_events is False and  c.request.url.__contains__('events'):
                contains_events = True
            if contains_activate is False and  c.request.url.__contains__('activate'):
                contains_events = True
        assert contains_events is True
        assert contains_events is True

        with open("bucketing.json", 'r') as f:
            content = f.read()
            assert len(content) > 2
            json_object = json.loads(content)
            last_modified = json_object['last_modified']
            assert last_modified is not None
            assert last_modified == "Fri,  05 Jun 2020 12:20:40 GMT"
            e_test_bucketing_200_again()


    try:
        try:
            os.remove("bucketing.json")
        except Exception as e:
            print("No Bucketing file")
        json_response = '{"campaigns":[{"variationGroups":[{"variations":[{"allocation":100,"modifications":{"type":"FLAG","value":{"featureEnabled":true}},"id":"xxxx"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":true,"key":"isVIPUser"}]}]},"id":"yyyy"},{"variations":[{"allocation":100,"modifications":{"type":"FLAG","value":{"featureEnabled":false}},"id":"cccc"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":false,"key":"isVIPUser"}]}]},"id":"vvvv"}],"type":"toggle","id":"aaaa"},{"variationGroups":[{"variations":[{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":null}},"id":"zzzz","reference":true},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":1111}},"id":"eeee"},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":3333}},"id":"rrrr"},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":22.22,"rank":2222}},"id":"tttt"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":"password","key":"access"}]}]},"id":"yyyy"}],"type":"ab","id":"iiii"}]}'

        headers = {
            "Last-Modified": "Fri,  05 Jun 2020 12:20:40 GMT"
        }
        responses.reset()
        responses.add(responses.GET,
                      'https://cdn.flagship.io/my_env_id/bucketing.json',
                      json=json.loads(json_response), status=200, adding_headers=headers)

        fs = Flagship.instance()
        fs.start(Config("my_env_id", "my_api_key", mode=Config.Mode.BUCKETING))
        assert os.path.isfile("bucketing.json")
        with open("bucketing.json", 'r') as f:
            json_object = json.loads(f.read())
            last_modified = json_object['last_modified']
            assert last_modified is not None
            assert last_modified == "Fri,  05 Jun 2020 12:20:40 GMT"
            test_bucketing_304()

    except Exception as e:
        print(e)
        assert False