import json
from time import sleep

from flagship import Flagship, Visitor
from flagship.config import DecisionApi
from flagship.flagship_context import FlagshipContext
import responses

from tests.test_constants_res import API_RESPONSE_1, DECISION_API_URL, ARIANE_URL, API_RESPONSE_2


def test_visitor_creation_default():
    Flagship.start('_env_id_', '_api_key_', DecisionApi())

    _visitor_1 = Flagship.new_visitor('_visitor_1')
    assert _visitor_1._visitor_id == '_visitor_1'
    assert _visitor_1._anonymous_id is None
    assert len(_visitor_1._context) == 2
    assert _visitor_1._context['fs_version'] == get_version()
    assert _visitor_1._context['fs_client'] == 'python'
    assert _visitor_1._is_authenticated is False
    assert _visitor_1._has_consented is True
    assert _visitor_1._configuration_manager is not None
    assert _visitor_1._config is not None
    assert isinstance(_visitor_1._config, DecisionApi)
    assert len(_visitor_1._modifications) == 0


def test_visitor_creation_custom():
    Flagship.start('_env_id_', '_api_key_', DecisionApi())

    class clazz:
        pass

    context = {
        'wrong': dict(),  # Won't be added
        'float': 3.14,
        'int': 12,
        'str': 'custom_string',
        'none': None,  # Won't be added
        'bool': False,
        'class': clazz()  # Won't be added
    }
    assert Flagship.get_visitor() is None
    _visitor_2 = Flagship.new_visitor('_visitor_2', context=context, authenticated=True, consent=False,
                                      instance_type=Visitor.Instance.SINGLE_INSTANCE)
    assert _visitor_2._visitor_id == '_visitor_2'
    assert _visitor_2._anonymous_id is not None
    assert len(_visitor_2._context) == 6
    assert _visitor_2._context['fs_version'] == get_version()
    assert _visitor_2._context['fs_client'] == 'python'
    assert _visitor_2._is_authenticated is True
    assert _visitor_2._has_consented is False
    assert _visitor_2._configuration_manager is not None
    assert _visitor_2._config is not None
    assert isinstance(_visitor_2._config, DecisionApi)
    assert len(_visitor_2._modifications) == 0


def test_visitor_creation_instance():
    Flagship.stop()

    Flagship.start('_env_id_', '_api_key_', DecisionApi())

    assert Flagship.get_visitor() is None

    _visitor_3 = Flagship.new_visitor('_visitor_3', instance_type=Visitor.Instance.SINGLE_INSTANCE)

    assert Flagship.get_visitor()._visitor_id == '_visitor_3'

    _visitor_4 = Flagship.new_visitor('_visitor_4', instance_type=Visitor.Instance.SINGLE_INSTANCE)

    assert Flagship.get_visitor()._visitor_id == '_visitor_4'

    _visitor_5 = Flagship.new_visitor('_visitor_5', instance_type=Visitor.Instance.NEW_INSTANCE)

    assert Flagship.get_visitor()._visitor_id == '_visitor_4'


def test_visitor_update_context():
    Flagship.start('_env_id_', '_api_key_', DecisionApi())

    _visitor_6 = Flagship.new_visitor('_visitor_6', instance_type=Visitor.Instance.NEW_INSTANCE)

    class clazz:
        pass

    context1 = {
        'wrong': dict(),  # Won't be added
        'float': 3.14,
        'int': 12,
        'str': 'custom_string',
        'none': None,  # Won't be added
        'bool': False,
        'class': clazz(),  # Won't be added
        'fs_client': 'not python',  # Won't be added
        'fs_version': '0.0.0',  # Won't be added
        'sdk_deviceType': 'unit_test',
        'sdk_osName': 0,    # Won't be added
        'sdk_interfaceName': 'test_visitor.py',
        FlagshipContext.LOCATION_COUNTRY: 'France'

    }
    _visitor_6.update_context(context1)

    assert len(_visitor_6._context) == 8    # +2 from preset context
    assert _visitor_6._context['fs_version'] == get_version()
    assert 'sdk_osName' not in _visitor_6._context
    assert _visitor_6._context['sdk_interfaceName'] == 'test_visitor.py'
    assert _visitor_6._context['int'] == 12
    assert _visitor_6._context[FlagshipContext.LOCATION_COUNTRY.value[0]] == 'France'

    _visitor_6.update_context(('sdk_interfaceName', 'test_visitor.py 2'))
    _visitor_6.update_context(('fs_client', 'not python'))
    _visitor_6.update_context(('sdk_osName', 'Ubuntu'))
    _visitor_6.update_context(('class', clazz()))
    _visitor_6.update_context(('int', 31))
    _visitor_6.update_context((FlagshipContext.APP_VERSION_NAME, "unit_test"))
    _visitor_6.update_context((FlagshipContext.APP_VERSION_CODE, "wrong"))

    assert len(_visitor_6._context) == 10
    assert _visitor_6._context['fs_version'] == get_version()
    assert _visitor_6._context['sdk_interfaceName'] == 'test_visitor.py 2'
    assert _visitor_6._context['int'] == 31
    assert _visitor_6._context['sdk_osName'] == 'Ubuntu'
    assert FlagshipContext.APP_VERSION_CODE.value[0] not in _visitor_6._context
    assert _visitor_6._context[FlagshipContext.APP_VERSION_NAME.value[0]] == 'unit_test'

@responses.activate
def test_visitor_get_flags():
    responses.reset()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, ARIANE_URL, body="", status=200)

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
    responses.add(responses.POST, ARIANE_URL, body="", status=200)

    _visitor_7.fetch_flags()

    assert _visitor_7.get_flag("featureEnabled", False).exists() is True
    assert _visitor_7.get_flag("featureEnabled", False).value(False) is True

    assert _visitor_7.get_flag("title", "default").exists() is True
    assert _visitor_7.get_flag("title", "default").value(False) == "Hey"
    assert _visitor_7.get_flag("title", 3).value(False) == 3

    assert _visitor_7.get_flag("string", "default").value(False) == "b"

    assert 'variation' in _visitor_7.get_flag("json", {}).value(False)
    assert 'string' not in _visitor_7.get_flag("json", {}).value(False)


@responses.activate
def test_flag_metadata():
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, ARIANE_URL, body="", status=200)

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
    responses.add(responses.POST, ARIANE_URL, body="", status=200)

    Flagship.start('_env_id_', '_api_key_', DecisionApi())

    _visitor_9 = Flagship.new_visitor('_visitor_9', instance_type=Visitor.Instance.NEW_INSTANCE)

    _visitor_9.fetch_flags()

    _visitor_9.get_flag("visitorIdColor", "default").user_exposed()
    _visitor_9.get_flag("visitorIdColor", "default").value(True)
    sleep(1)


def test_visitor_consent():
    pass

def test_visitor_xpc():
    pass

def test_visitor_strategy_panic():
    pass

def test_visitor_strategy_not_ready():
    pass

def test_visitor_strategy_no_consent():
    pass




def get_version():
    from flagship import __version__
    return __version__
