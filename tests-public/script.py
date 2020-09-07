# coding: utf8

import sys

from flagship.app import Flagship
from flagship.config import Config
from flagship.handler import FlagshipEventHandler
from flagship.visitor import FlagshipVisitor


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

    Flagship.instance().start(Config("your_env_id", "your_api_key_if_provided", event_handler=t))

    visitor = Flagship.instance().create_visitor("visitorId", {'isVIPUser': True})  # type: FlagshipVisitor

    visitor.synchronize_modifications()


init()
