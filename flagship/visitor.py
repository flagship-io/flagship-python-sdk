


class FlagshipVisitor:

    def __init__(self, visitor_id, context=None):
        self._visitor_id = visitor_id
        self._context = context

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

    def update_context(self, context):
        self._context = context

    def close(self):
        pass
