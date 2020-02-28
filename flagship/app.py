from flagship.visitor import FlagshipVisitor


class Flagship:

    class __Flagship:

        def __init__(self):
            self._is_initialized = False

        def start(self, config):
            self._config = config
            self._is_initialized = True

        def create_visitor(self, visitor_id, context):
            return FlagshipVisitor(visitor_id, context)

        def close(self):
            instance = None

    instance = None

    def __new__(cls, *args, **kwargs):
        if not Flagship.instance:
            Flagship.instance = Flagship.__Flagship(*args, **kwargs)
        return Flagship.instance
