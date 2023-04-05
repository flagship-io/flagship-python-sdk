import asyncio
import json
import sqlite3 as sl
import time
import traceback

import responses

from flagship import Flagship, Visitor
from flagship.cache_manager import SqliteCacheManager, CacheManager, VisitorCacheImplementation, HitCacheImplementation
from flagship.config import DecisionApi, Bucketing
from flagship.hits import Screen, Event, EventCategory
from flagship.log_manager import LogManager, LogLevel
from flagship.tracking_manager import TrackingManagerConfig, TrackingManagerStrategy
from test_constants_res import DECISION_API_URL, API_RESPONSE_1, ACTIVATE_URL, EVENTS_URL, API_RESPONSE_3, \
    BUCKETING_URL, BUCKETING_RESPONSE_1, BUCKETING_LAST_MODIFIED_1

db_name = "test_db"
db_path = "./cache/"
env_id = "_env_id_"
api_key = "_api_key_"


def get_db_hits():
    try:
        full_db_path = db_path + '/' + env_id + "-cache.db"
        con = sl.connect(full_db_path)
        with con:
            cursor = con.cursor()
            cursor.execute("SELECT id, data FROM HITS")
            result_as_dict = {}
            result = cursor.fetchall()
            if result:
                cursor.close()
                for k, v in result:
                    result_as_dict[k] = json.loads(v)
            return result_as_dict
    except:
        print(traceback.format_exc())
        return None


def remove_db():
    import shutil
    try:
        shutil.rmtree(db_path)
    except:
        pass


@responses.activate
def test_hit_continuous_strategy():
    Flagship.stop()
    remove_db()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=500)

    assert get_db_hits() is None
    Flagship.start(env_id, api_key, DecisionApi(timeout=3000,
                                                tracking_manager_config=TrackingManagerConfig(max_pool_size=10,
                                                                                              time_interval=2000),
                                                cache_manager=SqliteCacheManager(local_db_path=db_path)))
    time.sleep(0.1)  # time to let the first polling
    visitor = Flagship.new_visitor("test_visitor_1", instance_type=Visitor.Instance.SINGLE_INSTANCE)  # +1 consent
    visitor.fetch_flags()  # call /campaign
    visitor.send_hit(Screen("test_hit_continuous_strategy"))  # +1 Screen
    assert visitor.get_flag('string', "default").value() == 'default'  # +1 activate /activate
    assert len(get_db_hits()) == 3
    visitor.set_consent(False)  # +1 Consent -1 screen -1 Activate #
    assert len(get_db_hits()) == 2
    # time.sleep(100000000)
    visitor.set_consent(True)  # +1 Consent
    visitor.send_hit(Screen("test_hit_continuous_strategy"))  # +1 Screen
    assert len(get_db_hits()) == 4
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "action1"))  # +1 Event
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "action2"))  # +1 Event
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "action3"))  # +1 Event
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "action4"))  # +1 Event
    assert len(get_db_hits()) == 8
    time.sleep(2)  # Batch event (timer)
    #  --
    calls = responses.calls._calls
    body = json.loads(calls[2].request.body)
    assert body['t'] == 'BATCH'
    assert len(body['h']) == 8
    assert body['h'][0]['t'] == 'EVENT'
    assert body['h'][0]['el'] == 'python:true'
    assert body['h'][1]['t'] == 'EVENT'
    assert body['h'][1]['el'] == 'python:false'
    assert body['h'][2]['t'] == 'EVENT'
    assert body['h'][2]['el'] == 'python:true'
    assert body['h'][3]['t'] == 'SCREENVIEW'
    assert body['h'][3]['dl'] == 'test_hit_continuous_strategy'
    assert body['h'][4]['t'] == 'EVENT' == body['h'][5]['t'] == 'EVENT' == body['h'][6]['t'] == 'EVENT' == body['h'][7][
        't'] == 'EVENT'
    # --
    assert len(get_db_hits()) == 0
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "action5"))  # +1 Event
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "action6"))  # +1 Event
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "action7"))  # +1 Event
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "action8"))  # +1 Event
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "action9"))  # +1 Event
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "action10"))  # +1 Event
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "action11"))  # +1 Event
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "action12"))  # +1 Event
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "action13"))  # +1 Event
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "action14"))  # +1 Event # Batch event (max)
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "action15"))  # +1 Event
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "action16"))  # +1 Event
    # time.sleep(1)  ## Batch event (max)
    # --
    calls = responses.calls._calls
    body = json.loads(calls[3].request.body)
    assert body['t'] == 'BATCH'
    assert len(body['h']) == 10
    assert body['h'][0]['t'] == 'EVENT' and body['h'][0]['ea'] == 'action5'
    assert body['h'][1]['t'] == 'EVENT' and body['h'][1]['ea'] == 'action6'
    assert body['h'][2]['t'] == 'EVENT' and body['h'][2]['ea'] == 'action7'
    assert body['h'][3]['t'] == 'EVENT' and body['h'][3]['ea'] == 'action8'
    assert body['h'][4]['t'] == 'EVENT' and body['h'][4]['ea'] == 'action9'
    assert body['h'][5]['t'] == 'EVENT' and body['h'][5]['ea'] == 'action10'
    assert body['h'][6]['t'] == 'EVENT' and body['h'][6]['ea'] == 'action11'
    assert body['h'][7]['t'] == 'EVENT' and body['h'][7]['ea'] == 'action12'
    assert body['h'][8]['t'] == 'EVENT' and body['h'][8]['ea'] == 'action13'
    assert body['h'][9]['t'] == 'EVENT' and body['h'][9]['ea'] == 'action14'
    # --
    assert len(get_db_hits()) == 2

    Flagship.start(env_id, api_key, DecisionApi(timeout=3000,
                                                tracking_manager_config=TrackingManagerConfig(
                                                    max_pool_size=10,
                                                    time_interval=2000),
                                                cache_manager=SqliteCacheManager(
                                                    local_db_path=db_path)))
    time.sleep(2)  # Batch event (timer)
    # --
    calls = responses.calls._calls
    body = json.loads(calls[4].request.body)
    assert body['t'] == 'BATCH'
    assert len(body['h']) == 2
    assert body['h'][0]['t'] == 'EVENT' and body['h'][0]['ea'] == 'action15'
    assert body['h'][1]['t'] == 'EVENT' and body['h'][1]['ea'] == 'action16'
    # --
    assert len(get_db_hits()) == 0


@responses.activate
def test_hit_custom_cache_manager_panic():
    class CustomCacheManager(CacheManager, VisitorCacheImplementation, HitCacheImplementation):

        lookup_hit_iteration = 0
        # cached_hits = []
        cached_hits = {}
        nb_cached_hits = 0

        def open_database(self, env_id):
            pass

        def close_database(self):
            pass

        def __init__(self, **kwargs):
            CacheManager.__init__(self, timeout=200)

        async def cache_visitor(self, visitor_id, data):
            pass

        async def lookup_visitor(self, visitor_id):
            pass

        async def flush_visitor(self, visitor_id):
            pass

        def cache_hits(self, hits):
            self.nb_cached_hits += len(hits)
            # for k, v in hits.items():
            # if v['data']['content'] not in self.cached_hits:
            #     self.cached_hits.append(v['data']['content'])
            self.cached_hits.update(hits)

        async def lookup_hits(self):
            self.lookup_hit_iteration += 1
            if self.lookup_hit_iteration == 2:
                return self.cached_hits

        def flush_hits(self, hits_ids):
            pass

        def flush_all_hits(self):
            pass

    Flagship.stop()
    remove_db()
    responses.reset()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_3), status=200)  # PANIC
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)

    custom_cache_manager = CustomCacheManager()
    Flagship.start(env_id, api_key, DecisionApi(timeout=3000,
                                                tracking_manager_config=TrackingManagerConfig(max_pool_size=10,
                                                                                              time_interval=2000),
                                                cache_manager=custom_cache_manager))
    time.sleep(0.1)  # time to let first polling
    visitor = Flagship.new_visitor("test_visitor_1", instance_type=Visitor.Instance.SINGLE_INSTANCE)  # +1 consent
    visitor.send_hit(Screen("test_hit_panic_1"))  # +1 Screen
    visitor.send_hit(Screen("test_hit_panic_2"))  # +1 Screen
    visitor.send_hit(Screen("test_hit_panic_3"))  # +1 Screen
    visitor.fetch_flags()  # call /campaign => PANIC
    time.sleep(0.2)
    assert custom_cache_manager.nb_cached_hits == 8
    # assert custom_cache_manager.nb_cached_hits == 0  # PANIC

    responses.reset()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)
    visitor = Flagship.new_visitor("test_visitor_1", instance_type=Visitor.Instance.SINGLE_INSTANCE)
    visitor.fetch_flags()  # call /Campaign => READY (tracking manager restarted)
    time.sleep(2)
    calls = responses.calls._calls
    body = json.loads(calls[1].request.body)
    hit_array = body['h']
    for k, v in custom_cache_manager.cached_hits.items():
        assert v['data']['content'] in hit_array


@responses.activate
def test_hit_periodic_strategy():
    Flagship.stop()
    remove_db()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=500)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)

    assert get_db_hits() is None
    # Flagship.stop()
    Flagship.start(env_id, api_key, DecisionApi(timeout=3000,
                                                tracking_manager_config=TrackingManagerConfig(
                                                    strategy=TrackingManagerStrategy.BATCHING_WITH_PERIODIC_CACHING_STRATEGY,
                                                    max_pool_size=10,
                                                    time_interval=2000),
                                                cache_manager=SqliteCacheManager(local_db_path=db_path)))
    time.sleep(0.1)  # time to let the first polling go
    visitor = Flagship.new_visitor("test_visitor_1", instance_type=Visitor.Instance.SINGLE_INSTANCE)  # +1 consent
    visitor.fetch_flags()  # call /campaign
    visitor.send_hit(Screen("test_hit_periodic_1"))  # +1 Screen
    visitor.send_hit(Screen("test_hit_periodic_2"))  # +1 Screen
    assert visitor.get_flag("featureEnabled", False).value() is True  # +1 Activate
    assert visitor.get_flag("featureEnabled", False).value() is True  # +1 Activate
    assert len(get_db_hits()) == 0
    time.sleep(2.1)
    assert len(get_db_hits()) == 3

    responses.reset()
    # Flagship.stop()

    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)

    Flagship.start(env_id, api_key, DecisionApi(timeout=3000,
                                                tracking_manager_config=TrackingManagerConfig(
                                                    strategy=TrackingManagerStrategy.BATCHING_WITH_PERIODIC_CACHING_STRATEGY,
                                                    max_pool_size=10,
                                                    time_interval=2000),
                                                cache_manager=SqliteCacheManager(local_db_path=db_path)))
    visitor2 = Flagship.new_visitor("test_visitor_2", instance_type=Visitor.Instance.SINGLE_INSTANCE)  # +1 consent
    time.sleep(2.1)  # batch
    calls = responses.calls._calls
    body = json.loads(calls[0].request.body)
    hit_array = body['h']
    assert len(hit_array) == 4
    assert hit_array[0]['t'] == 'EVENT'
    assert hit_array[1]['t'] == 'SCREENVIEW'
    assert hit_array[2]['t'] == 'SCREENVIEW'
    assert hit_array[3]['t'] == 'EVENT'
    assert len(get_db_hits()) == 0


@responses.activate
def test_hit_no_batching_strategy():
    Flagship.stop()
    remove_db()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)

    assert get_db_hits() is None
    Flagship.start(env_id, api_key, DecisionApi(timeout=3000,
                                                tracking_manager_config=TrackingManagerConfig(
                                                    strategy=TrackingManagerStrategy._NO_BATCHING_CONTINUOUS_CACHING_STRATEGY,
                                                    max_pool_size=10,
                                                    time_interval=2000),
                                                cache_manager=SqliteCacheManager(local_db_path=db_path)))
    visitor3 = Flagship.new_visitor("test_visitor_3", instance_type=Visitor.Instance.SINGLE_INSTANCE)  # +1 Consent
    visitor3.fetch_flags()  # /Campaigns
    assert visitor3.get_flag("featureEnabled", False).value() is True  # +1 Activate
    visitor3.send_hit(Screen("test_hit_no_batching_strategy"))  # 1 Screen
    visitor3.send_hit(Screen("test_hit_no_batching_strategy2"))  # 1 Screen
    assert visitor3.get_flag("featureEnabled", False).value() is True  # +1 Activate
    visitor3.set_consent(False)  # +1 Consent
    visitor3.send_hit(Screen("test_hit_no_batching_strategy3"))  # 0 Screen
    visitor3.send_hit(Screen("test_hit_no_batching_strategy4"))  # 0 Screen
    calls = responses.calls._calls
    assert len(calls) == 7
    assert len(get_db_hits()) == 0
    responses.reset()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=500)
    visitor3.set_consent(True)  # +1 Consent
    visitor3.send_hit(Screen("test_hit_no_batching_strategy5"))  # +1 Screen
    visitor3.send_hit(Screen("test_hit_no_batching_strategy6"))  # +1 Screen
    assert visitor3.get_flag("featureEnabled", False).value() is True  # +1 Activate
    assert visitor3.get_flag("featureEnabled", False).value() is True  # +1 Activate
    calls = responses.calls._calls
    assert len(calls) == 5
    assert len(get_db_hits()) == 2


# polling timer

@responses.activate
def test_tracking_polling_timer():
    Flagship.stop()
    remove_db()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)

    class CustomLogManager(LogManager):

        def __init__(self):
            self.nb_polling = 0

        def log(self, tag, level, message):
            if 'Tracking Manager' in tag and 'Polling event' in message:
                self.nb_polling += 1

        def exception(self, exception, traceback):
            pass

    clm = CustomLogManager()
    Flagship.start(env_id, api_key, DecisionApi(timeout=3000,
                                                log_manager=clm,
                                                tracking_manager_config=TrackingManagerConfig(
                                                    strategy=TrackingManagerStrategy.BATCHING_WITH_CONTINUOUS_CACHING_STRATEGY,
                                                    max_pool_size=10,
                                                    time_interval=200),
                                                cache_manager=SqliteCacheManager(local_db_path=db_path)))
    time.sleep(1)
    assert clm.nb_polling >= 5


@responses.activate
def test_tracking_polling_timer():
    Flagship.stop()
    remove_db()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)

    class CustomLogManager(LogManager):

        def __init__(self):
            self.nb_polling = 0

        def log(self, tag, level, message):
            if 'Tracking Manager' in tag and 'Polling event' in message:
                self.nb_polling += 1

        def exception(self, exception, traceback):
            pass

    clm = CustomLogManager()
    Flagship.start(env_id, api_key, DecisionApi(timeout=3000,
                                                log_manager=clm,
                                                tracking_manager_config=TrackingManagerConfig(
                                                    max_pool_size=-1,
                                                    time_interval=50),
                                                ))
    time.sleep(1)
    visitor4 = Flagship.new_visitor("test_visitor_4", instance_type=Visitor.Instance.SINGLE_INSTANCE)  # +1 Consent
    visitor4.fetch_flags()
    assert visitor4.get_flag("featureEnabled", False).value() is True  # +1 Activate
    assert clm.nb_polling == 1
    assert get_db_hits() is None

@responses.activate
def test_tracking_no_cache_interface():
    Flagship.stop()
    remove_db()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=500)

    class CustomCacheManager0(CacheManager):

        def open_database(self, env_id):
            pass

        def close_database(self):
            pass

    ccm0 = CustomCacheManager0()

    Flagship.start(env_id, api_key, DecisionApi(timeout=3000,
                                                tracking_manager_config=TrackingManagerConfig(
                                                    max_pool_size=-1,
                                                    time_interval=50),
                                                cache_manager=ccm0
                                                ))
    time.sleep(1)
    visitor5 = Flagship.new_visitor("test_visitor_5", instance_type=Visitor.Instance.SINGLE_INSTANCE)  # +1 Consent
    visitor5.fetch_flags()
    assert visitor5.get_flag("featureEnabled", False).value() is True  # +1 Activate
    assert get_db_hits() is None
    visitor5.set_consent(False)

@responses.activate
def test_hit_data():
    Flagship.stop()
    remove_db()
    time.sleep(1)
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=500)

    class CustomCacheManager(CacheManager, HitCacheImplementation):

        def __init__(self, **kwargs):
            CacheManager.__init__(self, timeout=200)
            self.open_database_calls = 0
            self.close_database_calls = 0
            self.cache_hits_calls = 0
            self.lookup_hits_calls = 0
            self.flush_hits_calls = 0
            self.nb_flushed_hits = 0
            self.flush_all_hits_calls = 0
            self.cached_hits = dict()

        def open_database(self, env_id):
            self.open_database_calls += 1
            pass

        def close_database(self):
            self.close_database_calls += 1
            pass

        def cache_hits(self, hits):
            for k, h in hits.items():
                assert 'version' in h
                assert 'data' in h
                assert 'id' in h['data']
                assert 'timestamp' in h['data']
                assert 'visitorId' in h['data']
                assert 'anonymousId' in h['data']
                assert 'type' in h['data']
                assert 'content' in h['data']
            self.cache_hits_calls += 1
            self.cached_hits.update(hits)

        async def lookup_hits(self):
            self.lookup_hits_calls += 1
            return {
                'wrong data': {
                    'wrong_value': 1
                },
                'b9701838-35d8-4bfe-8ea8-0000000000': {
                    'version': 1,
                    'data': {
                        'id': 'b9701838-35d8-4bfe-8ea8-0000000000',
                        'type': 'EVENT',
                        'visitorId': 'test_visitor_0',
                        'anonymousId': None,
                        'timestamp': (int(time.time()) * 1000) - 3000,
                        'content': {
                            't': 'EVENT',
                            'ds': 'APP',
                            'ec': 'User Engagement',
                            'ea': 'from_cache',
                            'el': 'from_cache',
                            'vid': 'test_visitor_6',
                            'cuid': None
                        },
                    }
                }
            }

        def flush_hits(self, hits_ids):
            print('== FLUSH HITS == ' + str(hits_ids))
            self.flush_hits_calls += 1
            self.nb_flushed_hits += len(hits_ids)
            pass

        def flush_all_hits(self):
            self.flush_all_hits_calls += 1
            pass

    ccm = CustomCacheManager()

    Flagship.start(env_id, api_key, DecisionApi(timeout=3000,
                                                tracking_manager_config=TrackingManagerConfig(
                                                    max_pool_size=10,
                                                    time_interval=2000),
                                                cache_manager=ccm
                                                ))
    time.sleep(1)  # Load 1 Event from cache + polling
    visitor6 = Flagship.new_visitor("test_visitor_6", instance_type=Visitor.Instance.SINGLE_INSTANCE)  # +1 Consent
    visitor6.fetch_flags()
    assert visitor6.get_flag("featureEnabled", False).value() is True  # +1 Activate
    assert get_db_hits() is None
    visitor6.send_hit(Screen("test_hit_no_batching_strategy7"))  # +1 Screen
    visitor6.set_consent(False)  # +1 Consent
    visitor6.send_hit(Screen("test_hit_no_batching_strategy8"))  # +0 Screen
    assert visitor6.get_flag("featureEnabled", False).value() is True  # +0 Activate
    assert ccm.lookup_hits_calls == 1
    assert ccm.cache_hits_calls == 5
    assert ccm.flush_hits_calls == 2
    assert ccm.nb_flushed_hits == 3
    visitor6.set_consent(True)  # +1 Consent
    time.sleep(1.2)
    assert ccm.cache_hits_calls == 6
    assert ccm.nb_flushed_hits == 6


@responses.activate
def test_visitor_data_no_cache_interface():
    Flagship.stop()
    remove_db()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=500)

    class CustomCacheManager0(CacheManager):

        def open_database(self, env_id):
            pass

        def close_database(self):
            pass

    ccm0 = CustomCacheManager0()

    Flagship.start(env_id, api_key, DecisionApi(timeout=3000,
                                                tracking_manager_config=TrackingManagerConfig(
                                                    max_pool_size=-1,
                                                    time_interval=50),
                                                cache_manager=ccm0
                                                ))
    time.sleep(1)
    visitor5 = Flagship.new_visitor("test_visitor_5", instance_type=Visitor.Instance.SINGLE_INSTANCE)  # +1 Consent
    visitor5.fetch_flags()


@responses.activate
def test_visitor_data():
    Flagship.stop()
    remove_db()
    responses.add(responses.GET, BUCKETING_URL, json=json.loads(BUCKETING_RESPONSE_1), status=200,
                  headers=[("Last-Modified", BUCKETING_LAST_MODIFIED_1)])
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)

    class CustomCacheManager0(CacheManager, VisitorCacheImplementation):

        def __init__(self, **kwargs):
            CacheManager.__init__(self, **kwargs)
            self.nb_call_open_database = 0
            self.nb_call_close_database = 0
            self.nb_call_cache_visitor = 0
            self.nb_call_cache_visitor_10 = 0
            self.nb_call_lookup_visitor = 0
            self.nb_call_lookup_visitor_10 = 0
            self.nb_call_flush_visitor = 0
            self.cache_visitor_10 = {}

        def open_database(self, env_id):
            self.nb_call_open_database += 1
            pass

        def close_database(self):
            self.nb_call_close_database += 1
            pass

        async def cache_visitor(self, visitor_id, data):
            assert 'version' in data
            assert 'data' in data
            assert 'visitorId' in data['data']
            assert 'anonymousId' in data['data']
            assert 'isAuthenticated' in data['data']
            assert 'consent' in data['data']
            assert 'context' in data['data']
            assert 'assignationHistory' in data['data']
            assert 'campaigns' in data['data']
            if visitor_id == 'test_visitor_10':
                self.cache_visitor_10 = data
                if self.nb_call_cache_visitor_10 == 1:
                    assert data['version'] == 1
                    assert data['data']['visitorId'] == 'test_visitor_10'
                    assert data['data']['anonymousId'] is not None
                    assert data['data']['isAuthenticated'] is True
                    assert data['data']['consent'] is True
                    assert data['data']['context']['access'] == 'password'
                    assert len(data['data']['campaigns']) >= 1
                    assert data['data']['campaigns'][0]['exposed'] is True
                    assert data['data']['campaigns'][0]['campaignId'] == 'iiii'
                    assert data['data']['campaigns'][0]['variationGroupId'] == 'yyyy'
                    assert data['data']['campaigns'][0]['flags']['rank'] == 2222
                    assert data['data']['assignationHistory']['yyyy'] == 'tttt'
                self.nb_call_cache_visitor_10 += 1
            self.nb_call_cache_visitor += 1

        async def lookup_visitor(self, visitor_id):
            self.nb_call_lookup_visitor += 1
            if visitor_id == "test_visitor_9":
                return {
                    "wrong_format": {
                        "wrong_value": 1
                    }
                }
            elif visitor_id == "test_visitor_10":
                if self.nb_call_lookup_visitor_10 == 1:
                    self.cache_visitor_10['data']['assignationHistory']['yyyy'] = 'rrrr'
                    return self.cache_visitor_10
                self.nb_call_lookup_visitor_10 += 1
            return None

        async def flush_visitor(self, visitor_id):
            self.nb_call_flush_visitor += 1
            pass

    ccm0 = CustomCacheManager0(timeout=200)

    Flagship.start(env_id, api_key, Bucketing(timeout=3000,
                                                tracking_manager_config=TrackingManagerConfig(
                                                    max_pool_size=-1,
                                                    time_interval=50),
                                                cache_manager=ccm0
                                                # polling_interval=10000
                                                ))

    time.sleep(1)
    visitor9 = Flagship.new_visitor("test_visitor_9", instance_type=Visitor.Instance.NEW_INSTANCE)
    visitor9.fetch_flags()

    visitor10 = Flagship.new_visitor("test_visitor_10", instance_type=Visitor.Instance.NEW_INSTANCE, context={"access": 'password'}, authenticated=True)
    visitor10.fetch_flags()
    assert visitor10.get_flag('rank', -1).value() == 2222

    visitor11 = Flagship.new_visitor("test_visitor_11", instance_type=Visitor.Instance.NEW_INSTANCE)
    visitor11.fetch_flags()
    visitor11.set_consent(False)

    assert ccm0.nb_call_lookup_visitor == 3
    assert ccm0.nb_call_cache_visitor == 4
    assert ccm0.nb_call_flush_visitor == 1

    visitor10 = Flagship.new_visitor("test_visitor_10", instance_type=Visitor.Instance.NEW_INSTANCE,
                                     context={"access": 'password'}, authenticated=True)
    visitor10.fetch_flags()
    assert visitor10.get_flag('rank', -1).value() == 3333


@responses.activate
def test_visitor_timeout():
    Flagship.stop()
    remove_db()
    responses.add(responses.GET, BUCKETING_URL, json=json.loads(BUCKETING_RESPONSE_1), status=200,
                  headers=[("Last-Modified", BUCKETING_LAST_MODIFIED_1)])
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)

    class CustomLogManager(LogManager):

        def __init__(self):
            self.nb_timeout = 0

        def log(self, tag, level, message):
            if 'Cache Manager' in tag and 'lookup_visitor' in message and 'timed out' in message:
                self.nb_timeout += 1

        def exception(self, exception, traceback):
            pass


    class CustomCacheManager0(CacheManager, VisitorCacheImplementation):
        def open_database(self, env_id):
            pass

        def close_database(self):
            pass

        async def cache_visitor(self, visitor_id, data):
            pass

        async def lookup_visitor(self, visitor_id):
            print("[LOOKUP]")
            await asyncio.sleep(1)
            return 'LOOKUP'

        async def flush_visitor(self, visitor_id):
            pass

    ccm0 = CustomCacheManager0(timeout=2000)
    clm = CustomLogManager()
    Flagship.start(env_id, api_key, Bucketing(timeout=30000, cache_manager=ccm0, log_manager=clm))
    time.sleep(0.2)
    visitor11 = Flagship.new_visitor("test_visitor_11", instance_type=Visitor.Instance.NEW_INSTANCE,
                                     context={"access": 'password'}, authenticated=True)
    time.sleep(0.2)

    assert clm.nb_timeout == 0

    ccm0 = CustomCacheManager0(timeout=0.100)
    clm = CustomLogManager()
    Flagship.start(env_id, api_key, Bucketing(timeout=30000, cache_manager=ccm0, log_manager=clm))
    time.sleep(0.2)
    visitor11 = Flagship.new_visitor("test_visitor_11", instance_type=Visitor.Instance.NEW_INSTANCE,
                                     context={"access": 'password'}, authenticated=True)
    time.sleep(0.2)

    assert clm.nb_timeout == 1



