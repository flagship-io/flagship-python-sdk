import json
import os
from time import sleep

import responses

from flagship import Flagship, Visitor, Status
from flagship.config import Bucketing
from flagship.hits import Screen
from flagship.log_manager import LogLevel, LogManager
from flagship.status_listener import StatusListener
from flagship.targeting_comparator import TargetingComparator
from flagship.tracking_manager import TrackingManagerConfig, CacheStrategy
from test_constants_res import BUCKETING_RESPONSE_1, BUCKETING_URL, BUCKETING_LAST_MODIFIED_1, \
    BUCKETING_CACHED_RESPONSE_1, ACTIVATE_URL, SEGMENT_URL, BUCKETING_RESPONSE_2, BUCKETING_RESPONSE_PANIC, \
    BUCKETING_RESPONSE_EMPTY, EVENTS_URL


@responses.activate
def test_bucketing_config():
    responses.add(responses.GET, BUCKETING_URL, json=json.loads(BUCKETING_RESPONSE_1), status=200,
                  headers=[("Last-Modified", BUCKETING_LAST_MODIFIED_1)])

    Flagship.stop()
    Flagship.start('_env_id_', '_api_key_', Bucketing(polling_interval=500))
    calls = responses.calls._calls
    sleep(2)
    assert len(calls) >= 4

    responses.reset()
    responses.add(responses.GET, BUCKETING_URL, json=json.loads(BUCKETING_RESPONSE_1), status=200,
                  headers=[("Last-Modified", BUCKETING_LAST_MODIFIED_1)])

    Flagship.stop()
    Flagship.start('_env_id_', '_api_key_', Bucketing(polling_interval=200))
    calls = responses.calls._calls
    sleep(2)
    assert len(calls) >= 10

    responses.reset()
    responses.add(responses.GET, BUCKETING_URL, json=json.loads(BUCKETING_RESPONSE_1), status=200,
                  headers=[("Last-Modified", BUCKETING_LAST_MODIFIED_1)])

    Flagship.stop()
    Flagship.start('_env_id_', '_api_key_', Bucketing(polling_interval=-1))
    calls = responses.calls._calls
    sleep(0.5)
    assert len(calls) == 1

@responses.activate
def test_bucketing_file():

    responses.add(responses.GET, BUCKETING_URL, json=json.loads(BUCKETING_RESPONSE_1), status=200,
                  headers=[("Last-Modified", BUCKETING_LAST_MODIFIED_1)])
    os.path.isfile('._env_id_.decision')

    Flagship.stop()
    Flagship.start('_env_id_', '_api_key_', Bucketing(polling_interval=0, log_level=LogLevel.NONE))
    sleep(0.5)
    assert os.path.isfile('._env_id_.decision')
    with open('._env_id_.decision', 'r') as f:
        content = f.read()
        assert json.loads(content) == json.loads(BUCKETING_CACHED_RESPONSE_1)

@responses.activate
def test_bucketing_campaigns():
    responses.add(responses.GET, BUCKETING_URL, json=json.loads(BUCKETING_RESPONSE_1), status=200,
                  headers=[("Last-Modified", BUCKETING_LAST_MODIFIED_1)])
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)
    responses.add(responses.POST, SEGMENT_URL, body="", status=200)
    Flagship.stop()
    Flagship.start('_env_id_', '_api_key_', Bucketing(polling_interval=0,
                                                      log_level=LogLevel.NONE,
                                                      tracking_manager_config=TrackingManagerConfig(
                                                          cache_strategy=CacheStrategy.
                                                          _NO_BATCHING_CONTINUOUS_CACHING)))  # 1 bucketing
    sleep(0.5)

    visitor = Flagship.new_visitor("87524982740", instance_type=Visitor.Instance.NEW_INSTANCE,
                                   context={'isVIPUser': False}) #2 consent
    visitor.fetch_flags() #3 segment
    assert visitor.get_flag('featureEnabled', True).value() is False #4 activate
    assert visitor.get_flag('target', 'default').value() == 'default' #0

    visitor.update_context({
        'isVIPUser': True,
        'sdk_deviceModel': 'Google Pixel X'
    })

    calls = responses.calls._calls
    assert len(calls) == 4
    sleep(0.2)

    visitor.fetch_flags() #5 segment
    assert visitor.get_flag('featureEnabled', False).value() is True #6 activate
    assert visitor.get_flag('target', 'default').value() == 'is' #7 activate

    visitor.update_context({
        'isVIPUser': True,
        'sdk_deviceModel': 'Test Unit'
    })

    calls = responses.calls._calls
    assert len(calls) == 7
    sleep(0.2)

    visitor.fetch_flags() #8 segment
    assert visitor.get_flag('featureEnabled', False).value() is True #9 activate
    assert visitor.get_flag('target', 'default').value() == 'is not' #10 activate


    calls = responses.calls._calls
    assert len(calls) == 10
    for i in range(0, len(calls)):
        try:
            body = json.loads(calls[i].request.body)
            if i == 10:
                assert body['vid'] == '87524982740'
                assert body['cuid'] is None
                assert body['vaid'] == 'bu6lttip17b01emhqqqq'
        except:
            pass

@responses.activate
def test_bucketing_targeting():
    comparator = TargetingComparator()
    assert comparator.compare('EQUALS', 1, 1) is True
    assert comparator.compare('EQUALS', '_hey_', '_hey_') is True
    assert comparator.compare('EQUALS', 1.0, 1) is True
    assert comparator.compare('EQUALS', True, True) is True
    assert comparator.compare('EQUALS', 1, 2) is False
    assert comparator.compare('EQUALS', '_hey_', '__hey__') is False
    assert comparator.compare('EQUALS', 3.1, 3) is False
    assert comparator.compare('EQUALS', True, False) is False
    assert comparator.compare('EQUALS', 'two', ['one', 2, 'two', 3, 'three']) is True
    assert comparator.compare('EQUALS', 'two', ['one', 2, '-two-', 3, 'three']) is False

    assert comparator.compare('NOT_EQUALS', 1, 1) is False
    assert comparator.compare('NOT_EQUALS', '_hey_', '_hey_') is False
    assert comparator.compare('NOT_EQUALS', 1.0, 1) is False
    assert comparator.compare('NOT_EQUALS', True, True) is False
    assert comparator.compare('NOT_EQUALS', 1, 2) is True
    assert comparator.compare('NOT_EQUALS', '_hey_', '__hey__') is True
    assert comparator.compare('NOT_EQUALS', 3.1, 3) is True
    assert comparator.compare('NOT_EQUALS', True, False) is True
    assert comparator.compare('NOT_EQUALS', 'two', ['one', 2, 'two', 3, 'three']) is False
    assert comparator.compare('NOT_EQUALS', 'two', ['one', 2, '-two-', 3, 'three']) is True

    assert comparator.compare('CONTAINS', 'two', ['one', 2, 'two', 3, 'three']) is True
    assert comparator.compare('CONTAINS', 'two', ['one', 2, '-two-', 3, 'three']) is False
    assert comparator.compare('CONTAINS', 'mm-t-w-o-mm', ['one', 2, '-t-w-o-', 3, 'three']) is True
    assert comparator.compare('CONTAINS', 'twenty-two', 'two') is True
    assert comparator.compare('CONTAINS', 3, ['one', 2, '-t-w-o-', 3, 'three']) is True
    assert comparator.compare('CONTAINS', True, ['one', 2, '-t-w-o-', 3, 'three', True]) is True

    assert comparator.compare('NOT_CONTAINS', 'two', ['one', 2, 'two', 3, 'three']) is False
    assert comparator.compare('NOT_CONTAINS', 'two', ['one', 2, '-two-', 3, 'three']) is True
    assert comparator.compare('NOT_CONTAINS', 'mm-t-w-o-mm', ['one', 2, '-t-w-o-', 3, 'three']) is False
    assert comparator.compare('NOT_CONTAINS', 'twenty-two', 'two') is False
    assert comparator.compare('NOT_CONTAINS', 3, ['one', 2, '-t-w-o-', 3, 'three']) is False
    assert comparator.compare('NOT_CONTAINS', True, ['one', 2, '-t-w-o-', 3, 'three', True]) is False

    assert comparator.compare('GREATER_THAN', 'zzzz', ['a', 2, 'l', 3, 'a', True]) is True
    assert comparator.compare('GREATER_THAN', 'cccc', ['ddd', 'eeeeee']) is False
    assert comparator.compare('GREATER_THAN', 'zzzz', 'zzza') is True
    assert comparator.compare('GREATER_THAN', 'zzzz', 'zzzza') is False

    assert comparator.compare('LOWER_THAN', 'zzzz', ['a', 2, 'l', 3, 'a', True]) is False
    assert comparator.compare('LOWER_THAN', 'cccc', ['ddd', 'eeeeee']) is True
    assert comparator.compare('LOWER_THAN', 'zzzz', 'zzza') is False
    assert comparator.compare('LOWER_THAN', 'zzzz', 'zzzza') is True

    assert comparator.compare('GREATER_THAN_OR_EQUALS', 'zzzz', ['a', 2, 'l', 3, 'a', True]) is True
    assert comparator.compare('GREATER_THAN_OR_EQUALS', 'cccc', ['ddd', 'eeeeee']) is False
    assert comparator.compare('GREATER_THAN_OR_EQUALS', 'zzzz', 'zzza') is True
    assert comparator.compare('GREATER_THAN_OR_EQUALS', 'zzzz', 'zzzza') is False
    assert comparator.compare('GREATER_THAN_OR_EQUALS', 'zzzz', ['zzzza', 'zzzz']) is True

    assert comparator.compare('LOWER_THAN_OR_EQUALS', 'zzzz', ['a', 2, 'l', 3, 'a', True]) is False
    assert comparator.compare('LOWER_THAN_OR_EQUALS', 'cccc', ['ddd', 'eeeeee']) is True
    assert comparator.compare('LOWER_THAN_OR_EQUALS', 'zzzz', 'zzza') is False
    assert comparator.compare('LOWER_THAN_OR_EQUALS', 'zzzz', 'zzzza') is True
    assert comparator.compare('LOWER_THAN_OR_EQUALS', 'zzzz', ['zzzza', 'zzzz']) is True

    assert comparator.compare('STARTS_WITH', 'zzzz', ['a', 2, 'l', 3, 'a', True]) is False
    assert comparator.compare('STARTS_WITH', 'cccc', ['ddd', 'eeeeee']) is False
    assert comparator.compare('STARTS_WITH', 'zzzz', 'zzza') is False
    assert comparator.compare('STARTS_WITH', 'zzzz', 'zzzza') is False
    assert comparator.compare('STARTS_WITH', 'zzzz', ['zzzza', 2, True, 'zzzz']) is True

@responses.activate
def test_bucketing_cached_file():
    try:
        os.remove('._env_id_.decision')
    except OSError:
        pass
    responses.add(responses.GET, BUCKETING_URL, json=json.loads(BUCKETING_RESPONSE_1), status=200,
                  headers=[("Last-Modified", BUCKETING_LAST_MODIFIED_1)])
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    # responses.add(responses.POST, ARIANE_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)
    responses.add(responses.POST, SEGMENT_URL, body="", status=200)
    Flagship.stop()
    Flagship.start('_env_id_', '_api_key_', Bucketing(polling_interval=0, log_level=LogLevel.NONE, tracking_manager_config=TrackingManagerConfig(cache_strategy=CacheStrategy._NO_BATCHING_CONTINUOUS_CACHING)))  # 1 bucketing
    sleep(0.2)

    responses.reset()
    responses.remove(responses.GET, BUCKETING_URL)
    responses.add(responses.GET, BUCKETING_URL, json=json.loads(BUCKETING_RESPONSE_1), status=500,
                  headers=[("Last-Modified", BUCKETING_LAST_MODIFIED_1)])
    # responses.add(responses.POST, ARIANE_URL, body="", status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)
    responses.add(responses.POST, SEGMENT_URL, body="", status=200)
    Flagship.stop()

    Flagship.start('_env_id_', '_api_key_', Bucketing(polling_interval=0, log_level=LogLevel.NONE, tracking_manager_config=TrackingManagerConfig(cache_strategy=CacheStrategy._NO_BATCHING_CONTINUOUS_CACHING)))  # 1 bucketing
    sleep(0.2)
    visitor = Flagship.new_visitor("9356925", instance_type=Visitor.Instance.NEW_INSTANCE,
                                   context={'isVIPUser': False})  # 2 consent
    visitor.fetch_flags() #3 segment
    assert visitor.get_flag('featureEnabled', True).value() is False #4 activate
    assert visitor.get_flag('target', 'default').value() == 'default' #0

    visitor.update_context({
        'isVIPUser': True,
        'sdk_deviceModel': 'Google Pixel X'
    })

    calls = responses.calls._calls
    assert len(calls) == 4
    sleep(0.2)

db_path = "./cache/"
def remove_db():
    import shutil
    try:
        shutil.rmtree(db_path)
    except:
        pass

@responses.activate
def test_bucketing_alloc():
    remove_db()
    responses.add(responses.GET, BUCKETING_URL, json=json.loads(BUCKETING_RESPONSE_2), status=200,
                  headers=[("Last-Modified", BUCKETING_LAST_MODIFIED_1)])
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    # responses.add(responses.POST, ARIANE_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)
    responses.add(responses.POST, SEGMENT_URL, body="", status=200)
    Flagship.stop()
    Flagship.start('_env_id_', '_api_key_', Bucketing(polling_interval=0, log_level=LogLevel.NONE, tracking_manager_config=TrackingManagerConfig(
                                                    strategy=CacheStrategy._NO_BATCHING_CONTINUOUS_CACHING)))  # 1 bucketing
    sleep(0.5)
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
        visitor = Flagship.new_visitor(ids[i], instance_type=Visitor.Instance.NEW_INSTANCE,
                                       context={'isVIPUser': False})  # 2 consent
        visitor.fetch_flags()
        v25 = visitor.get_flag("variation", 0).value(False)
        v50 = visitor.get_flag("variation50", 0).value(False)
        print("{} v50 {} == variation50[{}] {}".format(ids[i], v50, i, variation50[i]))
        print("{} v25 {} == variation25[{}] {}".format(ids[i], v25, i, variation25[i]))
        if v25 != variation25[i]:
            print("Error = {} - expected {} got {}".format(ids[i], variation25[i], v25))
        if v50 != variation50[i]:
            print("Error = {} - expected {} got {}".format(ids[i], variation50[i], v50))
        assert v25 == variation25[i]
        assert v50 == variation50[i]


@responses.activate
def test_bucketing_panic():

    class CustomLogManager(LogManager):

        def __init__(self):
            self.deactivated_method_log_cnt = 0

        def log(self, tag, level, message):
            print(message)
            if 'deactivated: SDK is running in panic mode' in message:
                self.deactivated_method_log_cnt += 1

        def exception(self, exception, traceback):
            pass

    class CustomStatusListener(StatusListener):

        def __init__(self, function):
            self.function = function

        def on_status_changed(self, new_status):
            print("New status = " + str(new_status))
            if new_status.value >= Status.PANIC.value:
                self.function()

    custom_log_manager = CustomLogManager()


    def run():
        visitor = Flagship.new_visitor("87ab-5c2c-fe49-82dd-403a", instance_type=Visitor.Instance.NEW_INSTANCE,
                                       context={'isVIPUser': False})  # +0 consent
        visitor.fetch_flags()  # +0 context
        visitor.send_hit(Screen("test_bucketing_panic"))  #+0 hit
        visitor.authenticate("disabled")
        assert visitor.get_flag("key", 0).value() == 0  # +0 activate



    responses.add(responses.GET, BUCKETING_URL, json=json.loads(BUCKETING_RESPONSE_PANIC), status=200,  # +2 bucketing
                  headers=[("Last-Modified", BUCKETING_LAST_MODIFIED_1)])
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)
    responses.add(responses.POST, SEGMENT_URL, body="", status=200)
    Flagship.stop()
    Flagship.start('_env_id_', '_api_key_', Bucketing(polling_interval=600, status_listener=CustomStatusListener(run),
                                                      log_manager=custom_log_manager))
    sleep(1)
    calls = responses.calls._calls
    assert len(calls) == 2
    assert custom_log_manager.deactivated_method_log_cnt == 4
    sleep(1)



@responses.activate
def test_bucketing_304():

    class CustomStatusListener(StatusListener):

        def __init__(self, function):
            self.function = function

        def on_status_changed(self, new_status):
            print("New status = " + str(new_status))
            if new_status.value >= Status.PANIC.value:
                self.function()


    class Runner():

        visitor = None
        errors = 0

        def run(self, step=0):
            try:
                pass
                if self.visitor is None:
                    self.visitor = Flagship.new_visitor("87ab-5c2c-fe49-82dd-403a", instance_type=Visitor.Instance.NEW_INSTANCE,
                                                   context={'isVIPUser': True})  # +1 consent
                if step == 0:
                    self.visitor.fetch_flags()  # +1 context
                    assert self.visitor.get_flag("featureEnabled", False).value() is True  # +1 activate
                if step == 1:
                    self.visitor.fetch_flags()  # +1 context
                    assert self.visitor.get_flag("featureEnabled", False).value() is True  # +1 activate
                if step == 2:
                    self.visitor.fetch_flags()  # +1 context
                    assert self.visitor.get_flag("featureEnabled", 0).value() == 0  # +0 activate
            except Exception as e:
                self.errors += 1

    runner = Runner()

    responses.reset()
    responses.add(responses.GET, BUCKETING_URL, json=json.loads(BUCKETING_RESPONSE_1), status=200,
                  headers=[("Last-Modified", BUCKETING_LAST_MODIFIED_1)])
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)
    responses.add(responses.POST, SEGMENT_URL, body="", status=200)
    Flagship.stop()
    Flagship.start('_env_id_', '_api_key_', Bucketing(polling_interval=200, status_listener=CustomStatusListener(runner.run)))  # +1 bucketing
    sleep(0.2)

    responses.reset()
    responses.add(responses.GET, BUCKETING_URL, json=json.loads(BUCKETING_RESPONSE_EMPTY), status=304,
                  headers=[("Last-Modified", BUCKETING_LAST_MODIFIED_1)])
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)
    responses.add(responses.POST, SEGMENT_URL, body="", status=200)
    runner.run(1)
    sleep(0.2)  # +1 Bucketing

    responses.reset()
    responses.add(responses.GET, BUCKETING_URL, json=json.loads(BUCKETING_RESPONSE_EMPTY), status=200,
                  headers=[("Last-Modified", BUCKETING_LAST_MODIFIED_1)])
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)
    responses.add(responses.POST, SEGMENT_URL, body="", status=200)
    runner.run(2)
    sleep(0.2)  # +1 Bucketing
    assert runner.errors == 0

