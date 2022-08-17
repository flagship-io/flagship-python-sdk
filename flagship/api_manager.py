import json
import traceback

from flagship.status import Status
from flagship.constants import TAG_FETCH_FLAGS
from flagship.decision_manager import DecisionManager
from flagship.http_helper import HttpHelper
from flagship.utils import log_exception


class ApiManager(DecisionManager):

    def __init__(self, config, update_status_callback):
        super(ApiManager, self).__init__(config, update_status_callback)
        update_status_callback(config, Status.READY)

    def get_campaigns_modifications(self, visitor):
        modifications = dict()
        try:
            success, results = HttpHelper.send_campaign_request(visitor)
            if success:
                campaign_json = json.loads(results)
                campaigns = self.parse_campaign_response(campaign_json)
                if campaigns is not None:
                    for campaign in campaigns:
                        variation_groups = campaign.variation_groups
                        for variation_group in variation_groups:
                            variations = variation_group.variations
            #                 add assignment history
                            for k, v in variations.items():
                                modification_values = v.get_modification_values()
                                modifications.update(modification_values)
                self.update_status()
        except Exception as e:
            log_exception(TAG_FETCH_FLAGS, e, traceback.format_exc())
            return False, dict()
        return True, modifications

    def stop(self):
        #todo stop loop
        pass

    def authenticate(self, visitor, authenticated_id):
        if visitor._anonymous_id is None:
            visitor._anonymous_id = visitor._visitor_id
        visitor._visitor_id = authenticated_id
        visitor._is_authenticated = True

    def unauthenticate(self, visitor):
        if visitor._anonymous_id is not None:
            visitor._visitor_id = visitor._anonymous_id
            visitor._anonymous_id = None
            visitor._is_authenticated = False
