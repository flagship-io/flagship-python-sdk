

class Config:

    def __init__(self, env_id, api_key, debug=True):
        self.env_id = env_id
        self.api_key = api_key
        self.debug = debug
        self.timeout = 200  # in milliseconds
