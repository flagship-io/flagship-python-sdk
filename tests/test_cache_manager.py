import json
import os
import time
import traceback
import sqlite3 as sl
import responses

from flagship import Flagship, Visitor
from flagship.cache_manager import SqliteCacheManager
from flagship.config import DecisionApi
from flagship.hits import Screen, Event, EventCategory
from flagship.tracking_manager import TrackingManagerConfig
from flagship.utils import pretty_dict
from test_constants_res import DECISION_API_URL, API_RESPONSE_1, ARIANE_URL, ACTIVATE_URL, EVENTS_URL

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
    # --
    assert len(get_db_hits()) == 0
