class Targeting:

    def __init__(self, key, value, operator):
        self.key = key
        self.value = value
        self.operator = operator

    @staticmethod
    def parse(targeting_obj):
        key = targeting_obj['key']
        value = targeting_obj['value']
        operator = targeting_obj['operator']
        return Targeting(key, value, operator)

    def is_targeting_valid(self):
        return False  # todo



class TargetingList:

    def __init__(self, targetings):
        self.targetings = targetings

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

    @staticmethod
    def parse(targeting_group_obj):
        targeting_group = list()
        for targeting_group_list_obj in targeting_group_obj:
            targeting = TargetingList.parse(targeting_group_list_obj)
            targeting_group.append(targeting)
        return TargetingGroup(targeting_group)
