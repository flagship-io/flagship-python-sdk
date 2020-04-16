import logging
import traceback

from flagship import decorators
from flagship.decorators import exception_handler
from flagship.errors import FlagshipParsingError
from flagship.model.variation_group import VariationGroup


class Campaign:

    def __init__(self, campaign_id, variation_groups):
        self.campaign_id = campaign_id
        self.variation_groups = variation_groups

    def get_modifications(self):
        modifications = dict()
        for variation_group in self.variation_groups:
            for variation in variation_group.variations:
                modification = variation.modifications.values
                modifications.update(modification)
        return modifications

    def __str__(self):
        return 'campaign_id = {}, {}'.format(self.campaign_id, *self.variation_groups)

    @staticmethod
    def parse(json):
        try:
            campaign_id = json['id']
            variation_groups = list()
            variation_groups_obj = json['variationGroups'] if 'variationGroups' in json else json
            bucketing = type(variation_groups_obj) == list
            if bucketing:
                for variation_group_obj in variation_groups_obj:
                    variation_groups.append(VariationGroup.parse(variation_group_obj))
            else:
                new_variation_group = VariationGroup.parse(json, bucketing)
                if new_variation_group is not None:
                    variation_groups.append(new_variation_group)
            return Campaign(campaign_id, variation_groups)
        except (ValueError, Exception):
            if decorators.customer_event_handler is not None:
                decorators.customer_event_handler.on_log(logging.ERROR,
                                                         "An error occurred while parsing campaign json object.")
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
