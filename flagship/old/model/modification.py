import logging

from six import string_types

from flagship.old import decorators


class Modification:

    def __init__(self, key, campaign_id, variation_group_id, variation_id, reference, value):
        self.key = key
        self.campaign_id = campaign_id
        self.variation_group_id = variation_group_id
        self.variation_id = variation_id
        self.reference = reference
        self.value = value

    def __str__(self):
        return '{{ "campaign_id": "{}", "variation_group_id": "{}", "variation_id": "{}", "reference": {},  "key": "{}", "value": {} }}' \
            .format(self.campaign_id, self.variation_group_id, self.variation_id,
                    "true" if self.reference is True else "false", self.key,
                    self.value_to_str(self.value))

    @staticmethod
    def value_to_str(value):
        if value is None:
            return "null"
        elif isinstance(value, str) or isinstance(value, string_types):
            return '"{}"'.format(value)
        elif isinstance(value, bool):
            return "true" if value is True else "false"
        else:
            return value


class Modifications:

    def __init__(self, campaign_id, variation_group_id, variation_id, reference, value_type, values):
        self.campaign_id = campaign_id
        self.variation_group_id = variation_group_id
        self.variation_id = variation_id
        self.reference = reference
        self.values = values
        self.value_type = value_type

    def __str__(self):
        return '{{ "campaign_id": "{}", "variation_group_id": "{}", "variation_id": "{}", "reference": {}, "value_type": "{}",' \
               ' "values":{} }}'.format(self.campaign_id, self.variation_group_id, self.variation_id,
                                        "true" if self.reference is True else "false", self.value_type,
                                        self.__modifications_to_str())

    def __modifications_to_str(self):
        values = dict(self.values)
        result = '['
        for k, v in values.items():
            result += '{{ "key": "{}", "modification":{} }},'.format(k, str(v))

        if len(result) > 1:
            result = result[:-1]
        result += ']'
        return result

    @staticmethod
    def parse(campaign_id, variation_group_id, variation_id, reference, modifications_obj):
        value_type = modifications_obj['type']
        values = dict()
        values_obj = modifications_obj['value']

        for key in values_obj:
            value = values_obj[key]
            t = type(value)
            if isinstance(value, string_types):
                value = str(value)
            try:
                if value is None or t is int or t is float or t is str or t is bool or \
                        isinstance(value, list) or isinstance(value, dict) or t is unicode:
                    values[key] = Modification(key, campaign_id, variation_group_id, variation_id, reference, value)
            except Exception as e:
                if decorators.customer_event_handler is not None:
                    decorators.customer_event_handler.on_log(logging.ERROR,
                                                             "An error occurred while parsing modification json object.")
        return Modifications(campaign_id, variation_group_id, variation_id, reference, value_type, values)
