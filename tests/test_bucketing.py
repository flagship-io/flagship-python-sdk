# coding: utf8

import json
import os
import random
import string
import time
from unittest import TestCase

import responses

from flagship.app import Flagship
from flagship.config import Config
from flagship.helpers.hits import Page, Screen


def test_bucketing_wrong_config():
    class Wrong:
        def __init__(self):
            pass

    try:
        fs = Flagship.instance()
        fs.start("my_env_id", "my_api", Config(mode=Wrong))
        assert False
    except Exception as e:
        assert True


def test_bucketing_suite():
    a_test_bucketing_init()
    b_test_bucketing_304()
    c_test_bucketing_200_again()

@responses.activate
def b_test_bucketing_304():
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
    fs.start("my_env_id", "my_api_key", Config(mode=Config.Mode.BUCKETING, polling_interval=-1))
    visitor = Flagship.instance().create_visitor("ä",
                                                 {'isVIPUser': True, 'bin_a': 1,
                                                  'bin_b': 1})  # type: FlagshipVisitor
    visitor.update_context(('access', 'password'), True)
    assert visitor.get_modification('rank', "=null", True) != "=null"
    contains_activate = False
    contains_events = False
    for c in responses.calls:

        if contains_events is False and c.request.url.__contains__('events'):
            contains_events = True
        if contains_activate is False and c.request.url.__contains__('activate'):
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


@responses.activate
def a_test_bucketing_init():

    try:
        try:
            os.remove("bucketing.json")
        except Exception as e:
            print("No Bucketing file")
        json_response = '{"campaigns":[{"variationGroups":[{"variations":[{"allocation":100,"modifications":{"type":"FLAG","value":{"featureEnabled":true}},"id":"xxxx"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":true,"key":"isVIPUser"}]}]},"id":"yyyy"},{"variations":[{"allocation":100,"modifications":{"type":"FLAG","value":{"featureEnabled":false}},"id":"cccc"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":false,"key":"isVIPUser"}]}]},"id":"vvvv"}],"type":"toggle","id":"aaaa"},{"id":"bu6lgeu3bdt014iawwww","type":"perso","variationGroups":[{"id":"bu6lgeu3bdt014iaxxxx","targeting":{"targetingGroups":[{"targetings":[{"operator":"CONTAINS","key":"sdk_deviceModel","value":["Google Pixel 3","Google Pixel X","Google Pixel 0"]}]}]},"variations":[{"id":"bu6lgeu3bdt014iacccc","modifications":{"type":"JSON","value":{"target":null}},"reference":true},{"id":"bu6lgeu3bdt014iavvvv","modifications":{"type":"JSON","value":{"target":"is"}},"allocation":100}]},{"id":"bu6lttip17b01emhbbbb","targeting":{"targetingGroups":[{"targetings":[{"operator":"NOT_CONTAINS","key":"sdk_deviceModel","value":["Google Pixel 9","Google Pixel 9000"]}]}]},"variations":[{"id":"bu6lttip17b01emhnnnn","modifications":{"type":"JSON","value":{"target":null}},"reference":true},{"id":"bu6lttip17b01emhqqqq","modifications":{"type":"JSON","value":{"target":"is not"}},"allocation":100}]}]},{"variationGroups":[{"variations":[{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":null}},"id":"zzzz","reference":true},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":1111}},"id":"eeee"},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":3333}},"id":"rrrr"},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":22.22,"rank":2222}},"id":"tttt"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":"password","key":"access"}]}]},"id":"yyyy"}],"type":"ab","id":"iiii"}]}'
        headers = {
            "Last-Modified": "Fri,  05 Jun 2020 12:20:40 GMT"
        }
        responses.reset()
        responses.add(responses.GET,
                      'https://cdn.flagship.io/my_env_id/bucketing.json',
                      json=json.loads(json_response), status=200, adding_headers=headers)
        responses.add(responses.POST,
                                            'https://decision.flagship.io/v2/my_env_id/events',
                                            json=json.loads('{}'), status=200)

        fs = Flagship.instance()
        fs.start("my_env_id", "my_api_key", Config(mode=Config.Mode.BUCKETING, polling_interval=-1))
        assert os.path.isfile("bucketing.json")
        with open("bucketing.json", 'r') as f:
            json_object = json.loads(f.read())
            last_modified = json_object['last_modified']
            assert last_modified is not None
            assert last_modified == "Fri,  05 Jun 2020 12:20:40 GMT"
            # test_bucketing_304()

        visitor = fs.create_visitor("visitor_1", {'sdk_deviceModel': 'Google Pixel 9000'})
        assert visitor.get_modification("target", "default", False) == 'default'
        visitor.update_context(('sdk_deviceModel', 'Google Pixel 10'), True)
        assert visitor.get_modification("target", "default", False) == 'is not'
        visitor.update_context(('sdk_deviceModel', 'Google Pixel XXX'), True)
        assert visitor.get_modification("target", "default", False) == 'is'
    except Exception as e:
        print(e)
        assert False


@responses.activate
def c_test_bucketing_200_again():
    json_response = '{"campaigns":[{"variationGroups":[{"variations":[{"allocation":100,"modifications":{"type":"FLAG","value":{"featureEnabled":true}},"id":"xxxx"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":true,"key":"isVIPUser"}]}]},"id":"yyyy"},{"variations":[{"allocation":100,"modifications":{"type":"FLAG","value":{"featureEnabled":false}},"id":"cccc"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":false,"key":"isVIPUser"}]}]},"id":"vvvv"}],"type":"toggle","id":"aaaa"},{"variationGroups":[{"variations":[{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":null}},"id":"zzzz","reference":true},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":1111}},"id":"eeee"},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":3333}},"id":"rrrr"},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":22.22,"rank":2222}},"id":"tttt"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":"password","key":"access"}]}]},"id":"yyyy"}],"type":"ab","id":"iiii"}]}'
    headers = {
        "Last-Modified": "Fri,  05 Jun 2023 12:20:40 GMT"
    }
    responses.reset()
    responses.add(responses.GET,
                  'https://cdn.flagship.io/my_env_id/bucketing.json',
                  json=json.loads(json_response), status=200, adding_headers=headers)
    fs = Flagship.instance()
    fs.start("my_env_id", "my_api_key", Config(mode=Config.Mode.BUCKETING, polling_interval=-1))
    with open("bucketing.json", 'r') as f:
        content = f.read()
        assert len(content) > 2
        json_object = json.loads(content)
        last_modified = json_object['last_modified']
        assert last_modified is not None
        assert last_modified == "Fri,  05 Jun 2023 12:20:40 GMT"

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


# @responses.activate
# def test_bucketing_alloc():
#     try:
#         try:
#             os.remove("bucketing.json")
#         except Exception as e:
#             print("No Bucketing file")
#
#         json_response = '{"campaigns":[{"id":"bs8qvmo4nlr01fl9aaaa","type":"ab","variationGroups":[{"id":"bs8qvmo4nlr01fl9bbbb","targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","key":"fs_all_users","value":""}]}]},"variations":[{"id":"bs8qvmo4nlr01fl9cccc","modifications":{"type":"JSON","value":{"variation":null}},"reference":true},{"id":"bs8qvmo4nlr01fl9dddd","modifications":{"type":"JSON","value":{"variation":1}},"allocation":25},{"id":"bs8r09g4nlr01c77eeee","modifications":{"type":"JSON","value":{"variation":2}},"allocation":25},{"id":"bs8r09g4nlr01cdkffff","modifications":{"type":"JSON","value":{"variation":3}},"allocation":25},{"id":"bs8r09hsbs4011lbgggg","modifications":{"type":"JSON","value":{"variation":4}},"allocation":25}]}]},{"id":"bs8r119sbs4016mehhhh","type":"ab","variationGroups":[{"id":"bs8r119sbs4016meiiii","targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","key":"fs_all_users","value":""}]}]},"variations":[{"id":"bs8r119sbs4016mejjjj","modifications":{"type":"JSON","value":{"variation50":null}},"reference":true},{"id":"bs8r119sbs4016mekkkk","modifications":{"type":"JSON","value":{"variation50":1}},"allocation":50},{"id":"bs8r119sbs4016mellll","modifications":{"type":"JSON","value":{"variation50":2}},"allocation":50}]}]}]}'
#         responses.reset()
#         headers = {
#             "Last-Modified": "Fri,  05 Jun 2020 12:20:40 GMT"
#         }
#         responses.add(responses.GET,
#                       'https://cdn.flagship.io/my_env_id/bucketing.json',
#                       json=json.loads(json_response), status=200, headers=headers)
#         responses.add(responses.POST,
#                       'https://decision.flagship.io/v2/my_env_id/events',
#                       json=json.loads('{}'), status=200)
#
#         fs = Flagship.instance()
#         fs.start("my_env_id", "my_api_key", Config(mode=Config.Mode.BUCKETING, polling_interval=-1))
#
#         v150 = 0
#         v250 = 0
#         v125 = 0
#         v225 = 0
#         v325 = 0
#         v425 = 0
#
#         x = 50000
#         for i in range(0, x):
#             v = Flagship.instance().create_visitor(get_random_string(10) + "_" + str(i))
#             v.synchronize_modifications()
#             variation = v.get_modification("variation", 0)
#             variation50 = v.get_modification("variation50", 0)
#
#             if variation50 == 1:
#                 v150 += 1
#             elif variation50 == 2:
#                 v250 += 1
#             else:
#                 assert False
#             if variation == 1:
#                 v125 += 1
#             elif variation == 2:
#                 v225 += 1
#             elif variation == 3:
#                 v325 += 1
#             elif variation == 4:
#                 v425 += 1
#             else:
#                 assert False
#
#         print("Results : v150 {}, v250 {}".format(v150, v250))
#         print("Results : v125 {}, v225 {}, v325 {}, v425 {}".format(v125, v225, v325, v425))
#
#         min = (x / 2 - (x * 0.008))
#         max = (x / 2 + (x * 0.008))
#         assert min <= v150 <= max
#         assert min <= v250 <= max
#         assert v150 + v250 == x
#
#         min1 = (x / 4 - (x * 0.008))
#         max1 = (x / 4 + (x * 0.008))
#         assert min1 <= v125 <= max1
#         assert min1 <= v225 <= max1
#         assert min1 <= v325 <= max1
#         assert min1 <= v425 <= max1
#         assert v125 + v225 + v325 + v425 == x
#
#     except Exception as e:
#         print(e)
#         assert False


@responses.activate
def test_bucketing_alloc2():
    try:
        os.remove("bucketing.json")
    except Exception as e:
        print("No Bucketing file")

    json_response = '{"campaigns":[{"id":"bs8qvmo4nlr01fl9aaaa","type":"ab","variationGroups":[{"id":"bs8qvmo4nlr01fl9bbbb","targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","key":"fs_all_users","value":""}]}]},"variations":[{"id":"bs8qvmo4nlr01fl9cccc","modifications":{"type":"JSON","value":{"variation":null}},"reference":true},{"id":"bs8qvmo4nlr01fl9dddd","modifications":{"type":"JSON","value":{"variation":1}},"allocation":25},{"id":"bs8r09g4nlr01c77eeee","modifications":{"type":"JSON","value":{"variation":2}},"allocation":25},{"id":"bs8r09g4nlr01cdkffff","modifications":{"type":"JSON","value":{"variation":3}},"allocation":25},{"id":"bs8r09hsbs4011lbgggg","modifications":{"type":"JSON","value":{"variation":4}},"allocation":25}]}]},{"id":"bs8r119sbs4016mehhhh","type":"ab","variationGroups":[{"id":"bs8r119sbs4016meiiii","targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","key":"fs_all_users","value":""}]}]},"variations":[{"id":"bs8r119sbs4016mejjjj","modifications":{"type":"JSON","value":{"variation50":null}},"reference":true},{"id":"bs8r119sbs4016mekkkk","modifications":{"type":"JSON","value":{"variation50":1}},"allocation":50},{"id":"bs8r119sbs4016mellll","modifications":{"type":"JSON","value":{"variation50":2}},"allocation":50}]}]}]}'
    responses.reset()
    headers = {
        "Last-Modified": "Fri,  05 Jun 2020 12:20:40 GMT"
    }
    responses.add(responses.GET,
                  'https://cdn.flagship.io/my_env_id/bucketing.json',
                  json=json.loads(json_response), status=200, headers=headers)
    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/events',
                  json=json.loads('{}'), status=200)

    fs = Flagship.instance()
    fs.start("my_env_id", "my_api_key", Config(mode=Config.Mode.BUCKETING, polling_interval=-1))
    ids = ["202072017183814142",
           "202072017183860649",
           "202072017183828850",
           "202072017183818733",
           "202072017183823773",
           "202072017183894922",
           "202072017183829817",
           "202072017183842202",
           "202072017233645009",
           "202072017233690230",
           "202072017183886606",
           "202072017183877657",
           "202072017183860380",
           "202072017183972690",
           "202072017183912618",
           "202072017183951364",
           "202072017183920657",
           "202072017183922748",
           "202072017183943575",
           "202072017183987677"
           ]
    variation50 = [1, 1, 1, 1, 2, 1, 1, 1, 2, 2, 1, 1, 1, 2, 1, 1, 2, 2, 1, 1]
    variation25 = [4, 1, 2, 4, 2, 4, 1, 3, 2, 1, 4, 4, 1, 1, 2, 3, 4, 1, 3, 4]

    for i in range(0, len(ids)):
        v = Flagship.instance().create_visitor(ids[i])
        v.synchronize_modifications()
        v25 = v.get_modification("variation", 0)
        v50 = v.get_modification("variation50", 0)
        print("{} v50 {} == variation50[{}] {}".format(ids[i], v50, i, variation50[i]))
        print("{} v25 {} == variation25[{}] {}".format(ids[i], v25, i, variation25[i]))
        assert v25 == variation25[i]
        assert v50 == variation50[i]


@responses.activate
def test_bucketing_polling():
    responses.reset()
    try:
        os.remove("bucketing.json")
    except Exception as e:
        print("No Bucketing file")
    json_response = '{"campaigns":[{"variationGroups":[{"variations":[{"allocation":100,"modifications":{"type":"FLAG","value":{"featureEnabled":true}},"id":"xxxx"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":true,"key":"isVIPUser"}]}]},"id":"yyyy"},{"variations":[{"allocation":100,"modifications":{"type":"FLAG","value":{"featureEnabled":false}},"id":"cccc"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":false,"key":"isVIPUser"}]}]},"id":"vvvv"}],"type":"toggle","id":"aaaa"},{"variationGroups":[{"variations":[{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":null}},"id":"zzzz","reference":true},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":1111}},"id":"eeee"},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":3333}},"id":"rrrr"},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":22.22,"rank":2222}},"id":"tttt"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":"password","key":"access"}]}]},"id":"yyyy"}],"type":"ab","id":"iiii"}]}'
    headers = {
        "Last-Modified": "Fri,  05 Jun 2020 12:20:40 GMT"
    }
    responses.add(responses.GET, 'https://cdn.flagship.io/my_env_id/bucketing.json', json=json.loads(json_response),
                  status=200, headers=headers)

    def add_responses():
        responses.add(responses.POST,
                      'https://decision.flagship.io/v2/my_env_id/events',
                      json=json.loads('{}'), status=200)

        responses.add(responses.POST,
                      'https://decision.flagship.io/v2/my_env_id/events', status=200)

        responses.add(responses.POST, 'https://ariane.abtasty.com/', status=200)

        responses.add(responses.POST, 'https://decision.flagship.io/v2/activate', status=200)

    add_responses()

    fs = Flagship.instance()
    # # print "#=> " + str(fs._bucketing_manager.is_bucketing_thread_running())
    fs.start("my_env_id", "my_api_key", Config(mode=Config.Mode.BUCKETING, polling_interval=2))  # 1

    visitor = fs.create_visitor("visitor1")
    visitor2 = fs.create_visitor("visitor2")

    hit = Screen("test_bucketing_polling_panic")
    i = 0
    while i < 10:  # 10 + 5 polling

        visitor.update_context(("isVIPUser", i % 2 == 0), True)  # 1
        visitor.activate_modification("featureEnabled")  # 1
        visitor.send_hit(hit)  # 1

        visitor2.update_context(("isVIPUser", i % 2 == 1), True)  # 1
        visitor2.activate_modification("featureEnabled")  # 1
        visitor2.send_hit(hit)  # 1

        assert visitor.get_modification("featureEnabled", False) == (i % 2 == 0)
        assert visitor2.get_modification("featureEnabled", False) == (i % 2 == 1)

        i += 1
        time.sleep(1)
    # assert len(responses.calls) == 6
    assert len(responses.calls) == 67
    fs.close()


@responses.activate
def test_bucketing_panic():
    try:
        os.remove("bucketing.json")
    except Exception as e:
        print("No Bucketing file")

    json_response = '{"panic":true}'
    responses.reset()
    headers = {
        "Last-Modified": "Fri,  05 Jun 2020 12:20:40 GMT"
    }
    responses.add(responses.GET,
                  'https://cdn.flagship.io/my_env_id/bucketing.json',
                  json=json.loads(json_response), status=200, headers=headers)
    fs = Flagship.instance()
    fs.start("my_env_id", "my_api_key", Config(mode=Config.Mode.BUCKETING, polling_interval=2))  # 1

    visitor = fs.create_visitor("visitor1")
    visitor2 = fs.create_visitor("visitor2")
    hit = Page("test_bucketing_polling_panic")

    i = 0
    while i < 10:  # 6 polling

        visitor.update_context(("isVIPUser", i % 2 == 0), True)
        visitor.activate_modification("featureEnabled")
        visitor.send_hit(hit)

        visitor2.update_context(("isVIPUser", i % 2 == 1), True)
        visitor2.activate_modification("featureEnabled")
        visitor2.send_hit(hit)

        assert visitor.get_modification("featureEnabled", False) is False
        assert visitor2.get_modification("featureEnabled", False) is False

        i += 1
        time.sleep(1)

    assert (len(responses.calls) == 7 or len(responses.calls) == 6)
    fs.close()
