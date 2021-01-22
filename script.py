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

    Flagship.instance().start("bkk4s7gcmjcg07fke9dg", "Q6FDmj6F188nh75lhEato2MwoyXDS7y34VrAL4Aa",
                              Config(event_handler=t, mode=Config.Mode.API, polling_interval=5, timeout=2))
    v = Flagship.instance().create_visitor("visitorId_python_DS_web", {'isVIPUser': True})
    v.synchronize_modifications()
    value = v.get_modification("target", "default", True)
    v.send_hit(Page("https://pageviewurl.com DS web").with_page_title("title"))
    v.send_hit(Page("python page view DS web").with_page_title("title"))
    v.send_hit(Screen("python screen view DS web"))
    print(value)


init()
