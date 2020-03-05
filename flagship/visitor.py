from datetime import datetime
from flagship.decorators import exception_handler


class FlagshipVisitor:

    def __init__(self, visitor_id, context=None):
        self._visitor_id = visitor_id
        self._context = context
        self._last_call = datetime.now()

    def __getattribute__(self, name):
        if name != '_last_call':
            self._last_call = datetime.now()
        return super().__getattribute__(name)

    def send_hit(self):
        pass

    def synchronize_modifications(self):
        pass

    def get_modification(self, key, value, activate=False):
        pass

    def get_modifications(self, keys, values, activate=False):
        pass

    def activate_modifications(self, keys):
        pass

    @exception_handler
    def update_context(self, context):
        self._context = context
        # if self._cache:
        #     self._cache.save(self._visitor_id, context)

    def close(self):
        pass
