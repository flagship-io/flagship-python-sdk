import json
from time import sleep

import responses

from flagship import Flagship, Visitor
from flagship.config import DecisionApi
from flagship.flagship_context import FlagshipContext
from flagship.hits import Screen
from flagship.log_manager import LogManager
from flagship.tracking_manager import TrackingManagerConfig, CacheStrategy
from test_constants_res import API_RESPONSE_1, DECISION_API_URL, ACTIVATE_URL, \
    API_RESPONSE_3, EVENTS_URL


def test_visitor_creation_default():
    Flagship.start('_env_id_', '_api_key_', DecisionApi())

    _visitor_1 = Flagship.new_visitor('_visitor_1')
    assert _visitor_1.visitor_id == '_visitor_1'
    assert _visitor_1.anonymous_id is None
    assert len(_visitor_1.context) == 2
    assert _visitor_1.context['fs_version'] == get_version()
    assert _visitor_1.context['fs_client'] == 'python'
    assert _visitor_1.is_authenticated is False
    assert _visitor_1.has_consented is True
    assert _visitor_1._configuration_manager is not None
    assert _visitor_1._config is not None
    assert isinstance(_visitor_1._config, DecisionApi)
    assert len(_visitor_1._modifications) == 0


def test_visitor_creation_custom():
    Flagship.stop()
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
    _visitor_2 = Flagship.new_visitor('_visitor_2',
                                      context=context,
                                      authenticated=True,
                                      consent=False,
                                      instance_type=Visitor.Instance.SINGLE_INSTANCE)
    assert _visitor_2.visitor_id == '_visitor_2'
    assert _visitor_2.anonymous_id is not None
    assert len(_visitor_2.context) == 6
    assert _visitor_2.context['fs_version'] == get_version()
    assert _visitor_2.context['fs_client'] == 'python'
    assert _visitor_2.is_authenticated is True
    assert _visitor_2.has_consented is False
    assert _visitor_2._configuration_manager is not None
    assert _visitor_2._config is not None
    assert isinstance(_visitor_2._config, DecisionApi)
    assert len(_visitor_2._modifications) == 0


def test_visitor_creation_instance():
    Flagship.stop()

    Flagship.start('_env_id_', '_api_key_', DecisionApi())

    assert Flagship.get_visitor() is None

    _visitor_3 = Flagship.new_visitor('_visitor_3', instance_type=Visitor.Instance.SINGLE_INSTANCE)

    assert Flagship.get_visitor().visitor_id == '_visitor_3'

    _visitor_4 = Flagship.new_visitor('_visitor_4', instance_type=Visitor.Instance.SINGLE_INSTANCE)

    assert Flagship.get_visitor().visitor_id == '_visitor_4'

    _visitor_5 = Flagship.new_visitor('_visitor_5', instance_type=Visitor.Instance.NEW_INSTANCE)

    assert Flagship.get_visitor().visitor_id == '_visitor_4'


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
        'sdk_osName': 0,  # Won't be added
        'sdk_interfaceName': 'test_visitor.py',
        FlagshipContext.LOCATION_COUNTRY: 'France'

    }
    _visitor_6.update_context(context1)

    assert len(_visitor_6.context) == 8  # +2 from preset context
    assert _visitor_6.context['fs_version'] == get_version()
    assert 'sdk_osName' not in _visitor_6.context
    assert _visitor_6.context['sdk_interfaceName'] == 'test_visitor.py'
    assert _visitor_6.context['int'] == 12
    assert _visitor_6.context[FlagshipContext.LOCATION_COUNTRY.value[0]] == 'France'

    _visitor_6.update_context(('sdk_interfaceName', 'test_visitor.py 2'))
    _visitor_6.update_context(('fs_client', 'not python'))
    _visitor_6.update_context(('sdk_osName', 'Ubuntu'))
    _visitor_6.update_context(('class', clazz()))
    _visitor_6.update_context(('int', 31))
    _visitor_6.update_context((FlagshipContext.APP_VERSION_NAME, "unit_test"))
    _visitor_6.update_context((FlagshipContext.APP_VERSION_CODE, "wrong"))

    assert len(_visitor_6.context) == 10
    assert _visitor_6.context['fs_version'] == get_version()
    assert _visitor_6.context['sdk_interfaceName'] == 'test_visitor.py 2'
    assert _visitor_6.context['int'] == 31
    assert _visitor_6.context['sdk_osName'] == 'Ubuntu'
    assert FlagshipContext.APP_VERSION_CODE.value[0] not in _visitor_6.context
    assert _visitor_6.context[FlagshipContext.APP_VERSION_NAME.value[0]] == 'unit_test'


@responses.activate
def test_visitor_consent():
    Flagship.stop()
    responses.calls.reset()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    # responses.add(responses.POST, ARIANE_URL, body="", status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)

    Flagship.start('_env_id_', '_api_key_', DecisionApi(tracking_manager_config=TrackingManagerConfig(
                                                    cache_strategy=CacheStrategy._NO_BATCHING_CONTINUOUS_CACHING)))

    _visitor_10 = Flagship.new_visitor('_visitor_10', instance_type=Visitor.Instance.NEW_INSTANCE)#1
    _visitor_11 = Flagship.new_visitor('_visitor_11', instance_type=Visitor.Instance.NEW_INSTANCE, consent=False)
    _visitor_11.set_consent(True)
    sleep(0.3)
    _visitor_11.set_consent(False)
    sleep(0.3)
    calls = responses.calls._calls
    assert len(calls) == 4
    for i in range(0, len(calls)):
        c = calls[i]
        if EVENTS_URL in c.request.url:
            body = json.loads(c.request.body)
            if i == 0:
                assert body['t'] == 'EVENT'
                assert body['ds'] == 'APP'
                assert body['cid'] == '_env_id_'
                assert body['vid'] == '_visitor_10'
                assert body['ec'] == 'User Engagement'
                assert body['ea'] == 'fs_consent'
                assert body['el'] == 'python:true'
            if i == 1 or i == 3:
                assert body['t'] == 'EVENT'
                assert body['ds'] == 'APP'
                assert body['cid'] == '_env_id_'
                assert body['vid'] == '_visitor_11'
                assert body['ec'] == 'User Engagement'
                assert body['ea'] == 'fs_consent'
                assert body['el'] == 'python:false'
            if i == 2:
                assert body['t'] == 'EVENT'
                assert body['ds'] == 'APP'
                assert body['cid'] == '_env_id_'
                assert body['vid'] == '_visitor_11'
                assert body['ec'] == 'User Engagement'
                assert body['ea'] == 'fs_consent'
                assert body['el'] == 'python:true'


@responses.activate
def test_visitor_xpc():
    Flagship.stop()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    # responses.add(responses.POST, ARIANE_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)

    Flagship.start('_env_id_', '_api_key_', DecisionApi(tracking_manager_config=TrackingManagerConfig(
                                                    cache_strategy=CacheStrategy._NO_BATCHING_CONTINUOUS_CACHING)))

    visitor = Flagship.new_visitor('anonymous', instance_type=Visitor.Instance.NEW_INSTANCE)
    # anonymous
    visitor.fetch_flags()
    visitor.get_flag("visitorIdColor", "default").visitor_exposed()
    visitor.send_hit(Screen("test_visitor.py"))
    sleep(0.3)
    # authenticate user_001
    visitor.authenticate("user_001")
    visitor.fetch_flags()
    visitor.get_flag("visitorIdColor", "default").visitor_exposed()
    visitor.send_hit(Screen("test_visitor.py"))
    sleep(0.3)
    # unauthenticate
    visitor.unauthenticate()
    visitor.fetch_flags()
    visitor.get_flag("visitorIdColor", "default").visitor_exposed()
    visitor.send_hit(Screen("test_visitor.py"))
    sleep(0.3)
    calls = responses.calls._calls
    assert len(calls) == 10
    for i in range(0, len(calls)):
        body = json.loads(calls[i].request.body)
        if i == 0:
            assert body['vid'] == 'anonymous'
            assert body['cuid'] is None
        if i == 1:
            assert body['visitorId'] == 'anonymous'
            assert body['anonymousId'] is None
        if i == 2:
            # assert body['vid'] == 'anonymous'
            # assert body['aid'] is None
            assert body['batch'][0]['vid'] == 'anonymous'
            assert body['batch'][0]['aid'] is None
        if i == 3:
            assert body['vid'] == 'anonymous'
            assert body['cuid'] is None
        if i == 4:
            assert body['visitorId'] == 'user_001'
            assert body['anonymousId'] == 'anonymous'
        if i == 5:
            # assert body['vid'] == 'user_001'
            # assert body['aid'] == 'anonymous'
            assert body['batch'][0]['vid'] == 'user_001'
            assert body['batch'][0]['aid'] == 'anonymous'
        if i == 6:
            assert body['vid'] == 'anonymous'
            assert body['cuid'] == 'user_001'
        if i == 7:
            assert body['visitorId'] == 'anonymous'
            assert body['anonymousId'] is None
        if i == 8:
            # assert body['vid'] == 'anonymous'
            # assert body['aid'] is None
            assert body['batch'][0]['vid'] == 'anonymous'
            assert body['batch'][0]['aid'] is None
        if i == 9:
            assert body['vid'] == 'anonymous'
            assert body['cuid'] is None


@responses.activate
def test_visitor_strategy_panic():
    class CustomLogManager(LogManager):

        def __init__(self):
            self.deactivated_method_log_cnt = 0

        def log(self, tag, level, message):
            print(message)
            if 'deactivated: SDK is running in panic mode' in message:
                self.deactivated_method_log_cnt += 1

        def exception(self, exception, traceback):
            pass

    custom_log_manager = CustomLogManager()
    Flagship.stop()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_3), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    # responses.add(responses.POST, ARIANE_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)

    Flagship.start('_env_id_', '_api_key_', DecisionApi(log_manager=custom_log_manager, tracking_manager_config=TrackingManagerConfig(
                                                    cache_strategy=CacheStrategy._NO_BATCHING_CONTINUOUS_CACHING)))
    assert Flagship.status() == Flagship.status().READY
    visitor = Flagship.new_visitor("visitor_xxx")
    visitor.fetch_flags()
    sleep(0.3)
    assert Flagship.status() == Flagship.status().PANIC
    visitor.update_context(("key", "value"))
    visitor.authenticate("user_001")
    visitor.get_flag("visitorIdColor", "default").visitor_exposed()
    visitor.send_hit(Screen("test_visitor.py"))
    visitor.fetch_flags()
    visitor.set_consent(True)
    calls = responses.calls._calls
    sleep(0.1)
    assert len(calls) == 3
    assert custom_log_manager.deactivated_method_log_cnt == 4

    sleep(1)
    custom_log_manager.deactivated_method_log_cnt = 0
    responses.reset()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)
    sleep(0.1)
    visitor.fetch_flags()
    visitor.update_context(("key", "value"))
    visitor.authenticate("user_001")
    visitor.get_flag("visitorIdColor", "default").visitor_exposed()
    visitor.send_hit(Screen("test_visitor.py"))
    visitor.fetch_flags()
    visitor.set_consent(False)
    calls = responses.calls._calls
    assert len(calls) == 5
    assert custom_log_manager.deactivated_method_log_cnt == 0


@responses.activate
def test_visitor_strategy_not_ready():
    Flagship.stop()
    class CustomLogManager(LogManager):

        def __init__(self):
            self.deactivated_method_log_cnt = 0

        def log(self, tag, level, message):
            print(message)
            if 'deactivated: SDK is not started yet' in message:
                self.deactivated_method_log_cnt += 1

        def exception(self, exception, traceback):
            pass

    custom_log_manager = CustomLogManager()
    configuration_manager = Flagship.new_visitor("visitor_xxx")._configuration_manager
    configuration_manager.flagship_config.log_manager = custom_log_manager

    visitor = Visitor(configuration_manager, "visitor_xxx")

    visitor.fetch_flags()
    sleep(0.3)
    assert Flagship.status() == Flagship.status().NOT_INITIALIZED
    visitor.update_context(("key", "value"))
    visitor.authenticate("user_001")
    visitor.get_flag("visitorIdColor", "default").visitor_exposed()
    visitor.send_hit(Screen("test_visitor.py"))
    visitor.fetch_flags()
    visitor.set_consent(True)
    calls = responses.calls._calls
    sleep(0.1)
    assert len(calls) == 0
    assert custom_log_manager.deactivated_method_log_cnt == 10


@responses.activate
def test_visitor_strategy_no_consent():
    class CustomLogManager(LogManager):

        def __init__(self):
            self.deactivated_method_log_cnt = 0

        def log(self, tag, level, message):
            print(message)
            if 'deactivated' in message and 'consent' in message:
                self.deactivated_method_log_cnt += 1

        def exception(self, exception, traceback):
            pass

    custom_log_manager = CustomLogManager()
    Flagship.stop()

    # responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    # responses.add(responses.POST, ARIANE_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)

    Flagship.start('_env_id_', '_api_key_', DecisionApi(log_manager=custom_log_manager, tracking_manager_config=TrackingManagerConfig(
                                                    cache_strategy=CacheStrategy._NO_BATCHING_CONTINUOUS_CACHING)))
    assert Flagship.status() == Flagship.status().READY
    visitor = Flagship.new_visitor("visitor_xxx", consent=False)  # +1
    visitor.fetch_flags() # +1
    visitor.update_context(("key", "value"))
    visitor.authenticate("user_001")
    visitor.get_flag("visitorIdColor", "default").visitor_exposed()  ## X
    visitor.send_hit(Screen("test_visitor.py"))  ## X
    visitor.fetch_flags() # +1
    visitor.set_consent(True)  # +1
    calls = responses.calls._calls
    sleep(0.1)
    assert len(calls) == 4
    assert custom_log_manager.deactivated_method_log_cnt == 2


def get_version():
    from flagship import __version__
    return __version__
