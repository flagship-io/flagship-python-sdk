from enum import Enum


class Status(Enum):
    NOT_INITIALIZED = 0
    STARTING = 10
    POLLING = 20
    PANIC = 30
    READY = 100
