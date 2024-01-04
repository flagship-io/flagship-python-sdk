from enum import Enum


class Status(Enum):
    """
    Flagship Status enum
    """

    NOT_INITIALIZED = 0
    """
    Flagship SDK has not been started or initialized successfully.
    """

    STARTING = 10
    """
    Flagship SDK is starting.
    """

    POLLING = 20
    """
    Flagship SDK has been started successfully but is still polling campaigns (Bucketing Mode).
    """

    PANIC = 30
    """
    Flagship SDK is ready but is running in Panic mode: All features are disabled except 'fetchFlag' which refresh this 
    status.
    """

    READY = 100
    """
    Flagship SDK is ready to use.
    """

