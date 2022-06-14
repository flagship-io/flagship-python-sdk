from enum import Enum


class Visitor:

    class Instance(Enum):
        SINGLE_INSTANCE = "SINGLE_INSTANCE",
        NEW_INSTANCE = "NEW_INSTANCE"

    def __init__(self, configuration_manager, visitor_id, **kwargs):
        self.configuration_manager = configuration_manager
        self.visitor_id = visitor_id

