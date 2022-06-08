from flagship import Flagship
from flagship.old.config import Config
from flagship.old.handler import FlagshipEventHandler


def test_init():
    class CustomEventHandler(FlagshipEventHandler):
        def __init__(self):
            FlagshipEventHandler.__init__(self)

        def on_log(self, level, message):
            FlagshipEventHandler.on_log(self, level, ">>> " + message)
            # print("on log >> " + message)
            pass

        def on_exception_raised(self, exception, traceback):
            FlagshipEventHandler.on_exception_raised(self, exception, traceback)
            # print("on exception >> " + str(exception))
            pass

    fs = Flagship.instance()
    fs.start("my_env_id", "my_api_key", Config(event_handler=CustomEventHandler()))
    assert Flagship.instance()._config.env_id == "my_env_id"
    assert Flagship.instance()._config.api_key == "my_api_key"
    assert Flagship.instance()._config.event_handler is not None
    assert isinstance(Flagship.instance()._config.event_handler, CustomEventHandler)

