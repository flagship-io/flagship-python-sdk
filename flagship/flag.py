from flagship.flag_metadata import FlagMetadata


class Flag:

    def __init__(self, visitor, key, default_value):
        self.__visitor = visitor
        self.key = key
        self.default_value = default_value

    def value(self, user_exposed=True):
        value = self.__visitor._get_flag_value(self.key, self.default_value)
        if user_exposed:
            self.user_exposed()
        return value

    def user_exposed(self):
        self.__visitor.expose_flag(self.key)

    def exists(self):
        return self.metadata().exists()

    def metadata(self):
        return FlagMetadata(self.__visitor._get_modification(self.key))
