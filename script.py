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
    Flagship.start('bk87t3jggr10c6l6sdog', 'N1Rm3DsCBrahhnGTzEnha31IN4DK8tXl28IykcCX', Bucketing(timeout=3000,
                                                                                                   cache_manager=SqliteCacheManager(),
                                                                                                   tracking_manager_config=TrackingManagerConfig(
                                                                                                       time_interval=10000,
                                                                                                   max_pool_size=5)))  ## Demo
    # Flagship.start('bkk4s7gcmjcg07fke9dg', 'Q6FDmj6F188nh75lhEato2MwoyXDS7y34VrAL4Aa', Bucketing(timeout=3000,
    #                                                                                              cache_manager=SqliteCacheManager(),
    #                                                                                              tracking_manager_config=TrackingManagerConfig(
    #                                                                                                  time_interval=10000,
    #                                                                                                  max_pool_size=5)))  ## Demo
    time.sleep(2)
    visitor = Flagship.new_visitor('visitor-A', context={'testing_tracking_manager': True})
    visitor.fetch_flags()
    visitor.get_flag("my_flag", 'default').value()
    visitor.send_hit(Screen("screen 1"))
    visitor.send_hit(Screen("screen 2"))
    visitor.send_hit(Screen("screen 3"))
    visitor.send_hit(Screen("screen 4"))
    visitor.send_hit(Screen("screen 5"))
    time.sleep(200)

# def qa_4():
#     # Flagship.start('bk87t3jggr10c6l6sdog', 'N1Rm3DsCBrahhnGTzEnha31IN4DK8tXl28IykcCX', DecisionApi(timeout=3000,
#     #                                                                                                cache_manager=SqliteCacheManager(),
#     #                                                                                                tracking_manager_config=TrackingManagerConfig(
#     #                                                                                                    time_interval=10000,
#     #                                                                                                    max_pool_size=5)))  ## Demo
#     Flagship.start('bk87t3jggr10c6l6sdog', 'N1Rm3DsCBrahhnGTzEnha31IN4DK8tXl28IykcCX', DecisionApi(timeout=3000,
#                                                                                                    cache_manager=SqliteCacheManager(),
#                                                                                                    tracking_manager_config=TrackingManagerConfig(
#                                                                                                        time_interval=10000,
#                                                                                                        max_pool_size=5)))  ## Demo
#     time.sleep(0.2)
#     visitor = Flagship.new_visitor('visitor-A', context={'testing_tracking_manager': True})
#     # visitor.fetch_flags()
#     # print('################## offline ######################')
#     # time.sleep(5)
#     # visitor.get_flag("my_flag", 'default').value()
#     # visitor.send_hit(Screen("screen 1"))
#     # print('################## online ######################')
#     # time.sleep(30)
#     # visitorB = Flagship.new_visitor('visitor-B', context={'testing_tracking_manager': True})
#     # visitorB.fetch_flags()
#     # visitorB.get_flag("my_flag", 'default').value()
#
#     time.sleep(10000000)
#
# def qa_1():
#
#     # value = asyncio.run(asyncio.wait_for(toto(), timeout=2))
#     # # value = asyncio.run(asyncio.wait_for(toto(), timeout=2))
#     # print("Value = " + str(value))
#     # time.sleep(1)
#
#     # Flagship.start('bkk4s7gcmjcg07fke9dg', 'Q6FDmj6F188nh75lhEato2MwoyXDS7y34VrAL4Aa', Bucketing(timeout=3000))
#     Flagship.start('bk87t3jggr10c6l6sdog', 'N1Rm3DsCBrahhnGTzEnha31IN4DK8tXl28IykcCX', DecisionApi(timeout=3000,
#                                                                                                    cache_manager=SqliteCacheManager(),
#                                                                                                    tracking_manager_config=TrackingManagerConfig(
#                                                                                                        time_interval=10000,
#                                                                                                    max_pool_size=5)))  ## Demo
#     time.sleep(0.2)
#     visitor = Flagship.new_visitor('visitor-A', context={'testing_tracking_manager': True})
#     visitor.fetch_flags()
#     visitor.get_flag("my_flag", 'default').value()
#     visitor.send_hit(Screen("screen 1"))
#     visitor.send_hit(Screen("screen 2"))
#     visitor.send_hit(Screen("screen 3"))
#     visitor.send_hit(Screen("screen 4"))
#     visitor.send_hit(Screen("screen 5"))
#
# def qa_2():
#     Flagship.start('bk87t3jggr10c6l6sdog', 'N1Rm3DsCBrahhnGTzEnha31IN4DK8tXl28IykcCX', DecisionApi(timeout=3000,
#                                                                                                    cache_manager=SqliteCacheManager(),
#                                                                                                    tracking_manager_config=TrackingManagerConfig(
#                                                                                                        time_interval=10000,
#                                                                                                        max_pool_size=5)))  ## Demo
#     time.sleep(0.2)
#     visitor = Flagship.new_visitor('visitor-A', context={'testing_tracking_manager': True})
#     visitor.fetch_flags()
#     visitor.get_flag("my_flag", 'default').value()
#     visitor.send_hit(Screen("screen 1"))
#     time.sleep(5)
#     visitor.set_consent(False)
#     time.sleep(10)
#
# def qa_3():
#     Flagship.start('bk87t3jggr10c6l6sdog', 'N1Rm3DsCBrahhnGTzEnha31IN4DK8tXl28IykcCX', DecisionApi(timeout=3000,
#                                                                                                    cache_manager=SqliteCacheManager(),
#                                                                                                    tracking_manager_config=TrackingManagerConfig(
#                                                                                                        time_interval=10000,
#                                                                                                        max_pool_size=5)))  ## Demo
#     time.sleep(0.2)
#     visitor = Flagship.new_visitor('visitor-A', context={'testing_tracking_manager': True})
#     visitor.fetch_flags()
#     visitor.get_flag("my_flag", 'default').value()
#     visitor.send_hit(Screen("screen 1"))
#     time.sleep(10000000)
#
#


init()
