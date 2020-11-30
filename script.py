# coding: utf8
from datetime import date, datetime
import random
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
    Flagship.instance().start("bkk9glocmjcg0vtmdlng", "j2jL0rzlgVaODLw2Cl4JC3f4MflKrMgIaQOENv36",
                              Config(event_handler=t, mode=Config.Mode.API, polling_interval=5, timeout=10))
    # Flagship.instance().start("bkk4s7gcmjcg07fke9dg", "j2jL0rzlgVaODLw2Cl4JC3f4MflKrMgIaQOENv36",
    #                           Config(event_handler=t, mode=Config.Mode.API))

    # v = Flagship.instance().create_visitor("anonymous_1", False, {'isVIPUser': True})
    # v.synchronize_modifications()
    # print("VISITOR ID : " + str(v._visitor_id))
    # print("ANONYMOUS ID : " + str(v._anonymous_id))
    #
    # v.authenticate("logged_1", None, True)
    # print("VISITOR ID : " + str(v._visitor_id))
    # print("ANONYMOUS ID : " + str(v._anonymous_id))
    #
    # v.unauthenticate({}, True)
    # print("VISITOR ID : " + str(v._visitor_id))
    # print("ANONYMOUS ID : " + str(v._anonymous_id))
    #
    # v.authenticate("log_2", None, True)
    # print("VISITOR ID : " + str(v._visitor_id))
    # print("ANONYMOUS ID : " + str(v._anonymous_id))
    #
    # v.authenticate("log_3", None, True)
    # print("VISITOR ID : " + str(v._visitor_id))
    # print("ANONYMOUS ID : " + str(v._anonymous_id))

    v = Flagship.instance().create_visitor("log1", True, {'isVIPUser': True})
    v.synchronize_modifications()
    print("VISITOR ID : " + str(v._visitor_id))
    print("ANONYMOUS ID : " + str(v._anonymous_id))
    v.activate_modification("btnTitle")
    v.send_hit(Page("page"))

    v.unauthenticate(None, True)
    print("VISITOR ID : " + str(v._visitor_id))
    print("ANONYMOUS ID : " + str(v._anonymous_id))
    v.activate_modification("btnTitle")
    v.send_hit(Page("page"))

    v.authenticate("toto", None, True)
    print("VISITOR ID : " + str(v._visitor_id))
    print("ANONYMOUS ID : " + str(v._anonymous_id))
    v.activate_modification("btnTitle")
    v.send_hit(Page("page"))


    # v = Flagship.instance().create_visitor("visitorId 1", {'isVIPUser': True})
    # v2 = Flagship.instance().create_visitor("visitorId 2", {'isVIPUser': False})
    #
    # count = 0
    # run = True
    # while run:
    #     v.update_context(('isVIPUser', count % 2 == 0))
    #     v.synchronize_modifications()
    #     v.activate_modification('featureEnabled')
    #     v.send_hit(Page("page 1"))
    #
    #     v2.update_context(('isVIPUser', count % 2 == 1))
    #     v2.synchronize_modifications()
    #     v2.activate_modification('featureEnabled')
    #     v2.send_hit(Page("page 2"))
    #
    #     time.sleep(2)
    #     count += 1

    # Flagship.instance().close()

init()