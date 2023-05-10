import json
from time import sleep

import responses

from flagship import Flagship, Visitor
from flagship.config import DecisionApi
from flagship.tracking_manager import TrackingManagerConfig, CacheStrategy
from test_constants_res import DECISION_API_URL, API_RESPONSE_1, API_RESPONSE_2, ACTIVATE_URL, EVENTS_URL


@responses.activate
def test_visitor_get_flags():
    Flagship.stop()
    responses.reset()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)

    Flagship.start('_env_id_', '_api_key_', DecisionApi())

    _visitor_7 = Flagship.new_visitor('_visitor_7', instance_type=Visitor.Instance.NEW_INSTANCE)

    _visitor_7.fetch_flags()

    class clazz():
        pass

    assert _visitor_7.get_flag("int_do_not_exists", 4).value(False) == 4
    assert _visitor_7.get_flag("int_do_not_exists", 4).exists() is False
    assert _visitor_7.get_flag("string_do_not_exists", "nope").value(False) == "nope"
    assert _visitor_7.get_flag("float_do_not_exists", 1.11).value(False) == 1.11
    assert _visitor_7.get_flag("json_do_not_exists", {}).value(False) == {}
    assert _visitor_7.get_flag("array_do_not_exists", []).value(False) == []
    assert _visitor_7.get_flag("bool_do_not_exists", True).value(False) is True
    assert _visitor_7.get_flag("none_do_not_exists", None).value(False) is None
    assert isinstance(_visitor_7.get_flag("class_do_not_exists", clazz()).value(False), clazz)

    assert _visitor_7.get_flag("featureEnabled", False).exists() is True
    assert _visitor_7.get_flag("featureEnabled", False).value(False) is True

    assert _visitor_7.get_flag("title", "default").exists() is True
    assert _visitor_7.get_flag("title", "default").value(False) == "Hello"
    assert _visitor_7.get_flag("title", 3).value(False) == 3

    assert _visitor_7.get_flag("string", "default").value(False) == "default"

    assert 'variation' in _visitor_7.get_flag("json", {}).value(False)
    assert 'string' in _visitor_7.get_flag("json", {}).value(False)

    responses.reset()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_2), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)

    _visitor_7.fetch_flags()

    assert _visitor_7.get_flag("featureEnabled", False).exists() is False
    assert _visitor_7.get_flag("featureEnabled", False).value(False) is False

    assert _visitor_7.get_flag("title", "default").exists() is True
    assert _visitor_7.get_flag("title", "default").value(False) == "Hey"
    assert _visitor_7.get_flag("title", 3).value(False) == 3

    assert _visitor_7.get_flag("string", "default").value(False) == "b"

    assert 'variation' in _visitor_7.get_flag("json", {}).value(False)
    assert 'string' not in _visitor_7.get_flag("json", {}).value(False)


@responses.activate
def test_flag_metadata():
    Flagship.stop()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    # responses.add(responses.POST, ARIANE_URL, body="", status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)

    Flagship.start('_env_id_', '_api_key_', DecisionApi())

    _visitor_8 = Flagship.new_visitor('_visitor_8', instance_type=Visitor.Instance.NEW_INSTANCE)

    _visitor_8.fetch_flags()

    assert _visitor_8.get_flag("flag_do_not exists", "default").exists() is False
    metadata = _visitor_8.get_flag("flag_do_not exists", "default").metadata()
    assert metadata.variation_id == ""
    assert metadata.variation_group_id == ""
    assert metadata.campaign_id == ""
    assert metadata.campaign_slug == ""
    assert metadata.campaign_type == ""
    assert metadata.is_reference is False
    assert metadata.exists() is False
    assert len(metadata.toJson()) == 6
    assert metadata.toJson()['campaignId'] == ""
    assert metadata.toJson()['variationId'] == ""
    assert metadata.toJson()['variationGroupId'] == ""
    assert metadata.toJson()['campaignType'] == ""
    assert metadata.toJson()['campaignSlug'] == ""
    assert metadata.toJson()['isReference'] is False

    assert _visitor_8.get_flag("visitorIdColor", "default").exists() is True
    metadata = _visitor_8.get_flag("visitorIdColor", "default").metadata()
    assert metadata.variation_id == "bmsor064jaeg0goooooo"
    assert metadata.variation_group_id == "bmsor064jaeg0guuuuuu"
    assert metadata.campaign_id == "bmsor064jaeg0giiiiii"
    assert metadata.campaign_slug is None
    assert metadata.campaign_type == "ab"
    assert metadata.is_reference is False
    assert metadata.exists() is True
    assert len(metadata.toJson()) == 6
    assert metadata.toJson()['campaignId'] == "bmsor064jaeg0giiiiii"
    assert metadata.toJson()['variationId'] == "bmsor064jaeg0goooooo"
    assert metadata.toJson()['variationGroupId'] == "bmsor064jaeg0guuuuuu"
    assert metadata.toJson()['campaignType'] == "ab"
    assert metadata.toJson()['campaignSlug'] is None
    assert metadata.toJson()['isReference'] is False

    assert _visitor_8.get_flag("string", "default").exists() is True
    metadata = _visitor_8.get_flag("string", "default").metadata()
    assert metadata.variation_id == "c348750k33nnjpeeeeee"
    assert metadata.variation_group_id == "c348750k33nnjpaaaaaa"
    assert metadata.campaign_id == "c348750k33nnjpzzzzzz"
    assert metadata.campaign_slug is None
    assert metadata.campaign_type == "ab"
    assert metadata.is_reference is False
    assert metadata.exists() is True


@responses.activate
def test_flag_user_exposed():
    Flagship.stop()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    # responses.add(responses.POST, ARIANE_URL, body="", status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)

    Flagship.start('_env_id_', '_api_key_', DecisionApi(tracking_manager_config=TrackingManagerConfig(
                                                    cache_strategy=CacheStrategy._NO_BATCHING_CONTINUOUS_CACHING)))

    _visitor_9 = Flagship.new_visitor('_visitor_9', instance_type=Visitor.Instance.NEW_INSTANCE)

    _visitor_9.fetch_flags()

    _visitor_9.get_flag("visitorIdColor", "default").user_exposed()
    _visitor_9.get_flag("title", "default").value(True)
    assert _visitor_9.get_flag('string', "default").value(False) == "default"
    assert _visitor_9.get_flag('string', "default").value(True) == "default"
    sleep(1)

    calls = responses.calls._calls
    assert len(calls) == 5
    for i in range(0, len(calls)):
        c = calls[i]
        if ACTIVATE_URL in c.request.url:
            body = json.loads(c.request.body)
            assert body['cid'] == '_env_id_'
            if i == 2 or i == 3:
                assert body['batch'][0]['vid'] == '_visitor_9'
                assert body['batch'][0]['aid'] is None
                assert body['batch'][0]['caid'] == 'bmsor064jaeg0guuuuuu'
                assert body['batch'][0]['vaid'] == 'bmsor064jaeg0goooooo'
            if i == 4:
                # assert body['batch'][0]['cid'] == '_env_id_'
                assert body['batch'][0]['vid'] == '_visitor_9'
                assert body['batch'][0]['aid'] is None
                assert body['batch'][0]['caid'] == 'c348750k33nnjpaaaaaa'
                assert body['batch'][0]['vaid'] == 'c348750k33nnjpeeeeee'