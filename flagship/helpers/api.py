

class APIClient:

    def __init__(self, env_id):
        self._env_id = env_id
        self._url = 'https://api.flagship.io'

    @property
    def fs_url(self):
        return f'{self._url}/{self._env_id}'
