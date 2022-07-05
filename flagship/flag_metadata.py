import json


class FlagMetadata:

    def __init__(self, modification):
        self.campaign_id = modification.campaign_id if modification is not None else ""
        self.variation_group_id = modification.variation_group_id if modification is not None else ""
        self.variation_id = modification.variation_id if modification is not None else ""
        self.is_reference = modification.reference if modification is not None else False
        self.campaign_type = modification.type if modification is not None else ""
        self.campaign_slug = modification.slug if modification is not None else ""

    def exists(self):
        return self.campaign_id is not "" and self.variation_group_id is not "" and self.variation_id is not ""

    def toJson(self):
        return json.dumps(dict({
            "campaignId": self.campaign_id,
            "variationGroupId": self.variation_group_id,
            "variationId": self.variation_id,
            "isReference": self.is_reference,
            "campaignType": self.campaign_type,
            "campaignSlug": self.campaign_slug
        }))
