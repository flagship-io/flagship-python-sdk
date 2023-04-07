from flagship import Flagship, LogLevel
from flagship.config import DecisionApi
from flagship.decision_mode import DecisionMode
from flagship.log_manager import LogManager, FlagshipLogManager
from flagship.status_listener import StatusListener


def test_initialization_missing_config():
    try:
        Flagship.start('_end_id_', '_api_key_')
        assert Flagship.config() is not None
        Flagship.config().env_id == '_env_id_'
        assert Flagship.config().api_key == '_api_key_'
        assert Flagship.config().timeout == 2000
        assert Flagship.config().log_manager is not None
        assert Flagship.config().status_listener is None
        assert Flagship.config().decision_mode is DecisionMode.DECISION_API
    except Exception as e:
        assert False


def test_initialization_empty_env_and_config():
    try:
        Flagship.start('', '', DecisionApi())
    except Exception as e:
        return
    assert False


def test_initialization_default():
    try:
        Flagship.start("_env_id_", "_api_key_", None)
        assert Flagship.config() is not None
        assert Flagship.config().env_id == '_env_id_'
        assert Flagship.config().api_key == '_api_key_'
        assert Flagship.config().timeout == 2000
        assert Flagship.config().log_manager is not None
        assert Flagship.config().status_listener is None
        assert Flagship.config().decision_mode is DecisionMode.DECISION_API
        assert Flagship.config().log_level == LogLevel.ALL
        assert Flagship.config().polling_interval == 60000
    except Exception as e:
        assert False

    try:
        Flagship.start("_env_id_", "_api_key_", DecisionApi())
        assert Flagship.config() is not None
        assert Flagship.config().env_id == "_env_id_"
        assert Flagship.config().api_key == "_api_key_"
        assert Flagship.config().timeout == 2000
        assert Flagship.config().log_manager is not None
        assert Flagship.config().status_listener is None
        assert Flagship.config().decision_mode is DecisionMode.DECISION_API
        assert Flagship.config().log_level == LogLevel.ALL
        assert Flagship.config().polling_interval == 60000
    except Exception as e:
        assert False


def test_initialization_wrong():
    Flagship.start("_env_id_", "_api_key_", DecisionApi(
        timeout="wrong",
        log_level="wrong",
        log_manager="None",
        status_listener="wrong",
        polling_interval="wrong"
    ))
    assert Flagship.config().timeout == 2000
    assert Flagship.config().log_manager is not None
    assert Flagship.config().status_listener is None
    assert Flagship.config().decision_mode is DecisionMode.DECISION_API
    assert Flagship.config().log_level == LogLevel.ALL
    assert Flagship.config().polling_interval == 60000
    assert isinstance(Flagship.config().log_manager, FlagshipLogManager)


def test_initialization_right():
    class CustomLogManager(LogManager):

        def log(self, tag, level, message):
            pass

        def exception(self, exception, traceback):
            pass

    class CustomStatusListener(StatusListener):

        def on_status_changed(self, new_status):
            pass

    Flagship.start("_env_id_", "_api_key_", DecisionApi(
        timeout=3000,
        log_level=LogLevel.DEBUG,
        status_listener=CustomStatusListener(),
        polling_interval=2000,
        log_manager=CustomLogManager()

    ))
    assert Flagship.config().timeout == 3000
    assert Flagship.config().log_manager is not None
    assert isinstance(Flagship.config().status_listener, CustomStatusListener)
    assert Flagship.config().decision_mode is DecisionMode.DECISION_API
    assert Flagship.config().log_level == LogLevel.DEBUG
    assert Flagship.config().polling_interval == 2000
    assert isinstance(Flagship.config().log_manager, CustomLogManager)

    Flagship.start("_env_id_2", "_api_key_2", DecisionApi(
        timeout=4000,
        log_level=LogLevel.WARNING,
        polling_interval=500,
    ))
    assert Flagship.config().env_id == "_env_id_2"
    assert Flagship.config().api_key == "_api_key_2"
    assert Flagship.config().timeout == 4000
    assert Flagship.config().log_manager is not None
    assert Flagship.config().status_listener is None
    assert Flagship.config().decision_mode is DecisionMode.DECISION_API
    assert Flagship.config().log_level == LogLevel.WARNING
    assert Flagship.config().polling_interval == 500
    assert isinstance(Flagship.config().log_manager, FlagshipLogManager)