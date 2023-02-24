import json
import os
import time
import traceback
import sqlite3 as sl
import responses

from flagship import Flagship, Visitor
from flagship.cache_manager import SqliteCacheManager
from flagship.config import DecisionApi
from flagship.hits import Screen
from flagship.tracking_manager import TrackingManagerConfig
from test_constants_res import DECISION_API_URL, API_RESPONSE_1, ARIANE_URL, ACTIVATE_URL

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
            result = cursor.fetchall()
            if result:
                cursor.close()
                result_as_dict = {}
                for k, v in result:
                    result_as_dict[k] = json.loads(v)
                return result_as_dict
    except:
        print(traceback.format_exc())
        return None

def remove_db():
    import shutil
    shutil.rmtree(db_path)


@responses.activate
def test_hit_continuous_strategy():
    remove_db()
    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    responses.add(responses.POST, ARIANE_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=500)

    assert get_db_hits() is None
    Flagship.start(env_id, api_key, DecisionApi(timeout=3000,
                                                tracking_manager_config=TrackingManagerConfig(max_pool_size=10, time_interval=500000),
                                                cache_manager=SqliteCacheManager(local_db_path=db_path)))
    visitor = Flagship.new_visitor("test_visitor_1", instance_type=Visitor.Instance.SINGLE_INSTANCE)  # 1 consent
    visitor.fetch_flags()
    visitor.send_hit(Screen("test_hit_continuous_strategy"))  # 1 Screen
    assert visitor.get_flag('string', "default").value() == 'default'  # 1 activate
    assert len(get_db_hits()) == 3
    visitor.set_consent(False)  # 1 Consent - 1 screen - 1 Activate
    assert len(get_db_hits()) == 2
    # time.sleep(100000000)
    visitor.set_consent(True)  # 1 Consent
    visitor.send_hit(Screen("test_hit_continuous_strategy"))  # 1 Screen
    assert len(get_db_hits()) == 4
