from flagship.model.variation_group import VariationGroup


class Campaign:

    def __init__(self, campaign_id, variation_groups):
        self.campaign_id = campaign_id
        self.variation_groups = variation_groups

    def __str__(self):
        return 'campaign_id = {}, {}'.format(self.campaign_id, *self.variation_groups)

    @staticmethod
    def parse(json):
        campaign_id = json['id']
        variation_groups = list()
        variation_groups_obj = json['variationGroups'] if 'variationGroups' in json else json
        bucketing = type(variation_groups_obj) == list
        if bucketing:
            for variation_group_obj in variation_groups_obj:
                variation_groups.append(VariationGroup.parse(variation_group_obj))
        else:
            variation_groups.append(VariationGroup.parse(json, bucketing))
        return Campaign(campaign_id, variation_groups)

    @staticmethod
    def parse_campaigns(json):
        campaigns = list()
        campaigns_objs = json["campaigns"]
        for campaign_obj in campaigns_objs:
            campaigns.append(Campaign.parse(campaign_obj))
        return campaigns
