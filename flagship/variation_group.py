import traceback

from flagship.constants import _TAG_PARSING_VARIATION_GROUP, _ERROR_PARSING_VARIATION_GROUP
from flagship.errors import FlagshipParsingError
# from flagship import murmurHash
from flagship.targeting import TargetingGroup
from flagship.utils import log_exception, pretty_dict
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
        return dict({
            "campaign_id": self.campaign_id,
            "variation_group_id": self.variation_group_id,
            "variations": variation_list
        })

    def is_targeting_valid(self, context):
        return self.targeting_groups.is_targeting_valid(context)

    @staticmethod
    def parse(campaign_id, variation_group_obj, bucketing):
        try:
            variation_group_id = variation_group_obj['id'] if bucketing else variation_group_obj['variationGroupId']
            variations = dict()
            if not bucketing:
                variation_obj = variation_group_obj['variation']
                new_variation = Variation.parse(campaign_id, variation_group_id, variation_obj, bucketing)
                if new_variation is not None:
                    variations[new_variation.variation_id] = new_variation
            else:
                for variation_obj in variation_group_obj['variations']:
                    new_variation = Variation.parse(campaign_id, variation_group_id, variation_obj, bucketing)
                    variations[new_variation.variation_id] = new_variation
            targeting_groups = None
            if 'targeting' in variation_group_obj:
                targeting_obj = variation_group_obj['targeting']
                targeting_group_obj = targeting_obj['targetingGroups']
                targeting_groups = TargetingGroup.parse(targeting_group_obj)
            return VariationGroup(campaign_id, variation_group_id, variations, targeting_groups)
        except Exception as e:
            log_exception(_TAG_PARSING_VARIATION_GROUP, FlagshipParsingError(_ERROR_PARSING_VARIATION_GROUP),
                          traceback.format_exc())
            return None
