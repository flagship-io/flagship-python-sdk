# # coding: utf8
# import json
# import sys
#
# from flagship import Flagship
# from flagship import VisitorCacheManager
# from flagship..old.config import Config
# from flagship..old.handler import FlagshipEventHandler
# from flagship..old.helpers import Screen
#
#
# class CustomEventHandler(FlagshipEventHandler):
#     def __init__(self):
#         FlagshipEventHandler.__init__(self)
#
#     def on_log(self, level, message):
#         FlagshipEventHandler.on_log(self, level, ">>> " + message)
#         pass
#
#     def on_exception_raised(self, exception, traceback):
#         FlagshipEventHandler.on_exception_raised(self, exception, traceback)
#         pass
#
#
# class CustomVisitorCacheManager(VisitorCacheManager):
#
#     def save(self, visitor_id, visitor_data):
#         print("VisitorCacheManager look up " + json.dumps(visitor_data))
#
#     def lookup(self, visitor_id):
#         print("VisitorCacheManager look up " + visitor_id)
#         return None
#
# def init():
#     print(sys.version)
#     t = CustomEventHandler()
#
#     Flagship.instance().start("_my_env_id", "_my_api_key_",
#                               Config(event_handler=t, mode=Config.Mode.BUCKETING, polling_interval=5, timeout=0.1,
#                                      visitor_cache_manager=CustomVisitorCacheManager()))
#     v = Flagship.instance().create_visitor("visitorId_1", True, {'isVIPUser': True, 'daysSinceLastLaunch': 3})
#     v.synchronize_modifications()
#     value = v.get_modification("target", "default", True)
#     v.send_hit(Screen("python screen view"))
#     print(value)
# init()
import json
import sys
import time

import requests

import flagship.utils
from flagship import *
from flagship.config import DecisionApi, Bucketing
from flagship.flagship_context import FlagshipContext
from flagship.hits import Hit, Screen, Transaction, Event, EventCategory, Item, Page
from flagship.log_manager import LogManager
from flagship.status_listener import StatusListener
from flagship.tracking_manager import TrackingManagerConfig


def init():
    print(sys.version)
    # init_api()
    init_bucketing()

    # class CustomStatusListener(StatusListener):
    #
    #     def on_status_changed(self, new_status):
    #         print("New status = " + str(new_status))

    # class CustomLogManager(LogManager):
    #
    #     def log(self, tag, level, message):
    #         print(">>> " + tag + str(level) + message)
    #
    #     def exception(self, exception, traceback):
    #         pass

    # visitor0 = Flagship.new_visitor("toto 0", instance_type=Visitor.Instance.SINGLE_INSTANCE)
    # visitor0.fetch_flags()
    # print(str(visitor0.get_flag("nope 0", "default 0").value()))
    #
    # # Flagship.start("custom_end_id", "custom_api_key", DecisionApi(timeout=3000, status_listener=CustomStatusListener()))
    # Flagship.start("bkk4s7gcmjcg07fke9dg", "Q6FDmj6F188nh75lhEato2MwoyXDS7y34VrAL4Aa", DecisionApi(timeout=3000, status_listener=CustomStatusListener()))
    # # Flagship.start("custom_end_id", "custom_api_key", DecisionApi(timeout=3000, status_listener=CustomStatusListener(), log_manager=CustomLogManager()))
    # visitor = Flagship.new_visitor("toto", instance_type=Visitor.Instance.SINGLE_INSTANCE)
    # print(visitor._visitor_id)
    # print(Flagship.get_visitor()._visitor_id)
    # visitor.update_context({
    #     "coucou":3,
    #     "coucou2":2,
    #     "haha": False,
    #     "isVIPUser":True
    # })
    # visitor.update_context(('coucou3', 2))
    # visitor.fetch_flags()
    # print("Json.metadata > " + visitor.get_flag("json", dict()).metadata().toJson())
    # print("Json.exists > " + str(visitor.get_flag("json", dict()).exists()))
    # print("Json.value > " + str(visitor.get_flag("json", dict()).value(False)))
    #
    # print("string.metadata > " + str(visitor.get_flag("string", "default").metadata().toJson()))
    # print("string.exists > " + str(visitor.get_flag("string", "default").exists()))
    # print("string.value > " + str(visitor.get_flag("string", "default").value(False)))
    #
    # print("featureEnabled.metadata > " + str(visitor.get_flag("featureEnabled", False).metadata().toJson()))
    # print("featureEnabled.exists > " + str(visitor.get_flag("featureEnabled", False).exists()))
    # print("featureEnabled.value > " + str(visitor.get_flag("featureEnabled", False).value(False)))
    #
    # print("nope.metadata > " + str(visitor.get_flag("nope", 1).metadata().toJson()))
    # print("nope.exists > " + str(visitor.get_flag("nope", 1).exists()))
    # print("nope.value > " + str(visitor.get_flag("nope", 1).value(False)))
    #
    # visitor.get_flag("featureEnabled", False).user_exposed()
    # visitor.send_hit(Screen('Script.py'))
    # visitor.fetch_flags()
    # visitor.set_consent(False)
    # visitor.send_hit(Screen('Script.py 2'))
    # visitor.set_consent(True)
    # visitor.send_hit(Screen('Script.py 3'))

    # Flagship.start("bkk4s7gcmjcg07fke9dg", "Q6FDmj6F188nh75lhEato2MwoyXDS7y34VrAL4Aa",
    #                DecisionApi(timeout=3000))
    # visitor = Flagship.new_visitor("xxx_1", instance_type=Visitor.Instance.SINGLE_INSTANCE, context={
    #     "isVIPUser": True
    # }, consent=False)
    # visitor.fetch_flags()
    # featureEnabled = visitor.get_flag("featureEnabled", False).value(False)
    # print("=> " + str(featureEnabled))
    # visitor.send_hit(Screen("aaaaa"))
    #
    # visitor.authenticate("online_1")
    # visitor.fetch_flags()
    # featureEnabled = visitor.get_flag("featureEnabled", False).value(False)
    # print("=> " + str(featureEnabled))
    # visitor.send_hit(Screen("aaaaa"))
    #
    # visitor.unauthenticate()
    # visitor.fetch_flags()
    # featureEnabled = visitor.get_flag("featureEnabled", False).value(False)
    # print("=> " + str(featureEnabled))
    # visitor.send_hit(Screen("aaaaa"))



##################################################################

# def init_api():
#     Flagship.start("bkk4s7gcmjcg07fke9dg", "Q6FDmj6F188nh75lhEato2MwoyXDS7y34VrAL4Aa",
#                    DecisionApi(timeout=3000))
#     visitor = Flagship.new_visitor("_visitor_ze", instance_type=Visitor.Instance.SINGLE_INSTANCE, context={
#         # "isVIPUser": True,
#         'daysSinceLastLaunch': 3
#     }, consent=False)
#     visitor.fetch_flags()
#     featureEnabled = visitor.get_flag("featureEnabled", False).value(False)
#     print("=> " + str(featureEnabled))
#     visitor.send_hit(Screen("aaaaa"))
#
#     visitor.authenticate("online_1")
#     visitor.fetch_flags()
#     featureEnabled = visitor.get_flag("featureEnabled", False).value(False)
#     print("=> " + str(featureEnabled))
#     visitor.send_hit(Screen("aaaaa"))
#
#     visitor.unauthenticate()
#     visitor.fetch_flags()
#     featureEnabled = visitor.get_flag("featureEnabled", False).value(False)
#     print("=> " + str(featureEnabled))
#     visitor.send_hit(Screen("aaaaa"))



##################################################################

def init_bucketing():

    visitor = None
    class CustomStatusListener(StatusListener):

        def __init__(self, function):
            self.function = function

        def on_status_changed(self, new_status):
            print("New status = " + str(new_status))
            if new_status == Status.READY:
                self.function()

    def create_visitor():
        visitor = Flagship.new_visitor("111", instance_type=Visitor.Instance.SINGLE_INSTANCE)
        visitor.update_context({
            "coucou": 3,
            "coucou2": 2,
            "haha": False,
            "isVIPUser": True,
            "slug": True,
            "daysSinceLastLaunch": 3
        })
        visitor.fetch_flags()
        # time.sleep(5)
        print(visitor.get_flag("visitorIdColor", "default").value())

        time.sleep(1)
        visitor.send_hit(Screen("coucou 1"))
        visitor.send_hit(Screen("coucou 2"))
        visitor.send_hit(Screen("coucou 3"))
        visitor.send_hit(Screen("coucou 4"))
        visitor.send_hit(Screen("coucou 5"))
        time.sleep(1)
        visitor.send_hit(Transaction("TID_92470", "AFFILIATION"))
        visitor.send_hit(Transaction("TID_04444", "AFFILIATION2"))
        time.sleep(1)
        visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "ACTION 1"))
        visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "ACTION 2"))
        visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "ACTION 3"))
        visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "ACTION 4"))
        visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "ACTION 5"))
        time.sleep(4)
        visitor.send_hit(Item("TID_92470", "NAME", "SKU"))
        visitor.send_hit(Page("Not supposed to work"))
        visitor.send_hit(Page("https://www.supposed.towork.com"))


    Flagship.start("bkk4s7gcmjcg07fke9dg", "Q6FDmj6F188nh75lhEato2MwoyXDS7y34VrAL4Aa",
                   Bucketing(timeout=3000, status_listener=CustomStatusListener(create_visitor), polling_interval=10000,
                             tracking_manager_config=TrackingManagerConfig(pool_max_size=10, time_interval=5000)))
#
    time.sleep(20000)


init()
