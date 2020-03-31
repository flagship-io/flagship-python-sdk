from flagship.visitor import FlagshipVisitor
from flagship.helpers.api import APIClient
from flagship.config import Config

class Flagship:

    class __Flagship:

        _config: Config

        def __init__(self):
            self._is_initialized = False

        def start(self, config: Config):
            self._config = config
            self._is_initialized = True
            # self._cache_manager = self._config.get('cache_manager')

        def create_visitor(self, visitor_id, context):
            return FlagshipVisitor(self._config, visitor_id, context)

        def get_or_create_visitor(self, visitor_id, context):
            # if self._cache_manager:
            #     return self._cache_manager.get(visitor_id, context)
            return self.create_visitor(visitor_id, context)

        def close(self):
            instance = None

    instance = None

    def __new__(cls, *args, **kwargs):
        if not Flagship.instance:
            Flagship.instance = Flagship.__Flagship(*args, **kwargs)
        return Flagship.instance

