import time

from flagship import Flagship, Status
from flagship.config import DecisionApi, Bucketing
from flagship.status_listener import StatusListener


def test_initialization_status_listener_api():
    Flagship.stop()  # reset SDK
    status = []

    class CustomStatusListener(StatusListener):

        def on_status_changed(self, new_status):
            status.append(new_status.name)

    assert Flagship.status() == Status.NOT_INITIALIZED

    Flagship.start("_env_id_", "_api_key_", DecisionApi(
        status_listener=CustomStatusListener()
    ))
    assert len(status) == 2
    assert status[0] == Status.STARTING.name
    assert status[1] == Status.READY.name


def test_initialization_status_listener_bucketing():
    Flagship.stop()  # reset SDK
    status = []

    class CustomStatusListener(StatusListener):

        def on_status_changed(self, new_status):
            status.append(new_status.name)

    assert Flagship.status() == Status.NOT_INITIALIZED

    Flagship.start("_env_id_", "_api_key_", Bucketing(
        status_listener=CustomStatusListener()
    ))
    time.sleep(3)
    assert len(status) == 3
    assert status[0] == Status.STARTING.name
    assert status[1] == Status.POLLING.name
    assert status[2] == Status.READY.name
