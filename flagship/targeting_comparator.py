
class TargetingComparator:

    def __init__(self):
        pass

    def compare(self, tag, value0, value1):
        try:
            return {
                'EQUALS': self.equals,
                'NOT_EQUALS': self.not_equals,
                'CONTAINS': self.contains,
                'NOT_CONTAINS': self.not_contains,
                'GREATER_THAN': self.greater_than,
                'LOWER_THAN': self.lower_than,
                'GREATER_THAN_OR_EQUALS': self.greater_than_or_equals,
                'LOWER_THAN_OR_EQUALS': self.lower_than_or_equals,
                'STARTS_WITH': self.starts_with,
                'ENDS_WITH': self.ends_with
            }[tag](value0, value1)
        except Exception as e:
            return False

    def equals(self, value0, value1):
        try:
            if isinstance(value1, list) is False:
                return value0 == value1
            else:
                for i in range(0, len(value1)):
                    if value0 == value1[i]:
                        return True
                return False
        except Exception as e:
            return False

    def not_equals(self, value0, value1):
        try:
            if isinstance(value1, list) is False:
                return value0 != value1
            else:
                for i in range(0, len(value1)):
                    if value0 == value1[i]:
                        return False
                return True
        except Exception as e:
            return False

    def contains(self, value0, value1):
        try:
            if isinstance(value1, list) is False:
                return str(value1) in str(value0)
            else:
                for i in range(0, len(value1)):
                    if str(value1[i]) in str(value0):
                        return True
                return False
        except Exception as e:
            return False

    def not_contains(self, value0, value1):
        try:
            if isinstance(value1, list) is False:
                return str(value1) not in str(value0)
            else:
                for i in range(0, len(value1)):
                    if str(value1[i]) in str(value0):
                        return False
                return True
        except Exception as e:
            return False

    def greater_than(self, value0, value1):
        try:
            if isinstance(value1, list) is False:
                return value0 > value1
            else:
                for i in range(0, len(value1)):
                    if value0 > value1[i]:
                        return True
                return False
        except Exception as e:
            return False

    def lower_than(self, value0, value1):
        try:
            if isinstance(value1, list) is False:
                return value0 < value1
            else:
                for i in range(0, len(value1)):
                    if value0 < value1[i]:
                        return True
                return False
        except Exception as e:
            return False

    def greater_than_or_equals(self, value0, value1):
        try:
            if isinstance(value1, list) is False:
                return value0 >= value1
            else:
                for i in range(0, len(value1)):
                    if value0 >= value1[i]:
                        return True
                return False
        except Exception as e:
            return False

    def lower_than_or_equals(self, value0, value1):
        try:
            if isinstance(value1, list) is False:
                return value0 <= value1
            else:
                for i in range(0, len(value1)):
                    if value0 <= value1[i]:
                        return True
                return False
        except Exception as e:
            return False

    def starts_with(self, value0, value1):
        try:
            # return str(value0).startswith(str(value1))
            if isinstance(value1, list) is False:
                return str(value0).startswith(str(value1))
            else:
                for i in range(0, len(value1)):
                    if str(value0).startswith(str(value1[i])):
                        return True
                return False
        except Exception as e:
            return False

    def ends_with(self, value0, value1):
        try:
            # return str(value0).endswith(str(value1))
            if isinstance(value1, list) is False:
                return str(value0).endswith(str(value1))
            else:
                for i in range(0, len(value1)):
                    if str(value0).endswith(str(value1[i])):
                        return True
                return False
        except Exception as e:
            return False