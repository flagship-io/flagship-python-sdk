class Modification:
    def __init__(self, key, variation_group_id, variation_id, reference, value):
        self.key = key
        self.variation_group_id = variation_group_id
        self.variation_id = variation_id
        self.reference = reference
        self.value = value

    def __str__(self):
        return 'modification = {} {} {} {}'.format(self.variation_group_id, self.variation_id, self.reference,
                                                   self.value)


class Modifications:

    def __init__(self, variation_group_id, variation_id, reference, value_type, values):
        self.variation_group_id = variation_group_id
        self.variation_id = variation_id
        self.reference = reference
        self.values = values
        self.value_type = value_type

    def __str__(self):
        return 'modifications = {} {} {} {}'.format(self.variation_group_id, self.variation_id, self.reference,
                                                    self.value_type, self.values)

    @staticmethod
    def parse(variation_group_id, variation_id, reference, modifications_obj):
        value_type = modifications_obj['type']
        values = dict()
        values_obj = modifications_obj['value']
        for key in values_obj:
            value = values_obj[key]
            if value is None or type(value) == int or type(value) == str or type(value) == float or type(value) == bool:
                values[key] = Modification(key, variation_group_id, variation_id, reference, value)
        return Modifications(variation_group_id, variation_id, reference, value_type, values)
