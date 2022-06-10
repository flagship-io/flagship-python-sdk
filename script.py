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
from flagship.main.config import DecisionApi, Bucketing
from flagship.main.status_listener import StatusListener


def init():
    print(sys.version)

    class CustomStatusListener(StatusListener):

        def on_status_changed(self, new_status):
            print("New status = " + str(new_status))

    Flagship.start("zfzkefmefmekfj", "zlfdn", DecisionApi(timeout=3000, status_listener=CustomStatusListener()))

    Flagship._log("from here", LogLevel.CRITICAL, "aie aie aie")

init()
