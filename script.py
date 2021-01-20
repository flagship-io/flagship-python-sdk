# coding: utf8
import json
import sys

from flagship.app import Flagship
from flagship.cache.cache_visitor import VisitorCacheManager
from flagship.config import Config
from flagship.handler import FlagshipEventHandler


class CustomEventHandler(FlagshipEventHandler):
    def __init__(self):
        FlagshipEventHandler.__init__(self)

    def on_log(self, level, message):
        FlagshipEventHandler.on_log(self, level, ">>> " + message)
        pass

    def on_exception_raised(self, exception, traceback):
        FlagshipEventHandler.on_exception_raised(self, exception, traceback)
        pass


class CustomVisitorCacheManager(VisitorCacheManager):

    def save(self, visitor_id, visitor_data):
        print("visitor_data ==> " + json.dumps(visitor_data))

    def lookup(self, visitor_id):
        json_data = '{"version":1,"data":{"vId":"visitorId_2","vaIds":["bv6vqg65k9h02cuc1ae0", "bmsor064jaeg0gm49cmg"]}}'
        return json.loads(json_data)

def init():
    print(sys.version)
    t = CustomEventHandler()

    Flagship.instance().start("bkk4s7gcmjcg07fke9dg", "Q6FDmj6F188nh75lhEato2MwoyXDS7y34VrAL4Aa",
                              Config(event_handler=t, mode=Config.Mode.BUCKETING, polling_interval=5, timeout=0.1,
                                     visitor_cache_manager=CustomVisitorCacheManager()))
    v = Flagship.instance().create_visitor("visitorId_2", {'isVIPUser': True, 'daysSinceLastLaunch': 3})
    v.synchronize_modifications()

    print("> Get visitorIdColor = " + v.get_modification('visitorIdColor', 'default', False))
    print("> Get Title = " + v.get_modification('title', 'default', "default"))
    print("> Get featureEnabled = " + str(v.get_modification('featureEnabled', 'default', False)))
    print("> Get isRef = " + str(v.get_modification('isref', 'default', False)))


#["bmsor064jaeg0gm49cm0", "bmsorfe4jaeg0gi1bhr0", "bmsorfe4jaeg0gi1bhq0", "bu6lgeu3bdt014iap5b0", "bu6lttip17b01emh0l70", "bv6vpqjh6h101fk8lbtg"]
# > Get visitorIdColor = default
# > Get featureEnabled = True
# > Get isRef = nope

#[bv6vqg65k9h02cuc1ae0, bmsor064jaeg0gm49cm0]
init()