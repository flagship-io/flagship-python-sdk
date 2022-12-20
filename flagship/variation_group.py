from __future__ import unicode_literals
import random
import traceback
from collections import OrderedDict

from flagship.constants import TAG_PARSING_VARIATION_GROUP, ERROR_PARSING_VARIATION_GROUP
from flagship.errors import FlagshipParsingError
from flagship.murmur32x86 import murmurHash
from flagship.targeting import TargetingGroup
from flagship.utils import log_exception
from flagship.variation import Variation


class VariationGroup:

    def __init__(self, campaign_id, variation_group_id, variations, targeting_groups=None, selected_variation_id=None):
        self.campaign_id = campaign_id
        self.variation_group_id = variation_group_id
        self.variations = variations
        self.targeting_groups = targeting_groups
        self.selected_variation_id = selected_variation_id

    def to_dict(self):
        variation_list = list()
        for (k, v) in self.variations.items():
            variation_list.append(v.to_dict())
        # return dict({
        return OrderedDict({
            "campaign_id": self.campaign_id,
            "variation_group_id": self.variation_group_id,
            "variations": variation_list
        })

    def is_targeting_valid(self, context):
        return self.targeting_groups.is_targeting_valid(context)

    def select_variation(self, visitor):
        if self.variations is not None:
            murmur_allocation = self._get_murmur_allocation(self.variation_group_id, visitor.visitor_id)
            p = 0
            for (variation_id, variation) in self.variations.items():
                if variation.allocation > 0:
                    p += variation.allocation
                    if murmur_allocation < p:
                        return variation
        return None




    def _get_murmur_allocation(self, variation_group_id, visitor_id):
        try:
            # decoded_visitor_id = visitor_id.decode('utf-8')
            decoded_visitor_id = visitor_id
            return murmurHash(variation_group_id + decoded_visitor_id) % 100
        except Exception as e:
            print(traceback.print_exc())
            return random.randint(0, 99)


    @staticmethod
    def parse(campaign_id, campaign_type, campaign_slug, variation_group_obj, bucketing):
        try:
            variation_group_id = variation_group_obj['id'] if bucketing else variation_group_obj['variationGroupId']
            # variations = dict()
            variations = OrderedDict()
            if not bucketing:
                variation_obj = variation_group_obj['variation']
                new_variation = Variation.parse(campaign_id, campaign_type, campaign_slug, variation_group_id,
                                                variation_obj, bucketing)
                if new_variation is not None:
                    variations[new_variation.variation_id] = new_variation
            else:
                for variation_obj in variation_group_obj['variations']:
                    new_variation = Variation.parse(campaign_id, campaign_type, campaign_slug, variation_group_id,
                                                    variation_obj, bucketing)
                    variations[new_variation.variation_id] = new_variation
            targeting_groups = None
            if 'targeting' in variation_group_obj:
                targeting_obj = variation_group_obj['targeting']
                targeting_group_obj = targeting_obj['targetingGroups']
                targeting_groups = TargetingGroup.parse(targeting_group_obj)
            return VariationGroup(campaign_id, variation_group_id, variations, targeting_groups)
        except Exception as e:
            log_exception(TAG_PARSING_VARIATION_GROUP, FlagshipParsingError(ERROR_PARSING_VARIATION_GROUP),
                          traceback.format_exc())
            return None
