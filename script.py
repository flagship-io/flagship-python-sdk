# coding: utf8
import sys
import time

from flagship.app import Flagship
from flagship.config import Config
from flagship.handler import FlagshipEventHandler
from flagship.helpers.hits import Page


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

    Flagship.instance().start("ENV_ID", "API_KEY",
                              Config(event_handler=t, mode=Config.Mode.BUCKETING, polling_interval=5, timeout=0.1))
    v = Flagship.instance().create_visitor("visitorId 1", {'isVIPUser': True})
    v.synchronize_modifications()


init()
