from flagship import Flagship
from flagship.old.config import Config


def test_flagship_singleton():
    fs = Flagship.instance()
    fs.start("my_env_id", "my_api_key", Config())
    fs2 = Flagship.instance()
    fs2.start("my_env_id2", "my_api_key2", Config())
    assert fs._config is not None and fs2._config is not None
    assert fs == fs2
    assert fs._config == fs2._config
    assert fs._config.env_id == "my_env_id2" and fs2._config.env_id == "my_env_id2"
    assert fs._config.api_key == "my_api_key2" and fs2._config.api_key == "my_api_key2"


def test_is_started():
    assert Flagship.instance().is_flagship_started()
