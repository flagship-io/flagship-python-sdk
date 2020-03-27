import json


class VariationGroup:

    def __init__(self, variation_group_id, variations, targeting_groups, selected_variation_id):
        self.variation_group_id = variation_group_id
        self.variations = variations
        self.targeting_groups = targeting_groups
        self.selected_variation_id = selected_variation_id

    def __str__(self):
        return 'variation_group_id = {}'.format(self.variation_group_id)

    @staticmethod
    def parse(variation_group_obj, bucketing):
        variation_group_id = variation_group_obj['id'] if bucketing else variation_group_obj['variationGroupId']
        return VariationGroup(variation_group_id, "", "", "")
