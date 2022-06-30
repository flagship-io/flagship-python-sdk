import traceback

from flagship.modification import Modifications
from flagship.constants import _TAG_PARSING_VARIATION, _ERROR_PARSING_VARIATION
from flagship.errors import FlagshipParsingError
from flagship.utils import log_exception, pretty_dict


class Variation:

    def __init__(self, campaign_id, variation_group_id, variation_id, reference, modifications, allocation,
                 selected=False):
        self.campaign_id = campaign_id
        self.variation_group_id = variation_group_id
        self.variation_id = variation_id
        self.reference = reference
        self.modifications = modifications
        self.allocation = allocation
        self.selected = selected

    def to_dict(self):
        return dict({
            "campaign_id": self.campaign_id,
            "variation_group_id": self.variation_group_id,
            "variation_id": self.variation_id,
            "reference": "true" if self.reference else "false",
            "modifications": self.modifications.to_dict(),
            "allocation": self.allocation
        })

    @staticmethod
    def parse(campaign_id, variation_group_id, variation_obj, use_bucketing):
        try:
            variation_id = variation_obj['id']
            reference = variation_obj['reference'] if 'reference' in variation_obj else True
            modifications = Modifications.parse(campaign_id, variation_group_id, variation_id, reference,
                                                variation_obj['modifications'])
            if not use_bucketing:
                allocation = 100 if 'allocation' not in variation_obj else variation_obj['allocation']
            else:
                allocation = 0 if 'allocation' not in variation_obj else variation_obj['allocation']
            return Variation(campaign_id, variation_group_id, variation_id, reference, modifications, allocation)
        except Exception as e:
            log_exception(_TAG_PARSING_VARIATION, FlagshipParsingError(_ERROR_PARSING_VARIATION),
                          traceback.format_exc())
            return None

    def get_modification_values(self):
        return self.modifications.values
