import json
import logging
import random

from flagship import decorators
from flagship.model.variation import Variation
from flagship.model.targeting import TargetingGroup


class VariationGroup:

    def __init__(self, variation_group_id, variations, targeting_groups=None, selected_variation_id=None):
        self.variation_group_id = variation_group_id
        self.variations = variations
        self.targeting_groups = targeting_groups
        self.selected_variation_id = selected_variation_id

    def __str__(self):
        return '{{ "variation_group_id" : "{}", "variations" : {} }}'.format(self.variation_group_id, *self.variations)

    @staticmethod
    def parse(variation_group_obj, bucketing):
        try:
            variation_group_id = variation_group_obj['id'] if bucketing else variation_group_obj['variationGroupId']
            variations = list()
            selected_variation_id = None  # todo find in cache for bucketing
            if not bucketing:
                variation_obj = variation_group_obj['variation']
                new_variation = Variation.parse(variation_group_id, variation_obj)
                if new_variation is not None:
                    variations.append(new_variation)
                selected_variation_id = new_variation.variation_id
            else:
                r = random.randint(0, 100)
                p = 0
                selected_variation_id = None  # todo find in cache for bucketing
                for variation_obj in variation_group_obj['variations']:
                    new_variation = Variation.parse(variation_group_id, variation_obj)
                    p += new_variation.allocation
                    if r <= p:
                        if selected_variation_id is None:
                            selected_variation_id = new_variation.variation_id
                            new_variation.selected = True
                            # todo save alloc
                    variations.append(new_variation)

            targeting_groups = None
            if 'targeting' in variation_group_obj:
                targeting_obj = variation_group_obj['targeting']
                targeting_group_obj = targeting_obj['targetingGroups']
                targeting_groups = TargetingGroup.parse(targeting_group_obj)

            return VariationGroup(variation_group_id, variations, targeting_groups, selected_variation_id)

        except (ValueError, Exception):
            if decorators.customer_event_handler is not None:
                decorators.customer_event_handler.on_log(logging.ERROR,
                                                         "An error occurred while parsing variation group json object.")
            return None
