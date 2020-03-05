

class Config:

    def __init__(self, env_id, debug):
        self._env_id = env_id
        self._debug = debug
        self._timeout = 200  # in milliseconds
