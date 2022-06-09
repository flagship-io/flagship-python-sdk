class TargetingComparator:

    def __init__(self):
        pass

    def compare(self, tag, value0, value1):
        comparators = {
            'EQUALS': self.equals(value0, value1),
            'NOT_EQUALS': self.not_equals(value0, value1),
            'CONTAINS': self.contains(value0, value1),
            'NOT_CONTAINS': self.not_contains(value0, value1),
            'GREATER_THAN': self.greater_than(value0, value1),
            'LOWER_THAN': self.lower_than(value0, value1),
            'GREATER_THAN_OR_EQUALS': self.greater_than_or_equals(value0, value1),
            'LOWER_THAN_OR_EQUALS': self.lower_than_or_equals(value0, value1),
            'STARTS_WITH': self.starts_with(value0, value1),
            'ENDS_WITH': self.ends_with(value0, value1)
        }
        try:
            return comparators[tag]
        except Exception as e:
            return False

    def equals(self, value0, value1):
        try:
            return value0 == value1
        except Exception as e:
            return False

    def not_equals(self, value0, value1):
        try:
            return value0 != value1
        except Exception as e:
            return False

    def contains(self, value0, value1):
        try:
            return str(value1) in str(value0)
        except Exception as e:
            return False

    def not_contains(self, value0, value1):
        try:
            return str(value1) not in str(value0)
        except Exception as e:
            return False

    def greater_than(self, value0, value1):
        try:
            return value0 > value1
        except Exception as e:
            return False

    def lower_than(self, value0, value1):
        try:
            return value0 < value1
        except Exception as e:
            return False

    def greater_than_or_equals(self, value0, value1):
        try:
            return value0 >= value1
        except Exception as e:
            return False

    def lower_than_or_equals(self, value0, value1):
        try:
            return value0 <= value1
        except Exception as e:
            return False

    def starts_with(self, value0, value1):
        try:
            return str(value0).startswith(str(value1))
        except Exception as e:
            return False

    def ends_with(self, value0, value1):
        try:
            return str(value0).endswith(str(value1))
        except Exception as e:
            return False