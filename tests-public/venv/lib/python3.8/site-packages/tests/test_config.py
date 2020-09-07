from flagship.app import Flagship
from flagship.config import Config

def test_flagship_start_wrong_param():
    try:
        fs = Flagship.instance()
        fs.start("not_config_object")
        assert False
    except Exception as e:
        assert True


def test_flagship_start_wrong_param2():
    try:
        fs = Flagship.instance()
        fs.start(Config(12, 33))
        assert False
    except Exception as e:
        assert True


def test_config_params():
    try:
        fs = Flagship.instance()
        fs.start(Config("my_env_id", "my_api", event_handler=None))
        assert True
    except Exception as e:
        assert False


def test_config_handler_wrong_event_handler():

    class Wrong:
        def __init__(self):
            pass

    try:
        fs = Flagship.instance()
        fs.start(Config("my_env_id", "my_api", event_handler=Wrong()))
        assert False
    except Exception as e:
        assert True