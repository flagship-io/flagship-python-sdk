import json

from enum import Enum

from flagship.model.targeting_comparator import TargetingComparator


class Targeting:

    def __init__(self, key, value, operator):
        self.key = key
        self.value = value
        self.operator = operator

    @staticmethod
    def parse(targeting_obj):
        try:
            key = targeting_obj['key']
            value = targeting_obj['value']
            operator = targeting_obj['operator']
            return Targeting(key, value, operator)
        except Exception as e:
            return None

    def is_targeting_valid(self, context):

        if self.key not in context:
            return False

        value0 = context[str(self.key)]
        value1 = self.value

        try:
            if value0 is None:
                return False
            else:
                return TargetingComparator().compare(self.operator, value0, value1)
        except Exception as e:
            return False

class TargetingList:

    def __init__(self, targeting_list):
        self.targeting_list = targeting_list

    def is_targeting_valid(self, context):
        for targeting in self.targeting_list:
            if targeting is None or targeting.is_targeting_valid(context) is False:
                return False
        return True

    @staticmethod
    def parse(targeting_list_obj):
        targeting_list = list()
        for targeting_obj in targeting_list_obj:
            targeting = Targeting.parse(targeting_obj)
            targeting_list.append(targeting)
        return TargetingList(targeting_list)


class TargetingGroup:

    def __init__(self, targeting_group):
        self.targeting_group = targeting_group

    def is_targeting_valid(self, context):
        for group in self.targeting_group:
            if group.is_targeting_valid(context):
                return True
        return False

    @staticmethod
    def parse(targeting_group_obj):
        targeting_group = list()
        for targeting_group_list_obj in targeting_group_obj:
            if 'targetings' in targeting_group_list_obj:
                targeting = TargetingList.parse(targeting_group_list_obj['targetings'])
                targeting_group.append(targeting)
        return TargetingGroup(targeting_group)
