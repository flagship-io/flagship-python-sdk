import traceback
from collections import OrderedDict

from flagship.variation_group import VariationGroup
from flagship.utils import log_exception, pretty_dict
from flagship.constants import TAG_PARSING_CAMPAIGNS, ERROR_PARSING_CAMPAIGN
from flagship.errors import FlagshipParsingError


class Campaign:

    def __init__(self, campaign_id, variation_groups):
        self.campaign_id = campaign_id
        self.variation_groups = variation_groups

    def get_modifications(self, use_bucketing, context):
        # modifications = dict()
        modifications = OrderedDict()
        for variation_group in self.variation_groups:
            if use_bucketing is False:
                for key in variation_group.variations:
                    variation = variation_group.variations[key]
                    modification = variation.modifications.values
                    modifications.update(modification)
            else:
                variation_id = variation_group.selected_variation_id
                if variation_group.is_targeting_valid(context):
                    variation = variation_group.variations[variation_id]
                    modification = variation.modifications.values
                    modifications.update(modification)
                    break
        return modifications

    def to_dict(self):
        variation_groups_list = list()
        for vg in self.variation_groups:
            variation_groups_list.append(vg.to_dict())
        # return dict({
        return OrderedDict({
            "campaign_id": self.campaign_id,
            "variation_groups": variation_groups_list
        })

    @staticmethod
    def parse(json):
        try:
            campaign_id = json['id']
            campaign_type = json['type'] if 'type' in json else ""
            campaign_slug = json['slug'] if 'slug' in json else ""
            variation_groups = list()
            variation_groups_obj = json['variationGroups'] if 'variationGroups' in json else json
            bucketing = type(variation_groups_obj) == list
            if bucketing:
                for variation_group_obj in variation_groups_obj:
                    variation_groups.append(
                        VariationGroup.parse(campaign_id, campaign_type, campaign_slug, variation_group_obj, True))
            else:
                new_variation_group = VariationGroup.parse(campaign_id, campaign_type, campaign_slug, json, bucketing)
                if new_variation_group is not None:
                    variation_groups.append(new_variation_group)
            return Campaign(campaign_id, variation_groups)
        except (ValueError, Exception):
            log_exception(TAG_PARSING_CAMPAIGNS, FlagshipParsingError(ERROR_PARSING_CAMPAIGN), traceback.format_exc())
            return None

    @staticmethod
    def parse_campaigns(json):
        campaigns = list()
        if 'campaigns' in json:
            campaigns_objs = json["campaigns"]
            for campaign_obj in campaigns_objs:
                new_campaign = Campaign.parse(campaign_obj)
                if new_campaign is not None:
                    campaigns.append(new_campaign)
        return campaigns
