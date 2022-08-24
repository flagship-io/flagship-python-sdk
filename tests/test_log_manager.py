import time
from mock import mock_open, patch

from flagship import Flagship
from flagship.config import Bucketing
from flagship.log_manager import LogManager, LogLevel
from test_constants_res import BUCKETING_RESPONSE_1


@patch('io.open', mock_open(read_data=BUCKETING_RESPONSE_1))
@patch('os.path.isfile', return_value=True)
def test_initialization_custom_log_manager_only_debug(isfile_mock):
    Flagship.stop()  # reset SDK
    logs = []
    class CustomLogManager(LogManager):

        def log(self, tag, level, message):
            print('{}:{}:{}'.format(tag, level, message))
            logs.append('{}:{}:{}'.format(tag, level, message))

        def exception(self, exception, traceback):
            pass

    Flagship.start("_env_id_", "_api_key_", Bucketing(
        log_manager=CustomLogManager(),
        log_level=LogLevel.DEBUG
    ))
    time.sleep(1)
    print(str(logs))
    assert len(logs) == 3
    assert [log for log in logs if "has started successfully" in log] is not None

@patch('io.open', mock_open(read_data=BUCKETING_RESPONSE_1))
@patch('os.path.isfile', return_value=True)
def test_initialization_custom_log_manager_only_error(isfile_mock):
    Flagship.stop()  # reset SDK
    logs = []
    class CustomLogManager(LogManager):

        def log(self, tag, level, message):
            print('{}:{}:{}'.format(tag, level, message))
            logs.append('{}:{}:{}'.format(tag, level, message))

        def exception(self, exception, traceback):
            pass

    Flagship.start("_env_id_", "_api_key_", Bucketing(
        log_manager=CustomLogManager(),
        log_level=LogLevel.ERROR
    ))
    time.sleep(1)
    assert len(logs) == 5
    assert [log for log in logs if "403" in log] is not None
    assert [log for log in logs if "has started successfully" in log] is not None
    assert [log for log in logs if "SDK status has changed" in log] is not None

