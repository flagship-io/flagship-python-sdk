import asyncio
import sys
import time

from flagship import *
from flagship.cache_manager import SqliteCacheManager
from flagship.config import DecisionApi, Bucketing
from flagship.hits import Screen
from flagship.tracking_manager import TrackingManagerConfig


def init():
    print(sys.version)
    Flagship.start('__env_id__', '__api_key__', DecisionApi(timeout=3000,
                                                            cache_manager=SqliteCacheManager(),
                                                            log_level=LogLevel.ALL,
                                                            tracking_manager_config=TrackingManagerConfig(
                                                                time_interval=10000,
                                                                max_pool_size=5)))  ## Demo

    visitor = Flagship.new_visitor('visitor-A', context={'testing_tracking_manager': True})
    visitor.fetch_flags()
    visitor.get_flag("my_flag", 'default').value()
    visitor.send_hit(Screen("screen 1"))
    time.sleep(2)




init()