import logging

from flagship import decorators
from flagship.model.modification import Modifications


class Variation:

    def __init__(self, variation_group_id, variation_id, reference, modifications, allocation, selected=False):
        self.variation_group_id = variation_group_id
        self.variation_id = variation_id
        self.reference = reference
        self.modifications = modifications
        self.allocation = allocation
        self.selected = selected

    def __str__(self):
        return '{{ "variation_group_id": "{}", "variation_id": "{}", "reference": {}, "modifications": {},' \
               ' "allocation": {}, "selected": {} }} '.format(self.variation_group_id, self.variation_id,
                                                              "true" if self.reference is True else "false",
                                                              self.modifications, self.allocation,
                                                              "true" if self.selected is True else "false")

    @staticmethod
    def parse(variation_group_id, variation_obj):
        try:
            variation_id = variation_obj['id']
            reference = variation_obj['reference'] if 'reference' in variation_obj else True
            modifications = Modifications.parse(variation_group_id, variation_id, reference, variation_obj['modifications'])
            allocation = 100 if 'allocation' not in variation_obj else variation_obj['allocation']
            return Variation(variation_group_id, variation_id, reference, modifications, allocation)
        except (ValueError, Exception):
            if decorators.customer_event_handler is not None:
                decorators.customer_event_handler.on_log(logging.ERROR,
                                                         "An error occurred while parsing variation group json object.")
            return None
