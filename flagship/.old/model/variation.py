import logging

from flagship import decorators
from flagship import Modifications


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

    def __str__(self):
        return '{{ "campaign_id": "{}", "variation_group_id": "{}", "variation_id": "{}", ' \
               '"reference": {}, "modifications": {}, "allocation": {}, "selected": {} }} ' \
            .format(self.campaign_id, self.variation_group_id, self.variation_id,
                    "true" if self.reference is True else "false", self.modifications,
                    self.allocation, "true" if self.selected is True else "false")

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
            if decorators.customer_event_handler is not None:
                decorators.customer_event_handler.on_log(logging.ERROR,
                                                         "An error occurred while parsing variation json object.")
            return None
