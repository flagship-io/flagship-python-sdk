# coding: utf8
import sys
import time

from flagship.app import Flagship
from flagship.config import Config
from flagship.handler import FlagshipEventHandler
from flagship.helpers.hits import Page, Screen


class CustomEventHandler(FlagshipEventHandler):
    def __init__(self):
        FlagshipEventHandler.__init__(self)

    def on_log(self, level, message):
        FlagshipEventHandler.on_log(self, level, ">>> " + message)
        pass

    def on_exception_raised(self, exception, traceback):
        FlagshipEventHandler.on_exception_raised(self, exception, traceback)
        pass


def init():
    print(sys.version)
    t = CustomEventHandler()

    Flagship.instance().start("_my_env_id", "my_api_key",
                              Config(event_handler=t, mode=Config.Mode.API, timeout=2))
    v = Flagship.instance().create_visitor("visitor_uuid", {'isVIPUser': True})
    v.synchronize_modifications()
    value = v.get_modification("target", "default", True)
    v.send_hit(Screen("python screen view"))
    print(value)


init()
