import time

from flagship.config import DecisionApi
from flagship import *
from flagship.config import Bucketing
from flagship.status_listener import StatusListener
from flagship.tracking_manager import TrackingManagerConfig
from flagship.hits import Screen

def init():

    class CustomStatusListener(StatusListener):

        def on_status_changed(self, new_status):
            if new_status is Status.READY:
                print(new_status)
                visitor = Flagship.new_visitor(visitor_id='visitor-A', context={'isVIP': True, "int": 4973})
                visitor.fetch_flags()
                print(str(visitor.get_flag("my_flag", 'default').value()))
                visitor.send_hit(Screen("screen 1"))

    Flagship.start(
        '_ENV_ID_',
        '_API_KEY_',
        DecisionApi(
            timeout=3000,
            status_listener=CustomStatusListener(),
            log_level=LogLevel.ALL,
            tracking_manager_config=TrackingManagerConfig(time_interval=5000, max_pool_size=5)
        )
    )
    time.sleep(6)

init()
