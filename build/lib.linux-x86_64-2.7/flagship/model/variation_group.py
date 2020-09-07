import json
import logging
import random
import sys
import traceback

from flagship import decorators
from flagship.helpers.murmur32x86 import murmurHash
from flagship.model.targeting import TargetingGroup
from flagship.model.variation import Variation


class VariationGroup:

    def __init__(self, campaign_id, variation_group_id, variations, targeting_groups=None, selected_variation_id=None):
        self.campaign_id = campaign_id
        self.variation_group_id = variation_group_id
        self.variations = variations
        self.targeting_groups = targeting_groups
        self.selected_variation_id = selected_variation_id

    def __str__(self):
        variations = "["
        for (k, v) in self.variations.items():
            variations += str(v) + ","
        if len(variations) > 1:
            variations = variations[:-1]
        variations += "]"
        return '{{ "campaign_id": "{}", "variation_group_id" : "{}", "variations" : {} }}'. \
            format(self.campaign_id, self.variation_group_id, variations)

    def is_targeting_valid(self, context):
        return self.targeting_groups.is_targeting_valid(context)

    @staticmethod
    def parse(campaign_id, variation_group_obj, bucketing, visitor_id=None):
        try:
            variation_group_id = variation_group_obj['id'] if bucketing else variation_group_obj['variationGroupId']
            variations = dict()
            selected_variation_id = None  # todo find in cache for bucketing
            if not bucketing:
                variation_obj = variation_group_obj['variation']
                new_variation = Variation.parse(campaign_id, variation_group_id, variation_obj, bucketing)
                if new_variation is not None:
                    # variations.append(new_variation)
                    variations[new_variation.variation_id] = new_variation
                selected_variation_id = new_variation.variation_id
            else:
                if sys.version_info[0] < 3:
                    visitor_id = visitor_id.decode('utf-8')
                r = (murmurHash(variation_group_id + visitor_id) % 100) if visitor_id is not None else random.randint(0, 99)
                p = 0
                selected_variation_id = None  # todo find in cache for bucketing
                for variation_obj in variation_group_obj['variations']:
                    if 'allocation' in variation_obj:
                        new_variation = Variation.parse(campaign_id, variation_group_id, variation_obj, bucketing)
                        p += new_variation.allocation
                        if r < p:
                            if selected_variation_id is None:
                                selected_variation_id = new_variation.variation_id
                                new_variation.selected = True
                                # todo save alloc
                        # variations.append(new_variation)
                        variations[new_variation.variation_id] = new_variation
            targeting_groups = None
            if 'targeting' in variation_group_obj:
                targeting_obj = variation_group_obj['targeting']
                targeting_group_obj = targeting_obj['targetingGroups']
                targeting_groups = TargetingGroup.parse(targeting_group_obj)
            return VariationGroup(campaign_id, variation_group_id, variations, targeting_groups, selected_variation_id)

        except Exception as e:
            if decorators.customer_event_handler is not None:
                decorators.customer_event_handler.on_log(logging.ERROR,
                                                         "An error occurred while parsing variation group json object : ".format(
                                                             str(traceback.format_exc())))
            return None
