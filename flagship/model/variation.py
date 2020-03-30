from flagship.model.modification import Modifications


class Variation:

    def __init__(self, variation_group_id, variation_id, reference, modifications, allocation, selected=False):
        self.variation_group_id = variation_group_id
        self.variation_id = variation_id
        self.reference = reference
        self.modifications = modifications
        self.allocation = allocation
        self.selected = selected

    def __str__(self):
        return 'variation = {} {} {} {} {} {}'.format(self.variation_group_id, self.variation_id, self.reference,
                                                      self.modifications, self.allocation, self.selected)

    @staticmethod
    def parse(variation_group_id, variation_obj):
        variation_id = variation_obj['id']
        reference = variation_obj['reference']
        modifications = Modifications.parse(variation_group_id, variation_id, reference, variation_obj['modifications'])
        allocation = 100 if 'allocation' not in variation_obj else variation_obj['allocation']
        return Variation(variation_group_id, variation_id, reference, modifications, allocation)
