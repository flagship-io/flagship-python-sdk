import flagship
from flagship.decision_manager import DecisionManager
from flagship.http_helper import HttpHelper
from flagship.status import Status
from flagship.constants import _URL_DECISION_API, _URL_CAMPAIGNS


class ApiManager(DecisionManager):

    def __init__(self, config, update_status):
        super(ApiManager, self).__init__(config, update_status)
        # update_status(Status.READY)

    def get_campaigns_modifications(self, visitor):
        campaigns = dict()
        try:
            success, campaigns = self.__send_campaign_request(visitor)
        except:
            return False, dict()
        return success, campaigns

    def __send_campaign_request(self, visitor):
        config = visitor.configuration_manager.flagship_config
        url = _URL_DECISION_API + config.env_id + _URL_CAMPAIGNS
        headers = {
            "x-api-key": config.api_key,
            "x-sdk-client": "python",
            "x-sdk-version": flagship.__version__
        }
        content = {
            "visitorId": visitor.visitor_id,
            "anonymousId": visitor.anonymous_id,
            "trigger_hit": False,
            "context": visitor.context

        }
        success, response = HttpHelper.send_http_request(HttpHelper.RequestType.POST, url, headers, content,
                                                         config.timeout)
        self.update_status(Status.READY)
        if success:
            return response.status_code in range(200, 305), dict()
        else:
            return False, dict()

    def stop(self):
        pass
