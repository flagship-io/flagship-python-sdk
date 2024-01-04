from collections import OrderedDict


class FlagMetadata:
    """
    This class contains the flag campaign information.
    """

    def __init__(self, modification):
        self.campaign_id = modification.campaign_id if modification is not None else ""
        """
        Flag use case id.
        """

        self.variation_group_id = modification.variation_group_id if modification is not None else ""
        """
        Flag use case variation group id.
        """

        self.variation_id = modification.variation_id if modification is not None else ""
        """
        Flag use case variation id.
        """

        self.is_reference = modification.reference if modification is not None else False
        """
        Is Flag from the reference variation.
        """

        self.campaign_type = modification.type if modification is not None else ""
        """
        Flag use case type.
        """

        self.campaign_slug = modification.slug if modification is not None else ""
        """
        Flag use case custom slug.
        """

    def exists(self):
        """
        Check if this Flag exists in Flagship SDK
        @return: True if the Flag exists in Flagship SDK, False otherwise.
        """
        return self.campaign_id != "" and self.variation_group_id != "" and self.variation_id != ""

    def toJson(self):
        return OrderedDict({
            "campaignId": self.campaign_id,
            "variationGroupId": self.variation_group_id,
            "variationId": self.variation_id,
            "isReference": self.is_reference,
            "campaignType": self.campaign_type,
            "campaignSlug": self.campaign_slug
        })
