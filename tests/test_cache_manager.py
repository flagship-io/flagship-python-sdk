import json
import os
import time
import traceback
import sqlite3 as sl
import responses

from flagship import Flagship, Visitor
from flagship.cache_manager import SqliteCacheManager, CacheManager, VisitorCacheImplementation, HitCacheImplementation
from flagship.config import DecisionApi
from flagship.hits import Screen, Event, EventCategory
from flagship.tracking_manager import TrackingManagerConfig
from flagship.utils import pretty_dict
from test_constants_res import DECISION_API_URL, API_RESPONSE_1, ARIANE_URL, ACTIVATE_URL, EVENTS_URL, API_RESPONSE_3

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
    remove_db()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, ARIANE_URL, body="", status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=500)

    assert get_db_hits() is None
    Flagship.stop()
    Flagship.start(env_id, api_key, DecisionApi(timeout=3000,
                                                tracking_manager_config=TrackingManagerConfig(max_pool_size=10,
                                                                                              time_interval=2000),
                                                cache_manager=SqliteCacheManager(local_db_path=db_path)))
    visitor = Flagship.new_visitor("test_visitor_1", instance_type=Visitor.Instance.SINGLE_INSTANCE)  # +1 consent
    visitor.fetch_flags()  # call /campaign
    visitor.send_hit(Screen("test_hit_continuous_strategy"))  # +1 Screen
    assert visitor.get_flag('string', "default").value() == 'default'  # +1 activate
    assert len(get_db_hits()) == 3
    visitor.set_consent(False)  # +1 Consent -1 screen -1 Activate # /activate
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

        cached_hits = 0

        def open_database(self, env_id):
            pass

        def close_database(self):
            pass

        def __init__(self, **kwargs):
            super().__init__(timeout=200)

        def cache_visitor(self, visitor_id, data):
            pass

        def lookup_visitor(self, visitor_id):
            pass

        def flush_visitor(self, visitor_id):
            pass

        def cache_hits(self, hits):
            self.cached_hits += len(hits)

        def lookup_hits(self):
            pass

        def flush_hits(self, hits_ids):
            pass

        def flush_all_hits(self):
            pass

    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_3), status=200)
    responses.add(responses.POST, ARIANE_URL, body="", status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)
    remove_db()
    Flagship.stop()
    custom_cache_manager = CustomCacheManager()
    Flagship.start(env_id, api_key, DecisionApi(timeout=3000,
                                                tracking_manager_config=TrackingManagerConfig(max_pool_size=10,
                                                                                              time_interval=2000),
                                                cache_manager=custom_cache_manager))
    visitor = Flagship.new_visitor("test_visitor_1", instance_type=Visitor.Instance.SINGLE_INSTANCE)  # +1 consent
    visitor.send_hit(Screen("test_hit_panic_1"))  # +1 Screen
    visitor.send_hit(Screen("test_hit_panic_2"))  # +1 Screen
    visitor.send_hit(Screen("test_hit_panic_3"))  # +1 Screen
    visitor.fetch_flags()  # call /campaign
    assert custom_cache_manager.cached_hits == 8
