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
import sys

from flagship import *
from flagship.config import DecisionApi
from flagship.hits import Hit, Screen
from flagship.log_manager import LogManager
from flagship.status_listener import StatusListener


def init():
    print(sys.version)

    class CustomStatusListener(StatusListener):

        def on_status_changed(self, new_status):
            print("New status = " + str(new_status))

    class CustomLogManager(LogManager):

        def log(self, tag, level, message):
            print(">>> " + tag + str(level) + message)

        def exception(self, exception, traceback):
            pass

    # Flagship.start("custom_end_id", "custom_api_key", DecisionApi(timeout=3000, status_listener=CustomStatusListener()))
    Flagship.start("bkk4s7gcmjcg07fke9dg", "Q6FDmj6F188nh75lhEato2MwoyXDS7y34VrAL4Aa", DecisionApi(timeout=3000, status_listener=CustomStatusListener()))
    # Flagship.start("custom_end_id", "custom_api_key", DecisionApi(timeout=3000, status_listener=CustomStatusListener(), log_manager=CustomLogManager()))
    visitor = Flagship.new_visitor("toto", instance_type=Visitor.Instance.SINGLE_INSTANCE)
    print(visitor._visitor_id)
    print(Flagship.get_visitor()._visitor_id)
    visitor.update_context({
        "coucou":3,
        "coucou2":2,
        "haha": False,
        "isVIPUser":True
    })
    visitor.update_context(('coucou3', 2))
    visitor.fetch_flags()
    print("Json.metadata > " + visitor.get_flag("json", dict()).metadata().toJson())
    print("Json.exists > " + str(visitor.get_flag("json", dict()).exists()))
    print("Json.value > " + str(visitor.get_flag("json", dict()).value(False)))

    print("string.metadata > " + str(visitor.get_flag("string", "default").metadata().toJson()))
    print("string.exists > " + str(visitor.get_flag("string", "default").exists()))
    print("string.value > " + str(visitor.get_flag("string", "default").value(False)))

    print("featureEnabled.metadata > " + str(visitor.get_flag("featureEnabled", False).metadata().toJson()))
    print("featureEnabled.exists > " + str(visitor.get_flag("featureEnabled", False).exists()))
    print("featureEnabled.value > " + str(visitor.get_flag("featureEnabled", False).value(False)))

    print("nope.metadata > " + str(visitor.get_flag("nope", 1).metadata().toJson()))
    print("nope.exists > " + str(visitor.get_flag("nope", 1).exists()))
    print("nope.value > " + str(visitor.get_flag("nope", 1).value(False)))

    visitor.get_flag("featureEnabled", False).user_exposed()
    visitor.send_hit(Screen('Script.py'))
    visitor.fetch_flags()
    visitor.set_consent(False)
    visitor.send_hit(Screen('Script.py 2'))
    visitor.set_consent(True)
    visitor.send_hit(Screen('Script.py 3'))


init()
