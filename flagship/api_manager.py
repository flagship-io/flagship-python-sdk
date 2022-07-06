import json
import traceback

import flagship
from flagship.decision_manager import DecisionManager
from flagship.http_helper import HttpHelper
from flagship.utils import log_exception, pretty_dict
from flagship.status import Status
from flagship.constants import URL_DECISION_API, URL_CAMPAIGNS
from flagship.campaign import Campaign
from flagship.constants import TAG_FETCH_FLAGS


class ApiManager(DecisionManager):

    def __init__(self, config, update_status):
        super(ApiManager, self).__init__(config, update_status)
        # update_status(Status.READY)

    def get_campaigns_modifications(self, visitor):
        modifications = dict()
        try:
            success, results = self.__send_campaign_request(visitor)
            if success:
                # campaigns = Campaign.parse_campaigns(results)
                campaigns = self.parse_campaign_response(results)
                if campaigns is not None:
                    for campaign in campaigns:
                        variation_groups = campaign.variation_groups
                        for variation_group in variation_groups:
                            variations = variation_group.variations
            #                 add assignment history
                            for k, v in variations.items():
                                modification_values = v.get_modification_values()
                                modifications.update(modification_values)
        except Exception as e:
            log_exception(TAG_FETCH_FLAGS, e, traceback.format_exc())
            return False, dict()
        return True, modifications

    def __send_campaign_request(self, visitor):
        config = visitor._configuration_manager.flagship_config
        url = URL_DECISION_API + config.env_id + URL_CAMPAIGNS
        headers = {
            "x-api-key": config.api_key,
            "x-sdk-client": "python",
            "x-sdk-version": flagship.__version__
        }
        content = {
            "visitorId": visitor._visitor_id,
            "anonymousId": visitor._anonymous_id,
            "trigger_hit": False,
            "context": visitor._context

        }
        success, response = HttpHelper.send_http_request(HttpHelper.RequestType.POST, url, headers, content,
                                                         config.timeout)
        if success and len(response.content) > 0:
            # return True, json.loads(response.content.decode("utf-8"))
            return True, response.content
        else:
            return False, dict()

    def stop(self):
        pass
