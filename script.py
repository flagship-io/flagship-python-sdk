import asyncio
import time

from flagship import *
from flagship.cache_manager import SqliteCacheManager
from flagship.config import DecisionApi, Bucketing
from flagship.hits import Screen
from flagship.tracking_manager import TrackingManagerConfig


async def toto():
    print("je retourne toto")
    await asyncio.sleep(1)
    return 'toto'

def init():
    # print(sys.version)
    # from pglet import Text
    #
    # p = pglet.page('Script')
    # p.add(Text("Hello, world! hahaha 3"))
    # p.add(Textbox(placeholder="test"))
    qa_5()


def qa_5():

    # value = asyncio.run(asyncio.wait_for(toto(), timeout=2))
    # # value = asyncio.run(asyncio.wait_for(toto(), timeout=2))
    # print("Value = " + str(value))
    # time.sleep(1)

    # Flagship.start('bkk4s7gcmjcg07fke9dg', 'Q6FDmj6F188nh75lhEato2MwoyXDS7y34VrAL4Aa', Bucketing(timeout=3000))
    Flagship.start('bkk4s7gcmjcg07fke9dg', 'Q6FDmj6F188nh75lhEato2MwoyXDS7y34VrAL4Aa', DecisionApi(timeout=3000,
                                                                                                   cache_manager=SqliteCacheManager(),
                                                                                                    log_level=LogLevel.ALL,
                                                                                                   tracking_manager_config=TrackingManagerConfig(
                                                                                                       time_interval=10000,
                                                                                                   max_pool_size=5)))  ## Demo

    # Flagship.start('bkk4s7gcmjcg07fke9dg', 'Q6FDmj6F188nh75lhEato2MwoyXDS7y34VrAL4Aa', Bucketing(timeout=3000,
    #                                                                                              cache_manager=SqliteCacheManager(),
    #                                                                                              tracking_manager_config=TrackingManagerConfig(
    #                                                                                                  time_interval=10000,
    #                                                                                                  max_pool_size=5)))  ## Demo
    # time.sleep(2)
    #
    # visitor_list = list()
    # t1 = time.time() * 1000
    # print('t1 : ' + str(t1))
    # for i in range(0, 30000):
    #     print("i = " + str(i))
    #     visitor = Flagship.new_visitor('visitor-' + str(i), context={'id': str(i)})
    #     visitor_list.append(visitor)
    # t2 = time.time() * 1000
    # print('t2 : ' + str(t2))
    # print('total : ' + str(t2-t1))
    #
    # print('__________________')
    #
    # t1 = time.time() * 1000
    # print('t1 : ' + str(t1))
    # for v in visitor_list:
    #     print("i = " + str(v.visitor_id))
    # t2 = time.time() * 1000
    # print('t2 : ' + str(t2))
    # print('total : ' + str(t2 - t1))

    time.sleep(2)
    visitor = Flagship.new_visitor('visitor-A', context={'testing_tracking_manager': True})
    visitor.fetch_flags()
    visitor.get_flag("my_flag", 'default').value()
    visitor.send_hit(Screen("screen 1"))
    # visitor.send_hit(Screen("screen 2"))
    # visitor.send_hit(Screen("screen 3"))
    # visitor.send_hit(Screen("screen 4"))
    # visitor.send_hit(Screen("screen 5"))
    # time.sleep(2)

init()