import traceback

# from six import string_types
from flagship.constants import TAG_PARSING_MODIFICATION, ERROR_PARSING_MODIFICATION
from flagship.errors import FlagshipParsingError
from flagship.utils import log_exception


class Modification:

    def __init__(self, key, campaign_id, campaign_type, campaign_slug, variation_group_id, variation_id, reference,
                 value):
        self.key = key
        self.campaign_id = campaign_id
        self.variation_group_id = variation_group_id
        self.variation_id = variation_id
        self.reference = reference
        self.value = value
        self.type = campaign_type
        self.slug = campaign_slug


class Modifications:

    def __init__(self, campaign_id, campaign_type, campaign_slug, variation_group_id, variation_id, reference,
                 value_type, values):
        self.campaign_id = campaign_id
        self.campaign_type = campaign_type
        self.campaign_slug = campaign_slug
        self.variation_group_id = variation_group_id
        self.variation_id = variation_id
        self.reference = reference
        self.values = values
        self.value_type = value_type

    def to_dict(self):
        values_list = list()
        for k, v in self.values.items():
            values_list.append(dict({
                "key": k,
                "value": v.value
            }))
        return values_list

    @staticmethod
    def parse(campaign_id, campaign_type, campaign_slug, variation_group_id, variation_id, reference,
              modifications_obj):
        try:
            values = dict()
            value_type = modifications_obj['type']
            values_obj = modifications_obj['value']
            for key in values_obj:
                value = values_obj[key]
                t = type(value)
                if isinstance(value, str):
                    value = str(value)
                try:
                    # if value is None or t is int or t is float or t is str or t is bool or \
                    #         isinstance(value, list) or isinstance(value, dict) or t is unicode:
                    if value is None or t is int or t is float or t is str or t is bool or \
                            isinstance(value, list) or isinstance(value, dict):
                        values[key] = Modification(key, campaign_id, campaign_type, campaign_slug, variation_group_id,
                                                   variation_id, reference, value)
                except Exception as e:
                    log_exception(TAG_PARSING_MODIFICATION, FlagshipParsingError(ERROR_PARSING_MODIFICATION),
                                  traceback.format_exc())
            return Modifications(campaign_id, campaign_type, campaign_slug, variation_group_id, variation_id, reference,
                                 value_type, values)
        except Exception:
            return None
