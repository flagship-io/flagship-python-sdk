

class Config:

    def __init__(self, env_id, debug=True):
        self.env_id = env_id
        self.debug = debug
        self.timeout = 200  # in milliseconds
